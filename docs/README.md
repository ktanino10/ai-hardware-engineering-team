# Documentation

[English](README.md) | [日本語](README.ja.md)

Start with the [project overview](../README.md) and [contributor entry
point](../AGENTS.md). This index separates reader-facing language editions
without forking the engineering source of truth.

| Guide | Purpose |
|---|---|
| [Architecture](architecture.md) | Roles, evidence, tooling boundaries and human/design gates |
| [Workflow](workflow.md) | Phase entry/exit criteria, handoffs and change propagation |
| [Bounded work](work-execution.md) | Frozen contracts, reservations, progress and terminal outcomes |
| [Start a design cycle](commands/make-circuit.md) | Bounded kickoff prompt and variants |
| [Assembly evidence](assembly-evidence.md) | WIP evidence, manifests and separately approved documentation |
| [Rigid-body simulation](simulation.md) | Model, evidence and independent-review contract |
| [Evaluation](evaluation.md) | Single-agent versus multi-agent comparison |
| [Pages guide](pages.md) | Landing pages, viewer limitations and dashboard language behavior |
| [Language coverage](language-coverage.md) | Source revision, paired guides and deliberately shared material |

## Artifact entry points and operating instructions

These links also cover reader surfaces outside `docs/`. The language
selector is centralized here for source-bound records that must not be
rewritten merely to add navigation.

| Surface | English | Japanese |
|---|---|---|
| Datasheet metadata | [Policy and template](../datasheets/README.md) | [方針・テンプレート](datasheets.ja.md) |
| Firmware | [Overview](../firmware/README.md) | [分野の入口](firmware.ja.md) |
| Bench-IMU-01 firmware | [Build and behavior](../firmware/bench-imu-01/README.md) | [build・実装の説明](bench-imu-01-firmware.ja.md) |
| Schematic / PCB / fabrication exports | [Reading and regeneration](hardware.md) | [読み方・再生成](hardware.ja.md) |
| Mechanical / STL / drawings | [Source guides](hardware.md#mechanical-source-stl-and-drawings) | [全再生成手順](mechanical-artifacts.ja.md) |
| Simulator | [Run and interpret](simulator.md) | [実行・解釈](../simulation/README.md) |
| Startup trials | [Ten-second trials](startup.md) | [始動試験](../simulation/STARTUP.md) |
| Blender replay | [Commands and evidence](../simulation/blender/README.md) | [再描画・証拠](blender-replay.ja.md) |
| ROOT exchange | [Compiled adapter](../simulation/root/README.md) | [解析データ交換](root-analysis.ja.md) |
| Circuit viewer | [Modes and PDF regeneration](../visualization/circuit-viewer/README.md) | [操作・PDF 再生成](circuit-viewer.ja.md) |
| Assembly viewer | [Controls and limitations](../visualization/assembly-viewer/README.md) | [操作・限界](assembly-viewer.ja.md) |
| Dashboard | [Data and parsing](../visualization/dashboard/README.md) | [操作・解析規則](dashboard.ja.md) |

## Reading editions and shared records

English guides keep their existing paths so agent instructions, parsers and
section references continue to work. Japanese reading editions use
`.ja.md` siblings. Architecture/workflow reading editions explain the active
rules and link the original incident narratives rather than copying old
reviews into a second ledger. The coverage record distinguishes reading
editions from translations; it does not claim that every repository file is
translated.

Agent profiles, skills, scoped instructions, schemas, commands, code, design
records, Evidence IDs, findings, approvals and historical references are
shared. Their literal identifiers and status vocabulary are not translated.
An explanation never changes a source value, review verdict, human decision
or gate. If an edition disagrees with its source, treat it as a documentation
defect, consult the canonical source and reconcile the editions together.
