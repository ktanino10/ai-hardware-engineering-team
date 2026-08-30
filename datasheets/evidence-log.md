# Evidence Log — Evidence ID Registry

Every `DS-<CATEGORY>-<NNN>` Evidence ID cited anywhere in this repository
(`bom/`, `hardware/`, `validation/`, `requirements/traceability-matrix.md`)
must have exactly one row here. This is the single place the ID resolves to
an actual citation — update here, not by re-typing citation text elsewhere.

ID format: `DS-<CATEGORY>-<NNN>` — see `docs/architecture.md` §6.3 for the
category code convention (`MCU`, `IMU`, `PWR`, `CONN`, `SNS`, `MTR`, …).

| Evidence ID | Datasheet metadata record | Section | Table | Page | Parameter / Claim supported | Recorded by | Date |
|---|---|---|---|---|---|---|---|
| DS-MCU-001 | `<datasheets/manufacturer_partnumber_revX.md>` | `<e.g. 6.3.1>` | `<e.g. Table 8>` | `<e.g. 44>` | `<e.g. VDD Recommended Operating Condition>` | `<agent/human>` | `<date>` |

## Rules

- One row per distinct citation, even if two rows point at the same
  datasheet — a citation is (document, section/table/page, specific
  parameter), not just "the document".
- Never reuse a retired ID for a different citation.
- If a value later turns out to be `UNKNOWN` (couldn't actually be
  confirmed), do not assign it an Evidence ID — record it as `UNKNOWN` in
  the consuming artifact instead, and only add a row here once a real
  citation exists.
- `datasheets/README.md` "Used for Evidence IDs" field on each metadata
  record should list the IDs that cite it, kept roughly in sync with this
  table.
