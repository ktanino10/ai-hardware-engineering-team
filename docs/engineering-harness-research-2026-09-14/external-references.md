# External reference research（2026-09-14）

Scope: 16 URLs were treated as untrusted public references in the Cloud
research. No installer, package hook, MCP server or example script was run.
The [original Cloud document](https://github.com/ktanino10/ai-hardware-engineering-team/blob/2d3bb27bcb14ee04b30dd13b3bb5dd37402d4724/docs/engineering-harness-research-2026-09-14/external-references.md)
preserves its inspection history. The local successor retrieved only the
three previously inaccessible official pages and two specified pinned
LICENSE files; new observations, source hashes and separate native
version/help-only preflight are in [`local-supplement.md`](local-supplement.md).
Historical DNS failures remain observations of Cloud, not current site status.

## URL coverage

| # | URL | Cloud result / local successor | Inspected revision/source |
|---:|---|---|---|
| 1 | https://github.com/ignaciomolini/mcp-fusion360 | OK | README; latest commit `3419de8ae314f9a2c4a85770cf4b6c02163e0d7a` 2026-06-24; `mcp-server/src/tools.ts`; `Fusion360MCP/handlers.py`; MIT LICENSE |
| 2 | https://github.com/blwfish/freecad-mcp | Cloud OK; local LICENSE OK | README/TOOLS/SECURITY; pinned `ff13461e21e4b8bc1d97473e661ceeaf4e7d1bf6` 2026-09-14. Cloud README states LGPL-2.1-or-later; local pinned LICENSE contains LGPL v2.1 text. Grant-scope qualification below. |
| 3 | https://github.com/CREATeNG/freecad-mcp-bridge | OK | README; latest commit `5a4ecdde8492a315d8de4fe8aa08e579484cba60` 2026-07-08; MIT LICENSE |
| 4 | https://github.com/blwfish/kicad-mcp | OK | README; latest commit `33838c9b20445b95e3bae3a40b75eb4e5081ca28` 2026-09-14; server.py; pyproject; MIT LICENSE |
| 5 | https://github.com/NiRuLabs/kicad-mcp-server | OK | README; latest commit `2fd14d32fb2532071649cf6779b5e97b524e0a1b` 2026-07-28; server.py; tools.py; pyproject; MIT LICENSE |
| 6 | https://github.com/ahujasid/blender-mcp | OK | README; latest commit `5f8ddaf6e987c4aa0c3467fcc548838b28f64477` 2026-09-07; server dump; addon dump; MIT LICENSE |
| 7 | https://github.com/PoBruno/mcp-blender-agent | OK | README; latest commit `a45012e4fd6471c40e8ae5c2f001336aefe8100c` 2026-07-20; architecture docs; MIT LICENSE |
| 8 | https://www.blender.org/lab/mcp-server/ | Cloud BLOCKED/UNAVAILABLE; local HTTP 200 | Cloud fetch failed: `No address associated with hostname`. Local page/warning/add-on link verified; source implementation, license and runtime not inspected. See supplement `LOCAL-BLENDER`. |
| 9 | https://github.com/CoplayDev/unity-mcp | OK | README; latest commit `2fcc17957823f2494b7b1f7ade92c0fb56f4adb1` 2026-09-05; package.json; MIT LICENSE |
| 10 | https://agentcad.dev/ | Cloud BLOCKED/UNAVAILABLE; local HTTP 200 | Cloud fetch failed: `No address associated with hostname`. Local product/install/benchmark statements inspected as publisher claims, not measured results. See `LOCAL-AGENTCAD`. |
| 11 | https://github.com/jdilla1277/agentcad | Cloud OK; local LICENSE OK | README/pyproject; pinned `4e96365cfebb43650c164da7f661bd8a9968ff4c` 2026-09-14; local pinned root LICENSE verifies Apache License 2.0 text. |
| 12 | https://github.com/ai-cad-labs/ai-cad | OK | README; latest commit `c7503b4febd3bfa3368c1df38adb187eeb375fd7` 2026-08-09; ADR-0006; ADR-0012; Apache-2.0 LICENSE |
| 13 | https://github.com/writeitai/team-harness | OK | README; latest commit `c07e3ab4b33018649e4f4ba6c79174da246ab973` 2026-07-20; pyproject; Apache-2.0 LICENSE |
| 14 | https://github.com/agentharnesses/agentharnesses | OK | README; latest commit `0d855c606e1977a00f7e6c7511b218bf54de7f2f` 2026-08-19; harnesses-ref README; LICENSE |
| 15 | https://github.com/harnessworks/harness-starter-kit | OK | README; latest commit `62437bec264b2deed83353e8209660d645e86828` 2026-06-18; validation docs; theory docs; MIT LICENSE |
| 16 | https://www.opendesign.com/ja/products/mcp-servers | Cloud BLOCKED/UNAVAILABLE; local HTTP 200 | Cloud fetch failed: `No address associated with hostname`. Local prerelease/product/commercial statements inspected, not GA, runtime or confinement verification. See `LOCAL-ODA`. |

Commit dates and "latest commit" wording in unchanged Cloud rows mean **latest at that Cloud inspection**, not current branch tips. The parent separately verified on 2026-09-14 around 22:10 JST that all 13 pinned GitHub SHAs resolve, all 13 repositories are non-archived with `isFork=false`, and root LICENSE files exist. That metadata is not proof of no code ancestry, maturity, effective license scope or passing tests; it was not a new source audit by this successor.

## OSS comparison matrix

Exactly one **current recommendation** per project follows. `ADAPT` means a pattern-only proposal, not package adoption; future possibilities belong in the separate condition column. No dependency is adopted or installed by this matrix. Tool/test counts below are publisher/document claims unless explicitly source-inspected, not executed reliability or maturity measurements.

| Project | Domain | MCP/API | State | Validation | Rollback | Tool surface (not a reliability ranking) | Security | License | Source row / Cloud commit date | Current recommendation | Reason / future condition |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Fusion360 MCP | Fusion 360 CAD | MCP stdio Node -> localhost HTTP -> Fusion Python add-in | Design/document introspection; parameters | Zod; Vitest/manual tests documented, not run here | Source-inspected parameter snapshots/restore on `computeAll()` failure | 11 typed tools; geometry/introspection | Live-session mutation; localhost auth not verified | MIT | #1 / 2026-06-24 | **ADAPT** | Typed-tool and parameter-restore patterns only; not the first adapter or general geometry rollback. |
| freecad-mcp | FreeCAD CAD/CAM/mesh | Live/headless MCP bridge | Instance discovery, logs, document state | README reports 1430 unit + 147 integration tests; counts/coverage/pass status not independently verified | Documented checkpoint/recovery helpers | Broad typed groups plus arbitrary Python | Python/filesystem/OS reach; local single-user assumption; update check | LGPL v2.1 LICENSE text verified; README claims `-or-later`, grant scope unresolved | #2 / 2026-09-14 | **REFERENCE ONLY** | Future wrapping requires its own scope, license/compatibility and runtime review; documented breadth is not proven maturity. |
| FreeCAD MCP Bridge (CREATeNG) | FreeCAD live bridge | Loopback HTTP inside FreeCAD | Toggle, output paging/history | README-level paging; implementation tests not inspected | Output history, not verified document rollback | Python/file execution | Loopback access is not a sandbox; no telemetry per docs | MIT | #3 / 2026-07-08 | **REFERENCE ONLY** | Session-toggle/history reference; no verified typed engineering gate. |
| blwfish/kicad-mcp | KiCad EDA | FastMCP stdio; Python/CLI bridge | Project/schematic/PCB/DRC/export | README reports 2000+ tests; pytest/ruff/mypy declared, not run or coverage-audited here | Owned artifact rollback not verified | Advertised schematic/PCB/analyze/export/DRC/autoroute | Broad filesystem/subprocess access | MIT | #4 / 2026-09-14 | **REFERENCE ONLY** | CLI-first uses installed native KiCad, **not this package**. Its pinned revision is not linked to Primary's dated `ctx` incident; a future MCP wrapper needs separate approval/tests. |
| NiRuLabs/kicad-mcp-server | KiCad EDA / IPC | MCP -> IPC protobuf | Connected board; batch transaction IDs | Bounded source inspection; tests not verified | `begin_commit` / `end_commit`, commit/drop | Nets/pads/tracks/vias/routing | IPC token and source-path exposure; installer not fetched | MIT | #5 / 2026-07-28 | **ADAPT** | Transaction vocabulary only; live IPC/token setup adds unnecessary first-MVP scope, not a measured maturity verdict. |
| ahujasid/blender-mcp | Visualization/modeling | MCP + addon/socket | Scene and generated assets | README features; source safe-mode checks | No owned engineering rollback verified | Raw `execute_code` plus optional safe mode | Arbitrary Python/network/credential paths | MIT | #6 / 2026-09-07 | **REJECT** | Excluded from MVP; retain the documented risks as reference, not a visualization-to-validation substitution. |
| PoBruno/mcp-blender-agent | Typed Blender operations | Node MCP -> HTTP -> addon | Refs, graph snapshots/diffs | Structured response/typed-input architecture; tests not run | Grouped undo/graph restore pattern | Documented 200+ typed operations | Localhost without auth; do not expose remotely | MIT | #7 / 2026-07-20 | **ADAPT** | Typed responses/refs and grouped-restore patterns only; any future visualization adapter remains non-authoritative. |
| Blender official lab MCP server | Experimental Blender interface | Page describes external MCP/addon/client | Runtime state UNKNOWN | No engineering validation tested | UNKNOWN | Python API interface per official page | Explicit warning: generated code has no guards against deletion/remote disclosure; recommends VM/non-sensitive system | UNKNOWN; linked source/license not inspected | #8 / local page | **REFERENCE ONLY** | Page is now accessible; add-on v1.0.3 link names Blender 5.1.0 minimum. Not built-in LLM support, installation permission or runtime acceptance. |
| Unity MCP | Visualization/XR/game tools | Unity Editor MCP package | Project/scene assets | Test framework dependency; test/profiling/build features per docs | Not verified | 47 tools/Roslyn validation per docs | Editor control; remote/auth behavior not exercised | MIT | #9 / 2026-09-05 | **REFERENCE ONLY** | Possible later XR/digital-twin/training surface, never an engineering approval authority. |
| AgentCAD (website + source) | build123d-native / CadQuery-compatible CAD | Local CLI + MCP per project | Versioned builds/outputs/metrics | JSON/check-spec/inspect described; no local CAD validation run | Retains last successful build per docs; Primary restore not verified | Execute/render/export/validate/inspect/diff | Local viewer; native-stack compatibility not tested | Apache-2.0 root LICENSE verified locally | #10–11 / 2026-09-14 | **ADAPT** | CLI/output/versioning patterns only. Published Python 3.10–3.12 support does not establish compatibility with Rev5's reported Python 3.14 environment; author benchmarks are not our results. |
| AI-CAD | Multi-agent mechanical CAD | Coding-agent/filesystem harness | Checkpoint/reflection/file dashboard | Rulebook and deterministic-gate design described, not executed | Proposal-before-promotion pattern | CadQuery/render/measure/spec/export | Environment/symlink/Python constraints; not installed | Apache-2.0 | #12 / 2026-08-09 | **ADAPT** | Versioned proposal/promotion and resume patterns only; no wholesale architecture or team import. |
| Team Harness | Multi-model orchestration | Python CLI/SDK -> worker CLIs | Run/session manifests | Capability/retry/circuit-breaker contracts | No artifact rollback | CLI/model abstraction | API-key/env risk; bypass flags in examples not executed | Apache-2.0 | #13 / 2026-07-20 | **REFERENCE ONLY** | Existing roles already cover orchestration; future abstraction needs a new scoped decision, not another factory now. |
| Agent Harnesses | Harness specification | HARNESS.md/routing/reference CLI | Directory context/capability bundles | Reference validation commands documented | Not engineering artifact rollback | Progressive disclosure | Instruction packaging, not a security boundary | Cloud README: Apache-2.0 code / CC-BY-4.0 docs; GitHub classifier `NOASSERTION` | #14 / 2026-08-19 | **REFERENCE ONLY** | Root HARNESS.md would duplicate current instructions; full license-scope review remains separate. |
| Harness Starter Kit | Repository harness adoption | Prompt-first docs/scripts/skills | Constraints/feedback/evaluation loop | Smoke/lifecycle checks are not proof of effectiveness | No domain rollback | Drift/effectiveness-report patterns | Clone/install prompts not followed | MIT | #15 / 2026-06-18 | **ADAPT** | Evaluation/failure-memory patterns only; no root adoption or new instruction files. |
| ODA MCP Servers | STEP/IFC/DWG interoperability | Shared MCP tool/geometry schema per vendor | Prerelease, Q3 2026 planned | Determinism is a vendor claim, not measured | UNKNOWN | Local/on-prem or network transports per page | Confinement depends on deployment/model; not independently tested | Core SDK annual subscription / royalty-free terms per vendor; not OSS or an exact price | #16 / local page | **REFERENCE ONLY** | Future interoperability reference only; no proof of GA/connectivity, registration, contact, install or upload. |

The parent's GitHub license classifiers were MIT for rows #1/#3/#4/#5/#6/#7/#9/#15, LGPL-2.1 for #2, Apache-2.0 for #11/#12/#13 and NOASSERTION for #14. These are metadata, not a full license review. Local inspection closes the two **LICENSE-file retrieval** gaps: FreeCAD's generic LGPL v2.1 text (§13 and example notice) alone does not settle this project's `only` versus `or-later` grant; preserve the separate Cloud README claim pending actual grant review. AgentCAD's pinned Apache 2.0 text is verified, not its full dependency/license compatibility.

## Focused comparison conclusions

### Fusion patterns

Fusion360 MCP demonstrates a useful parameter/introspection/mutation split: read parameters/bodies/features/sketches first, then mutate through typed tools. Its `update_user_parameter` snapshots all user parameter expressions before mutation and attempts restore on `computeAll()` failure. That is a good **pattern**, but it is not a general rollback solution: it covers user parameters, not arbitrary geometry/features, exported files, or another writer’s concurrent changes.

### FreeCAD projects

`blwfish/freecad-mcp` documents broader state/diagnostic/fixture/async/workbench coverage than the inspected CREATeNG README. That is a documentation comparison, **not verified greater maturity or test reliability**. Its documented Python/filesystem/OS reach requires more than an optional path wrapper for any future untrusted-writer isolation claim. `CREATeNG/freecad-mcp-bridge` offers a smaller session-toggle/history pattern but still centers on live Python execution. Neither runtime was exercised; neither package is adopted.

### KiCad projects and MVP suitability

Recommend one **native KiCad CLI adapter** because the public EDA artifact-to-evidence handoff is Rev5-relevant and ERC/DRC offer narrow, measurable commands. A committed fixture still requires an installed executable, libraries and actual successful domain runs. Local version/help success does not prove real clean/failing ERC/DRC acceptance.

Primary `docs/architecture.md` §5.2 describes a **2026-08-31 environment-specific** 5-working/11-failing MCP observation and real CLI/ERC use. It does **not** establish that `blwfish/kicad-mcp` at `33838c9b20445b95e3bae3a40b75eb4e5081ca28` has that bug; README test counts do not establish a comparative reliability ranking either. CLI-first neither installs nor depends on that MCP project. NiRuLabs' transaction vocabulary is useful as a pattern, but live IPC/token work is not needed for the proposed bounded proof.

### Blender/visualization

Raw generated Python (`ahujasid/blender-mcp`) has a broad file/network execution surface; optional safe mode is not engineering validation. PoBruno's typed-operation/grouped-undo design supplies narrower patterns, not a demonstrated reliability win. The locally accessible [official Blender page](https://www.blender.org/lab/mcp-server/) explicitly warns of unguarded generated-code deletion/disclosure and recommends an isolated/non-sensitive system. Its "official" label, linked add-on and published examples do not authorize installation or turn visualization into DRC/ERC/mechanical acceptance.

### Unity

Unity MCP is useful as a future XR/Quest/training/digital-twin visualization adapter with editor/test/build tooling. It must not become an engineering validation authority for CAD/EDA/physical evidence.

### AgentCAD / AI-CAD

AgentCAD describes a compact generated-code -> versioned-output/metrics/diff CLI contract; AI-CAD describes a larger filesystem-resumable CAD workflow with gate-before-promotion. Adapt those **patterns**, not the packages or their claimed effectiveness. AgentCAD's website advertises Python 3.10–3.12 and author-reported GPT-5 Nano/CADGenBench gains; neither Python 3.14 compatibility nor a Rev5/Harness improvement was measured here. No install/example prompt or benchmark percentage enters our experiment results.

### General harnesses

Team Harness is useful for model/worker abstraction, caller context and rate-limit circuit breakers, but it optimizes coordination breadth rather than the Primary’s immediate EDA reliability proof. Agent Harnesses/HARNESS.md and Harness Starter Kit emphasize progressive disclosure, constraints, feedback, memory and evaluation; Primary already has AGENTS/copilot-instructions/skills/workflows, so adding root `HARNESS.md` now would duplicate policy instead of proving reliability. Use the concepts, not the files, in the first MVP.
