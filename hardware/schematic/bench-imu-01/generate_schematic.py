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
    for num in ("1", "2", "3", "7", "8", "11", "13", "14", "15", "16", "17",
                "18", "20", "26", "27", "28", "29", "30", "31", "32"):
        b.no_connect("U1", num)

    b.sch.to_file(str(HERE / f"{PROJECT_NAME}.kicad_sch"))

    # --- Write the project-local symbol library (BMI270 only) --------
    bmi_lib = SymbolLib(symbols=[build_bmi270_symbol()])
    bmi_lib.to_file(str(HERE / f"{PROJECT_NAME}.kicad_sym"))

    print(f"Wrote {HERE / (PROJECT_NAME + '.kicad_sch')}")
    print(f"Wrote {HERE / (PROJECT_NAME + '.kicad_sym')}")
    print(f"Placed {len(b.placed)} symbols, {b._nc_count} no-connects")


if __name__ == "__main__":
    main()
