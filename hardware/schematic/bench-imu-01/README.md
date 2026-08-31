# Bench-IMU-01 — Real KiCad Project (Rev 2, corrected)

This is this repository's **first real KiCad project** — a genuine
`.kicad_pro`/`.kicad_sch` pair (plus a project-local `.kicad_sym` for the one
part not in any standard library), not the structured Markdown
schematic-equivalent document this repository used for every prior design
cycle. It captures **Bench-IMU-01 Rev 2** (already Design Complete, PR #6),
as corrected for **ISS-014** (see below) — the authoritative net-by-net
rationale remains `hardware/schematic/bench-imu-01-design.md`; this project
is the physically-verifiable artifact built from it, not a replacement for
its rationale.

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
| `bench-imu-01.kicad_sch` | The real schematic — 23 components, every net from the corrected design doc |
| `bench-imu-01.kicad_sym` | Project-local symbol library — BMI270 only (not in any standard KiCad library) |
| `sym-lib-table` | Registers the project-local `bench-imu-01` symbol library |
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
| MH1–MH4 | Mounting holes | *excluded from schematic* | — | No electrical net — standard KiCad convention places these in the PCB editor only; out of scope per this task's explicit no-PCB-layout instruction |

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

## Explicit scope boundaries

- **No PCB layout** (footprint placement, routing, copper pours) — out of
  scope per this task's kickoff; `kicad-validate_project`'s "Missing PCB
  layout file" finding is expected, not a gap to close here.
- **ERC is a real, working `kicad-cli` capability**, verified this session
  — but there is still no ERC *MCP tool* (the MCP wrapper surface has no
  `run_erc_check`-equivalent). Both facts are true simultaneously; neither
  should be quoted without the other.
- **No SPICE simulation claimed.** `libngspice.dylib` is bundled with this
  KiCad install, but `kicad-cli` has no `sim` subcommand — no scriptable
  path found. Remains Future Integration for *automated* use.
- **This project does not touch** the parallel, in-progress Rev 3
  (motor-driver) session's branch or files.
