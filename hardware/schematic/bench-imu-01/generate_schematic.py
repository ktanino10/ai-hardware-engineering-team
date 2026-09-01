#!/usr/bin/env python3
"""Generate hardware/schematic/bench-imu-01/bench-imu-01.kicad_sch (+ .kicad_pro,
+ the project-local bench-imu-01.kicad_sym for BMI270) programmatically.

Why this script exists (tooling honesty, matches this repo's own conventions):
no MCP tool or CLI command in this environment can *create or edit* a KiCad
schematic -- every `kicad-*` MCP tool is read/analyze-only (validate_project,
extract_schematic_netlist, analyze_schematic_connections, find_component_
connections, identify_circuit_patterns, analyze_bom, run_drc_check, etc.), and
`kicad-cli` itself has no "create schematic" subcommand (only `sch erc`,
`sch export`, `sch upgrade`). This script uses `kiutils` (a third-party,
MIT-licensed KiCad-6+ file format library, https://github.com/mvnmgrx/kiutils,
installed via `pip install kiutils` -- a one-off authoring aid, not a runtime
project dependency) to construct valid KiCad object graphs and serialize them
to the real `.kicad_sch`/`.kicad_sym` S-expression format, which is then
normalized to this machine's native KiCad 10.0.1 format via
`kicad-cli sch upgrade` and independently verified with `kicad-cli sch erc`
plus the real `kicad-*` MCP tools (see the design notes in README.md).

Every symbol/footprint/pin fact below is sourced from the real, installed
KiCad 10.0.1 symbol/footprint libraries (or, for the BMI270 custom symbol,
from `hardware/schematic/bench-imu-01-design.md` section 5.3's own
DS-IMU-077-cited pin table) and cross-checked against
`hardware/schematic/bench-imu-01-design.md` (Rev 2, corrected) net-by-net.
Re-run this script any time the design changes -- it is the source of truth
for how the .kicad_sch/.kicad_sym files were produced, not a one-off throwaway.

Requires: pip install kiutils (tested against kiutils==1.4.8)
Usage:    python3 generate_schematic.py
"""
from __future__ import annotations

import copy
import uuid
from pathlib import Path

from kiutils.items.common import Effects, Font, Justify, Position, Stroke
from kiutils.items.schitems import (
    Connection,
    LocalLabel,
    NoConnect,
    Property,
    SchematicSymbol,
    SymbolProjectInstance,
    SymbolProjectPath,
)
from kiutils.schematic import PageSettings, Schematic
from kiutils.symbol import Symbol, SymbolLib, SymbolPin

KICAD_SYMBOLS = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
HERE = Path(__file__).resolve().parent
PROJECT_NAME = "bench-imu-01"

GRID = 2.54  # mm (0.1in) -- placed-symbol *origins* are chosen as multiples of
             # this; the underlying schematic connection grid is 1.27mm, and
             # real library pin offsets are themselves multiples of 1.27mm, so
             # every real pin lands on-grid automatically once its symbol's
             # origin is 2.54mm-aligned.


def snap(v: float) -> float:
    """Round away binary floating-point noise (e.g. 96.19000000000001) WITHOUT
    quantizing to a coarser grid. Earlier revisions of this script quantized to
    GRID here, which used Python's banker's-rounding on exact .5-multiple
    inputs and silently collapsed distinct, correctly 1.27mm-spaced pins onto
    the same coordinate (caught via a real `pin_to_pin` ERC conflict on the
    BMI270 symbol's own pins during self-verification) -- never quantize an
    already-precise, library-derived coordinate to a coarser grid.
    """
    return round(v, 4)


def patch_alternate_pin_function(sch_path: Path, ref: str, pin_number: str, alternate: str) -> None:
    """Activate a real per-instance KiCad "alternate pin function"
    (`(pin "<num>" (alternate "<name>") (uuid ...))`) on one specific
    placed symbol instance, as a raw text post-process of an already-
    written `.kicad_sch` file.

    Why this exists (Hardware Reviewer Cycle 6, ISS-030): `kiutils`
    1.4.8's `SchematicSymbol.pins` model is a bare `{pin_number: uuid}`
    mapping (confirmed by reading its own source) with no way to express
    this real, needed-here KiCad 7+ per-instance mechanism. Some MCU
    library symbols shared across a whole silicon family (e.g.
    `MCU_ST_STM32G0:STM32G031K8Tx`) declare a physical pin's *base*
    electrical type as `no_connect` with the real, in-use function
    (e.g. "PA9") only selectable as an alternate -- without activating
    it, KiCad's netlist compiler places that pin on a synthetic
    `unconnected-` net regardless of any wire/label visually drawn to
    it, silently dropping it from every net it was actually meant to
    join. Scoped narrowly to the named component's own symbol-instance
    block (found by its `(property "Reference" "<ref>"` line) so the
    same pin number on a *different* component is never touched.

    The `(alternate ...)` token must be a CHILD of the `(pin ...)`
    s-expression, not a sibling appended after its closing paren (an
    earlier version of this function inserted it as a new line after the
    pin block instead of inside it, which produces a structurally invalid
    file KiCad refuses to load at all -- caught immediately by re-running
    `kicad-cli sch erc` on the result, exactly the kind of tool-based
    self-verification this project's own conventions require before
    trusting any generated-file edit). `kiutils` writes each pin as a
    single physical line, `(pin "<num>" (uuid <uuid>))` -- this patch
    does an in-place string replacement on that exact line rather than
    inserting a new one.
    """
    text = sch_path.read_text()
    lines = text.splitlines(keepends=True)

    ref_marker = f'(property "Reference" "{ref}"'
    start = next((i for i, ln in enumerate(lines) if ref_marker in ln), None)
    if start is None:
        raise ValueError(f"patch_alternate_pin_function: no symbol instance found for ref={ref!r}")
    # This component's own instance block runs until the next symbol
    # instance's "Reference" property (or end of file).
    end = next(
        (i for i in range(start + 1, len(lines)) if '(property "Reference" "' in lines[i]),
        len(lines),
    )

    pin_open = f'(pin "{pin_number}" '
    pin_idx = next(
        (i for i in range(start, end) if pin_open in lines[i]),
        None,
    )
    if pin_idx is None:
        raise ValueError(
            f"patch_alternate_pin_function: no pin {pin_number!r} found on ref={ref!r}"
        )
    if lines[pin_idx].count(pin_open) != 1:
        raise ValueError(
            f"patch_alternate_pin_function: ambiguous match for pin {pin_number!r} on ref={ref!r}"
        )

    lines[pin_idx] = lines[pin_idx].replace(pin_open, f'{pin_open}(alternate "{alternate}") ', 1)
    sch_path.write_text("".join(lines))
    print(f"Patched {ref} pin {pin_number}: activated alternate function {alternate!r}")


# ---------------------------------------------------------------------------
# Library symbol loading helpers
# ---------------------------------------------------------------------------

_lib_cache: dict[str, SymbolLib] = {}


def _load_lib(lib_filename: str) -> SymbolLib:
    if lib_filename not in _lib_cache:
        _lib_cache[lib_filename] = SymbolLib().from_file(str(KICAD_SYMBOLS / lib_filename))
    return _lib_cache[lib_filename]


def load_symbol(lib_filename: str, symbol_name: str, new_lib_id: str) -> Symbol:
    """Load a real library symbol, flattening any `extends` relationship
    (KiCad embeds a fully-resolved, flattened copy in a schematic's own
    lib_symbols table -- confirmed empirically this session against a real
    KiCad-10-native schematic; the raw `extends` mechanism is a
    standalone-library-file-only convenience, not reproduced verbatim when
    caching a symbol into a schematic).
    """
    lib = _load_lib(lib_filename)
    sym = next(s for s in lib.symbols if s.libId == symbol_name)
    flat = copy.deepcopy(sym)
    if flat.extends:
        base = next(s for s in lib.symbols if s.libId == flat.extends)
        flat.units = copy.deepcopy(base.units)
        flat.pinNames = base.pinNames if not flat.pinNames else flat.pinNames
        flat.extends = None
    flat.libId = new_lib_id
    return flat


def pin_local_positions(sym: Symbol) -> dict[str, tuple[float, float]]:
    """Return {pin_number: (local_x, local_y)} exactly as defined in the
    symbol library (KiCad's internal Y-up convention -- see `abs_pos` for the
    sheet-placement Y-flip)."""
    out: dict[str, tuple[float, float]] = {}
    for unit in sym.units:
        for pin in unit.pins:
            out[pin.number] = (pin.position.X, pin.position.Y)
    return out


def pin_outward_directions(sym: Symbol) -> dict[str, str]:
    """Return {pin_number: 'up'|'down'|'left'|'right'}, the direction a wire
    stub should extend FROM each pin's connection point to move AWAY from the
    symbol body (continuing outward past the pin's own drawn leg, never back
    across it towards the body or an adjacent pin at the same pitch).

    A pin's `(at x y angle)` places its connection point at (x, y) with the
    pin's own drawn leg extending, in the symbol's local (Y-up) coordinate
    system, in the direction `angle` (0=+X, 90=+Y, 180=-X, 270=-Y) BACK
    TOWARD the body -- so the outward direction (away from the body) is
    `angle + 180`. This is then mapped from local Y-up to the sheet's
    global Y-down convention (only Y is flipped; symbols are all placed at
    rotation 0 in this design, so no further rotation is needed).

    Getting this right matters: an earlier revision of this script used a
    single hard-coded 'down' stub direction for every pin regardless of its
    own angle, which (self-verification caught this via `kicad-cli sch erc`
    + `sch export netlist` showing many unrelated nets merged into one) on a
    densely-packed multi-pin IC symbol very often placed 2.54mm stub
    endpoints exactly ON TOP of the *next* pin at the same 2.54mm pitch,
    silently short-circuiting adjacent, functionally unrelated pins.
    """
    local_to_global = {0: "right", 90: "up", 180: "left", 270: "down"}
    out: dict[str, str] = {}
    for unit in sym.units:
        for pin in unit.pins:
            outward_local = (pin.position.angle + 180) % 360
            out[pin.number] = local_to_global[outward_local]
    return out


# ---------------------------------------------------------------------------
# Schematic-building helpers
# ---------------------------------------------------------------------------

class SchBuilder:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.sch = Schematic.create_new()
        self.sch.uuid = str(uuid.uuid4())
        self.sch.paper = PageSettings(paperSize="A3")
        self._lib_ids_added: set[str] = set()
        self.placed: dict[str, dict] = {}  # ref -> {"sym", "pos", "pins_abs", "pins_dir"}
        self._nc_count = 0
        self._used_endpoints: dict[tuple[float, float], tuple[str, str]] = {}

    def add_lib_symbol(self, sym: Symbol) -> None:
        if sym.libId in self._lib_ids_added:
            return
        self.sch.libSymbols.append(sym)
        self._lib_ids_added.add(sym.libId)

    def place(
        self,
        ref: str,
        value: str,
        sym: Symbol,
        x: float,
        y: float,
        footprint: str = "",
        datasheet: str = "",
        extra_props: list[tuple[str, str]] | None = None,
    ) -> dict:
        """Place one instance of `sym` at sheet position (x, y), angle 0.
        Returns a dict with the instance's absolute pin positions for wiring.
        """
        self.add_lib_symbol(sym)
        x, y = snap(x), snap(y)
        inst_uuid = str(uuid.uuid4())
        pins = {p: str(uuid.uuid4()) for p in pin_local_positions(sym)}

        props = [
            Property(key="Reference", value=ref, id=0,
                      position=Position(X=x + 2.54, Y=y - 5.08, angle=0), effects=Effects()),
            Property(key="Value", value=value, id=1,
                      position=Position(X=x + 2.54, Y=y - 2.54, angle=0), effects=Effects()),
            Property(key="Footprint", value=footprint, id=2,
                      position=Position(X=x, Y=y, angle=0), effects=Effects(hide=True)),
            Property(key="Datasheet", value=datasheet, id=3,
                      position=Position(X=x, Y=y, angle=0), effects=Effects(hide=True)),
        ]
        for k, v in (extra_props or []):
            props.append(Property(key=k, value=v, id=len(props),
                                    position=Position(X=x, Y=y, angle=0), effects=Effects(hide=True)))

        instance = SchematicSymbol(
            libraryNickname=sym.libId.split(":")[0],
            entryName=sym.libId.split(":")[1],
            position=Position(X=x, Y=y, angle=0),
            unit=1, inBom=True, onBoard=True, dnp=False, fieldsAutoplaced=True,
            uuid=inst_uuid,
            properties=props,
            pins=pins,
            instances=[SymbolProjectInstance(
                name=self.project_name,
                paths=[SymbolProjectPath(sheetInstancePath="/" + self.sch.uuid, reference=ref, unit=1)],
            )],
        )
        self.sch.schematicSymbols.append(instance)

        pins_abs = {}
        for num, (lx, ly) in pin_local_positions(sym).items():
            pins_abs[num] = (snap(x + lx), snap(y - ly))
        info = {"sym": sym, "pos": (x, y), "pins_abs": pins_abs,
                "pins_dir": pin_outward_directions(sym), "ref": ref}
        self.placed[ref] = info
        return info

    def pin(self, ref: str, number: str) -> tuple[float, float]:
        return self.placed[ref]["pins_abs"][number]

    def connect(self, net: str, points: list[tuple[str, str]], stub: float = 2.54,
                direction_map: dict[tuple[str, str], str] | None = None) -> None:
        """Connect every (ref, pin_number) in `points` to a common net `net`,
        by drawing a short wire stub away from each pin's exact connection
        point and placing a same-named LocalLabel at the stub's far end.
        Same-named local labels on one schematic sheet are electrically
        connected in KiCad -- this is the standard, robust way to wire a
        many-way net (e.g. GND/3V3) without drawing long point-to-point wire
        runs across the page. The stub direction defaults to each pin's own
        real outward direction (see `pin_outward_directions`), never a
        single hard-coded direction, specifically to avoid stubs landing on
        an unrelated neighboring pin at the same pitch.
        """
        direction_map = direction_map or {}
        for ref, num in points:
            x, y = self.pin(ref, num)
            d = direction_map.get((ref, num)) or self.placed[ref]["pins_dir"][num]
            dx, dy = {"up": (0, -stub), "down": (0, stub), "left": (-stub, 0), "right": (stub, 0)}[d]
            end = (snap(x + dx), snap(y + dy))
            prior = self._used_endpoints.get(end)
            if prior is not None and prior[0] != net:
                raise ValueError(
                    f"Stub endpoint collision at {end}: net {net!r} ({ref}.{num}) "
                    f"would land on top of net {prior[0]!r} ({prior[1]}). Pass an explicit "
                    f"direction_map override for one of these two connections."
                )
            self._used_endpoints[end] = (net, f"{ref}.{num}")
            self.sch.graphicalItems.append(Connection(
                type="wire",
                points=[Position(X=x, Y=y), Position(X=end[0], Y=end[1])],
                stroke=Stroke(width=0, type="default"),
            ))
            label_angle = {"up": 90, "down": 90, "left": 0, "right": 0}[d]
            justify = "left" if d in ("down", "right") else "left"
            self.sch.labels.append(LocalLabel(
                text=net,
                position=Position(X=end[0], Y=end[1], angle=label_angle),
                effects=Effects(font=Font(height=1.27, width=1.27),
                                  justify=Justify(horizontally=justify)),
            ))

    def no_connect(self, ref: str, number: str) -> None:
        x, y = self.pin(ref, number)
        self.sch.noConnects.append(NoConnect(position=Position(X=x, Y=y)))
        self._nc_count += 1


# ---------------------------------------------------------------------------
# Custom BMI270 symbol (not present in any standard KiCad library --
# authored pin-for-pin from hardware/schematic/bench-imu-01-design.md
# section 5.3's own DS-IMU-077-cited 14-pin table)
# ---------------------------------------------------------------------------

def build_bmi270_symbol() -> Symbol:
    # Pin (number, name, electrical_type, side) -- side determines which
    # edge of the body rectangle the pin is drawn on, and hence its
    # rotation angle (0=points right from a left-edge pin, 180=points left
    # from a right-edge pin, matching standard KiCad IC symbol convention).
    left_pins = [
        ("1", "SDO", "input"),
        ("2", "ASDx", "bidirectional"),
        ("3", "ASCx", "output"),
        ("4", "INT1", "output"),
        ("5", "VDDIO", "power_in"),
        ("6", "GNDIO", "power_in"),
        ("7", "GND", "power_in"),
    ]
    right_pins = [
        ("8", "VDD", "power_in"),
        ("9", "INT2", "output"),
        ("10", "OCSB", "output"),
        ("11", "OSDO", "output"),
        ("12", "CSB", "input"),
        ("13", "SCx", "bidirectional"),
        ("14", "SDx", "bidirectional"),
    ]
    # 7 pins/side, 2.54mm pitch, centered on Y=0 (a clean multiple of the
    # 2.54mm grid throughout -- avoids the half-grid tie-rounding hazard of
    # calling snap() on already-exact coordinates, which previously
    # collapsed adjacent pins onto the same Y via banker's rounding).
    n = len(left_pins)
    first_y = (n - 1) * 2.54 / 2  # 7 pins -> 7.62
    top_y = first_y + 2.54
    bottom_y = -top_y
    body_w = 15.24  # 6 grid units wide

    sym = Symbol(
        libraryNickname=PROJECT_NAME,
        entryName="BMI270",
        pinNames=None,
        inBom=True, onBoard=True,
        properties=[
            Property(key="Reference", value="U", id=0,
                      position=Position(X=-body_w / 2, Y=top_y + 2.54, angle=0), effects=Effects()),
            Property(key="Value", value="BMI270", id=1,
                      position=Position(X=-body_w / 2, Y=top_y + 5.08, angle=0), effects=Effects()),
            Property(key="Footprint", value="Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm", id=2,
                      position=Position(X=0, Y=0, angle=0), effects=Effects(hide=True)),
            Property(key="Datasheet",
                      value="https://www.bosch-sensortec.com/products/motion-sensors/imus/bmi270/", id=3,
                      position=Position(X=0, Y=0, angle=0), effects=Effects(hide=True)),
            Property(key="Description",
                      value="Bosch Sensortec BMI270 6-axis IMU (accel+gyro), LGA-14, I2C/SPI -- "
                            "custom symbol, no standard-library part exists for this MPN; pins "
                            "sourced from hardware/schematic/bench-imu-01-design.md section 5.3 "
                            "(DS-IMU-077)", id=4,
                      position=Position(X=0, Y=0, angle=0), effects=Effects(hide=True)),
        ],
        units=[],
    )
    body_unit = Symbol(entryName="BMI270", unitId=0, styleId=1)
    from kiutils.items.syitems import SyRect
    body_unit.graphicItems.append(SyRect(
        start=Position(X=-body_w / 2, Y=top_y), end=Position(X=body_w / 2, Y=bottom_y),
        stroke=Stroke(width=0.254, type="default"),
    ))
    pin_unit = Symbol(entryName="BMI270", unitId=1, styleId=1)

    def add_side(pins, x_edge, angle, y_start):
        y = y_start
        for number, name, etype in pins:
            pin_unit.pins.append(SymbolPin(
                electricalType=etype, graphicalStyle="line",
                position=Position(X=x_edge, Y=y, angle=angle),
                length=2.54, name=name, number=number,
                nameEffects=Effects(font=Font(height=1.27, width=1.27)),
                numberEffects=Effects(font=Font(height=1.27, width=1.27)),
            ))
            y -= 2.54

    left_x = -body_w / 2 - 2.54
    right_x = body_w / 2 + 2.54
    add_side(left_pins, left_x, 0, first_y)     # pins on the left edge point right (angle 0)
    add_side(right_pins, right_x, 180, first_y)  # pins on the right edge point left (angle 180)

    sym.units = [body_unit, pin_unit]
    return sym


def build_drv10983_symbol() -> Symbol:
    """DRV10983 (U5, new Rev 3) -- like BMI270, no standard-library symbol
    exists for this MPN. Real 24-pin HTSSOP pinout independently re-verified
    this session directly against TI's own primary datasheet text
    (SLVSCP6H, https://www.ti.com/lit/ds/symlink/drv10983.pdf, pin diagram
    on the device's own top-level application schematic page) -- confirmed
    to match hardware/schematic/bench-imu-01-design.md section 7.5.4/13's
    own pin table exactly (independently re-derived from the primary source,
    not copied from the design doc without cross-check). Standard HTSSOP
    pin numbering: 1-12 down the left edge, 13-24 up the right edge (24
    bottom-right, wrapping to 13 at the bottom, per the datasheet's own
    diagram) -- so `right_pins` below is listed 24-down-to-13 (top to
    bottom) to match `add_side()`'s top-to-bottom placement convention,
    the same as `build_bmi270_symbol()` above.
    """
    left_pins = [
        ("1", "VCP", "passive"),
        ("2", "CPP", "passive"),
        ("3", "CPN", "passive"),
        ("4", "SW", "passive"),
        ("5", "SWGND", "power_in"),
        ("6", "VREG", "power_out"),
        ("7", "V1P8", "power_out"),
        ("8", "GND", "power_in"),
        ("9", "V3P3", "power_out"),
        ("10", "SCL", "bidirectional"),
        ("11", "SDA", "bidirectional"),
        ("12", "FG", "output"),
    ]
    right_pins = [
        ("24", "VCC", "power_in"),
        ("23", "VCC", "power_in"),
        ("22", "W", "passive"),
        ("21", "W", "passive"),
        ("20", "V", "passive"),
        ("19", "V", "passive"),
        ("18", "U", "passive"),
        ("17", "U", "passive"),
        ("16", "PGND", "power_in"),
        ("15", "PGND", "power_in"),
        ("14", "DIR", "input"),
        ("13", "SPEED", "input"),
    ]
    n = len(left_pins)
    first_y = (n - 1) * 2.54 / 2  # 12 pins -> 13.97
    top_y = first_y + 2.54
    bottom_y = -top_y
    body_w = 15.24

    sym = Symbol(
        libraryNickname=PROJECT_NAME,
        entryName="DRV10983",
        pinNames=None,
        inBom=True, onBoard=True,
        properties=[
            Property(key="Reference", value="U", id=0,
                      position=Position(X=-body_w / 2, Y=top_y + 2.54, angle=0), effects=Effects()),
            Property(key="Value", value="DRV10983", id=1,
                      position=Position(X=-body_w / 2, Y=top_y + 5.08, angle=0), effects=Effects()),
            Property(key="Footprint", value="Package_SO:HTSSOP-24-1EP_4.4x7.8mm_P0.65mm_EP3.2x5mm", id=2,
                      position=Position(X=0, Y=0, angle=0), effects=Effects(hide=True)),
            Property(key="Datasheet", value="https://www.ti.com/lit/ds/symlink/drv10983.pdf", id=3,
                      position=Position(X=0, Y=0, angle=0), effects=Effects(hide=True)),
            Property(key="Description",
                      value="Texas Instruments DRV10983 sensorless 3-phase BLDC motor driver, "
                            "HTSSOP-24 (PWP), exposed pad -- custom symbol, no standard-library "
                            "part exists for this MPN; pins independently re-verified against the "
                            "primary datasheet (SLVSCP6H) this session, cross-checked against "
                            "hardware/schematic/bench-imu-01-design.md section 7.5.4/13", id=4,
                      position=Position(X=0, Y=0, angle=0), effects=Effects(hide=True)),
        ],
        units=[],
    )
    body_unit = Symbol(entryName="DRV10983", unitId=0, styleId=1)
    from kiutils.items.syitems import SyRect
    body_unit.graphicItems.append(SyRect(
        start=Position(X=-body_w / 2, Y=top_y), end=Position(X=body_w / 2, Y=bottom_y),
        stroke=Stroke(width=0.254, type="default"),
    ))
    pin_unit = Symbol(entryName="DRV10983", unitId=1, styleId=1)

    def add_side(pins, x_edge, angle, y_start):
        y = y_start
        for number, name, etype in pins:
            pin_unit.pins.append(SymbolPin(
                electricalType=etype, graphicalStyle="line",
                position=Position(X=x_edge, Y=y, angle=angle),
                length=2.54, name=name, number=number,
                nameEffects=Effects(font=Font(height=1.27, width=1.27)),
                numberEffects=Effects(font=Font(height=1.27, width=1.27)),
            ))
            y -= 2.54

    left_x = -body_w / 2 - 2.54
    right_x = body_w / 2 + 2.54
    add_side(left_pins, left_x, 0, first_y)
    add_side(right_pins, right_x, 180, first_y)

    # Pin 25 = EP (exposed thermal pad) -- ADDED (Hardware Reviewer Cycle 6,
    # ISS-031, HIGH): the real 24-pin HTSSOP/PWP package has a 25th
    # electrical contact, the exposed pad, per TI's own datasheet Pin
    # Configuration table (DS-MTR-052) -- this custom symbol previously
    # defined only pins 1-24, omitting it entirely (unlike U6's real
    # library symbol, which does model its own exposed pad as pin 21).
    # Drawn as a bottom-edge pin (matching how KiCad's own library symbols
    # conventionally represent an EP distinct from the 4-sided lead pins),
    # wired to GND alongside U5's other GND-family pins (5/8/15/16).
    pin_unit.pins.append(SymbolPin(
        electricalType="power_in", graphicalStyle="line",
        position=Position(X=0, Y=bottom_y - 2.54, angle=90),
        length=2.54, name="EP", number="25",
        nameEffects=Effects(font=Font(height=1.27, width=1.27)),
        numberEffects=Effects(font=Font(height=1.27, width=1.27)),
    ))

    sym.units = [body_unit, pin_unit]
    return sym


# ---------------------------------------------------------------------------
# Main: build the real Bench-IMU-01 Rev 2 (corrected) schematic
# ---------------------------------------------------------------------------

def main() -> None:
    b = SchBuilder(PROJECT_NAME)

    # --- Load real library symbols -----------------------------------
    stm32 = load_symbol("MCU_ST_STM32G0.kicad_sym", "STM32G031K8Tx", "MCU_ST_STM32G0:STM32G031K8Tx")
    ldo = load_symbol("Regulator_Linear.kicad_sym", "TLV75533PDBV", "Regulator_Linear:TLV75533PDBV")
    esd = load_symbol("Power_Protection.kicad_sym", "USBLC6-2SC6", "Power_Protection:USBLC6-2SC6")
    usbc = load_symbol("Connector.kicad_sym", "USB_C_Receptacle_USB2.0_16P",
                        "Connector:USB_C_Receptacle_USB2.0_16P")
    header4 = load_symbol("Connector_Generic.kicad_sym", "Conn_01x04", "Connector_Generic:Conn_01x04")
    sw_push = load_symbol("Switch.kicad_sym", "SW_Push", "Switch:SW_Push")
    led = load_symbol("Device.kicad_sym", "LED", "Device:LED")
    res = load_symbol("Device.kicad_sym", "R", "Device:R")
    cap = load_symbol("Device.kicad_sym", "C", "Device:C")
    pwr_flag = load_symbol("power.kicad_sym", "PWR_FLAG", "power:PWR_FLAG")
    bmi270 = build_bmi270_symbol()

    # --- Rev 3-5 motor-subsystem symbols (new this revision) ---------
    # U6: real library symbol -- TI's own KiCad footprint association
    # (Package_SO:HTSSOP-20-1EP_..._ThermalVias) is reused as-is below, a
    # CONFIRMED library-maintained symbol<->footprint pairing, not a guess.
    tps26631 = load_symbol("Power_Management.kicad_sym", "TPS26631PWP",
                            "Power_Management:TPS26631PWP")
    # J4: real CUI/Same Sky part has 3 physical terminals (center pin +
    # sleeve + an unpopulated N.O./N.C. switch contact) -- Barrel_Jack_Switch
    # is the matching 3-pin symbol (vs. the 2-pin plain Barrel_Jack), pairing
    # with the part-specific BarrelJack_CUI_PJ-102AH_Horizontal footprint
    # (also 3 pads) below.
    barrel_jack = load_symbol("Connector.kicad_sym", "Barrel_Jack_Switch",
                               "Connector:Barrel_Jack_Switch")
    # D2 (STPS3L60, real Schottky) -- Device:D_Schottky, pin1=K/pin2=A.
    d_schottky = load_symbol("Device.kicad_sym", "D_Schottky", "Device:D_Schottky")
    # D3 (SMBJ16A, real UNIDIRECTIONAL TVS) -- deliberately Device:D_Zener,
    # not Device:D_TVS: D_TVS's own graphic is a symmetric bowtie (two
    # triangles apex-to-apex), KiCad's standard symbol for a BIDIRECTIONAL
    # TVS, and its pins are named generically "A1"/"A2" with no K/A
    # polarity. SMBJ16A is explicitly unidirectional (design doc section
    # 7.5.2/13); D_Zener's single-diode graphic + real K(pin1)/A(pin2)
    # naming correctly conveys a one-directional clamping device, matching
    # how this design's own net list already states polarity ("cathode-to-
    # VM_MOTOR/anode-to-GND"). A disclosed symbol-choice substitution, not
    # an electrical-function change -- footprint (D_SMB) is unaffected.
    d_zener = load_symbol("Device.kicad_sym", "D_Zener", "Device:D_Zener")
    # F1 (Littelfuse 30R500UF, PTC fuse) -- generic 2-pin Device:Fuse;
    # footprint is custom-built below (no matching library footprint exists
    # for this specific radial PTC's real 10.2mm lead spacing/14mm body).
    fuse = load_symbol("Device.kicad_sym", "Fuse", "Device:Fuse")
    # M1's phase-wire interconnect: a plain 3-pin generic connector (the
    # motor itself is off-board, wired via 3 leads -- see the placement
    # comment below for the ASSUMPTION this represents).
    conn3 = load_symbol("Connector_Generic.kicad_sym", "Conn_01x03", "Connector_Generic:Conn_01x03")
    drv10983 = build_drv10983_symbol()

    # --- Place symbols (rough logical-block layout on an A3 sheet) ---
    # Block 1: USB-C power input + ESD + LDO (left)
    j1 = b.place("J1", "USB4105-GH-A", usbc, 25.4, 50.8,
                  footprint="Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
                  datasheet="~")
    u4 = b.place("U4", "USBLC6-2SC6", esd, 76.2, 45.72,
                  footprint="Package_TO_SOT_SMD:SOT-23-6",
                  datasheet="https://www.st.com/resource/en/datasheet/usblc6-2sc6.pdf")
    r1 = b.place("R1", "5.1k", res, 50.8, 30.48, footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = b.place("R2", "5.1k", res, 55.88, 30.48, footprint="Resistor_SMD:R_0603_1608Metric")
    c1 = b.place("C1", "1uF", cap, 96.52, 33.02, footprint="Capacitor_SMD:C_0603_1608Metric")
    u3 = b.place("U3", "TLV75533PDBV", ldo, 121.92, 45.72,
                  footprint="Package_TO_SOT_SMD:SOT-23-5",
                  datasheet="https://www.ti.com/lit/ds/symlink/tlv755p.pdf")
    c2 = b.place("C2", "0.47uF", cap, 147.32, 33.02, footprint="Capacitor_SMD:C_0603_1608Metric")

    # Block 2: MCU periphery (center)
    u1 = b.place("U1", "STM32G031K8T6", stm32, 200.66, 63.5,
                  footprint="Package_QFP:LQFP-32_7x7mm_P0.8mm",
                  datasheet="https://www.st.com/resource/en/datasheet/stm32g031k8.pdf")
    c3 = b.place("C3", "100nF", cap, 172.72, 27.94, footprint="Capacitor_SMD:C_0603_1608Metric")
    c4 = b.place("C4", "100nF", cap, 180.34, 27.94, footprint="Capacitor_SMD:C_0603_1608Metric")
    c8 = b.place("C8", "1uF", cap, 187.96, 27.94, footprint="Capacitor_SMD:C_0603_1608Metric")
    c5 = b.place("C5", "100nF", cap, 165.1, 91.44, footprint="Capacitor_SMD:C_0603_1608Metric")
    sw1 = b.place("SW1", "SW_PUSH", sw_push, 190.5, 106.68,
                   footprint="Button_Switch_THT:SW_PUSH_6mm", datasheet="~")

    # Block 3: IMU interface (right)
    u2 = b.place("U2", "BMI270", bmi270, 297.18, 63.5,
                  footprint="Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm",
                  datasheet="https://www.bosch-sensortec.com/products/motion-sensors/imus/bmi270/")
    r3 = b.place("R3", "4.7k", res, 261.62, 27.94, footprint="Resistor_SMD:R_0603_1608Metric")
    r4 = b.place("R4", "4.7k", res, 266.7, 27.94, footprint="Resistor_SMD:R_0603_1608Metric")
    c6 = b.place("C6", "100nF", cap, 322.58, 45.72, footprint="Capacitor_SMD:C_0603_1608Metric")
    c7 = b.place("C7", "100nF", cap, 330.2, 45.72, footprint="Capacitor_SMD:C_0603_1608Metric")
    c9 = b.place("C9", "1uF", cap, 337.82, 45.72, footprint="Capacitor_SMD:C_0603_1608Metric")

    # Block 4/5: UART header, SWD header, status LED
    j2 = b.place("J2", "UART", header4, 246.38, 137.16,
                  footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", datasheet="~")
    j3 = b.place("J3", "SWD", header4, 264.16, 137.16,
                  footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", datasheet="~")
    r5 = b.place("R5", "330", res, 213.36, 111.76, footprint="Resistor_SMD:R_0603_1608Metric")
    d1 = b.place("D1", "LED", led, 213.36, 127.0, footprint="LED_SMD:LED_0603_1608Metric", datasheet="~")

    # Block 5.5: Motor Driver + Reaction Wheel subsystem (new Rev 3-5,
    # design doc section 7.5). Placed in its own region of the sheet,
    # physically distinct from Blocks 1-5 above -- mirrors this design's own
    # explicit instruction (section 9/section 10) to keep the motor-driver
    # group physically separated from the IMU (U2) for vibration/thermal
    # isolation; the real physical separation is enforced at PCB placement
    # time (PCB Engineer), but the schematic sheet layout previews the same
    # intent.
    #
    # Sub-block A: input protection chain (J4 -> F1 -> D2 -> D3)
    j4 = b.place("J4", "PJ-102AH", barrel_jack, 25.4, 200.66,
                  footprint="Connector_BarrelJack:BarrelJack_CUI_PJ-102AH_Horizontal",
                  datasheet="https://www.sameskydevices.com/product/resource/pj-102ah.pdf")
    f1 = b.place("F1", "30R500UF", fuse, 53.34, 200.66,
                  footprint="bench-imu-01:Fuse_Littelfuse_30R500UF_Radial_D14.0mm_P10.2mm",
                  datasheet="https://www.littelfuse.com/assetdocs/littelfuse_ptc_30r_datasheet?assetguid=46bd151a-f029-4cec-aeef-2614869244f4")
    d2 = b.place("D2", "STPS3L60", d_schottky, 78.74, 200.66,
                  footprint="Diode_SMD:D_SMB",
                  datasheet="https://www.st.com/resource/en/datasheet/stps3l60.pdf")
    d3 = b.place("D3", "SMBJ16A", d_zener, 104.14, 213.36,
                  footprint="Diode_SMD:D_SMB",
                  datasheet="https://www.littelfuse.com/products/tvs-diodes/automotive-and-commercial-vehicle/smbj/smbj16a")
    c16 = b.place("C16", "1uF", cap, 104.14, 187.96, footprint="Capacitor_SMD:C_0603_1608Metric")
    # PWR_FLAG for the VM_MOTOR net (fed by an off-board DC source through
    # J4, same convention as PF1/PF2 above for VBUS_5V/GND) -- required so
    # ERC's power_pin_not_driven check doesn't flag U6 IN(1-3)/IN_SYS(6),
    # which are power_in-type pins with no power_out driver on this sheet.
    pf3 = b.place("#FLG03", "PWR_FLAG", pwr_flag, 129.54, 200.66, footprint="")

    # Sub-block B: U6 supervisory eFuse/load-switch controller (new Rev 5)
    u6 = b.place("U6", "TPS26631PWPR", tps26631, 144.78, 220.98,
                  footprint="Package_SO:HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm_Mask2.96x2.96mm_ThermalVias",
                  datasheet="https://www.ti.com/lit/ds/symlink/tps2663.pdf")
    r11 = b.place("R11", "10k", res, 144.78, 187.96, footprint="Resistor_SMD:R_0603_1608Metric")
    r12 = b.place("R12", "887k", res, 172.72, 187.96, footprint="Resistor_SMD:R_0603_1608Metric")
    r13 = b.place("R13", "60.4k", res, 180.34, 187.96, footprint="Resistor_SMD:R_0603_1608Metric")
    r14 = b.place("R14", "88.7k", res, 187.96, 187.96, footprint="Resistor_SMD:R_0603_1608Metric")
    r15 = b.place("R15", "3.57k", res, 172.72, 254.0, footprint="Resistor_SMD:R_0603_1608Metric")
    c17 = b.place("C17", "22nF", cap, 180.34, 254.0, footprint="Capacitor_SMD:C_0603_1608Metric")

    # Sub-block C: U5 DRV10983 motor driver + its own reference-circuit
    # passives (new Rev 3)
    u5 = b.place("U5", "DRV10983", drv10983, 228.6, 220.98,
                  footprint="Package_SO:HTSSOP-24-1EP_4.4x7.8mm_P0.65mm_EP3.2x5mm",
                  datasheet="https://www.ti.com/lit/ds/symlink/drv10983.pdf")
    c10 = b.place("C10", "10uF", cap, 203.2, 187.96, footprint="Capacitor_SMD:C_0805_2012Metric")
    c11 = b.place("C11", "0.1uF", cap, 210.82, 187.96, footprint="Capacitor_SMD:C_0603_1608Metric")
    c12 = b.place("C12", "0.1uF", cap, 218.44, 187.96, footprint="Capacitor_SMD:C_0603_1608Metric")
    r9 = b.place("R9", "39", res, 203.2, 254.0, footprint="Resistor_SMD:R_1206_3216Metric")
    c13 = b.place("C13", "10uF", cap, 210.82, 254.0, footprint="Capacitor_SMD:C_0805_2012Metric")
    c14 = b.place("C14", "1uF", cap, 218.44, 254.0, footprint="Capacitor_SMD:C_0603_1608Metric")
    r10 = b.place("R10", "1k", res, 256.54, 187.96, footprint="Resistor_SMD:R_0603_1608Metric")
    r6 = b.place("R6", "4.75k", res, 264.16, 254.0, footprint="Resistor_SMD:R_0603_1608Metric")
    r7 = b.place("R7", "4.75k", res, 271.78, 254.0, footprint="Resistor_SMD:R_0603_1608Metric")
    r8 = b.place("R8", "4.75k", res, 279.4, 254.0, footprint="Resistor_SMD:R_0603_1608Metric")
    c15 = b.place("C15", "1uF", cap, 264.16, 187.96, footprint="Capacitor_SMD:C_0603_1608Metric")

    # M1: T-Motor MN2206-13 KV2000 is off-board (a 27mm-diameter rotating
    # BLDC motor mounted to the separate mechanical bearing/flywheel
    # structure, not this logic/driver PCB -- design doc section 10 itself
    # leaves "on-board or off-board" and "connector choice at the
    # wire-to-board interface" explicitly UNRESOLVED, flagging it as a
    # layout-time decision). ASSUMPTION (PCB Engineer decision, disclosed):
    # represented here as a plain 3-pin interconnect (phase U/V/W); real
    # footprint chosen at PCB-layout time is a 5.0mm-pitch terminal block
    # (TerminalBlock_MaiXu_MX126-5.0-03P) for real-wire termination at this
    # design's up-to-3A worst-case motor-phase current -- a wider pitch than
    # J2/J3's 2.54mm signal headers specifically for that current margin.
    m1 = b.place("M1", "T-Motor_MN2206-13_conn", conn3, 302.26, 220.98,
                  footprint="TerminalBlock:TerminalBlock_MaiXu_MX126-5.0-03P_1x03_P5.00mm",
                  datasheet="~")

    # --- Wire every net from bench-imu-01-design.md section 12 (corrected) ---
    # VBUS_5V: J1 VBUS -> U4 VBUS(5) -> C1 -> U3 IN(1). Real TLV75533PDBV
    # symbol pin numbering (verified against the real KiCad library symbol,
    # not assumed): 1=IN, 2=GND, 3=EN, 4=NC, 5=OUT -- corrects the design
    # doc's own "IN(pin2)" citation (a separate, low-severity, non-electrical
    # pin-number discrepancy noted in README.md; does not affect this net's
    # membership, only which physical pin the label refers to).
    # J1's USB2.0_16P symbol exposes 4 VBUS pins (A4,A9,B4,B9); wire them all.
    b.connect("VBUS_5V", [("J1", "A4"), ("J1", "A9"), ("J1", "B4"), ("J1", "B9"),
                            ("U4", "5"), ("C1", "1"), ("U3", "1")])
    # EN_VIN: firm, unconditional direct tie, U3 EN(3) -> U3 IN(1) -- same
    # electrical node as VBUS_5V at U3's own IN pin.
    b.connect("VBUS_5V", [("U3", "3")])
    # CC1 / CC2: USB-C CC pull-downs to GND (through R1/R2)
    b.connect("CC1", [("J1", "A5"), ("R1", "1")])
    b.connect("CC2", [("J1", "B5"), ("R2", "1")])
    # 3V3: U3 OUT(5) -> C2 -> MCU VDD/VDDA (combined, pin 4) -> IMU VDD/VDDIO ->
    # I2C pull-ups -> J2/J3 3V3 reference pins. (R5/LED are a SERIES path, not
    # part of the 3V3 net -- see LED_CTRL/LED_A below.)
    b.connect("3V3", [("U3", "5"), ("C2", "1"), ("U1", "4"), ("C3", "1"), ("C4", "1"), ("C8", "1"),
                        ("U2", "8"), ("C6", "1"), ("U2", "5"), ("C7", "1"), ("C9", "1"),
                        ("R3", "2"), ("R4", "2"), ("J2", "4"), ("J3", "1")])
    # GND: single ground plane/net -- every GND-role pin. Real Device:LED pin
    # numbering (verified): 1=K (cathode), 2=A (anode) -- cathode (1) returns
    # to GND here.
    b.connect("GND", [
        ("J1", "A1"), ("J1", "A12"), ("J1", "B1"), ("J1", "B12"), ("J1", "SH"),
        ("U4", "2"), ("R1", "2"), ("R2", "2"), ("C1", "2"), ("C2", "2"),
        ("U1", "5"), ("C3", "2"), ("C4", "2"), ("C5", "2"), ("C8", "2"), ("U3", "2"),
        ("U2", "6"), ("U2", "7"), ("C6", "2"), ("C7", "2"), ("C9", "2"),
        ("SW1", "2"), ("D1", "1"), ("J2", "3"), ("J3", "3"),
    ])
    # PWR_FLAG symbols: tell ERC that VBUS_5V and GND are legitimately
    # externally-sourced power nets (fed by an off-board USB supply, not by
    # any power_out pin drawn on this sheet) -- standard KiCad practice for
    # exactly this situation, not a workaround; without it ERC's
    # power_pin_not_driven check correctly (if noisily) flags every
    # power_in pin fed only from a passive-type connector pin.
    pf1 = b.place("#FLG01", "PWR_FLAG", pwr_flag, 15.24, 76.2, footprint="")
    b.connect("VBUS_5V", [("#FLG01", "1")], direction_map={("#FLG01", "1"): "up"})
    pf2 = b.place("#FLG02", "PWR_FLAG", pwr_flag, 96.52, 111.76, footprint="")
    b.connect("GND", [("#FLG02", "1")], direction_map={("#FLG02", "1"): "up"})
    # NRST: MCU PF2/NRST (pin 6, shared pad) -> C5 -> GND; also -> SW1 -> GND.
    b.connect("NRST", [("U1", "6"), ("C5", "1"), ("SW1", "1")])
    # SWDIO / SWCLK
    b.connect("SWDIO", [("U1", "24"), ("J3", "4")])
    b.connect("SWCLK", [("U1", "25"), ("J3", "2")])
    # I2C2_SCL / I2C2_SDA -- corrected this session (ISS-014): real physical
    # pins are PA11 (22) / PA12 (23), not the nonexistent PB10/PB11.
    b.connect("I2C2_SCL", [("U1", "22"), ("R3", "1"), ("U2", "13")])
    b.connect("I2C2_SDA", [("U1", "23"), ("R4", "1"), ("U2", "14")])
    # IMU_CSB -> VDDIO (selects I2C mode) -- same net as 3V3 at the IMU's own
    # VDDIO pin; IMU_SDO -> GND (selects I2C address 0x68).
    b.connect("3V3", [("U2", "12")])
    b.connect("GND", [("U2", "1")])
    # UART_TX / UART_RX
    b.connect("UART_TX", [("U1", "9"), ("J2", "1")])
    b.connect("UART_RX", [("U1", "10"), ("J2", "2")])
    # LED_CTRL / LED_A: R5 is a SERIES resistor between PA5 and D1's anode --
    # two distinct electrical nets, not one shared net (a single "LED_CTRL"
    # net spanning both sides of R5 would incorrectly short it out). Real
    # Device:LED pin numbering (verified): 2=A (anode).
    b.connect("LED_CTRL", [("U1", "12"), ("R5", "1")])
    b.connect("LED_A", [("R5", "2"), ("D1", "2")])

    # --- Rev 3-5 motor-subsystem nets (design doc section 12) ---------
    # Each design-doc net-list row is a PHYSICAL SIGNAL PATH description
    # (arrows crossing a series element), not a flat net-membership list --
    # re-derived into distinct electrical nets below, split at every
    # resistor/diode/fuse boundary (a series element's two terminals are
    # never the same net).
    #
    # Input protection chain: J4(tip) -> F1 -> D2 -> D3's cathode/U6 IN.
    # J4 pin mapping (Barrel_Jack_Switch symbol, matching the real 3-pad
    # BarrelJack_CUI_PJ-102AH_Horizontal footprint) is an ASSUMPTION, not
    # CONFIRMED: the real Same Sky PJ-102AH datasheet's own mechanical
    # drawing/schematic diagram could not be rendered by this session's
    # tooling (PDF diagram lost in text extraction). Best available
    # evidence (a web search citing the primary datasheet + a DigiKey
    # mirror) gives pin1=sleeve, pin2=switch(N.C., unpopulated),
    # pin3=tip/center(+) -- used here, flagged prominently for human
    # verification against the real mechanical drawing before fabrication.
    # Low blast-radius even if reversed: D2's series reverse-polarity
    # protection fails safe (blocks conduction) rather than damaging
    # anything if J4's tip/sleeve assignment is actually swapped.
    b.connect("VM_MOTOR_RAW", [("J4", "3"), ("F1", "1")])
    b.connect("GND", [("J4", "1")])
    b.no_connect("J4", "2")
    b.connect("VM_MOTOR_F1", [("F1", "2"), ("D2", "2")])
    # D2 = D_Schottky, pin1=K(cathode)/pin2=A(anode); D3 = D_Zener (chosen
    # for correct K/A unidirectional polarity, see symbol-load comment
    # above), pin1=K(cathode)/pin2=A(anode). Design doc: "D2 anode <- F1;
    # D2 cathode -> D3 (cathode-to-VM_MOTOR/anode-to-GND)".
    b.connect("VM_MOTOR", [("D2", "1"), ("D3", "1"), ("U6", "1"), ("U6", "2"), ("U6", "3"),
                             ("U6", "6"), ("R12", "1"), ("C16", "1"), ("#FLG03", "1")],
              direction_map={("#FLG03", "1"): "up"})
    b.connect("GND", [("D3", "2"), ("C16", "2")])
    # U6 UVLO/OVP divider: IN_SYS -[R12]- UVLO -[R13]- OVP -[R14]- GND.
    b.connect("U6_UVLO_TAP", [("R12", "2"), ("U6", "7"), ("R13", "1")])
    b.connect("U6_OVP_TAP", [("R13", "2"), ("U6", "8"), ("R14", "1")])
    b.connect("GND", [("R14", "2")])
    # U6 ILIM / dVdT
    b.connect("U6_ILIM", [("U6", "11"), ("R15", "1")])
    b.connect("GND", [("R15", "2")])
    b.connect("U6_dVdT", [("U6", "10"), ("C17", "1")])
    b.connect("GND", [("C17", "2")])
    # U6 GND (pin 9) + PowerPAD (pin 21 -- KiCad's own convention for this
    # 1EP/HTSSOP-20 symbol's exposed-pad virtual pin, confirmed against the
    # real library symbol this session) + PGTH tied to GND.
    b.connect("GND", [("U6", "9"), ("U6", "21"), ("U6", "16")])
    # U6 EN/SHDN: U1 PA9 (pin 19, direct tie, no series resistor) -> U6
    # SHDN(13); R11 (10k) shunt pulldown on the same node (fail-safe-OFF).
    b.connect("U6_EN", [("U1", "19"), ("U6", "13"), ("R11", "1")])
    b.connect("GND", [("R11", "2")])
    # U6 floating pins (all explicitly sanctioned floating configurations
    # per TI's own guidance, design doc section 7.5.10): B_GATE(4), DRV(5)
    # -- no external reverse-polarity FET used; MODE(12) -- selects
    # Latch-off overload response; IMON(14), FLT(15), PGOOD(17) -- unused
    # this revision.
    for num in ("4", "5", "12", "14", "15", "17"):
        b.no_connect("U6", num)
    # U6 OUT -> U5 VCC (a distinct net from "VM_MOTOR" above -- U6's
    # internal load-switch separates them when disabled).
    b.connect("U5_VCC", [("U6", "18"), ("U6", "19"), ("U6", "20"),
                           ("U5", "23"), ("U5", "24"), ("C10", "1"), ("C11", "2")])
    b.connect("GND", [("C10", "2")])
    # U5 charge-pump network (VCP/CPP/CPN) -- internal gate-drive only, no
    # MCU/external connection beyond the reference-circuit caps.
    b.connect("U5_VCP", [("U5", "1"), ("C11", "1")])
    b.connect("U5_CPP", [("U5", "2"), ("C12", "1")])
    b.connect("U5_CPN", [("C12", "2"), ("U5", "3")])
    # U5 internal regulator (linear mode): SW -[R9]- VREG -[C13]- GND;
    # V1P8 -[C14]- GND. Explicitly NOT connected to the board's 3V3 rail
    # (Option A, design doc section 7.5.3).
    b.connect("U5_SW", [("U5", "4"), ("R9", "1")])
    b.connect("U5_VREG", [("R9", "2"), ("U5", "6"), ("C13", "1")])
    b.connect("GND", [("C13", "2")])
    b.connect("U5_V1P8", [("U5", "7"), ("C14", "1")])
    b.connect("GND", [("C14", "2")])
    # U5's own V3P3 output biases the FG/I2C1 pull-ups (a different domain
    # from the board's main 3V3 rail, per Option A).
    b.connect("U5_V3P3", [("U5", "9"), ("R6", "2"), ("R7", "2"), ("R8", "2"), ("C15", "1")])
    b.connect("GND", [("C15", "2"), ("U5", "8"), ("U5", "5"), ("U5", "16"), ("U5", "15"), ("U5", "25")])
    # MCU <-> U5 signal pins: SPEED (PA8/TIM1_CH1, PWM), DIR (PB1), FG
    # (PA6/TIM3_CH1), I2C1 SCL/SDA (PB6/PB7) -- pin numbers per the
    # corrected design doc section 11 pin table.
    b.connect("SPEED_PWM", [("U1", "18"), ("U5", "13"), ("R10", "1")])
    b.connect("GND", [("R10", "2")])
    b.connect("DIR", [("U1", "16"), ("U5", "14")])
    b.connect("FG_TACH", [("U5", "12"), ("R6", "1"), ("U1", "13")])
    b.connect("I2C1_SCL", [("U1", "30"), ("R7", "1"), ("U5", "10")])
    b.connect("I2C1_SDA", [("U1", "31"), ("R8", "1"), ("U5", "11")])
    # Motor phase outputs -> M1 (off-board, via the new 3-pin interconnect;
    # M1 pin assignment U=1/V=2/W=3 is this design's own arbitrary but
    # internally-consistent choice, since M1 is a 3-phase BLDC with no
    # fixed "correct" phase-to-pin convention -- swapping any two phases
    # only reverses rotation direction, not a wiring defect).
    b.connect("MOTOR_PHASE_U", [("U5", "17"), ("U5", "18"), ("M1", "1")])
    b.connect("MOTOR_PHASE_V", [("U5", "19"), ("U5", "20"), ("M1", "2")])
    b.connect("MOTOR_PHASE_W", [("U5", "21"), ("U5", "22"), ("M1", "3")])

    # --- No-connects: deliberately unpopulated pins -------------------
    for num in ("A6", "A7", "A8", "B6", "B7", "B8"):
        b.no_connect("J1", num)  # D+/D-/SBU pins -- power-only port, REQ-105 (this
                                   # 16-pin USB2.0-only symbol has no SuperSpeed pins)
    for num in ("1", "3", "4", "6"):
        b.no_connect("U4", num)  # I/O1 (pins 1,6) / I/O2 (pins 3,4) -- no D+/D- on this board
    for num in ("2", "3", "4", "9", "10", "11"):
        b.no_connect("U2", num)  # ASDx, ASCx, INT1, INT2, OCSB, OSDO -- polling, no aux i/f
    # U1's full free-GPIO inventory per the corrected design doc section 11
    # (DS-MCU-064): every real, bonded-out pin not otherwise committed above.
    # Pins 13/16/18/30/31 (PA6/PB1/PA8/PB6/PB7) removed from this list this
    # revision -- now wired to the motor subsystem above, not free. Pin 19
    # (PA9) was never in this list (a pre-existing Rev 2 gap -- neither
    # wired nor no-connected in that script; now resolved by this
    # revision's U6_EN wiring).
    for num in ("1", "2", "3", "7", "8", "11", "14", "15", "17", "20",
                "26", "27", "28", "29", "32"):
        b.no_connect("U1", num)

    sch_path = HERE / f"{PROJECT_NAME}.kicad_sch"
    b.sch.to_file(str(sch_path))

    # --- Post-process: activate U1 pin 19's "PA9" alternate pin function
    # (Hardware Reviewer Cycle 6, ISS-030, CRITICAL). Root cause: the real
    # MCU_ST_STM32G0 library symbol (shared across the whole STM32G031x4/
    # 6/8 family) declares physical pin 19's *base* electrical type as
    # `no_connect`, name "NC/PA9" -- PA9 is only a selectable *alternate*
    # pin function, a real per-instance KiCad 7+ mechanism
    # (`(pin "19" (alternate "PA9"))`) that `kiutils` 1.4.8's
    # `SchematicSymbol.pins` object model does not expose (confirmed by
    # reading its own source -- only a bare {pin_number: uuid} mapping).
    # Previously mis-classified in this project's own README as a benign,
    # cosmetic ERC warning; Cycle 6 independently proved the wire is not
    # actually recognized by KiCad's netlist compiler at all without this
    # activation (U1 pin 19 lands on a synthetic `unconnected-` net, and
    # `/U6_EN` silently lacks its MCU-driven member), permanently disabling
    # the entire motor/reaction-wheel subsystem. Patched here as a raw
    # text post-process (not the object model, which cannot express this)
    # so the fix is reproducible by re-running this script, not a one-off
    # hand-edit of the generated file that would silently drift from it.
    patch_alternate_pin_function(sch_path, ref="U1", pin_number="19", alternate="PA9")

    # --- Write the project-local symbol library (BMI270 + DRV10983) --
    bmi_lib = SymbolLib(symbols=[build_bmi270_symbol(), build_drv10983_symbol()])
    bmi_lib.to_file(str(HERE / f"{PROJECT_NAME}.kicad_sym"))

    print(f"Wrote {sch_path}")
    print(f"Wrote {HERE / (PROJECT_NAME + '.kicad_sym')}")
    print(f"Placed {len(b.placed)} symbols, {b._nc_count} no-connects")


if __name__ == "__main__":
    main()
