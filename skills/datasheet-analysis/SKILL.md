# Skill: Datasheet Analysis

## Purpose

Systematically extract design constraints from a manufacturer datasheet so
downstream design/review work has a grounded, structured, citable source of
truth instead of prose that has to be re-read and re-interpreted every time.

## When to use

Any time a datasheet is introduced for a part in active consideration or
use (Component Selection, Circuit Design, or re-verification triggered by a
Hardware Reviewer finding).

## Inputs

- The manufacturer datasheet (a local working copy — never committed to the
  repo, see §6.2 of `docs/architecture.md` and `datasheets/README.md`).

## Procedure

1. **Identify the official datasheet.** Record manufacturer, part number,
   revision/version, publication date, and the **official URL** it was
   retrieved from. Create/update its metadata record in `datasheets/`
   (filename convention in `datasheets/README.md`) — this is what actually
   gets committed, not the PDF.
2. **Separate the three categories explicitly — never blend them:**
   - **Absolute Maximum Ratings** — values that, if exceeded even
     momentarily, risk permanent damage. Not an operating point.
   - **Recommended Operating Conditions** — the range the part is designed
     to run in.
   - **Typical Characteristics** — representative values under stated test
     conditions; not a guarantee.
3. **Extract parameters into the standard table:**

   ```
   | Parameter | Min | Typ | Max | Unit | Source |
   |---|---|---|---|---|---|
   | Supply Voltage (VDD) | 1.71 | 3.3 | 3.6 | V | DS-MCU-001 |
   ```

   `Source` is an Evidence ID (`docs/architecture.md` §6.3), not a bare page
   number — register the full citation in `datasheets/evidence-log.md`
   (metadata record + §section + Table N + p.page + which parameter/claim
   it supports).
4. **Extract application/reference circuit notes**: decoupling capacitor
   values and placement guidance, pull-up/pull-down ranges, power-sequencing
   requirements, timing diagrams (setup/hold, rise/fall, bus timing).
5. **Extract the pin function table** (for MCU-like parts): pin name,
   function, direction, alternate functions, special notes (boot-strap,
   NC, etc.).
6. **Flag UNKNOWN** for anything not explicitly stated. Do not infer a value
   from a similar part's datasheet and present it as this part's number.
7. **Flag contradictions** — between sections of the same datasheet, or
   between revisions if more than one is in play.
8. **Note the test conditions attached to any Typical value** — a "typical"
   number without its test condition (temperature, voltage, load) is not
   safely comparable to your actual design point.

## Output

- One metadata record per datasheet in `datasheets/`.
- Evidence ID entries in `datasheets/evidence-log.md`.
- The consolidated `Parameter | Min | Typ | Max | Unit | Source` table(s),
  attached to whichever artifact needs them (`bom/component-selection.md`
  during selection, the Circuit Engineer's design rationale log during
  design).
- A list of UNKNOWNs and contradictions found.

## Common pitfalls to avoid

- Treating a Typical value as if it were guaranteed.
- Missing a footnote/condition that changes what a number actually means
  (e.g. "at Ta = 25°C" vs. your actual operating temperature).
- Mixing Absolute Maximum and Recommended Operating values in the same
  column.
- Copying large verbatim blocks of datasheet text/diagrams instead of
  extracting the specific facts needed (see the copyright policy,
  `docs/architecture.md` §6.2).
