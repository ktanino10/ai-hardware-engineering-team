# Datasheets — Metadata-Only Reference Policy

**This repository is public. Manufacturer datasheets are copyrighted works.
Do not commit the actual datasheet files (PDF, etc.) to this directory or
anywhere else in the repository.** `.gitignore` blocks common binary
extensions under `datasheets/` as a backstop, but the real rule is: don't
put them here in the first place.

## What goes in this directory

One metadata record per datasheet, named:

```
datasheets/<manufacturer>_<part-number>_<revision>.md
```

Example: `datasheets/stmicroelectronics_stm32f103c8t6_rev14.md`

Each metadata record uses this template:

```markdown
# <Manufacturer> <Part Number> Datasheet — Rev <revision>

- **Manufacturer**: <name>
- **Part Number**: <part number>
- **Datasheet Title**: <exact title as printed on the document>
- **Revision / Version**: <e.g. Rev 14>
- **Publication Date**: <date printed on the document, or UNKNOWN>
- **Official URL**: <manufacturer's own URL for this datasheet>
- **Retrieved Date**: <date this was fetched/reviewed>
- **Local cache note**: <e.g. "cached locally on <name>'s machine, not
  committed" — do not paste a path that only exists on one contributor's
  disk as if it were a repo path>
- **Used for Evidence IDs**: <list of Evidence IDs in
  datasheets/evidence-log.md that cite this record, kept in sync manually>
```

## Why metadata-only

- Avoids redistributing copyrighted manufacturer content from a public repo.
- The **official URL** lets any human independently re-fetch the exact same
  document and verify a cited section/table/page.
- Extracted constraint tables (`Parameter | Min | Typ | Max | Unit | Source`)
  elsewhere in the repo are this project's own structured factual
  extraction — not a bulk reproduction of the datasheet's original text or
  diagrams. Keep extraction to the minimum facts needed to support a design
  decision.
- This is a pragmatic engineering/repo-hygiene policy, not a legal opinion.
  For a formal legal determination (e.g. for a future space-flight program),
  consult the repository owner / legal counsel.

## Evidence citation format

Anywhere in the repo, cite evidence by **Evidence ID**
(`docs/architecture.md` §6.3), not by re-typing a filename/page number
directly:

```
[Source: DS-IMU-003]
```

Look up `DS-IMU-003` in `evidence-log.md` for the full citation (which
metadata record, section/table/page, and what parameter/claim it supports).

## See also

- `evidence-log.md` — the Evidence ID registry.
- `docs/architecture.md` §6 — full evidence model and copyright policy.
- `.github/instructions/datasheets.instructions.md` — Copilot-enforced rules
  for this directory.
