# Reference case: ai-ready workflow maintenance

## Scope and status

- Author/date: Copilot-assisted workflow maintenance, 2026-09-06.
- Guidance: **CANDIDATE**, pending independent review and human PR approval/merge.
- Human request: use `johnpapa/ai-ready` when improving this agent framework.
  Comparison baseline: `c9f8fda45ac4434be657b066ae28115afc08c3c8` on
  `copilot/workflow-convergence`, not the running Rev5 worktree.
- Project adoption: implemented on this feature branch; not deployed to main
  or existing App sessions. No hardware, part, requirement or safety change.

## Source identity

The public reference was pinned to `ab8aed2aaefb186061cd7549daefad0248598636`
and inspected on 2026-09-06. Its skill declares version 1.3.0 and MIT licensing.
These are source locators, not hardware Evidence IDs. The skill was not
installed or executed; the adaptations below use original project-specific
wording rather than copied templates.

| Key | Publisher and exact source | Content SHA256 | Relevant scope |
|---|---|---|---|
| AR-SKILL | John Papa, [ai-ready skill](https://github.com/johnpapa/ai-ready/blob/ab8aed2aaefb186061cd7549daefad0248598636/skills/ai-ready/SKILL.md) | `c83a13842174aea60974c533f894d587af829c86ca5a998ac82ee30e86434455` | Steps 1d, 2, 3, 6, 7 and 8: drift, contributor context, maintenance matrix and PR handoff. |
| AR-GUIDE | John Papa, [repository agent guide](https://github.com/johnpapa/ai-ready/blob/ab8aed2aaefb186061cd7549daefad0248598636/AGENTS.md) | `40c1d91cd8e2bbfe5b27251ea7874fd0485bbcc7efcc019340d0080cc7f12e27` | Thin entry point; one canonical skill with supporting material loaded on demand. |

## Observations and scope

| Class | Observation | Limit |
|---|---|---|
| OBSERVED | The skill inspects existing configuration before proposing additions and calls for actual repository commands and dependency/update relationships. | Its own repository is a documentation skill, unlike our Python/C/native-CAD project. Its setup commands are not ours. |
| PUBLISHED CLAIM | Its readiness score counts satisfied assets out of twelve. | That is not a measured reduction in our run time, credit consumption, defects or hardware risk. No score/badge is adopted. |
| OBSERVED | A read-only sample request for the latest ten inline PR comments in our repo returned four. Two comments on PR19 identify the same merge-status inconsistency in different files. | This is a narrow sample, not a finding that many independent PRs repeat the problem. The historical PR17 state was not re-audited here. |

The sampled comments are
[PR19 change-log feedback](https://github.com/ktanino10/ai-hardware-engineering-team/pull/19#discussion_r3914573624),
[PR19 README feedback](https://github.com/ktanino10/ai-hardware-engineering-team/pull/19#discussion_r3914573538),
[PR19 coordinate-convention feedback](https://github.com/ktanino10/ai-hardware-engineering-team/pull/19#discussion_r3914573587)
and [PR43 read-only token feedback](https://github.com/ktanino10/ai-hardware-engineering-team/pull/43#discussion_r3930104438).
No comments were posted or historical design records rewritten.

## Transfer and actual next work

| Existing gap | Bounded adaptation and owner | Counterexample / non-transfer |
|---|---|---|
| No short root contributor guide or PR template; README sends every reader into the full architecture. | Workflow maintainer adds `AGENTS.md`, a concise README onramp and `.github/PULL_REQUEST_TEMPLATE.md`, using existing commands and real outcome fields. | Copying every role into AGENTS would increase context and create another conflicting policy source. |
| Update relationships are spread across the workflow and role histories. | Workflow maintainer adds a small maintenance matrix to the common instructions; existing Python tests check onboarding links and configuration entry-point drift. | The matrix routes affected updates; it does not demand new copies of every historical artifact. |
| Publication-state claims and least-privilege CI are visible in actual review feedback. | PR handoff distinguishes local/pushed/merged/task/design states. The existing configuration CI gets `contents: read`; its required job name is retained. | A local commit cannot prove a merge; a checked template box cannot approve hardware. Other jobs may legitimately need different token permissions. |

Do not create another CI pipeline, changelog, role hierarchy or speculative MCP
configuration to fill the reference's asset checklist. Existing workflows,
`validation/change-log.md` and runtime-verified native tools remain authoritative.
Cloud setup, issue forms and plugin installation are outside this bounded change.

## Comparison and review

- Candidate outputs: `AGENTS.md`, common maintenance matrix, README onramp,
  PR template, configuration pinning and existing workflow regression coverage.
- Held constraints: fourteen roles, their technical ownership, existing hardware
  gates, active sessions, native capabilities and the prior duplicate-dispatch guard.
- Behavioral/performance comparison with real App sessions: **NOT RUN**.
  Source inspection and repository tests cannot establish a faster design cycle.
- Independent reviewer, exact reviewed candidate commit and introducing PR:
  **PENDING**. Human promotion: **PENDING**.
- Revisit applicability if the reference changes, the repository's command/
  registration graph changes, or actual operation contradicts these assumptions.
  Future outcome measurements use `docs/evaluation.md`, not a new scoring service.
