# Primary repository assessment checkpoint（外部調査前）

Task key: `engineering-harness-research-design-2026-09-14`  
Checkpoint time: 2026-09-14T08:56Z（UTC）  
Primary repository: `ktanino10/ai-hardware-engineering-team`  
Requested verified public main: `a6ebb82d712746087aa1735198f5a3778d799fd7`  
Fetched current `main`: `a6ebb82d712746087aa1735198f5a3778d799fd7`（main は requested SHA と一致し、追加差分なし）  
Working branch/starting HEAD: `copilot/engineering-harness-research-design` at `2135294a4da8cf4aed7a9082586721f7e0ad42c4`  
Bounded-work reservation: `tools/agent_workflow.py start` succeeded; run_id `5424f05e-4911-408b-a8fe-ea805b3ee4e2`; local recorded state only, not design approval.

## Ordering record

この文書は、外部 reference URL を開く前に作成した Primary Repository grounded checkpoint である。ここまでに読んだ primary inputs は `AGENTS.md`, `.github/copilot-instructions.md`, `docs/work-execution.md`, `docs/workflow.md`, `docs/architecture.md`, `docs/assembly-evidence.md`, `docs/simulation.md`, `tools/agent_workflow.py`, `tools/check_assembly_evidence.py`, `tools/check_open_issues.py`, `tools/check_id_uniqueness.py`, `tools/check_mechanical_pcb_sync.py`, 関連 workflow YAML, CODEOWNERS, PR #76/#77 の public metadata/file scope である。`.github/agents/` 本文はこの session の上位境界により直接読まない。role roster と boundaries は `docs/architecture.md` と `.github/copilot-instructions.md` に記録された public summary に基づく。

## Current architecture（現状）

- Repository mission は「単一 AI が plausibly-looking circuit を書く」ことの置換であり、primary-source evidence、narrow role ownership、independent review、human authority を要求する（`docs/architecture.md:10-22`）。
- Workflow は Requirements → Component → Datasheet → Circuit → Independent Review → Validation → Design Complete Gate を中心に、Mechanical WIP/Review、Firmware Bring-up、Power Architecture、Simulation lane を分岐させる（`docs/workflow.md:25-73`）。
- 実装済み roles は 14 個で、Hardware Lead が orchestration/gates、domain agents が artifacts、reviewers が independent verdicts を持つ（`docs/architecture.md:78-95`）。
- Durable Source of Truth は repository files (`requirements/`, `bom/`, `hardware/`, `validation/`, `simulation/`, `docs/`) であり、chat message ではない（`docs/workflow.md:459-466`）。
- Repository-local execution state は `tools/agent_workflow.py` が Git common dir の SQLite に保存する。これは live telemetry でも approval でもない（`docs/workflow.md:467-472`, `docs/work-execution.md:155-176`）。
- Session-local `todos` は planning であり、cross-session execution authority ではない（`docs/workflow.md:473-485`）。

## Existing harness-like features（既存 harness 相当機能）

| Capability | Existing enforcement | Source | Boundary |
|---|---|---|---|
| Bounded work reservation | `agent_workflow.py start` validates owner role, immutable commits, clean config, inputs, write scope, dependency artifacts, duplicate RUNNING tasks | `tools/agent_workflow.py:86-137`, `tools/agent_workflow.py:189-239` | Does not launch/monitor/stop agents (`docs/work-execution.md:60-64`) |
| RUNNING/DONE/BLOCKED state | SQLite rows record run_id, task_id, session, worktree, fingerprint, summary, next action, artifacts | `tools/agent_workflow.py:149-166`, `tools/agent_workflow.py:242-290` | RUNNING is reservation, not proof of a live worker (`docs/work-execution.md:123-130`) |
| Shared-ledger serialization | Non-Hardware-Lead writes to shared ledgers are rejected | `tools/agent_workflow.py:24-28`, `tools/agent_workflow.py:81-83`, `tools/agent_workflow.py:117-119` | Guard is admission, not OS permission boundary (`docs/work-execution.md:172-176`) |
| Dependency handoff binding | DONE artifacts are hashed and consumer inputs must contain exact recorded bytes | `tools/agent_workflow.py:205-219`, `tools/tests/test_agent_workflow.py:176-229` | Only declared dependencies; no transitive invalidation graph beyond explicit handoffs |
| Assembly evidence contract | Manifest validates source_revision, source/file SHA-256, WIP/APPROVED state, Fusion producer, approval binding | `tools/check_assembly_evidence.py:164-251` | Not geometry or safety certification (`tools/check_assembly_evidence.py:1-5`) |
| Current assembly dependency invalidation | `current.json` selects live manifest; changed dependencies trigger manifest validation | `tools/check_assembly_evidence.py:280-353`, `docs/assembly-evidence.md:234-258` | Only assembly current package scope |
| Hardware gate | CI parses `validation/open-issues.md` for CRITICAL/HIGH status and diff-aware exemption | `tools/check_open_issues.py:1-47`, `.github/workflows/hardware-gate.yml:1-64` | It checks Markdown state, not engineering validity of fixes |
| ID uniqueness | CI scans ECO/ISS/MISS/DS namespaces for duplicates | `tools/check_id_uniqueness.py:1-40`, `.github/workflows/id-uniqueness-check.yml:1-44` | No semantic approval; namespace collision only |
| Mechanical-PCB sync | Advisory CI compares `.scad` board dimensions/hole constants with `.kicad_pcb` outline/hole positions | `tools/check_mechanical_pcb_sync.py:1-45`, `.github/workflows/mechanical-pcb-sync-check.yml:1-55` | Narrow scalar geometry check; not connector/courtyard/clearance proof (`tools/check_mechanical_pcb_sync.py:32-37`) |
| Simulation provenance | Run evidence binds input/model/output hashes and verifies current vs historical outputs | `docs/simulation.md:124-170` | Simulation is never hardware/assembly approval (`docs/simulation.md:35-44`) |
| Human review path | CODEOWNERS requires @ktanino10 review on hardware, mechanical, firmware, validation change-log, BOM, requirements | `.github/CODEOWNERS:1-15` | CODEOWNERS is GitHub review policy, not technical proof |

## Current failure modes（分類付き）

| Failure mode | Classification | Causal source / evidence | Existing regression coverage | Harness design implication |
|---|---|---|---|---|
| MCP/server tool existence and capability are over-claimed | Code-supported / documented real incident | KiCad MCP 5-working/11-failing split and client-dependent errors are recorded; raw `kicad-cli` workaround is required (`docs/architecture.md:283-348`) | No generic adapter contract test; documented as policy | Harness must record requested tool vs actual invoked adapter/version/result semantics |
| DRC/ERC result can be conflated with wrapper exit/file existence | Policy gap | Architecture already warns to use real KiCad CLI and report exact semantics (`docs/architecture.md:340-362`) | No generic result-normalizer yet | Gate engine must parse domain result payloads and block on semantic failure, not exit 0 alone |
| Cross-discipline mechanical/PCB drift can persist | Reproduced historical failure, now partly covered | MISS-034 rationale in sync checker (`tools/check_mechanical_pcb_sync.py:5-11`) | `tools/check_mechanical_pcb_sync.py` covers board outline/hole pairs | Harness needs explicit dependency graph and STALE state for all dependent evidence, not one bespoke pair |
| Markdown table parser truncation can hide findings or ID rows | Reproduced historical failure, now covered for specific tables | `tools/check_open_issues.py:9-24`, `tools/check_id_uniqueness.py:28-40` | Dedicated parser tests in tools/tests | Harness should prefer typed JSON evidence/state records over free-text table parsing for machine gates |
| Duplicate semantic IDs across branches | Reproduced historical failure, covered | `tools/check_id_uniqueness.py:10-26` | ID uniqueness CI | Harness must allocate scoped operation/evidence IDs transactionally or derive collision-resistant IDs |
| Work reservation can be mistaken for live execution | Policy gap / code-supported boundary | `docs/work-execution.md:60-64`, `docs/work-execution.md:123-130` | `test_work_status_cannot_be_used_as_physical_approval` covers state vocabulary (`tools/tests/test_agent_workflow.py:259-266`) | Harness must separate operation reservation, live adapter lease, and terminal attestation |
| Database transaction rollback is mistaken for artifact rollback | Policy gap | `agent_workflow.py` only records SQLite state; no artifact snapshots/restore path (`tools/agent_workflow.py:149-166`, `tools/agent_workflow.py:242-260`) | No artifact rollback tests | MVP needs operation-owned snapshots and revision fences; no generic `git reset` |
| Source mismatch detection is not transitive dependency invalidation | Code-supported limitation | `agent_workflow.py` validates declared direct inputs/dependency artifacts only (`tools/agent_workflow.py:205-219`) | Dependency artifact tests cover direct handoff (`tools/tests/test_agent_workflow.py:176-229`) | Harness must model artifact graph edges and stale downstream approvals |
| APPROVED assembly can be invalidated by re-exported artifacts | Reproduced covered case | Evidence fingerprint excludes review artifact but binds source/output artifacts (`tools/check_assembly_evidence.py:154-161`, `tools/tests/test_assembly_evidence.py:120-125`) | Yes for assembly evidence | Generalize fingerprinting to other domains |
| Capability-blocked Fusion/native/video can be mislabeled as equivalent output | Covered for assembly | Fusion workflow and suffix/producer checks (`tools/check_assembly_evidence.py:192-227`, `tools/tests/test_assembly_evidence.py:176-188`) | Yes for assembly | Adapter layer must preserve producer/provenance and block unsupported substitutions |
| Policy-only PR checks can be stuck or blocked by unrelated findings | Reproduced historical CI issue, partly covered | Required-check no path-filter rationale (`.github/workflows/hardware-gate.yml:8-35`, `.github/workflows/agent-frontmatter-lint.yml:12-19`) | Diff-aware checks | Harness must distinguish applicability/N/A from PASS/FAIL and make required checks deterministic |
| Firmware defects could be incorrectly coupled into Design Complete | Policy gap already addressed in architecture | Firmware branch deliberately does not feed hardware gate (`docs/workflow.md:356-367`) | Firmware review file separate | Harness must support gate scope and not over-couple validation domains |
| Missing evidence can be parked as indefinite human approval | Policy gap | Assembly contract says UNKNOWN needs owner/action, not indefinite waiting (`docs/assembly-evidence.md:62-68`) | No generic blocker aging/escalation check | Harness must require owner, next action, and approval binding fields for exceptions |

## Project state / open PR overlap

- Current public main comparison is recorded once in the checkpoint header above; the fetched SHA matched the requested verified SHA at this checkpoint.
- Open public PRs observed: #78 (this WIP), #77 firmware Linux build documentation, #76 public CLI/workflow-tool verification with no file changes, #74 CI smoke for Rev5 host package, #73 public-safe Rev5 host sequencer/source records.
- PR #76 is useful bounded prior evidence that public CLI/workflow commands succeeded, but it has no adopted main changes and is not proof of this Harness architecture.
- PR #77 is useful bounded prior evidence for Linux firmware compilation, but it is unmerged and changes firmware documentation plus a separate docs receipt, not this task's `docs/engineering-harness-research-2026-09-14/` write scope.
- Recent Actions for PR #78 initially reported `action_required` with zero jobs/logs for several required workflows; no failed job logs were available through GitHub Actions API. Treat as workflow/action permission state, not a code failure reproduced by this task.

## Immediate architecture gaps to carry into external comparison

1. No common Harness state schema for design revision, evidence revision, validation status, adapter operation identity, cost/model identity, retry and rollback outcome across all domains.
2. Existing direct dependency checks are strong for declared handoffs and assembly manifests but do not provide a repository-wide transitive invalidation engine.
3. Existing CI is deterministic but fragmented by file/domain; there is no unified gate result object that captures PASS/FAIL/N/A/BLOCKED/STALE and semantic result evidence.
4. Rollback currently exists mainly as database transaction safety and preservation of immutable historical files; application-level owned rollback is not implemented.
5. Tool integrations are described and sometimes verified per session, but lack a model/tool-independent adapter interface that normalizes snapshot/execute/validate/commit-or-rollback.
6. Human approval is documented and CODEOWNERS-protected for key paths, but not yet bound by a typed approval object to exact operation input/evidence/artifact hashes outside assembly manifests.

