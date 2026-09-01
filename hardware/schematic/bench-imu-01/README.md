# Bench-IMU-01 — Real KiCad Project (Rev 2 corrected, extended to Rev 3-5)

This is this repository's **first real KiCad project** — a genuine
`.kicad_pro`/`.kicad_sch` pair (plus project-local `.kicad_sym`/`.pretty`
libraries for parts not in any standard library), not the structured
Markdown schematic-equivalent document this repository used for every
prior design cycle. It originally captured **Bench-IMU-01 Rev 2** (already
Design Complete, PR #6), as corrected for **ISS-014** (see below) — and was
extended this session (PCB Engineer, Phase 6,
`docs/architecture-evolution.md` §37) to add the **Rev 3-5 Motor Driver +
Reaction Wheel subsystem** (U5/U6/M1/J4/D2/D3/F1/R6-R15/C10-C17), which had
been fully designed and human-approved in
`hardware/schematic/bench-imu-01-design.md` §7.5 and
`bom/component-selection.md` but never transcribed into this real KiCad
project until now — the authoritative net-by-net rationale remains
`hardware/schematic/bench-imu-01-design.md`; this project is the
physically-verifiable artifact built from it, not a replacement for its
rationale.

## Tooling honesty (verify-before-use, per this repo's own discipline)

- **KiCad 10.0.1 + `kicad-cli` genuinely installed and used.** Verified
  directly (`kicad-cli version`), not assumed from a kickoff prompt.
- **Every `kicad-*` MCP tool is read/analyze-only** — none can create or
  edit a schematic. This project was authored by hand-constructing a valid
  KiCad object graph with [`kiutils`](https://github.com/mvnmgrx/kiutils)
  (a third-party, MIT-licensed KiCad-6+ file format library installed via
  `pip install kiutils` — a one-off authoring aid, not a runtime project
  dependency) and serializing it to real `.kicad_sch`/`.kicad_sym`
  S-expression files — see `generate_schematic.py`, the source of truth for
  *how* this project was produced. Re-run it any time the design changes.
- **A real, significant MCP tool bug was discovered and precisely
  characterized this session**: of the 16 `kicad-*` MCP tools, only 5
  (`list_projects`, `get_project_structure`, `validate_project`,
  `get_drc_history_tool`, `open_project`) actually work. **This 5/16 split is
  robust** — independently reproduced by a delegated Hardware Reviewer pass
  and by a separate PR auditor pass, each from a different session, each
  getting the identical count. The other 11 all take a `ctx: Context`
  parameter (`extract_project_netlist`, `extract_schematic_netlist`,
  `analyze_schematic_connections`, `find_component_connections`,
  `identify_circuit_patterns`, `analyze_project_circuit_patterns`,
  `analyze_bom`, `export_bom_csv`, `generate_pcb_thumbnail`,
  `generate_project_thumbnail`, `run_drc_check`) and consistently fail — but
  **the exact client-visible error text is MCP-client-dependent, not a
  single universal fact** (corrected here after the PR auditor's own
  independent pass surfaced this): omitting `ctx` entirely gets
  `Input validation error: 'ctx' is a required property` for all 11, every
  time, in every client tested — a client-side schema rejection before the
  tool body ever runs. Explicitly supplying a placeholder `ctx` value (e.g.
  `{}`) instead gets past that check and lets each tool's real body
  execute — at which point most fail with `Context is not available outside
  of a request` (traced to the local `kicad-mcp` server's own source,
  `kicad_mcp/tools/netlist_tools.py` and siblings: these call
  `await ctx.report_progress(...)`, needing a live FastMCP request context
  this environment's tool-calling bridge does not supply), while
  `run_drc_check` instead correctly executes
  (`{"success":false,"error":"PCB file not found in project"}` — a correct
  result given no `.kicad_pcb` exists, not a bug) and
  `generate_project_thumbnail` fails with yet another, unrelated error
  (`'FunctionTool' object is not callable`). Both the "omit `ctx`" and
  "supply `ctx`" behaviors were independently reproduced twice by the
  Hardware Lead after the discrepancy surfaced — neither observation was
  wrong, they reflect different calling patterns. This is a genuine,
  reproducible server-side defect (the ctx-injection gap itself), **not**
  an artifact of this project's own construction — but report the *count*
  as the robust fact, and the *specific error text* with its
  client-dependency caveat attached, not as a single universal detail.
  **Worked around** by using `kicad-cli` directly for the equivalent
  verification (`sch export netlist`, `sch export bom`, `sch erc`) — the
  same underlying KiCad engine these MCP tools wrap, so the verification is
  equally real and does not depend on this client-specific nuance at all.
  `kicad-cli sch erc` itself is a genuine, working capability this session
  also newly confirmed (see `docs/architecture.md` §5.2/§13, corrected).

## Directory contents

| File | What it is |
|---|---|
| `bench-imu-01.kicad_pro` | Project file (hand-authored JSON; not GUI-generated) |
| `bench-imu-01.kicad_sch` | The real schematic — 48 components (23 Rev 2 + 25 new Rev 3-5 motor subsystem), every net from the corrected design doc |
| `bench-imu-01.kicad_sym` | Project-local symbol library — BMI270 and DRV10983 (neither in any standard KiCad library) |
| `bench-imu-01.pretty/` | Project-local footprint library — F1's custom radial-PTC footprint (no matching library footprint exists for the real Littelfuse 30R500UF) |
| `sym-lib-table` | Registers the project-local `bench-imu-01` symbol library |
| `fp-lib-table` | Registers the project-local `bench-imu-01` footprint library |
| `generate_schematic.py` | The actual generation script — re-run to regenerate/modify |

## Symbol/footprint decisions (every one disclosed, per this repo's evidence conventions)

| Ref | Part | Symbol | Footprint | Confidence |
|---|---|---|---|---|
| U1 | STM32G031K8T6 | `MCU_ST_STM32G0:STM32G031K8Tx` | `Package_QFP:LQFP-32_7x7mm_P0.8mm` | CONFIRMED — exact real-part symbol (ST's own official CubeMX data, DS-MCU-064), exact footprint (matches symbol's own `Footprint` property) |
| U2 | BMI270 | **custom**, `bench-imu-01:BMI270` | `Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm` | CONFIRMED footprint (real Bosch-specific LGA-14 footprint, exact match to the design doc's stated 2.5×3.0×0.83mm package); symbol ASSUMPTION on exact pin *placement*/layout (left/right split, 2.54mm pitch) since no real footprint pinout diagram was available — pin *identity* (number/name/function) is CONFIRMED against DS-IMU-077 |
| U3 | TLV75533PDBVR | `Regulator_Linear:TLV75533PDBV` | `Package_TO_SOT_SMD:SOT-23-5` | CONFIRMED — exact part match (R = tape/reel packaging only, no functional difference); footprint exact |
| U4 | USBLC6-2SC6 | `Power_Protection:USBLC6-2SC6` | `Package_TO_SOT_SMD:SOT-23-6` | CONFIRMED — exact real MPN symbol, exact footprint |
| J1 | USB-C receptacle | `Connector:USB_C_Receptacle_USB2.0_16P` | `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | ASSUMPTION (disclosed) — the design doc never formally selects J1's MPN (§3.1: "J1's exact MPN is not formally selected"). Symbol chosen to match the doc's own "D+/D- present on the connector but left unpopulated" language (§3.2/§12) — a 16-pin USB2.0-only symbol has real D+/D-/SBU pins to leave NC, unlike the design doc's illustrative-only GCT USB4125 reference (which is actually a real 6-pin *power-only* part with no D+/D- pins at all — using its footprint would silently overclaim an MPN decision the Circuit Engineer explicitly declined to make). Footprint picked from the same illustrative manufacturer family (GCT) at the correct 16-pin count, explicitly flagged as illustrative-for-completeness, not a Component-Engineer-approved MPN |
| J2, J3 | 4-pin headers | `Connector_Generic:Conn_01x04` | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | CONFIRMED pattern match to the design doc's own cited NUCLEO-G031K8 CN4 minimal-header convention |
| SW1 | Momentary N.O. pushbutton | `Switch:SW_Push` | `Button_Switch_THT:SW_PUSH_6mm` | ASSUMPTION (disclosed) — design doc doesn't select an exact MPN either |
| D1 | Generic indicator LED | `Device:LED` | `LED_SMD:LED_0603_1608Metric` | ASSUMPTION (disclosed) — design doc explicitly states "MPN not selected" |
| R1–R5, C1–C9 | Passives | `Device:R` / `Device:C` | 0603 SMD | ASSUMPTION on package size (design doc never specifies; 0603 chosen for consistency, easily changed) |
| MH1–MH4 | Mounting holes | *excluded from schematic* | — | No electrical net — standard KiCad convention places these in the PCB editor only |

### New Rev 3-5 motor subsystem (PCB Engineer, this session — design doc §7.5/§11/§12/§13)

| Ref | Part | Symbol | Footprint | Confidence |
|---|---|---|---|---|
| U5 | TI DRV10983 | **custom**, `bench-imu-01:DRV10983` | `Package_SO:HTSSOP-24-1EP_4.4x7.8mm_P0.65mm_EP3.4x7.8mm_Mask2.4x4.68mm_ThermalVias` | Pin count/names/body **CONFIRMED** — independently re-verified this session directly against TI's own primary datasheet (SLVSCP6H, fetched live), not merely copied from the design doc. Footprint body size (4.4×7.8mm, 24-pin thermally-enhanced HTSSOP) CONFIRMED against the same primary source; exact exposed-pad sub-variant is **ASSUMPTION** — a web-search-derived pad estimate (~4.4×2.45mm) didn't exactly match any installed KiCad EP-mask variant, so the smallest/most conservative discrete-pad option was chosen (mirrors this project's own "CONFIRMED-via-standard, not part-specific" precedent already used for the MCU/LDO Rev 2 footprints, design doc §10). **Corrected 2026-09-02 (Hardware Reviewer Cycle 6, ISS-031, HIGH, partially fixed):** the custom symbol originally omitted pin 25 (EP/exposed pad) entirely — the schematic never modeled the pad as an electrical node at all, unlike U6's real library symbol which does. Fixed by adding pin 25 to `build_drv10983_symbol()` and wiring it to GND; the chosen footprint's own pad numbering (`(pad "25" smd rect ...)`, independently confirmed by inspecting the `.kicad_mod` file directly) already matches. **RESOLVED 2026-09-02 (continued-iteration round per Chief Engineer disposition)**: switched to a real, standard KiCad library footprint (`...ThermalVias`) with an 18-via thermal array (0.3mm drill/0.6mm pad, matching SLMA002/SLMA004's own "0.3-0.33mm" guidance) plus a larger 3.4x7.8mm F.Cu land — independently justified this cycle by re-reading DRV10983's OWN primary datasheet text (DS-MTR-081, not just the generic PowerPAD app notes): "...connected to bottom side of PCB through vias for better thermal spreading" and "Keep the thermal pad connection as large as possible... one piece of copper without any gaps." Independently re-verified: ERC clean; a standalone pad/net audit confirms all 20 physical pad-25 members (2 lands + 18 vias) share one correct GND net; DRC re-run x3 stays within the established baseline band (384/367/374 violations, 0 unconnected), no regression. The exact EP numeric dimension remains an ASSUMPTION (the primary datasheet's own mechanical package-outline drawing is a vector image, still not text-extractable by this session's tooling) — disclosed, not silently resolved — but this no longer blocks a genuine, via-stitched thermal connection. See `validation/open-issues.md` ISS-031 |
| U6 | TI TPS26631PWPR | `Power_Management:TPS26631PWP` (real library symbol) | `Package_SO:HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm_Mask2.96x2.96mm_ThermalVias` | **CONFIRMED** — real library symbol with the footprint pre-associated by KiCad's own library maintainers (not independently chosen); pin numbers cross-checked against the design doc's own §7.5.10 pinout table, exact match including the symbol's pin 21 = PowerPAD (exposed-pad virtual pin) |
| J4 | Same Sky PJ-102AH | `Connector:Barrel_Jack_Switch` (3-pin, matching the real 3-terminal part) | `Connector_BarrelJack:BarrelJack_CUI_PJ-102AH_Horizontal` | Footprint **CONFIRMED** (part-specific, name match, 3 pads). Pin-to-function mapping (sleeve/switch/tip) is **ASSUMPTION** — the primary datasheet's own mechanical drawing/schematic diagram could not be rendered by this session's tooling (PDF diagram lost in text extraction); used pin1=sleeve/GND, pin2=switch(N.C., unpopulated), pin3=tip/VM_MOTOR per a web search citing the primary datasheet + a DigiKey mirror. **Flagged for human verification against the real mechanical drawing before fabrication** — low blast-radius if wrong, since D2's series reverse-polarity protection fails safe (blocks conduction) rather than damaging anything if J4's tip/sleeve assignment is actually reversed |
| D2 | ST STPS3L60 | `Device:D_Schottky` | `Diode_SMD:D_SMB` | CONFIRMED — SMB package explicitly stated in design doc §13; standard K/A Schottky symbol |
| D3 | Littelfuse SMBJ16A | `Device:D_Zener` (substituted for `Device:D_TVS`) | `Diode_SMD:D_SMB` | Footprint CONFIRMED. Symbol choice is a disclosed substitution: SMBJ16A is explicitly **unidirectional**, but KiCad's generic `D_TVS` symbol is drawn as a symmetric bowtie (the standard *bidirectional*-TVS glyph) with generic "A1"/"A2" pin names, no K/A polarity. `D_Zener`'s single-diode graphic + real K(1)/A(2) naming correctly conveys a one-directional clamping device, matching this design's own net-list language ("cathode-to-VM_MOTOR/anode-to-GND") unambiguously — an electrically-equivalent, more precise symbol choice, not a functional change |
| F1 | Littelfuse 30R500UF | `Device:Fuse` (generic 2-pin) | **custom**, `bench-imu-01:Fuse_Littelfuse_30R500UF_Radial_D14.0mm_P10.2mm` | ASSUMPTION/custom — no KiCad library footprint matches this specific radial PTC fuse. Built to web-search-derived real dimensions (14mm body diameter, 10.2mm lead spacing); exact lead diameter (pad/drill sizing) is an ESTIMATE (datasheet's own lead-diameter spec not independently re-pulled this session), sized generously for a 5A-class radial lead |
| M1 (interconnect) | T-Motor MN2206-13 (off-board motor, wired via 3 leads) | `Connector_Generic:Conn_01x03` | `TerminalBlock:TerminalBlock_MaiXu_MX126-5.0-03P_1x03_P5.00mm` | **ASSUMPTION, disclosed** — design doc §10 explicitly leaves "M1 on-board or off-board" and "connector choice at the wire-to-board interface" unresolved, flagging it as a layout-time decision. M1 is a 27mm-diameter rotating BLDC motor that mounts to the separate mechanical bearing/flywheel structure (a parallel session's own scope), not this logic/driver PCB — so a real phase-wire interconnect is required here. A 5.0mm-pitch terminal block was chosen over a 2.54mm-pitch signal header (as J2/J3 use) specifically for higher current margin at this design's ≤3A worst-case motor-phase current. Phase-to-pin assignment (U=1/V=2/W=3) is this design's own arbitrary-but-consistent choice — swapping any two phases only reverses rotation direction, not a wiring defect |
| R6, R7, R8 | 4.75kΩ (FG/I2C1 pull-ups, referenced to U5's own V3P3) | `Device:R` | `Resistor_SMD:R_0603_1608Metric` | ASSUMPTION on package (no wattage stated; low-current bias/pull-up, 0603 consistent with the rest of the board) |
| R9 | 39Ω **¼W** (SW–VREG linear-mode select) | `Device:R` | `Resistor_SMD:R_1206_3216Metric` | **CONFIRMED-by-rating, not an arbitrary package choice** — the design doc explicitly states a ¼W power rating (DS-MTR-065 Table 11); a 0603 package (~1/10W typical) cannot safely dissipate ¼W, so 1206 (conventionally rated for ¼W) was chosen instead of following the rest-of-board 0603 convention |
| R10 | 1kΩ (SPEED pulldown) | `Device:R` | `Resistor_SMD:R_0603_1608Metric` | **CONFIRMED** — 0603 is explicitly stated in the design doc's own parts list (§13), not this session's own choice |
| R11–R15 | 10kΩ / 887kΩ / 60.4kΩ / 88.7kΩ / 3.57kΩ (U6 SHDN pulldown + OVP/UVLO divider + ILIM) | `Device:R` | `Resistor_SMD:R_0603_1608Metric` | ASSUMPTION on package (no wattage stated; µA-to-low-mA-level bias currents throughout, 0603 adequate) |
| C10, C13 | 10µF (U5 VCC/VREG decoupling, ≥16-25V-class rail) | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` | **ASSUMPTION, deliberately not 0603** — 10µF ceramic at this voltage class faces real DC-bias capacitance derating in an 0603 case size (a genuine practical/electrical concern, not merely stylistic); 0805 is the more reliable, still-small choice for this specific value+voltage combination |
| C11, C12, C14–C17 | 0.1µF / 1µF / 22nF (charge pump, V1P8, V3P3, U6 IN bypass, dVdT) | `Device:C` | `Capacitor_SMD:C_0603_1608Metric` | ASSUMPTION on package — these values/voltage classes don't face the same 0603 derating concern as C10/C13 above, so 0603 is kept consistent with the rest of the board |

**Real pin-numbering corrections found and fixed during construction** (beyond
the headline ISS-014 finding below): the design doc's own citation of
`TLV75533PDBVR`'s IN pin as "pin 2" does not match the real symbol (1=IN,
2=GND, 3=EN, 4=NC, 5=OUT) — a LOW-severity, purely-cosmetic pin-number
citation error (no electrical/topology impact; this schematic uses the
correct real pin numbers throughout). Not raised as its own ISS-### entry
(disproportionate for a LOW-severity, no-impact citation nit per
`docs/architecture.md` §7.1) — noted here for transparency instead.

## ISS-014 — the headline finding this project surfaced

While verifying real symbol/footprint availability (before wiring anything),
independent research against ST's own official machine-readable pin
database (`STMicroelectronics/STM32_open_pin_data` GitHub repo, DS-MCU-064)
found that **the STM32G031K8T6's real LQFP-32 package has no PB10/PB11 pins
at all** — the IMU I2C2 bus as documented in Rev 2 (already Design
Complete) could not be physically wired. Real I2C2 is available at
**PA11 (SCL, pin 22) / PA12 (SDA, pin 23)** instead (same peripheral
instance, default/unremapped pin-sharing state, no conflict with any other
net in this design). This schematic is built on the corrected pins.

Full finding, evidence, and fix: `validation/open-issues.md` ISS-014,
`validation/change-log.md` ECO-006, `datasheets/evidence-log.md`
DS-MCU-064–067, and the "Rev 2, corrected" changelog entry + new §19 at the
top of `hardware/schematic/bench-imu-01-design.md`.

## Real tool verification (actual output, not paraphrased)

### `kicad-cli sch erc --severity-all` (real ERC, this session's own newly-confirmed capability)

```
ERC report (2026-08-31, Encoding UTF8)
Report includes: Errors, Warnings, Exclusions

***** Sheet /
[lib_symbol_mismatch]: Symbol 'TLV75533PDBV' does not match the copy in library 'Regulator_Linear'
    ; warning
    @(121.92 mm, 45.72 mm): Symbol U3 [TLV75533PDBV]

 ** ERC messages: 1  Errors 0  Warnings 1
```

**Zero errors.** The one remaining warning is expected and benign: this
project's `lib_symbols` cache stores a *flattened* copy of `TLV75533PDBV`
(its real `units`/pins merged in directly from the base symbol it
`extends`, `TLV70012_SOT23-5` — confirmed empirically that KiCad embeds
schematics' cached library symbols this way, not via a live `extends` link)
rather than an unflattened copy preserving the live `extends` reference —
a deliberate, disclosed construction choice (see `generate_schematic.py`
`load_symbol()`), not an electrical defect. Getting to zero real errors
took several rounds of genuine bugs found and fixed via this exact
ERC+netlist-export self-verification loop (see "Bugs found and fixed"
below) — this is exactly why the independent, tool-based verification step
matters, not a formality.

### `kicad-cli sch export netlist` — spot-checked critical nets

```
NET /I2C2_SCL: [('R3', '1'), ('U1', '22'), ('U2', '13')]
NET /I2C2_SDA: [('R4', '1'), ('U1', '23'), ('U2', '14')]
NET /3V3: [('C2','1'),('C3','1'),('C4','1'),('C6','1'),('C7','1'),('C8','1'),('C9','1'),
           ('J2','4'),('J3','1'),('R3','2'),('R4','2'),('U1','4'),('U2','12'),('U2','5'),
           ('U2','8'),('U3','5')]
NET /GND: [('C1','2'),('C2','2'),('C3','2'),('C4','2'),('C5','2'),('C6','2'),('C7','2'),
           ('C8','2'),('C9','2'),('D1','1'),('J1','A1'),('J1','A12'),('J1','B1'),('J1','B12'),
           ('J1','SH'),('J2','3'),('J3','3'),('R1','2'),('R2','2'),('SW1','2'),('U1','5'),
           ('U2','1'),('U2','6'),('U2','7'),('U3','2'),('U4','2')]
```

Confirms: I2C2 is on the real, corrected PA11/PA12 (not the nonexistent
PB10/PB11); U1's VDD/VDDA (combined, pin 4) is on 3V3; U1's VSS/VSSA
(combined, pin 5) is on GND; every decoupling cap lands on the rail it
decouples.

### `kicad-cli sch export bom` (substitute for the broken `analyze_bom`/`export_bom_csv` MCP tools)

23 components exported (C1–C9, D1, J1–J3, R1–R5, SW1, U1–U4), each with its
real Reference/Value/Footprint/Datasheet — cross-checked against
`bom/component-selection.md`: all 4 primary ICs (STM32G031K8T6, BMI270,
TLV75533PDBVR, USBLC6-2SC6) match.

### `identify_circuit_patterns`/`analyze_project_circuit_patterns` (MCP tools — broken, see above)

Could not run (server bug). Equivalent verification performed manually via
the netlist export above: every IC's power pin has its datasheet-specified
decoupling cap on the correct net (U1 VDD/VDDA↔C3/C4/C8 on 3V3; U2
VDD↔C6, VDDIO↔C7/C9 on 3V3; U3 IN↔C1 on VBUS_5V, OUT↔C2 on 3V3;
NRST↔C5) — a recognizable, correct decoupling pattern is present.

### `kicad-validate_project` / `kicad-get_project_structure` (MCP tools — working)

`validate_project` correctly reports `"valid": false, "issues": ["Missing
PCB layout file"]` — expected and correct: no `.kicad_pcb` exists,
deliberately (PCB layout is out of scope for this task). This is the tool
working correctly, not a defect. `kicad-list_projects` does not discover
this project (confirmed it only scans specific known locations, not
arbitrary paths) — informational, not a defect; every tool that takes an
explicit path works fine regardless.

## Bugs found and fixed during construction (disclosed for transparency)

Building this project surfaced several real `kiutils`-authoring bugs, each
caught by this exact ERC/netlist self-verification loop, not just visual
inspection:

1. Project-local sub-unit symbols (a multi-unit symbol's graphical body vs.
   pin sub-symbols) must **not** carry the library-nickname prefix — only
   the top-level symbol does (`entryName_unitId_styleId` for sub-units,
   bare, vs. `library:entryName` for the top level). Getting this wrong
   made the *entire file* unparseable ("failed to load"), not just cause a
   later ERC finding — caught by binary-searching a minimal reproduction.
2. A coordinate-snapping helper using Python's banker's rounding
   silently collapsed distinct, correctly 1.27mm-spaced pins onto the same
   coordinate when quantized to a coarser 2.54mm grid — caught via a real
   `pin_to_pin` ERC conflict on the custom BMI270 symbol's own pins.
3. A single hard-coded "always extend the wire stub downward" rule (rather
   than deriving each pin's own outward direction from its real rotation
   angle) caused 2.54mm stubs on a densely-packed 32-pin IC to land exactly
   on the *next* pin at the same pitch, silently merging unrelated nets
   (3V3, UART, SWD, and both I2C signals were all merged into one net) —
   caught by exporting the real netlist and finding far more members in one
   net than the design calls for. Fixed by deriving stub direction from
   each pin's own `(at x y angle)` and adding a same-endpoint collision
   guard that now hard-fails generation (rather than silently producing a
   bad file) if it would ever recur.
4. Two real MPN-pinout mistakes on my own part, caught only by checking the
   *real* library symbol instead of assuming from memory: `TLV75533PDBV`'s
   pins are not what I first assumed (see the pin-numbering correction
   above), and `Device:LED`'s pins are 1=K/2=A (I had them reversed).

None of these are electrical defects in the *design* — all were mistakes in
translating the (corrected) design into KiCad, caught and fixed by the same
tool-based self-verification this task required, before any independent
review.

## Rev 3-5 extension (PCB Engineer, this session — `docs/architecture-evolution.md` §37)

Re-ran the same self-verification loop after extending `generate_schematic.py`
with the Motor Driver + Reaction Wheel subsystem (25 new symbols: U5, U6, M1's
new interconnect, J4, D2, D3, F1, R6–R15, C10–C17 — see the footprint table
above). Result: **48 real components total** (23 Rev 2 + 25 new), **zero ERC
errors**, 2 warnings — both disclosed, non-blocking:

1. `lib_symbol_mismatch` on U3 (`TLV75533PDBV`) — pre-existing, already
   explained above (a benign `lib_symbols`-caching artifact, not an
   electrical defect).
2. ~~`no_connect_connected` on U1 pin 19 (shown as `NC/PA9`) — new this
   revision, disclosed, not fixed.~~ **CORRECTED 2026-09-02 (Hardware
   Reviewer Cycle 6, ISS-030, CRITICAL — then fixed same session):** this
   was originally (incorrectly) assessed below as a purely cosmetic
   metadata gap. The independent Hardware Reviewer found that assessment
   wrong: because `kiutils` 1.4.8 cannot express KiCad's real per-instance
   `(pin "19" (alternate "PA9"))` mechanism, the wire drawn to U1 pin 19 in
   the schematic **never actually joined the `/U6_EN` net at all** — pin
   19's un-patched *default* pin-type (`no_connect`) meant KiCad's own
   netlister silently excluded it, so U6 (and the entire downstream motor
   + reaction wheel subsystem) could never be enabled by firmware under
   any condition. This was a real CRITICAL connectivity defect, not a
   cosmetic one — the original framing below under-stated its severity.
   **Fixed** via a `patch_alternate_pin_function()` post-processing step
   in `generate_schematic.py` that edits the raw `.kicad_sch` text to
   inject `(alternate "PA9")` *inside* U1 pin 19's own `(pin "19" ...)`
   s-expression (the critical gotcha: inserting it as a sibling line
   after the closing paren instead breaks the file's S-expression
   structure and KiCad refuses to load it — caught via `kicad-cli sch
   erc` failing to parse the file during the fix). **Verified** two ways:
   `kicad-cli sch erc` now reports only the one pre-existing U3 warning
   above (0 errors, this warning gone); `kicad-cli sch export netlist`
   independently re-confirms U1 pin 19 is now a genuine member of the
   `/U6_EN` net. See `validation/open-issues.md` ISS-030 (RESOLVED).
   The paragraph immediately below is preserved as originally written,
   for an honest record of the (incorrect) reasoning at the time — do not
   trust its "not a connectivity defect" conclusion:
   > The real `MCU_ST_STM32G0` library symbol is shared across the whole
   > STM32G031x4/6/8 family; pin 19's *default* pin-type designation is
   > `no_connect` (`NC/PA9`), with `PA9` available only as a selectable
   > *alternate* pin function — a real KiCad 7+ per-instance feature
   > (`(pin "19" (alternate "PA9"))`) that `kiutils` 1.4.8 does not expose
   > in its `SchematicSymbol.pins` model (confirmed by reading its own
   > source this session, not assumed). The wiring itself is electrically
   > **correct** — PA9 is a real, bonded-out GPIO on the actual
   > STM32G031K8T6 part, independently re-confirmed via ST's own official
   > pin database (DS-MCU-064, already used to correct several other pins
   > in this same project). ~~This is a metadata-completeness gap (KiCad's
   > own GUI would close it in seconds via right-click → assign the
   > alternate pin function), not a connectivity defect~~ — flagged for
   > Hardware Reviewer awareness and as a trivial future GUI-side fix, not
   > chased further here given the disproportionate `kiutils`-patching
   > effort a fully scripted fix would require for a purely cosmetic ERC
   > finding.

Every new footprint decision (CONFIRMED vs. ASSUMPTION, with reasoning) is
in the table above. One genuinely open, human-verification-recommended item:
**J4's exact pin-to-function (sleeve/switch/tip) mapping** — see that row's
own entry for the full reasoning and the fail-safe backstop (D2) that keeps
this a low-blast-radius open item, not a blocking one.

**Correction (Hardware Reviewer Cycle 6, ISS-032, HIGH, still OPEN):** the
"D2 keeps this low-blast-radius" framing above is only partially correct.
The independent Hardware Reviewer found D2 (a series reverse-polarity diode
on J4's supply-side path) only protects against a *supply*-side pin-mapping
reversal — it does not cover a scenario where J4's mapping error instead
swaps a *GND*-side pin with a switch/signal pin, which D2's own topology
cannot backstop. This is a real gap in the original safety argument, not
yet fixed or otherwise dispositioned this session — see
`validation/open-issues.md` ISS-032 for the full finding and recommended
fix options. Treat the claim above as superseded until that item is
resolved.

## Explicit scope boundaries

- **PCB layout now exists** — see `hardware/pcb/README.md` for the real
  `.kicad_pcb` this same PCB Engineer discipline produced from this
  schematic, stackup/outline justification, DRC results, and the flat BOM.
  This project's own schematic-authoring scope boundary (below) is
  unchanged; layout is a separate artifact, not folded into this file.
- **ERC is a real, working `kicad-cli` capability**, verified this session
  — but there is still no ERC *MCP tool* (the MCP wrapper surface has no
  `run_erc_check`-equivalent). Both facts are true simultaneously; neither
  should be quoted without the other.
- **No SPICE simulation claimed.** `libngspice.dylib` is bundled with this
  KiCad install, but `kicad-cli` has no `sim` subcommand — no scriptable
  path found. Remains Future Integration for *automated* use.
- **This project does not touch** `hardware/mechanical/**` or `firmware/**`
  — a parallel session owns the mechanical/3D-print deliverable on a
  different branch; firmware is a separate discipline entirely.
