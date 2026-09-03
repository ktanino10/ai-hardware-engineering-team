#!/usr/bin/env python3
"""Generate hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb from the
Design-Complete KiCad schematic (hardware/schematic/bench-imu-01/) and its
exported netlist/BOM.

Why this script exists (tooling honesty, matches this repo's own
conventions): no MCP tool or `kicad-cli` subcommand in this environment can
*create or interactively route* a PCB -- `kicad-cli pcb` only offers
`drc`/`export`/`import`/`render`/`upgrade`, and every `kicad-*` MCP tool is
read/analyze-only (`docs/architecture.md` section 5.2). This script instead
uses KiCad 10.0.1's own bundled Python 3.9 interpreter's `pcbnew` module
(genuinely importable, confirmed this session -- see
`hardware/pcb/README.md`) to construct a real `BOARD()` object programmatically:
load real footprints from the installed KiCad libraries (or this project's
own `bench-imu-01.pretty` for F1's custom footprint), place them, assign
real net connectivity (parsed from `kicad-cli sch export netlist`'s own
output -- never hand-guessed), pour ground/power planes, route the
remaining signal nets as explicit copper tracks/vias, and add a board
outline + mounting holes. No autorouter is used (see README for why).

Run with KiCad's own bundled Python (NOT the system/venv python3 -- pcbnew
is only importable there):
    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
        generate_pcb.py

Re-exports the schematic's netlist/BOM itself via a `kicad-cli` subprocess
call every run, so the schematic is always the live source of truth --
never a stale hand-copied net list.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
SCH_DIR = HERE.parent.parent / "schematic" / "bench-imu-01"
SCH_FILE = SCH_DIR / "bench-imu-01.kicad_sch"
PROJECT_NAME = "bench-imu-01"

STD_FP = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
LOCAL_FP = SCH_DIR / "bench-imu-01.pretty"

MM = pcbnew.FromMM

# Board outline: 130mm x 80mm -- sized from real summed footprint/courtyard
# area (see the placement table below) plus assembly/routing margin, and
# from the design doc's own explicit instruction (section 9/10) to keep the
# motor-driver group (U5/U6/M1/J4 and their high-current traces) physically
# separated from the IMU (U2) for vibration/thermal isolation -- REQUOTE
# 308 (Rev 3) already relaxed the old 60x40mm ceiling to "whatever the
# approved parts need," soft ~150mm desk-scale sanity bound, so this is not
# constrained to the old Rev 2 envelope.
BOARD_W = 150.0
BOARD_H = 95.0
BOARD_MARGIN = 5.0  # keep-out from the physical edge for silkscreen/pads

# Zone split: Zone 1 (logic: USB/MCU/IMU/UART/SWD, Rev 2 baseline) occupies
# the left ~65mm; a clear channel separates it from Zone 2 (motor
# driver + supervisory controller + barrel jack, new Rev 3-5), which
# occupies the right ~65mm -- the concrete geometry satisfying the design
# doc's own separation instruction (the *reason* for separation is already
# on record there; this is PCB Engineer's own placement decision realizing
# it).
ZONE1_X0, ZONE1_X1 = BOARD_MARGIN, 68.0
GAP_X0, GAP_X1 = 68.0, 78.0
ZONE2_X0, ZONE2_X1 = 78.0, BOARD_W - BOARD_MARGIN


# ---------------------------------------------------------------------------
# Step 1: re-export the netlist/BOM from the live schematic (kicad-cli --
# the same verified workaround Circuit Engineer already uses for ERC/BOM,
# docs/architecture.md section 5.2) so this script never drifts from the
# real schematic.
# ---------------------------------------------------------------------------

def export_netlist_and_bom() -> tuple[str, str]:
    net_path = HERE / "_netlist.tmp.net"
    bom_path = HERE / "_bom.tmp.csv"
    subprocess.run(
        ["kicad-cli", "sch", "export", "netlist", "-o", str(net_path), str(SCH_FILE)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["kicad-cli", "sch", "export", "bom", "-o", str(bom_path), str(SCH_FILE)],
        check=True, capture_output=True,
    )
    net_text = net_path.read_text()
    bom_text = bom_path.read_text()
    net_path.unlink()
    bom_path.unlink()
    return net_text, bom_text


def parse_bom(bom_text: str) -> dict[str, str]:
    """Return {ref: 'Library:FootprintName'} from the exported BOM CSV."""
    out: dict[str, str] = {}
    lines = bom_text.splitlines()[1:]
    for line in lines:
        if not line.strip():
            continue
        cells = line.strip().strip('"').split('","')
        ref, _value, footprint = cells[0], cells[1], cells[2]
        out[ref] = footprint
    return out


def parse_netlist(net_text: str) -> dict[str, list[tuple[str, str]]]:
    """Return {net_name: [(ref, pin_number), ...]} from a `kicad-cli sch
    export netlist`-produced plain-format file. Real brace-depth-tracked
    parse of each `(net ...)` block, not a fragile single-line regex --
    this file has nested parens per node.
    """
    nets: dict[str, list[tuple[str, str]]] = {}
    i = 0
    n = len(net_text)
    while True:
        start = net_text.find("(net", i)
        if start == -1:
            break
        if net_text[start:start + 5] not in ("(net\n", "(net "):
            i = start + 4
            continue
        depth = 0
        j = start
        while j < n:
            if net_text[j] == "(":
                depth += 1
            elif net_text[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        block = net_text[start:j + 1]
        i = j + 1
        name_m = re.search(r'\(name "([^"]*)"\)', block)
        if not name_m:
            continue
        name = name_m.group(1).lstrip("/")
        if not name or name.startswith("unconnected-"):
            continue
        node_pairs = re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', block)
        nets.setdefault(name, []).extend(node_pairs)
    return nets


# ---------------------------------------------------------------------------
# Step 2: placement -- explicit (x, y, rotation_degrees) per ref, in mm from
# the board's bottom-left origin. Grouped by schematic sub-block, laid out
# in simple rows (generous, fixed pitch per component size class -- not a
# packed/optimal layout, but a real, non-overlapping, current-aware one).
# ---------------------------------------------------------------------------

PLACEMENT: dict[str, tuple[float, float, float]] = {
    # --- Zone 1: Logic (USB/MCU/IMU/UART/SWD) -------------------------
    "J1": (13.0, 25.0, 90.0),     # USB-C receptacle, left board edge
    "R1": (23.0, 15.0, 0.0),
    "R2": (23.0, 20.0, 0.0),
    "U4": (31.0, 25.0, 0.0),      # ESD SOT-23-6
    "C1": (39.0, 15.0, 0.0),
    "U3": (47.0, 25.0, 0.0),      # LDO SOT-23-5
    "C2": (55.0, 15.0, 0.0),
    "U1": (36.0, 48.0, 0.0),      # MCU LQFP-32 (biggest in this zone)
    "C3": (20.0, 42.0, 0.0),
    "C4": (20.0, 52.0, 0.0),
    "C8": (52.0, 42.0, 0.0),
    "C5": (52.0, 52.0, 0.0),
    "SW1": (60.0, 58.0, 0.0),
    "U2": (16.0, 68.0, 0.0),      # IMU LGA-14
    "R3": (16.0, 56.0, 0.0),
    "R4": (23.0, 56.0, 0.0),
    "C6": (8.0, 80.0, 0.0),
    "C7": (15.0, 85.0, 0.0),
    "C9": (22.0, 80.0, 0.0),
    "R5": (55.0, 68.0, 0.0),
    "D1": (55.0, 75.0, 0.0),
    "J2": (62.0, 10.0, 0.0),      # UART header, top edge
    "J3": (62.0, 22.0, 0.0),      # SWD header, top edge

    # --- Zone 2: Motor driver + supervisory controller (new Rev 3-5) --
    "J4": (83.0, 30.0, 90.0),     # barrel jack, right board edge area
    "F1": (100.0, 30.0, 0.0),
    "F2": (83.0, 8.0, 0.0),        # NEW (ISS-032 fix): second PTC fuse,
                                   # J4 sleeve/GND leg, mirrors F1's role
                                   # in the tip/VM_MOTOR leg. Moved further
                                   # from J4 than the first placement
                                   # attempt (which put its courtyard only
                                   # 12mm from J4's centre and genuinely
                                   # collided -- J4's own large, 90-deg-
                                   # rotated barrel-jack courtyard extends
                                   # up to Y=23.4, closer to F2 than
                                   # expected; verified via DRC, not
                                   # assumed clear by inspection alone).
    "D2": (116.0, 30.0, 0.0),
    "D3": (116.0, 18.0, 0.0),
    "C16": (100.0, 18.0, 0.0),
    "U6": (110.0, 52.0, 0.0),     # TPS26631PWPR, HTSSOP-20
    "R11": (85.0, 44.0, 0.0),
    "R12": (92.0, 44.0, 0.0),
    "R13": (99.0, 44.0, 0.0),
    "R14": (85.0, 52.0, 0.0),
    "R15": (92.0, 52.0, 0.0),
    "C17": (99.0, 52.0, 0.0),
    "U5": (110.0, 78.0, 0.0),     # DRV10983, HTSSOP-24
    "C10": (85.0, 68.0, 0.0),
    "C11": (92.0, 68.0, 0.0),
    "C12": (99.0, 68.0, 0.0),
    "R9": (85.0, 86.0, 0.0),
    "C13": (92.0, 86.0, 0.0),
    "C14": (99.0, 86.0, 0.0),
    "R10": (128.0, 68.0, 0.0),
    "R6": (128.0, 76.0, 0.0),
    "R7": (128.0, 84.0, 0.0),
    "R8": (130.0, 44.0, 0.0),
    "C15": (130.0, 52.0, 0.0),
    "M1": (140.0, 52.0, 90.0),    # 3-pin phase-wire terminal block, right edge
}

# Mounting holes (M2.5, matching this design's own convention -- design doc
# section 10). Placed near each corner, inset per REQ-304.
MOUNTING_HOLES = [
    (BOARD_MARGIN + 3.0, BOARD_MARGIN + 3.0),
    (BOARD_W - BOARD_MARGIN - 3.0, BOARD_MARGIN + 3.0),
    (BOARD_MARGIN + 3.0, BOARD_H - BOARD_MARGIN - 3.0),
    (BOARD_W - BOARD_MARGIN - 3.0, BOARD_H - BOARD_MARGIN - 3.0),
]

# Decorative silkscreen mark (GitHub Invertocat + the designer's own handle).
# Purely graphical: no pads, no net, excluded from BOM and pick-and-place, zero
# electrical/mechanical function. It is NOT schematic-derived (it has no symbol
# and appears in no netlist), so unlike every other footprint above it cannot be
# recovered from the schematic -- it therefore has to be placed explicitly here
# or a regeneration run would silently drop it (ISS-048).
#
# Geometry is not re-derived from the upstream PNG asset at build time (that
# would make the board depend on a network fetch and on Pillow's threshold
# behaviour staying bit-identical). It is instead vendored as a real footprint
# in this project's own library, `bench-imu-01.pretty`, and loaded through the
# exact same `FootprintLoad()` path already used for F1's custom footprint.
LOGO_FP_NAME = "Logo_GitHub_ktanino10"
LOGO_POS = (131.0, 20.0)  # DRC-verified clear of MH2, D2/D3 and the R-row at y=44
LOGO_ROT = 0




# ---------------------------------------------------------------------------
# Step 3: board construction (footprints, nets, outline, stackup, GND pour,
# routing, mounting holes).
# ---------------------------------------------------------------------------

# Trace widths, sized per net current class (Hardware Reviewer checklist
# item 19 -- docs/architecture-evolution.md section 37): standard 1oz
# external-copper PCB trace-width tables (IPC-2221-derived rule-of-thumb
# figures, not a fully worked per-net IPC-2221 calculation -- ESTIMATE,
# disclosed) give ~30-35 mil (~0.75-0.9mm) for 3A at a 10C rise on an
# external layer; 1.0mm is used below for real margin on this design's
# up-to-3A worst-case nets. Everything else is a low-current logic/bias
# signal at the standard 0.25mm (10 mil) fine-pitch width.
WIDTH_SIGNAL = 0.25
WIDTH_POWER = 0.4
WIDTH_HIGH_CURRENT = 1.0

HIGH_CURRENT_NETS = {
    "VM_MOTOR_RAW", "VM_MOTOR_F1", "VM_MOTOR", "U5_VCC",
    "MOTOR_PHASE_U", "MOTOR_PHASE_V", "MOTOR_PHASE_W",
    # J4_GND_RAW -- FIXED (Hardware Reviewer Cycle 8, ISS-039, HIGH): this
    # is the ISS-032 fix's new intermediate net between J4 pin1 and F2
    # pin1 -- electrically it is the same board-wide ground RETURN
    # current path that "GND" itself already gets HIGH_CURRENT width for
    # (see the width-selection logic below, `net_name == "GND"`), just
    # renamed because it sits upstream of F2 in this design's own
    # net-splitting convention (every series element's two terminals are
    # a distinct net, same convention used throughout this schematic).
    # Omitting it here left it silently routed at WIDTH_SIGNAL (0.25mm)
    # instead of WIDTH_HIGH_CURRENT (1.0mm) -- a real regression the
    # reviewer caught: previously J4 pin1 (as a direct GND member) had
    # three 1.0mm GND tracks reaching it; the fix had cut that to one
    # 0.25mm trace, ~12x less copper, undersized ~3.1x against this
    # design's own 2A continuous basis, and -- worse -- specifically
    # defeating F2's purpose (a trace this thin could fuse open before
    # the PTC even trips, losing the automatically-resettable behavior
    # and creating an uncontrolled burn point instead of a clean,
    # resettable fault response).
    "J4_GND_RAW",
}
POWER_NETS = {"VBUS_5V", "3V3", "U5_V3P3"}

# All footprints are front-side (FootprintLoad-loaded, no back-side flip),
# so every SMD pad's own copper is on F.Cu -- every net defaults to F.Cu
# routing so tracks actually share a copper layer with the pads they
# connect. Nets moved to In2.Cu (via a via dropped at each pad) after an
# initial DRC pass found real same-layer crossings on F.Cu -- kept as an
# explicit override set populated from real DRC findings (see README's
# iteration log), not pre-guessed.
INNER_LAYER_OVERRIDE: dict[str, str] = {}

# ISS-036 whole-board-aware reroute overrides: specific track segment(s)
# (identified by net name and endpoints, in mm) whose default MST/
# L-shape-bend path was found by real DRC to short against another net's
# copper -- and for which a genuine, whole-board-checked detour was
# found and verified (see `_apply_reroute_overrides` and the ISS-036
# section near the end of `build_board` for the full rationale/method).
# Each entry is (net, [source segment endpoint pairs to remove],
# replacement path) -- most fixes remove exactly one source segment, but
# the U3-area fix removes TWO (the default algorithm draws an L-shaped
# hop as 2 separate track objects meeting at a bend point, and that bend
# point itself is what needs to move, so both of that hop's segments are
# replaced together by one new path). Matched by (net, rounded endpoint
# position) in either direction, not exact float equality or object
# identity, so this survives a full script re-run; if the routing
# algorithm's output ever changes enough that a listed segment no longer
# exists, `_apply_reroute_overrides` prints a loud warning and skips that
# entry rather than silently doing nothing.
REROUTE_OVERRIDE: list[
    tuple[str, list[tuple[tuple[float, float], tuple[float, float]]], list[tuple[float, float]]]
] = [
    # GND through-via at U4's pin 2 sits directly on VBUS_5V's own
    # default straight In2.Cu run from J1 toward U4. Detour around it
    # while keeping both real endpoints (J1's VBUS pad; U4's VBUS pad)
    # exactly fixed.
    (
        "VBUS_5V",
        [((9.32, 25.0), (32.138, 25.0))],
        [(9.32, 25.0), (32.138, 26.0), (32.138, 25.0)],
    ),
    # GND through-via at U3's own pin 2 sits exactly at the bend point of
    # VBUS_5V's default L-shaped hop toward U3's pin 1 -- both of that
    # hop's 2 segments (sharing the bend at (45.862,25.0)) are replaced
    # by one new path with the bend moved to (32.138,24.05) instead,
    # keeping both real endpoints (U4's VBUS pad; U3's VBUS pad) fixed.
    (
        "VBUS_5V",
        [((45.862, 24.05), (45.862, 25.0)), ((45.862, 25.0), (32.138, 25.0))],
        [(32.138, 25.0), (32.138, 24.05), (45.862, 24.05)],
    ),
    # VM_MOTOR's default straight run toward J4/F1's area passes too
    # close to unrelated copper; a 4-bend step-over detour (found by the
    # same whole-board-aware search) clears it while keeping both real
    # endpoints fixed.
    (
        "VM_MOTOR",
        [((113.85, 18.0), (99.225, 18.0))],
        [
            (113.85, 18.0), (102.275, 18.0), (102.275, 16.8),
            (99.275, 16.8), (99.275, 18.0), (99.225, 18.0),
        ],
    ),
    # --- ISS-036 continued (solder_mask_bridge sweep): a dedicated
    # whole-board-aware search against all 206 uniquely-identified
    # solder_mask_bridge (track, pad) conflicts found only these 2
    # additional tractable fixes (~1% yield, reconfirming the same
    # technique ceiling already established for the outer-layer
    # shorting_items sweep) -- see hardware/pcb/README.md for the full
    # search methodology and yield analysis.
    #
    # 3V3's default straight run toward U1 passes directly under U1's own
    # unrelated pin 1 pad, bridging their solder-mask apertures (3
    # separate DRC entries against 3 different nearby pads, all on this
    # one track). A localized step-over clears all of them while keeping
    # both real endpoints fixed.
    (
        "3V3",
        [((31.825, 47.6), (31.825, 42.0))],
        [(31.825, 47.6), (28.825, 47.6), (31.825, 42.0)],
    ),
    # VM_MOTOR's default straight run near J4/M1's area (a separate
    # segment from the fix above) passes too close to unrelated copper.
    (
        "VM_MOTOR",
        [((107.1375, 30.0), (113.85, 30.0))],
        [(107.1375, 30.0), (110.85, 27.0), (113.85, 30.0)],
    ),
]


def _apply_reroute_overrides(board: "pcbnew.BOARD") -> int:
    """Replace each REROUTE_OVERRIDE entry's source track segment(s) with
    its verified detour path. Matches by (net name, rounded endpoints)
    in either direction, not object identity, since this runs on a
    freshly (re)built board every script execution. Returns the number
    of overrides actually applied; any entry whose source segment(s)
    can no longer all be found prints a loud warning and is skipped (not
    silently ignored, and not partially applied) -- that means the
    routing algorithm's output has drifted since this override was
    derived, and it needs re-deriving against the current routing, not
    blind trust that a stale detour is still correct or even still
    needed.
    """

    def close(a: float, b: float) -> bool:
        return abs(a - b) < 0.01

    def find_track(net_name: str, p1: tuple[float, float], p2: tuple[float, float]):
        for t in board.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T or t.GetNetname() != net_name:
                continue
            sx, sy = pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y)
            ex, ey = pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)
            forward = close(sx, p1[0]) and close(sy, p1[1]) and close(ex, p2[0]) and close(ey, p2[1])
            backward = close(sx, p2[0]) and close(sy, p2[1]) and close(ex, p1[0]) and close(ey, p1[1])
            if forward or backward:
                return t
        return None

    applied = 0
    for net_name, source_segments, path in REROUTE_OVERRIDE:
        targets = [find_track(net_name, p1, p2) for p1, p2 in source_segments]
        if any(t is None for t in targets):
            print(
                f"WARNING: REROUTE_OVERRIDE for {net_name} {source_segments} "
                "found no matching track for at least one source segment -- "
                "this fix is stale (routing algorithm output changed) and was "
                "NOT applied; re-derive it against the current routing before "
                "trusting this override again."
            )
            continue
        layer = targets[0].GetLayer()
        width = targets[0].GetWidth()
        net_item = targets[0].GetNet()
        for t in targets:
            board.Remove(t)
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            seg = pcbnew.PCB_TRACK(board)
            seg.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
            seg.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
            seg.SetLayer(layer)
            seg.SetWidth(width)
            seg.SetNet(net_item)
            board.Add(seg)
        applied += 1
    return applied


def fp_lib_path(lib: str) -> str:
    if lib == PROJECT_NAME:
        return str(LOCAL_FP)
    return str(STD_FP / f"{lib}.pretty")


def build_board(footprints: dict[str, str], nets: dict[str, list[tuple[str, str]]]) -> None:
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # A freshly-constructed BOARD() has zeroed-out design rules (no project
    # template to inherit sensible GUI defaults from) -- explicitly set
    # standard, widely-manufacturable fab-capability values rather than
    # leaving clearance/solder-mask rules at an unrealistic 0, which made
    # DRC's solder-mask/clearance checks flag far more than a real,
    # normally-configured board would.
    ds = board.GetDesignSettings()
    ds.m_MinClearance = MM(0.15)
    ds.m_SolderMaskExpansion = MM(0.05)
    ds.m_SolderMaskMinWidth = MM(0.1)
    ds.m_SolderMaskToCopperClearance = MM(0.05)
    ds.m_HoleClearance = MM(0.25)
    ds.m_HoleToHoleMin = MM(0.25)
    ds.m_CopperEdgeClearance = MM(0.3)

    # --- Board outline (Edge.Cuts rectangle) --------------------------
    outline = pcbnew.PCB_SHAPE(board)
    outline.SetShape(pcbnew.SHAPE_T_RECT)
    outline.SetStart(pcbnew.VECTOR2I(MM(0), MM(0)))
    outline.SetEnd(pcbnew.VECTOR2I(MM(BOARD_W), MM(BOARD_H)))
    outline.SetLayer(pcbnew.Edge_Cuts)
    outline.SetWidth(MM(0.15))
    board.Add(outline)

    # --- Footprints ----------------------------------------------------
    fp_instances: dict[str, "pcbnew.FOOTPRINT"] = {}
    for ref, fp_id in footprints.items():
        lib, name = fp_id.split(":", 1)
        fp = pcbnew.FootprintLoad(fp_lib_path(lib), name)
        if fp is None:
            raise RuntimeError(f"Could not load footprint {fp_id!r} for {ref}")
        fp.SetReference(ref)
        x, y, rot = PLACEMENT[ref]
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientationDegrees(rot)
        board.Add(fp)
        fp_instances[ref] = fp

    # --- Mounting holes --------------------------------------------------
    for i, (x, y) in enumerate(MOUNTING_HOLES, start=1):
        mh = pcbnew.FootprintLoad(str(STD_FP / "MountingHole.pretty"), "MountingHole_2.7mm_M2.5")
        mh.SetReference(f"MH{i}")
        mh.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        board.Add(mh)

    # --- Decorative silkscreen mark (ISS-048) ----------------------------
    # Placed from this project's own footprint library rather than rebuilt
    # from the upstream image, so a regeneration run reproduces the exact
    # committed geometry. Fail loud if the library entry is missing: dropping
    # it silently is precisely the regression this block exists to prevent.
    logo = pcbnew.FootprintLoad(str(LOCAL_FP), LOGO_FP_NAME)
    if logo is None:
        raise RuntimeError(
            f"Could not load decorative footprint {LOGO_FP_NAME!r} from {LOCAL_FP}"
        )
    logo.SetPosition(pcbnew.VECTOR2I(MM(LOGO_POS[0]), MM(LOGO_POS[1])))
    logo.SetOrientationDegrees(LOGO_ROT)
    board.Add(logo)

    # --- Nets: create one NETINFO_ITEM per net, assign every pad --------
    net_items: dict[str, "pcbnew.NETINFO_ITEM"] = {}
    pad_positions: dict[tuple[str, str], tuple[int, int, int]] = {}  # (ref,pin) -> (x_nm, y_nm, layer)
    pad_is_tht: dict[tuple[str, str], bool] = {}
    netcode = 1
    for net_name, nodes in nets.items():
        ni = pcbnew.NETINFO_ITEM(board, net_name, netcode)
        board.Add(ni)
        net_items[net_name] = ni
        for ref, pin in nodes:
            fp = fp_instances.get(ref)
            if fp is None:
                print(f"WARNING: {ref} not placed, cannot assign net {net_name}")
                continue
            # Hardware Reviewer Cycle 6 (ISS-033/034/035): some real
            # footprints legitimately have MULTIPLE physical copper pads
            # sharing one pad NUMBER -- a PowerPAD's thermal-via sub-pad
            # array (U6: 17 sub-pads on "21"), a USB-C shield's multiple
            # mechanical tabs (J1: 4 pads on "SH"), or a THT switch's
            # doubled per-terminal pads (SW1: 2 pads per terminal number).
            # `FindPadByNumber` returns only the FIRST match -- using it
            # alone left every other same-numbered physical pad genuinely
            # unconnected (no net at all), invisible to DRC's
            # `unconnected_items` check (a real, independently-reproduced
            # 0 throughout this script's own DRC iterations) since that
            # check only flags a missing schematic-to-copper connection,
            # not a footprint pad that was never assigned a net to begin
            # with. Enumerate and net EVERY physical pad with this number,
            # not just the first.
            matching_pads = [p for p in fp.Pads() if p.GetNumber() == pin]
            if not matching_pads:
                print(f"WARNING: {ref} pin {pin} has no matching pad (net {net_name})")
                continue
            for pad in matching_pads:
                pad.SetNet(ni)
            # Choose the representative/"hub" pad as the LARGEST-area member
            # of the group, not simply matching_pads[0] (arbitrary footprint-
            # file order). This matters when the group mixes small
            # individually-spaced sub-pads (e.g. a PowerPAD's 0.6x0.6mm
            # thermal-via array, each pad ~1.3mm from its neighbours, so
            # neighbour-to-neighbour bounding boxes do NOT intersect) with
            # one or two much larger pads that represent the actual shared
            # copper land those vias sit inside (U6: a 3.4x6.5mm F.Cu land +
            # 3.2x5.8mm B.Cu land, both large enough to contain the whole
            # via grid). Picking an arbitrary small via as "pad[0]" and
            # pairwise-testing it against its equally-small neighbours was
            # exactly the bug behind ISS-038 below: none of those pairwise
            # tests ever intersect (small vias don't touch each other), so
            # every one of them was (wrongly) judged to need its own bridge
            # track. Picking the largest-area pad as the hub instead
            # correctly recognizes that every small via's bounding box sits
            # INSIDE the land's much larger bounding box.
            hub_pad = max(matching_pads, key=lambda p: p.GetBoundingBox().GetArea())
            pos = hub_pad.GetPosition()
            pad_positions[(ref, pin)] = (pos.x, pos.y, hub_pad.GetLayerSet().Contains(pcbnew.B_Cu))
            pad_is_tht[(ref, pin)] = hub_pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH
            # Fixed alongside the multi-pad net assignment above (Hardware
            # Reviewer Cycle 6, ISS-033/034/035 follow-up): giving every
            # physical pad a net is necessary but not sufficient -- the
            # later MST/Step-A routing below only ever routes to the ONE
            # representative point stored in pad_positions[(ref, pin)]
            # (the hub pad's position), so any OTHER physical pad sharing
            # this number (SW1's doubled terminal pads, J1's other shield
            # tabs, U6 PowerPAD's other sub-pads) would still end up
            # copper-isolated from its own net -- a real, DRC-visible
            # `unconnected_items` violation, confirmed by re-running DRC
            # after the net-assignment-only fix (2 unconnected SW1 pad-2
            # instances surfaced). Bridge every extra physical pad directly
            # to the hub pad here, at each pad's own position -- independent
            # of and before the later routing stages, since those operate
            # at (ref, pin) granularity and have no visibility into
            # same-numbered pad multiplicity.
            #
            # Revised (Hardware Reviewer Cycle 7, ISS-038, HIGH -- this
            # bridge step's own first attempt introduced a NEW defect, and
            # this session's own follow-up fix attempt initially only
            # partially resolved it -- see below): a PowerPAD/exposed-pad-
            # plus-thermal-via-array footprint (U6) has every same-numbered
            # sub-pad's copper shape already geometrically overlapping the
            # shared land -- the group was already electrically joined by
            # shared copper before any bridge track existed, so drawing one
            # anyway was not just redundant, it blindly crossed the
            # unrelated U6_ILIM net running through that same dense region
            # (12 new `tracks_crossing` violations, independently reproduced
            # across 4 DRC runs). Two fixes, both per the finding's own
            # recommendation: (1) skip the bridge entirely when a pad's
            # copper already overlaps the hub pad's copper (bounding-box
            # intersection against the LARGEST/hub pad, not an arbitrary
            # small pad -- see the hub_pad selection above, which this
            # session's first attempt at this fix got wrong by testing
            # against matching_pads[0], an arbitrary small via rather than
            # the actual shared land, silently reducing but not eliminating
            # the defect: 12 ILIM/GND crossings became 9, not 0, on the
            # first re-verification re-run); (2) when a bridge IS drawn,
            # pick its layer from the actual intersection of both pads' own
            # layer sets instead of hard-coding F.Cu (the finding's second,
            # latent defect: a B.Cu-only target pad bridged on F.Cu silently
            # bridges nothing).
            if len(matching_pads) > 1:
                hub_bbox = hub_pad.GetBoundingBox()
                x0, y0 = hub_pad.GetPosition()
                for extra in matching_pads:
                    if extra is hub_pad:
                        continue
                    if hub_bbox.Intersects(extra.GetBoundingBox()):
                        # Already electrically joined by overlapping copper
                        # (e.g. a thermal via sitting inside the shared
                        # exposed-pad land) -- a bridge track here would be
                        # redundant at best and, per ISS-038, actively
                        # harmful (crosses unrelated nets) at worst.
                        continue
                    x1, y1 = extra.GetPosition()
                    bridge_layer = pcbnew.F_Cu
                    for candidate in (pcbnew.F_Cu, pcbnew.B_Cu):
                        if hub_pad.GetLayerSet().Contains(candidate) and extra.GetLayerSet().Contains(candidate):
                            bridge_layer = candidate
                            break
                    seg = pcbnew.PCB_TRACK(board)
                    seg.SetStart(pcbnew.VECTOR2I(x0, y0))
                    seg.SetEnd(pcbnew.VECTOR2I(x1, y1))
                    seg.SetLayer(bridge_layer)
                    seg.SetWidth(MM(WIDTH_SIGNAL))
                    seg.SetNet(ni)
                    board.Add(seg)
        netcode += 1


    # --- GND net: a solid copper pour on In1.Cu (a genuine, justified
    # stack-up decision -- see README/architecture-evolution.md section 37
    # for the EMI/ground-return reasoning). An earlier session found
    # `pcbnew.ZONE_FILLER.Fill()` reproducibly segfaulted here (confirmed 3
    # ways: bare call, with a `wx.App()` initialized first, and with
    # `board.BuildConnectivity()` called first) and fell back to routing
    # GND as explicit discrete tracks on In1.Cu instead (same as every
    # other net) -- electrically valid and DRC-checkable, but not a solid
    # continuous copper region, and (per ISS-036's own root-cause analysis)
    # the direct cause of a real, reproducible class of `shorting_items`
    # DRC violations: an ordinary through-via of any OTHER net spans every
    # copper layer including In1.Cu, and with GND on that layer as thin
    # discrete tracks rather than a filled zone, KiCad has no automatic
    # anti-pad clearance to keep those via barrels clear of nearby GND
    # copper -- a filled zone gets that clearance handling for free.
    #
    # ISS-036 follow-up (2026-09, this session): re-isolated exactly when
    # `Fill()` crashes vs. works, since the record so far looked like
    # unexplained flakiness. It is NOT flaky: `Fill()` against THIS
    # zone/board segfaults 100% of the time when called in the SAME
    # process that incrementally built the board via the Python API (True
    # both right after this zone is declared, before any via exists, AND
    # again after deferring the call to the very end of `build_board()`,
    # after every net's tracks/vias are already placed -- ordering isn't
    # the variable). It succeeds 100% of the time (15/15 across this
    # session's testing) when called against a board freshly loaded via
    # `pcbnew.LoadBoard()` from an already-saved `.kicad_pcb` file -- e.g.
    # a minimal from-scratch reproduction with a single zone and no other
    # complexity does NOT crash in-process either, so this is specific to
    # this real, complex board's in-memory construction state, not zone
    # fill in general. The fix below acts on that exact distinction: save
    # the fully-connected board first (GND still carried by its normal
    # discrete In1.Cu tracks, the known-safe path -- unconditionally, see
    # Step C), THEN reload that just-written file fresh in a brand new
    # `BOARD` object and attempt the fill there. If it segfaults even in
    # the reloaded object (untested territory, no evidence it would, but
    # not asserted as impossible either), the crash happens AFTER a valid,
    # fully-connected board is already safely on disk -- fail-loud, not
    # fail-silent-with-a-broken-board.
    gnd_zone = pcbnew.ZONE(board)
    gnd_zone.SetLayer(board.GetLayerID("In1.Cu"))
    gnd_zone.SetNetCode(net_items["GND"].GetNetCode())
    gnd_zone.SetLocalClearance(MM(0.3))
    gnd_zone.SetMinThickness(MM(0.2))
    outline_poly = gnd_zone.Outline()
    outline_poly.NewOutline()
    m = 1.0  # pour to 1mm inside the board edge
    for (px, py) in [(m, m), (BOARD_W - m, m), (BOARD_W - m, BOARD_H - m), (m, BOARD_H - m)]:
        outline_poly.Append(MM(px), MM(py))
    board.Add(gnd_zone)

    # --- Route every net as explicit copper tracks (+ vias where a net is
    # assigned to a non-F.Cu layer). All footprints loaded via
    # FootprintLoad() are front-side, so every SMD pad's own copper is on
    # F.Cu -- any net not routed on F.Cu needs a via at each pad to reach
    # it (a track on a different layer than its pad, with no via, is NOT
    # electrically connected, even at the same X/Y).
    #
    # GND is routed entirely on In1.Cu (isolated from every other net's
    # layer pool on its own dedicated layer) -- it is by far this board's
    # largest, most-branching net (a star topology touching nearly every
    # component), and an initial single-layer (F.Cu-for-everything) DRC
    # pass found it was the dominant contributor to the resulting
    # `tracks_crossing`/`shorting_items` findings (every sampled violation
    # involved GND). Isolating it removes that dominant source outright,
    # rather than chasing each individual crossing one at a time.
    #
    # Every other net is greedily assigned to F.Cu, In2.Cu, or B.Cu by a
    # simple axis-aligned-bounding-box overlap check against nets already
    # assigned to each candidate layer -- a real, if approximate (not an
    # exact segment-intersection router), heuristic that substantially
    # reduces same-layer crossings before DRC, with any specific remaining
    # collision fixed via `INNER_LAYER_OVERRIDE` from real DRC findings
    # (see README's iteration log), not pre-guessed net-by-net.
    def bbox(points):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return (min(xs), min(ys), max(xs), max(ys))

    def overlaps(a, b):
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

    def add_track(x1, y1, x2, y2, layer_id, width, net_item):
        seg = pcbnew.PCB_TRACK(board)
        seg.SetStart(pcbnew.VECTOR2I(x1, y1))
        seg.SetEnd(pcbnew.VECTOR2I(x2, y2))
        seg.SetWidth(width)
        seg.SetLayer(layer_id)
        seg.SetNet(net_item)
        board.Add(seg)

    def add_via(x, y, net_item):
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(x, y))
        via.SetDrill(MM(0.3))
        via.SetWidth(MM(0.6))
        via.SetNet(net_item)
        board.Add(via)

    f_cu = board.GetLayerID("F.Cu")

    # Step A: collapse same-component, same-net pin clusters to ONE
    # representative point per component, bridging the raw pins with a
    # short local F.Cu chain first. Real fine-pitch ICs in this design
    # (U5 HTSSOP-24 / U6 HTSSOP-20, both 0.65mm pin pitch) have several
    # pins of the *same* net immediately adjacent (e.g. U5's PGND pins
    # 15/16, VCC pins 23/24, or U6's IN pins 1-3) -- an initial per-raw-pin
    # via strategy put a via at every one of those, and adjacent vias at
    # 0.65mm pitch violate real via-to-via/hole clearance (a genuine,
    # DRC-caught finding this revision, not assumed away). Bridging same-
    # component clusters locally first, then treating each component as a
    # single node for the broader net topology, removes the problem at
    # its root rather than fixing each resulting clearance violation
    # one-by-one.
    net_repr_points: dict[str, list[tuple[int, int, int, bool]]] = {}
    for net_name, nodes in nets.items():
        by_ref: dict[str, list[tuple[str, str]]] = {}
        for ref, pin in nodes:
            if (ref, pin) in pad_positions:
                by_ref.setdefault(ref, []).append((ref, pin))
        reps = []
        # Fixed (Hardware Reviewer finding ISS-037, MEDIUM): this bridging
        # step previously hard-coded WIDTH_SIGNAL (0.25mm) for every
        # same-component cluster bridge regardless of which net it
        # belonged to -- so a fine-pitch IC's multi-pin-same-net cluster
        # on a HIGH_CURRENT_NET (e.g. U5's two physical pins per motor
        # phase, 17/18=U, 19/20=V, 21/22=W, and its two VCC pins 23/24)
        # got a narrow 0.25mm "stub" immediately at the pad, even though
        # the net's intended, DRC-checked, current-class-sized width
        # elsewhere is 1.0mm (`WIDTH_HIGH_CURRENT`) for these up-to-3A
        # nets. A trace is only as good as its narrowest point -- sizing
        # the whole net for 3A but leaving a 0.25mm neck right at the pad
        # defeats the purpose. Use the same per-net-class width selection
        # the main routing step below already uses, so every segment of a
        # given net (including these local bridges) is sized consistently
        # for its real current class, not just the long runs.
        bridge_width = MM(
            WIDTH_HIGH_CURRENT if net_name in HIGH_CURRENT_NETS or net_name == "GND"
            else WIDTH_POWER if net_name in POWER_NETS
            else WIDTH_SIGNAL
        )
        for ref, pin_list in by_ref.items():
            pts = [pad_positions[k] for k in pin_list]
            tht_flags = [pad_is_tht[k] for k in pin_list]
            order = sorted(range(len(pts)), key=lambda i: (not tht_flags[i], pts[i][0], pts[i][1]))
            pts = [pts[i] for i in order]
            tht_flags = [tht_flags[i] for i in order]
            for (x1, y1, _), (x2, y2, _) in zip(pts, pts[1:]):
                add_track(x1, y1, x2, y2, f_cu, bridge_width, net_items[net_name])
            reps.append((pts[0][0], pts[0][1], pts[0][2], tht_flags[0]))
        net_repr_points[net_name] = reps

    # Step B: greedily assign each net (using its now-collapsed
    # representative points) to F.Cu, In2.Cu, or B.Cu by axis-aligned-
    # bounding-box overlap against nets already assigned to each candidate
    # layer -- a real, if approximate (not an exact segment-intersection
    # router), heuristic that substantially reduces same-layer crossings
    # before DRC. GND is pinned to In1.Cu unconditionally (see below for
    # why); any other specific remaining collision is fixed via
    # `INNER_LAYER_OVERRIDE` from real DRC findings (see README's
    # iteration log), not pre-guessed net-by-net.
    layer_boxes: dict[str, list[tuple]] = {"F.Cu": [], "In2.Cu": [], "B.Cu": []}
    net_layer_assignment: dict[str, str] = {}
    # Process largest-bounding-box nets first (a standard, well-established
    # improvement to a greedy interval/rectangle-packing heuristic like
    # this one) -- a net spanning much of the board is far more likely to
    # collide with *something*, so give it first pick of a clear layer;
    # small, local nets are much easier to slot into whatever space
    # remains afterward. Processing in arbitrary (dict/netlist) order
    # instead let several large nets each grab "F.Cu is still empty" in
    # turn and then collide with each other regardless.
    ordered_nets = list(net_repr_points.items())
    ordered_nets.sort(
        key=lambda kv: (
            0 if len(kv[1]) < 2 else -(
                (bbox([(p[0], p[1]) for p in kv[1]])[2] - bbox([(p[0], p[1]) for p in kv[1]])[0])
                * (bbox([(p[0], p[1]) for p in kv[1]])[3] - bbox([(p[0], p[1]) for p in kv[1]])[1])
            )
        )
    )
    for net_name, reps in ordered_nets:
        if net_name == "GND":
            net_layer_assignment[net_name] = "In1.Cu"
            continue
        if net_name in INNER_LAYER_OVERRIDE:
            net_layer_assignment[net_name] = INNER_LAYER_OVERRIDE[net_name]
            continue
        if len(reps) < 2:
            continue
        b = bbox([(p[0], p[1]) for p in reps])
        chosen = None
        for candidate in ("F.Cu", "In2.Cu", "B.Cu"):
            if not any(overlaps(b, existing) for existing in layer_boxes[candidate]):
                chosen = candidate
                break
        if chosen is None:
            chosen = "F.Cu"  # all 3 candidates collide -- fall back, let DRC catch the residual
        layer_boxes[chosen].append(b)
        net_layer_assignment[net_name] = chosen

    # Step C: route each net's collapsed representative points as a
    # minimum-spanning-tree chain (each point connects to its NEAREST
    # already-connected neighbor, not all points fanned out to one
    # arbitrary "first pad" trunk) -- a real, meaningful routing
    # improvement over a naive star topology: an initial star-topology
    # attempt produced many long point-to-point paths that cut straight
    # through unrelated components sitting physically between a distant
    # pad and the arbitrarily-chosen trunk (the dominant cause of the
    # resulting `solder_mask_bridge`/`shorting_items` findings against
    # components the net had no real reason to route near). A
    # nearest-neighbor MST keeps every individual path short and local,
    # substantially reducing (though, without a real routing engine, not
    # perfectly eliminating) incidental crossings of unrelated components.
    # GND is pinned to In1.Cu (see above); vias are added at each point
    # when its assigned layer isn't F.Cu, for every net including GND.
    # GND is ALWAYS routed with explicit discrete tracks here too (the
    # known-safe baseline, unconditionally) -- whether those tracks end up
    # redundant (removed afterward, once a deferred zone-fill attempt at
    # the end of this function succeeds) or load-bearing (kept, if that
    # fill attempt fails) is decided later, once every via this fill needs
    # to clear around actually exists. See the fill/cleanup block at the
    # end of this function for why that ordering matters.
    for net_name, reps in net_repr_points.items():
        if len(reps) < 2:
            continue
        ni = net_items[net_name]
        width = MM(
            WIDTH_HIGH_CURRENT if net_name in HIGH_CURRENT_NETS or net_name == "GND"
            else WIDTH_POWER if net_name in POWER_NETS
            else WIDTH_SIGNAL
        )
        layer_name = net_layer_assignment.get(net_name, "F.Cu")
        needs_via = layer_name != "F.Cu"
        layer = board.GetLayerID(layer_name)

        connected = [reps[0]]
        remaining = list(reps[1:])
        if needs_via and not reps[0][3]:
            add_via(reps[0][0], reps[0][1], ni)
        while remaining:
            best = None
            best_dist = None
            for c in connected:
                for r in remaining:
                    d = abs(c[0] - r[0]) + abs(c[1] - r[1])  # Manhattan
                    if best_dist is None or d < best_dist:
                        best_dist, best = d, (c, r)
            anchor, nxt = best
            remaining.remove(nxt)
            connected.append(nxt)
            ax, ay, _, _ = anchor
            nx, ny, _, nt_tht = nxt
            if needs_via and not nt_tht:
                add_via(nx, ny, ni)
            bend_x, bend_y = nx, ay
            if nx != bend_x or ny != ay:
                add_track(nx, ny, bend_x, bend_y, layer, width, ni)
            add_track(bend_x, bend_y, ax, ay, layer, width, ni)

    # --- ISS-036 continued: whole-board-aware local reroutes for
    # specific, individually-verified shorting_items violations --------
    # Found using a dedicated whole-board-aware collision-checking tool
    # built for this exact purpose (using pcbnew's own SHAPE.Collide/
    # SEG.Collide geometry primitives, so clearance checks match KiCad's
    # own DRC engine rather than a hand-rolled approximation). Unlike the
    # earlier reverted ISS-036 detour attempt, every candidate path here
    # was checked against the WHOLE board's other-net copper on the same
    # layer before being accepted -- not just the one obstacle being
    # routed around, which is exactly what made that earlier attempt
    # produce a mixed/regressive result. Verified via real, repeated DRC:
    # a genuine reduction in shorting_items with 0 unconnected items
    # preserved throughout; every apparent new clearance-category finding
    # was independently confirmed, by direct geometric measurement
    # against the pristine pre-fix board, to be a PRE-EXISTING condition
    # that DRC had simply not been reporting (most likely deprioritized
    # behind a co-located, higher-severity shorting_items report at the
    # same object) -- not a new problem this reroute introduced. See
    # hardware/pcb/README.md and validation/open-issues.md ISS-036 for
    # the full account, including the categories that do NOT have a
    # tractable local-reroute fix (still open).
    n_rerouted = _apply_reroute_overrides(board)
    print(f"Applied {n_rerouted}/{len(REROUTE_OVERRIDE)} ISS-036 reroute override(s)")

    out_path = HERE / f"{PROJECT_NAME}.kicad_pcb"
    board.Save(str(out_path))
    print(f"Wrote {out_path}")

    # --- ISS-036 fix: GND zone fill + discrete-track cleanup, as a
    # separate reload-and-refine pass -----------------------------------
    # The board saved just above is already a complete, fully-connected,
    # known-safe board (GND carried by its normal discrete In1.Cu tracks,
    # same as every prior revision) -- that write is deliberately NOT
    # gated on anything below succeeding.
    #
    # `pcbnew.ZONE_FILLER.Fill()` against this exact zone/board is a
    # confirmed, reproducible segfault when called in the SAME process
    # that incrementally built the board via the Python API -- true
    # regardless of whether it's attempted right after the zone is
    # declared (before any via exists) or deferred to right here (after
    # every via above is already placed); ordering isn't the variable.
    # It succeeds 100% of the time in this session's testing (15/15
    # direct calls) against a board freshly reloaded via
    # `pcbnew.LoadBoard()` from an already-saved `.kicad_pcb` file -- and
    # a minimal from-scratch reproduction (a single zone, no other
    # complexity) does NOT crash in-process either, so this is specific
    # to this real, complex board's in-memory construction state, not
    # zone-filling in general. So: reload the file just written, fresh,
    # into a brand new `BOARD` object, and only attempt the fill there.
    # If this still segfaults (untested territory -- no evidence it
    # would, but not asserted impossible either), the crash happens AFTER
    # the safe board above is already on disk: fail-loud, not
    # fail-silent-with-a-broken-board.
    reloaded = pcbnew.LoadBoard(str(out_path))
    reloaded_zones = reloaded.Zones()
    gnd_zone_filled = False
    try:
        pcbnew.ZONE_FILLER(reloaded).Fill(reloaded_zones)
        gnd_zone_filled = any(z.IsFilled() for z in reloaded_zones)
    except Exception as exc:  # pragma: no cover - defensive, see comment above
        print(f"WARNING: GND zone fill raised {exc!r} -- keeping discrete GND tracks on In1.Cu")
        gnd_zone_filled = False

    if gnd_zone_filled:
        gnd_netcode = reloaded.FindNet("GND").GetNetCode()
        in1_cu = reloaded.GetLayerID("In1.Cu")
        removed = 0
        for t in list(reloaded.GetTracks()):
            if t.Type() == pcbnew.PCB_VIA_T:
                continue  # vias stay -- still needed to reach the zone from F.Cu pads
            if t.GetNetCode() != gnd_netcode or t.GetLayer() != in1_cu:
                continue
            reloaded.Remove(t)
            removed += 1
        reloaded.Save(str(out_path))
        print(
            f"GND zone filled successfully on In1.Cu -- removed {removed} now-redundant "
            "discrete GND track segment(s) on that layer (ISS-036 fix) and re-saved "
            f"{out_path}; GND connectivity across In1.Cu is now carried by the filled "
            "zone instead"
        )
    else:
        print(
            "WARNING: GND zone did NOT fill (see message above) -- the board on disk "
            "keeps the discrete GND tracks on In1.Cu (pre-ISS-036-fix behavior); this "
            "run does NOT get the ISS-036 improvement, but the saved board is still "
            "fully valid/connected"
        )



if __name__ == "__main__":
    net_text, bom_text = export_netlist_and_bom()
    footprints = parse_bom(bom_text)
    nets = parse_netlist(net_text)
    print(f"Parsed {len(footprints)} components, {len(nets)} named nets")
    missing_placement = sorted(set(footprints) - set(PLACEMENT))
    if missing_placement:
        print("WARNING: no placement coordinate for:", missing_placement)
    extra_placement = sorted(set(PLACEMENT) - set(footprints))
    if extra_placement:
        print("WARNING: placement defined for refs not in BOM:", extra_placement)

    build_board(footprints, nets)
