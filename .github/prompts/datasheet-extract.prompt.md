---
description: 'Extract design constraints from a specific datasheet into the standard Parameter|Min|Typ|Max|Unit|Source table, with Evidence IDs.'
agent: agent
---

Act as an operator of `.github/skills/datasheet-analysis/SKILL.md`.

Datasheet / part: ${input:part:e.g. "STMicroelectronics STM32F103C8T6, Rev 14"}

Do:
1. Confirm (or create) its metadata record in `datasheets/` per
   `datasheets/README.md` — manufacturer, part number, revision, official
   URL, retrieval date. Do not add the actual PDF to the repo.
2. Extract parameters into the standard table, explicitly separating
   Absolute Maximum Ratings / Recommended Operating Conditions / Typical
   Characteristics:

   ```
   | Parameter | Min | Typ | Max | Unit | Source |
   |---|---|---|---|---|---|
   ```

3. Assign an Evidence ID (`DS-<CATEGORY>-<NNN>`) to each row and register
   the full citation (metadata record, section, table, page, parameter) in
   `datasheets/evidence-log.md`.
4. Extract the recommended application circuit notes (decoupling values,
   pull-up/down ranges, power-sequencing, timing diagrams) and, for
   MCU-like parts, the pin function table.
5. List anything not explicitly stated as `UNKNOWN` — do not infer from a
   similar part. List any contradictions found between sections/revisions.

Output: the extraction table(s), the new/updated `datasheets/evidence-log.md`
rows, and the UNKNOWN/contradiction list.
