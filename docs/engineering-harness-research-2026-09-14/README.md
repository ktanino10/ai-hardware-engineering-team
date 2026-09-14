# Engineering Harness research/design milestone（2026-09-14）

これは `engineering-harness-research-design-2026-09-14` の pre-implementation deliverable set と、同日 local successor による限定修正である。元の [Cloud 5-document history](https://github.com/ktanino10/ai-hardware-engineering-team/tree/2d3bb27bcb14ee04b30dd13b3bb5dd37402d4724/docs/engineering-harness-research-2026-09-14) を保持し、新しい取得結果と version/help-only receipt は [`local-supplement.md`](local-supplement.md) に分けた。MVP 実装、外部 MCP install、repo-wide restructure、root `HARNESS.md` 追加、実 ERC/DRC、実験結果生成は行っていない。

## Decision summary

Recommended MVP: **Incremental Harness Core + one native KiCad CLI adapter — CANDIDATE, human choice pending**.

狙いは Rev5 三軸設計と AI の扱いの改善を並行して支える、**EDA validation evidence → test-only review-readiness decision** の最小実験である。既存 admission/CI を保持し、one-adapter の controlled invocation/output path 上だけで lifecycle、validation verdict、freshness、gate、recovery を分けて記録する。実 KiCad の clean/failing ERC/DRC と、残る失敗クラスの matched synthetic fault injection を A/B 両群で比較する。CLI-first は外部 KiCad MCP package の採用でも、全 MCP が壊れているという判断でもない。

現在確認できた native 能力は **KiCad 10.0.1 の version/ERC-help/DRC-help が exit 0** まで。Actual domain execution/acceptance は **NOT_RUN**、MVP reliability milestone は **incomplete/unproven**。Fixture の成功、rollback 成功、typed approval、task `DONE` は、既存 Rev5 blocker の解消・Design Complete・物理許可を意味しない。

## Documents

| Document | Purpose |
|---|---|
| [`primary-assessment.md`](primary-assessment.md) | Historical pre-external-research checkpoint plus labelled attribution/authority corrections; agent-profile bodies NOT_REVIEWED |
| [`external-references.md`](external-references.md) | Coverage of all 16 requested URLs, OSS matrix, ADOPT/ADAPT/WRAP/REFERENCE ONLY/REJECT decisions |
| [`architecture-proposal.md`](architecture-proposal.md) | Responsibilities, alternatives, recommended architecture/MVP, state/dependency/gate/evidence/retry/rollback/human/security/GitHub strategies |
| [`experiment-contract.md`](experiment-contract.md) | Candidate matched A/B contract; every failure class in both arms, with real/synthetic coverage and positive controls |
| [`local-supplement.md`](local-supplement.md) | Source-linked local successor receipt, pinned LICENSE/page gap closure, exact native preflight limits and remaining human choice |

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
| 28 | Implementation Roadmap | this README, [`Implementation roadmap (later task only)`](#implementation-roadmap-later-task-only) |

## Implementation roadmap (later task only)

1. Human Chief Engineer chooses the smallest MVP/adapter scope; no automatic adoption or implementation follows this research.
2. Only after that choice, reserve a new bounded implementation task with explicit `tools/`/test write scope and agreed execution limits.
3. Add separate operation/verdict/freshness/gate/recovery records alongside existing `agent_workflow`, not a replacement admission tool.
4. Add one installed-native KiCad CLI adapter and tiny owned test fixtures; no MCP package, arbitrary shell/export or irreversible-action permission.
5. Cover direct-input checks, retries, bounded output restore and path mistakes under the explicitly cooperative-writer assumption, not a claimed OS sandbox.
6. Freeze and run all matched A/B cases, including mandatory real clean/failing ERC/DRC, invalid outline/geometry, corrupt outputs and positive controls. Missing real-tool coverage leaves the milestone PARTIAL.
7. Publish actual outcomes/cost availability; equal A/B results are no demonstrated improvement. Any additional adapter or adoption needs another explicit human decision after reviewing measured benefit.

## Unresolved decisions / prerequisites

- Human approval is required before implementing the MVP architecture.
- Local version/help observations do not transfer to every later runner or replace actual clean/failing ERC/DRC fixtures. Missing capability = `BLOCKED` observation and incomplete mandatory coverage, not a proven MVP.
- The three historical Cloud DNS gaps are locally closed for **page retrieval**; linked source/runtime, vendor guarantees and comparative test reliability are not thereby verified.
- The two pinned LICENSE-file gaps are closed, but FreeCAD `only` versus `or-later` grant scope and full license/dependency compatibility still require review before adoption.
- Agent-profile bodies remain NOT_REVIEWED. CODEOWNERS enforcement is NOT_VERIFIED; typed actor/date records cannot prove human authority.
- Direct-only dependency checking does not solve transitive invalidation. Optional wrappers cannot prevent unmanaged CLI/MCP calls or arbitrary same-UID namespace mutation.
- No real hardware, manufacturing export, first power-on/flashing, private/local Rev5 artifact, simulation/control change or new physical permission is authorized by this package.
