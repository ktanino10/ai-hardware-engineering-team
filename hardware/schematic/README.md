# Schematic Design Files

This directory holds schematic design artifacts (e.g. a KiCad project's
schematic files, or exported schematic documents).

## Conventions

- If using KiCad, keep the project openable with the `kicad-*` tools
  available in this environment (`docs/architecture.md` §5.2):
  `list_projects`, `get_project_structure`, `validate_project`,
  `extract_schematic_netlist`, `analyze_schematic_connections`,
  `identify_circuit_patterns`.
- Every non-trivial design decision reflected here should have a
  corresponding entry in the Circuit Engineer's design rationale log
  (attach it alongside the schematic, or reference it from
  `validation/design-review.md`), citing an Evidence ID from
  `datasheets/evidence-log.md`.
- Do not hand-edit a schematic to "fix" a Hardware Reviewer finding without
  logging the change in `validation/change-log.md` (ECO).
