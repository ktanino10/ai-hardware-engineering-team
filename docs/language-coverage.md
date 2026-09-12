# Public language coverage

[English](language-coverage.md) | [日本語](language-coverage.ja.md) | [Guide index](README.md)

**Source and configuration baseline:**
`f259608bd6d4e673393bb6ed4924ea7dc892cb6d`.
Only the public checkout is the input to these editions. No private
branch, raw endpoint, source package or private history is imported.
References already present in the public text remain references; they
were not followed to obtain additional design material.

## What “covered” means

The [machine-readable inventory](language-coverage.json) maps **all 26
pre-existing reader entry points** (root README/AGENTS, seven active
framework guides, and seventeen domain/readme/procedure entries).
Each row names its exact source and English/
Japanese destination; the test checks inventory completeness for README
surfaces and rejects unclassified Markdown paths.

`translation` means the operational explanation is rendered in the other
language, preserving command grammar and boundaries. `reading-edition`
means the active explanation/procedures have been edited for readers while
long historical narratives, numerical design tables, per-part decisions
and original review receipts remain linked in their canonical source.
**A reading edition is not a line-for-line translation of that source.**
No missing historical or engineering translation is advertised as complete.

The root and [domain index](README.md#artifact-entry-points-and-operating-instructions)
provide EN/JA navigation even for source-bound files intentionally left
unchanged. Japanese-only simulator/startup procedures now have substantive
English editions, not English headings over Japanese instructions.

## Coverage by surface

| Surface | Treatment |
|---|---|
| Root README and contributor entry | Separate EN/JA pages, paired navigation, complete role/command entry points |
| Architecture and workflow | Existing canonical English paths/headings unchanged except navigation; Japanese active-rule reading editions, with historical incident prose linked |
| Bounded work and kickoff | Separate Japanese contract explanation, JSON/CLI grammar and bounded prompt; canonical execution paths unchanged |
| Assembly contract | Japanese fields, status/approval requirements, artifact coverage, invalidation and invocation; schema/templates shared |
| Simulation contract and evaluation | Japanese explanation of model/evidence/gate boundaries and metrics; numerical source records shared |
| Datasheet metadata | Japanese policy and complete metadata template; actual copyrighted files never added |
| Firmware overview/board | Japanese scope, pin/command/telemetry explanation and build instructions; stale historical margin claims not promoted to current safety claims |
| Schematic/PCB/fab | EN/JA reading guide, exact rendering/export commands, equivalence checks, independent/human holds; past layout iterations/BOM decisions stay shared |
| Mechanical/STL/drawings | EN/JA access, full Japanese STL/2D command sequences and drafting/Blender pipelines; stale legacy demos and source-frame differences disclosed |
| Simulator/startup | English operational editions including setup, run/replay/suite/verify, all case distinctions and startup/accounting caveats |
| Blender/ROOT | Japanese command sequences, saved-native validation, encoding/data exchange and operation-specific tool limitations |
| Circuit/assembly/dashboard guides | Japanese controls, derivation, parsing, regeneration and limitations; original long implementation histories remain shared |
| Pages landing | Separate static EN/JA pages, shared CSS; no build/deployment machinery added |
| Dashboard UI | Existing EN/JA dictionary/data split retained; explicit language links and language-aware Back added |
| Circuit/assembly UI | Existing English UI and shared data retained; Japanese descriptions do not claim to translate those runtime interfaces |

## Deliberately shared material, not omitted by accident

All remaining tracked Markdown is classified by explicit prefixes/paths in
the inventory:

- `.github/`: executable agent/skill/scoped instructions, prompts and PR
  template stay canonical. Japanese reader explanations do not become a
  second adopted configuration.
- `requirements/`, `bom/`, `datasheets/` metadata/evidence, design and
  review files in `hardware/`, `firmware/`, `simulation/`, `validation/`:
  source values, Evidence IDs, findings, approvals, FMEA, ECO, physical
  bring-up/assembly procedures and hash-bound records stay shared. These
  safety-bearing procedures are **not newly translated or reapproved**.
  The reader guides link them rather than replacing their exact decisions.
- `docs/architecture-evolution.md` and `docs/reference-cases/`: historical
  evolution and source-scoped reference learning remain shared English/
  source-language records. They are not silently rewritten as current policy.
- Code, schemas, CAD, BOM CSV, binary/media artifacts, source datasets,
  trajectories and manifests are shared regardless of display language.
  The runtime paths listed in the inventory remain unchanged by this work.

Original domain READMEs are left in place to avoid invalidating engineering
provenance merely to add a language switch. Their localized destinations
live under `docs/`; both indexes are the common navigation entry.

## Maintenance and validation

Update a source and its affected reading edition together; retain the
distinction between current rules and dated observations. Keep IDs, units,
literal command options, status vocabulary and cited human decisions
unchanged. An unexplained conflict is a documentation defect, not a new
engineering decision.

The existing workflow unittest command includes inventory, local Markdown
links/anchors, paired Pages links and dashboard language regressions:

```sh
PYTHONPATH=tools python3 -m unittest discover -s tools/tests -p 'test_*workflow*.py'
```

Dashboard behavior is exercised with Node's built-in VM/assert modules
(explicitly skipped if Node is unavailable), without a package dependency
or live data fetch. These checks do not certify semantic translation,
physical artifacts, native CAD or hardware. Publication/deployment and
independent acceptance remain separate from local documentation checks.
