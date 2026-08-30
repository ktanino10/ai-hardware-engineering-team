# PCB Layout Files

This directory holds PCB layout artifacts (e.g. a KiCad project's `.kicad_pcb`
file and related layout documents).

## Conventions

- Run DRC before any "pre-fabrication" human approval gate
  (`docs/architecture.md` §10) using `run_drc_check`; track results over
  time with `get_drc_history_tool` (feeds `docs/evaluation.md` metrics).
- Attach a visual snapshot (`generate_pcb_thumbnail` /
  `generate_project_thumbnail`) to `validation/design-review.md` for the
  human reviewing the pre-fabrication gate.
- ERC is **not** currently available as a tool in this environment — do not
  claim schematic-level electrical rule checking has been done via ERC
  until such a tool exists (`docs/architecture.md` §13).
- Keep BOM consistent with `bom/component-selection.md` — use `analyze_bom`
  / `export_bom_csv` to check for drift before a "major BOM change" gate.
