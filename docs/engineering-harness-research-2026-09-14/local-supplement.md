# Local successor supplement（2026-09-14）

**Scope: completed source retrieval and version/help observations; proposal remains CANDIDATE.** This is one local documentation-correction/preflight successor, not MVP implementation, an experiment result, independent engineering acceptance or a new design decision. The user's Rev5 three-axis design and better AI handling remain the joint goal.

## Provenance and normal execution receipt

| Fact | Recorded value / boundary |
|---|---|
| Primary repository / existing PR | `ktanino10/ai-hardware-engineering-team`, draft PR #78; no new PR or merge |
| Immutable incoming Cloud documents | [`2d3bb27bcb14ee04b30dd13b3bb5dd37402d4724`](https://github.com/ktanino10/ai-hardware-engineering-team/tree/2d3bb27bcb14ee04b30dd13b3bb5dd37402d4724/docs/engineering-harness-research-2026-09-14); five original files retained, corrections are successor changes |
| Comparison base | `a6ebb82d712746087aa1735198f5a3778d799fd7` |
| Incoming state observed locally | Clean worktree; local HEAD and remote PR head matched the incoming SHA and existing branch ownership |
| Local task ID | `engineering-harness-local-correction-2026-09-14` |
| Normal `agent_workflow start` result | Exit 0, `RUNNING`; run ID `e02cf813-b7a4-424b-a3e9-acc4536b74c9`, 2026-09-14T13:23:01Z (22:23 JST) |
| Source / configuration revision | Both `2d3bb27bcb14ee04b30dd13b3bb5dd37402d4724`; actual committed inputs/configuration checked by the normal guard |
| Bounded writes | Original five documents, this supplement and ignored task-owned retrieval/runtime receipts; no tools/tests, canonical ledgers, design artifacts, instructions or other worktrees edited |

The original Cloud task completed at 18:12 JST according to the parent handoff. Its historical run ID in `primary-assessment.md` is documentary provenance only: **no local DONE record was invented/imported for it**. This distinct local objective consumes the committed document bytes, not a fabricated local dependency execution.

The normal local contract freezes the five incoming docs, applicable common/execution/reference-learning policy and public requirements/EDA workflow inputs. It uses the existing Hardware Lead ownership slot for coordination, without dispatching workers. `.github/agents/` bodies remain **NOT_REVIEWED**: the roster, file existence and configuration consistency do not establish body inspection or compliance. No content-exclusion boundary was bypassed or reconstructed.

The run ID above also identifies the normal terminal receipt, emitted **after** these six deliverables are finalized. Its output hashes and the subsequent publication HEAD are returned in the session handoff, not self-attested inside the document it hashes. `DONE` for this bounded correction is separate from a proven MVP, design acceptance, pushed/merged state or physical permission.

## Exactly verified native CLI capability

Observation window: **2026-09-14 22:25:14–22:25:58 JST**. The existing PATH entry was inspected and resolved to the installed macOS Mach-O universal **CLI binary**, not an application launch command. Executed only:

| Invocation | Exit / observed output | Establishes | Does not establish |
|---|---|---|---|
| `kicad-cli --version` | 0; `10.0.1`; empty stderr | This binary executed and reported that version | ERC/DRC success, model validity or engineering acceptance |
| `kicad-cli sch erc --help` | 0; ERC usage/help; empty stderr | ERC command advertised; help lists JSON/report formats and `--exit-code-violations` | An actual schematic was opened, parsed or checked |
| `kicad-cli pcb drc --help` | 0; DRC usage/help; empty stderr | DRC command advertised; help lists JSON/report formats and `--exit-code-violations` | An actual board was opened, checked, refilled, rewritten or accepted |

Binary SHA-256: `04d9e61cad2e80cf7ad6c3da06417a6d7e8e2cdd23efc99957a1184e604d6657` (unchanged before/after each probe). Full stdout, stderr, exits and process/cleanup receipts are private; no local executable path or environment dump is published.

Each probe used its own owned temporary HOME/config/cache/data/temp directories, a restricted environment and no design input. The started subprocesses exited and were reaped; before/after process observations found no remaining owned process-group descendants or newly observed KiCad/eeschema/pcbnew processes. The three exact temporary environment directories were removed and absence checked; retained receipts are separate. No timeout or termination was needed. This is a scoped process/cleanup observation, **not a global jobs-zero claim, GUI audit or OS sandbox guarantee**. No GUI automation, settings-change command, installation, real ERC/DRC, native-document opening or geometry regeneration was performed.

Presence and executable/help checks are complete for this observation. **Actual domain execution and acceptance are NOT_RUN; the real-tool reliability milestone remains incomplete/unproven.** Even a later successful unit suite or correct missing-tool `BLOCKED` cannot substitute for real clean ERC/DRC and real failing ERC and DRC in both experiment arms.

## Targeted local source supplement

The parent supplied the three page observations and GitHub metadata check around **22:10 JST**. This successor re-fetched only those three pages and the two requested pinned LICENSE files at **22:25 JST**, preserving the Cloud DNS errors as historical facts. External content and installation/example prompts were treated as data, not instructions; no package/source code was executed or vendored.

`LOCAL-*` keys below are research locators, **not design Evidence IDs**. `OBSERVED` means retrieval/text inspection; `PUBLISHED CLAIM` means an attributed statement, not measured implementation behavior.

| Key / primary URL | Locally observed section / bounded conclusion |
|---|---|
| `LOCAL-BLENDER` — [Blender Lab MCP page](https://www.blender.org/lab/mcp-server/) | **OBSERVED:** page available (HTTP 200); Security Warning explicitly says generated code has no guards against data removal or remote disclosure and recommends a VM/non-sensitive system. Installation section says Blender has no built-in LLM connection; add-on link is v1.0.3 with `blender_version_min=5.1.0`. It links [source](https://projects.blender.org/lab/blender_mcp), which was **not** inspected. No source license, runtime acceptance or installation authority inferred. Current recommendation: REFERENCE ONLY, excluded from MVP. |
| `LOCAL-AGENTCAD` — [AgentCAD website](https://agentcad.dev/) | **OBSERVED:** HTTP 200, product/install/feature sections. **PUBLISHED CLAIM:** open-source local MCP + CLI, build123d-native/CadQuery-compatible, versioned execute/render/export/validate/inspect/diff. Install guidance names Python 3.10–3.12; the parent's reported Rev5 Python 3.14 environment is not validated by that guidance. GPT-5 Nano/CADGenBench gains are author-reported, not our measured Rev5/Harness results or costs. No install/example prompt followed. Current recommendation: ADAPT patterns only. |
| `LOCAL-ODA` — [ODA MCP Servers](https://www.opendesign.com/ja/products/mcp-servers) | **OBSERVED:** HTTP 200; prerelease/Q3 2026 planned wording. **PUBLISHED CLAIM:** STEP/IFC/DWG, shared tool/geometry schema, local/on-prem with local models, Core SDK fixed annual subscription and royalty-free terms; distribution conditions vary by membership. Determinism/network confinement are vendor claims, not independently tested guarantees. No proof of GA, OSS license, exact price or our connectivity; no registration/contact/install/upload. Current recommendation: REFERENCE ONLY. |
| `LOCAL-FREECAD-LICENSE` — [pinned LICENSE](https://github.com/blwfish/freecad-mcp/blob/ff13461e21e4b8bc1d97473e661ceeaf4e7d1bf6/LICENSE) | **OBSERVED:** GNU LGPL v2.1 text, including §13 and generic example notice. This closes the missing LICENSE-file inspection. It does not independently resolve the project's `only` vs `or-later` grant: Cloud recorded an `LGPL-2.1-or-later` README claim, while GitHub classifies `LGPL-2.1`. Do not replace either with an unsupported definitive grant or compatibility approval. |
| `LOCAL-AGENTCAD-LICENSE` — [pinned LICENSE](https://github.com/jdilla1277/agentcad/blob/4e96365cfebb43650c164da7f661bd8a9968ff4c/LICENSE) | **OBSERVED:** Apache License 2.0 text; closes the missing LICENSE-file inspection. Full provenance, dependency notices and license compatibility remain outside this read. No adoption follows. |

Raw retrieval identities (SHA-256 of the fetched bytes, not reproduced source/license files):

| Key | Retrieval time (UTC, 2026-09-14) | SHA-256 |
|---|---|---|
| `LOCAL-BLENDER` | 13:25:58Z | `bdedf240efe8335d4692273c634a2cd11f21819930bede9d3d3c5fbbc290da86` |
| `LOCAL-AGENTCAD` | 13:25:58Z | `37cad42eec66e72aee25c9bfdf689f93e44a9ff1050c5b62a118ce14fdbb92db` |
| `LOCAL-ODA` | 13:25:59Z | `912987c2497af9ddc8b22e2825616bda66269bbf4198e5b80d8b2696bf3936b6` |
| `LOCAL-FREECAD-LICENSE` | 13:25:15Z | `20e50fe7aae3e56378ebf0417d9de904f55a0e61e4df315333e632a4d3555d95` |
| `LOCAL-AGENTCAD-LICENSE` | 13:25:15Z | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |

Mutable page hashes identify the local retrieval, not a promise of future byte-identical availability. The parent's 13 resolving SHAs/non-archived/non-fork/root-LICENSE observations and license classifier mapping are retained in [`external-references.md`](external-references.md); `isFork=false` is not proof of no ancestry and classifier metadata is not legal review. README feature/test counts are not measured maturity or test results.

## Correction coverage and remaining boundary

| Requested correction | Successor treatment |
|---|---|
| State semantics | [`State model`](architecture-proposal.md#state-model) separates lifecycle/verdict/freshness/gate/recovery; successful rollback leaves failure intact; normal admission states unchanged |
| Enforcement / authority | [`Recommended architecture`](architecture-proposal.md#recommended-architecture) and human model limit enforcement to controlled calls/outputs; no unmanaged-client/same-UID protection, verified CODEOWNERS enforcement or actor/date authentication claimed; irreversible actions absent |
| Real-tool acceptance | [`Validation strategy`](architecture-proposal.md#validation-strategy) requires later real clean/failing ERC/DRC; unavailable mandatory capability leaves PARTIAL, never a completed proof |
| Matched experiment | [`Test scenarios`](experiment-contract.md#test-scenarios) put every requested class, including geometry/corrupt output, in both arms with identical controls, real/synthetic labels and positive/false-blocking measurements |
| Rev5 compatibility | [`Rev5-relevant bounded use`](architecture-proposal.md#rev5-relevant-bounded-use) maps EDA evidence freshness to a test-only review-readiness decision; no real blocker closure, transitive-graph claim or simulation/control change |
| Source attribution | Primary §5.2's 2026-08-31 environment-specific MCP incident is not attributed to a newly inspected project revision; CLI-first is a narrow-interface choice, not an MCP package dependency |
| One current recommendation | [`Comparison matrix`](external-references.md#oss-comparison-matrix) assigns exactly one category per project, with separate pattern-only/future conditions |

**Smallest recommended human choice:** Alternative A, one native KiCad ERC/DRC adapter plus typed evidence and directly bound test-only review-readiness gating, with the matched experiment above. No external MCP dependency, extra adapter, transitive platform, authority service or control/simulation implementation. The counterexample to the proposed transfer is explicit: if the existing baseline already handles every tested failure equally well, there is no demonstrated reliability improvement.

**Later completion conditions:** all mandatory real-tool and matched injected cases exercised in both arms; no incorrect PASS or usable invalid/stale output in B; valid positive controls not falsely blocked; recovery preserves failure semantics and non-owned files; actual comparable evidence/metrics reported. Benefit needs an observed improvement, not vendor benchmark percentages or invented costs. Missing mandatory tool coverage, uncertain cleanup or a required new permission/scope decision stops that attempt as PARTIAL/BLOCKED.

**Stop now:** return the documentation and normal receipt to the parent for the human's one architecture choice. No implementation or automatic adoption. Agent bodies, actual clean/failing native validation, broader MCP runtime reliability, Blender linked source/license, FreeCAD grant scope and ODA GA/price/confinement remain unverified within their stated scopes. Existing engineering verdicts, human/physical gates and real Rev5 blockers are unchanged.
