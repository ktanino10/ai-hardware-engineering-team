# Engineering Harness research/design milestone（2026-09-14）

これは `engineering-harness-research-design-2026-09-14` の pre-implementation deliverable set である。MVP 実装、外部 MCP install、repo-wide restructure、root `HARNESS.md` 追加、実験結果生成は行っていない。

## Decision summary

Recommended MVP: **Incremental Harness Core + one KiCad CLI adapter**.

理由: Primary repository already has bounded-work reservations, deterministic CI checks, KiCad source artifacts and documented KiCad CLI/ERC facts. The smallest reliability proof is therefore not an all-integrations platform; it is a thin Harness layer that normalizes operation state/evidence/gates/rollback around one deterministic KiCad adapter and a synthetic/test-only A/B experiment.

## Documents

| Document | Purpose |
|---|---|
| [`primary-assessment.md`](primary-assessment.md) | Primary repository assessment saved before external reference research |
| [`external-references.md`](external-references.md) | Coverage of all 16 requested URLs, OSS matrix, ADOPT/ADAPT/WRAP/REFERENCE ONLY/REJECT decisions |
| [`architecture-proposal.md`](architecture-proposal.md) | Responsibilities, alternatives, recommended architecture/MVP, state/dependency/gate/evidence/retry/rollback/human/security/GitHub strategies |
| [`experiment-contract.md`](experiment-contract.md) | Frozen Harness-vs-no-Harness A/B experiment design for the later MVP task |

## 28-deliverable coverage map

| # | Required deliverable | Covered in |
|---:|---|---|
| 1 | Current Architecture Assessment | `primary-assessment.md` Current architecture |
| 2 | Existing Harness-like Features | `primary-assessment.md` Existing harness-like features |
| 3 | Current Failure Modes | `primary-assessment.md` Current failure modes |
| 4 | Layer Responsibility Matrix | `architecture-proposal.md` Layer responsibility matrix |
| 5 | Architecture Gaps | `primary-assessment.md` Immediate architecture gaps |
| 6 | External Reference Research | `external-references.md` URL coverage and focused comparisons |
| 7 | OSS Comparison Matrix | `external-references.md` OSS comparison matrix |
| 8 | ADOPT/ADAPT/WRAP/REFERENCE ONLY/REJECT decisions | `external-references.md` Recommendation column and focused conclusions |
| 9 | Proposed Harness Architecture | `architecture-proposal.md` Recommended architecture |
| 10 | Alternative Architecture | `architecture-proposal.md` Architecture alternatives |
| 11 | Critical Review | `architecture-proposal.md` Critical self-review |
| 12 | State Model | `architecture-proposal.md` State model |
| 13 | Dependency Model | `architecture-proposal.md` Dependency model |
| 14 | Gate Model | `architecture-proposal.md` Gate model |
| 15 | Validation Strategy | `architecture-proposal.md` Validation strategy; `experiment-contract.md` scenarios |
| 16 | Evidence Model | `architecture-proposal.md` Evidence model |
| 17 | Retry Model | `architecture-proposal.md` Retry model |
| 18 | Rollback Model | `architecture-proposal.md` Rollback model |
| 19 | Human Approval Model | `architecture-proposal.md` Human approval model |
| 20 | Tool Adapter Architecture | `architecture-proposal.md` Tool adapter architecture |
| 21 | Multi-model Strategy | `architecture-proposal.md` Multi-model strategy |
| 22 | Security Assessment | `architecture-proposal.md` Security assessment; `external-references.md` Security column |
| 23 | GitHub System-of-Record Strategy | `architecture-proposal.md` GitHub system-of-record strategy |
| 24 | Mermaid Architecture Diagram | `architecture-proposal.md` Mermaid diagram |
| 25 | Proposed Folder Structure | `architecture-proposal.md` Proposed folder structure |
| 26 | MVP | `architecture-proposal.md` MVP recommendation |
| 27 | Harness vs No-Harness Experiment | `experiment-contract.md` |
| 28 | Implementation Roadmap | this README, [`Implementation roadmap（later task only）`](#implementation-roadmaplater-task-only) |

## Implementation roadmap（later task only）

1. Human Chief Engineer reviews this proposal and chooses MVP/adapter scope.
2. Create a new bounded implementation task with explicit write scope for `tools/` and tests.
3. Add minimal typed Harness schema and state/gate CLI.
4. Add one KiCad CLI adapter and synthetic fixtures.
5. Add tests for state, dependency, gate, retry, rollback and security path fences.
6. Run the A/B experiment contract and publish measured results under a new dated MVP evidence directory.
7. Only after successful measured benefit, consider additional adapters (Fusion parameter, AgentCAD/FreeCAD, typed Blender visualization) one at a time.

## Unresolved decisions / prerequisites

- Human approval is required before implementing the MVP architecture.
- KiCad CLI availability on the later MVP runner must be preflighted; unavailable tool = `BLOCKED`, not success.
- External blocked URLs (AgentCAD website, Blender official lab, ODA) need re-check if they become decision-critical.
- Licensing review is required before vendoring or depending on any external project; this milestone recommends patterns, not dependency adoption.
- No real hardware, manufacturing export, first power-on, first flashing, or private/local Rev5 artifact is authorized by this package.
