---
description: 'Datasheets are the immutable Source of Truth: metadata-only references, never commit the actual copyrighted document.'
applyTo: 'datasheets/**'
---

- This repository is public. Never commit an actual datasheet file (PDF,
  etc.) under `datasheets/` — `.gitignore` blocks common binary extensions
  here as a backstop, but the rule is: don't add them in the first place.
- Only add/edit **metadata reference records** (`*.md`): manufacturer, part
  number, revision/version, publication date, official URL, retrieval date.
  Follow the exact template in `datasheets/README.md`.
- Never rewrite, paraphrase away, or "helpfully summarize" the numeric
  content of a datasheet inside a metadata record — a metadata record
  describes the *document*, it does not reproduce the document's content.
  Extracted parameter values belong in `Parameter | Min | Typ | Max | Unit |
  Source` tables elsewhere (`bom/`, `hardware/`), each row citing an
  Evidence ID.
- Every Evidence ID (`DS-<CATEGORY>-<NNN>`) used anywhere in the repository
  must have a corresponding row in `datasheets/evidence-log.md` with the
  full citation (metadata record, section/table/page, parameter/claim).
- If a datasheet cannot be found for a part under serious consideration, do
  not fabricate values or infer them from a similar part — write `UNKNOWN`
  and escalate to the human (`docs/architecture.md` §10).
