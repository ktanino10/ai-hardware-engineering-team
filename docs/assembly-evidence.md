# Assembly evidence contract

This is the revision-aware handoff for applicable multi-part assemblies, not
a new design discipline or a replacement for the five Design Complete
conditions in `docs/architecture.md` section 8. Existing Mechanical Lead and
Reviewer rules already require achievable assembly order and interference
checks. This contract makes their early evidence inspectable instead of
leaving animation until after approval or treating a scalar PCB check as
an integrated assembly review.

Rigid-body dynamics has a separate [simulation contract](simulation.md).
Its hashed model/trajectory/video evidence follows the same revision and
invalidation principles, but is not this assembly manifest and cannot
replace Fusion native storyboards or a published assembly-process video.
Numerical simulation acceptance grants no physical or assembly approval.

## Two states, one geometry owner

| State | Required behavior | What it does not authorize |
|---|---|---|
| **WIP - NOT ASSEMBLY READY** | Start assembly-process planning, geometry evidence and animation during interface/enclosure design. Identify missing inputs, label approximations, generate the evidence possible now, and obtain early blocker reviews. Refresh after source changes. | Missing interfaces are not resolved by labeling them WIP. No final readiness, fabrication, power-on, safety acceptance or release claim. |
| **APPROVED assembly documentation** | Complete the evidence package, obtain independent Mechanical Reviewer acceptance of this exact revision, and cite its Design Complete and named safety decisions. Release the instructions, native animation and playable published video together. | Documentation approval is not permission to fabricate, energize, flash firmware or operate rotating hardware. Each named physical-action gate remains separately required. |

Use WIP labels on documents, storyboard titles/callouts and exported views/
videos, not only in the manifest. Incomplete evidence must not prevent an
early review that can find a blocker. It must prevent calling that review
final readiness. An APPROVED package requires all required interfaces and
assembly evidence resolved/reviewed, with existing human risk dispositions
stated accurately; this contract grants no new risk acceptance.

Mechanical Lead alone owns mechanical assembly/enclosure geometry; PCB
Engineer retains board-layout ownership. A visualization pass may implement
the source-defined insertion sequence, but must not silently resize a part,
move its installed pose, change a mating relationship, or invent a new build
order to make a render work. Route a discovered defect back through Hardware
Lead to the appropriate source owner, then regenerate and independently
re-review the affected package.

## Responsibility and escalation

Hardware Lead owns **overall interface completion**, not merely collection
of each discipline's conditional report. Assign every sourceable gap a
named owner, investigation and next action: Circuit Engineer for electrical/
connector/power facts; PCB Engineer for populated board geometry, holes and
placements; Mechanical Lead for geometry, retention and assembly paths;
Manufacturing Engineer for process-dependent fits, supports and structural
assumptions. Mechanical Lead populates the interface file; Systems Engineer
retains technical boundary/trade-off ownership when genuine conflicts arise.
Mechanical Reviewer independently accepts or rejects the evidence.

PCB Engineer can supply bounded **WIP physical-interface preparation** before
Design Complete (`docs/workflow.md` Phase 4a): source-grounded package/
populated-board/mated-connector envelopes, provisional outline/mount/placement
geometry and explicit gaps. This breaks the circular dependency between
board geometry, mechanical evidence and the shared gate; it does not authorize
general routing, fabrication-ready release or physical action. The full PCB
layout/release path still requires the approved schematic, independent
Hardware Reviewer review and existing named gates.

`UNKNOWN` is a truthful state, not a terminal deliverable. Search the
authoritative project/manufacturer sources, or recommend a concrete
alternative with trade-offs. If a datasheet cannot be found, escalate without
guessing. Architecture, component, major BOM and safety changes still need
the human Chief Engineer's **named decision with meaningful options**. Do
not turn a sourceable fact into indefinite "waiting for Kyosuke approval,"
or interpret a request to finish the package as approval of a risk.

## Required artifact contents

Create `hardware/mechanical/assembly-evidence/<assembly>/<revision>/manifest.json`
from [`templates/assembly-manifest.json`](templates/assembly-manifest.json).
Register that revision in
`hardware/mechanical/assembly-evidence/<assembly>/current.json` using
[`templates/assembly-current.json`](templates/assembly-current.json):
`{"schema_version": 1, "assembly": "<assembly>", "revision": "<revision>"}`.
Update this pointer when moving to a new revision; preserve older manifests
unchanged. The pointer makes live dependency checks unambiguous without
retroactively applying today's source files to historical evidence.
Reports and generated files may live in that revision directory or existing
project artifact locations; the manifest links their exact paths and hashes.
The template is deliberately incomplete, not evidence for any historical
revision. Do not modify historical conclusions to satisfy it.

| Artifact key | Minimum content for an accepted package |
|---|---|
| `tool_preflight` | Dated, operation-specific runtime capability matrix; official references, version/connection observations, execution path, limitations and any precise handoff. See the visualization skill. |
| `component_map` | Required physical inventory derived from requirements/BOM/interfaces, not just what happens to be rendered. Stable source-part/instance ID -> named Fusion component/occurrence -> source file/hash, units, axes and installed transform. Account for every required sensor/board/driver/power interface. |
| `assembly_instructions` | Parts/fasteners/tools, actual numbered insertion/seating/fastening/connection order, retention and tool approach/access, removal/service sequence, stage IDs matching storyboards, source facts vs allocations vs UNKNOWNs, named safety stop points. |
| `installed_assembly` | Full installed-state evidence and measurements for the entire inventory, with the coverage below, source/version linkage, tolerances and explicit unresolved cases. Not a bare PCB rectangle or an attractive picture. |
| `assembly_stages` | Evidence at each insertion, seating, fastening, connection and removal stage. Identify moving and installed parts, fixtures/temporary retention, tool/harness access, path method, measurements, sampling and limits. Match the instruction/storyboard stage IDs. |
| `drawings` | Readable assembled and per-part orthographic views plus labeled overview/exploded views where useful, dimension/source cross-references and revision/WIP labels. List every delivered file, not only a directory or uninspected export log. |
| `native_animation` | Genuine Autodesk Fusion design/archive, with named physical components and saved assembly storyboards; supported `.f3d` or `.f3z` as appropriate. Reopen and inspect the saved artifact, including references and storyboard persistence. |
| `animation_video` | A genuinely playable video published from Fusion Animation, documenting scope/storyboards, duration, format, playback and provenance. Do not rename another renderer's output or substitute stills. |
| `independent_review` | Dated Mechanical Reviewer report identifying scope (early blocker review vs final acceptance), source revision and reviewed artifact hashes, coverage/limitations and verdict. Preserve the existing shared findings backlog and severity rules. |

For **both the full installed assembly and every relevant stage**, cover:

- Populated PCB/component envelopes on both sides, fully mated connectors,
  actual mounts/standoffs/fasteners and required insulation.
- All required sensors, sensor orientations/positions, daughterboards,
  drivers, power interfaces and other purchased modules; omissions stay
  visible even if source dimensions are still UNKNOWN.
- Motors including bells, shafts, hubs, wheels and rotating swept
  envelopes; supports, bearings and their real seated relationships.
- Screw heads, nuts, washers, inserts, retention and actual tool access.
- Retained harness routes, connector mating/unmating envelopes, strain
  relief/bend allowances and routes through/past panels and moving parts.
- Insertion/seating/removal paths, assembly fixtures, intermediate support,
  fastening direction and support-material removal where applicable.

Separate **source dimensions**, **engineering allocations**
(`ASSUMPTION`/`ESTIMATE`, with rationale) and **UNKNOWN** inputs. A simplified
envelope may conservatively bound a sourced part but must identify what it
omits; it cannot silently replace a missing mating or mounting design.
Distinguish intentional fused-print unions, bearing/contact surfaces and
qualified process interference from forbidden overlap between separate
parts. Record the contacting pair, purpose and qualification; do not exempt
all overlap by declaring "touching is expected."

Animation is **not collision analysis** and proves neither continuous-path
clearance nor support removal, strength, safety or functionality. A sampled
path check must state the sampled poses/spacing, tolerance, envelope/model
fidelity and untested intervals; do not call it continuous collision proof.
Explode/home interpolation is a presentation technique, not automatically
a physically feasible insertion path. Never move a final installed pose to
hide an unknown or an interference.

## Manifest schema (version 1)

Top-level fields:

- `schema_version: 1`, `assembly`, `revision`, `state: WIP | APPROVED`,
  `author` (role/session identity) and `source_revision` (full Git commit
  hash). The directory names must equal `assembly` and `revision`.
- `sources`: nonempty list of `{path, sha256}` references to the canonical
  geometry, PCB, BOM, interfaces and other inputs actually used. Commit the
  source snapshot first. Every source hash must match both that commit and
  the current checkout; a branch name or an old matching scalar is not a
  source revision.
- `retired_sources`: optional list of `{path, sha256, source_revision,
  reason}` for intentionally removed/replaced source or artifact files.
  The old commit must contain the matching file and the current path must
  be absent. Preserve historical manifests rather than deleting them.
- `animation`: `{"workflow": "FUSION", "alternative_approval": null}` by
  default. Fusion Animation is the standard for applicable multi-part
  assemblies here and is mandatory when explicitly requested.
- `artifacts`: exactly the nine keys above, each with `owner` and a status.
- `approval: null` for WIP; the approval object below for APPROVED.

Artifact status records:

```json
{
  "status": "PRESENT",
  "owner": "mechanical-lead:<session>",
  "source_revision": "<same full source commit>",
  "files": [{"path": "<repository-relative file>", "sha256": "<64 hex digits>"}]
}
```

`PRESENT` means the referenced files exist, **not** that their content is
complete or independently accepted. Partial reports identify their gaps and
keep the package WIP. `native_animation` and `animation_video` additionally
require `"producer": "Autodesk Fusion Animation"` under the Fusion workflow;
the reviewer must check that provenance, not trust the string or extension.

```json
{
  "status": "BLOCKED",
  "owner": "mechanical-lead:<session>",
  "reason": "<specific missing source or capability, with investigation result>",
  "next_action": "<smallest actionable owner task or human handoff>"
}
```

`PENDING` has the same fields as `BLOCKED`, for work not yet performed.
Neither may claim `files` as delivered. A capability-blocked Fusion export
does not waive Fusion, stop preparation of other evidence, or become a
PRESENT native file because a script has been prepared.

Only an explicit human-approved alternative may set
`animation.workflow: APPROVED_ALTERNATIVE`. Its `alternative_approval`
contains `name` (human), ISO `date`, `rationale`, `workflow` (actual tool) and
`record: {path, sha256, section}` locating the decision. Native/video
`producer` must then equal that workflow. Native and video deliverables
remain required; an alternative is not a blanket waiver of assembly evidence.

For APPROVED, all nine artifacts must be PRESENT. `approval` contains:

- `name` (independent reviewer identity, different from `author`, matching
  `independent_review.owner`), `role: mechanical-reviewer`, ISO `date`,
  `rationale`, `verdict: PASS`, the same `source_revision`.
- `evidence_sha256`: the fingerprint printed by the checker for the complete
  WIP package before final review. It covers assembly/revision/author, source
  revision/references, retirements, animation choice and all artifact records
  except `independent_review`, using sorted-key compact JSON and SHA-256.
  Excluding the review itself avoids a self-referential hash; regenerating
  any reviewed output invalidates acceptance even if source geometry is unchanged.
- `record: {path, sha256, section}` pointing to one of the exact files in
  `independent_review`, not an unrelated document.
- `design_complete: {path, sha256, section}` pointing to this revision's
  actual Design Complete decision, not an invented ECO.
- `safety_decisions: {path, sha256, section}` locating the named human
  architecture/component/BOM/safety decisions applicable to this release.
  That record also identifies physical-action gates still held, including
  PCB/mechanical fabrication, first power-on and first flashing. Instructions
  retain those stop points; release does not grant those later permissions.

The reviewer must check the underlying decisions and all five Design
Complete conditions, not merely file existence. Critical findings cannot
be accepted-risk; existing HIGH acceptance does not auto-extend to changed
configurations. Reserve shared ECO/ISS/MISS/Evidence IDs with the integrating
session before writing them (`docs/workflow.md` section 4.1).

## Automated boundary and invocation

The existing Python CI runner executes stdlib `unittest` coverage and
`tools/check_assembly_evidence.py` on every PR. No new test framework, CAD
integration or plugin is installed. PR discovery reuses
`check_open_issues.compute_pr_changed_files()` (merge-base, full history).
The checker then lists paths at those endpoints without rename collapsing
and with NUL delimiters, so a manifest rename cannot hide deletion of history.

In this integrated-assembly repository the changed-path selection is
deliberately conservative: `hardware/**`, `bom/**` and
`visualization/assembly-viewer/**` changes require updated revision manifests,
and each changed file must be linked as source, artifact or explicit
retirement. SCAD/KiCad design inputs (including `.kicad_mod`, `.kicad_sym`,
`fp-lib-table` and `sym-lib-table`), BOM files and the mechanical interface
must be linked as sources, not disguised as downstream outputs.

Each assembly's `current.json` selects its live manifest. A change to any
current source, artifact, independent report or approval/gate record triggers
validation even outside the physical prefixes (for example a referenced
`validation/` report or `requirements/` input). This prevents report-only edits
from leaving a stale APPROVED package behind an N/A result. All current
reference paths must be canonical repository-relative paths with **no symlink
in any component**, including parent directories. Path identity is checked
before dependency selection or N/A, not only after a manifest is selected:
an alias cannot hide changes to the real tracked target or to the alias
itself. Use the real tracked path and refresh the manifest/review rather than
following an alias. This path check does not retroactively inspect inactive
historical manifests or turn hash checks into geometry/safety acceptance.
Changing a current pointer or manifest also triggers validation. Do not delete pointers or
manifests, or edit a pre-existing inactive historical manifest; move the
pointer to the new revision instead. Multiple revisions may be created before
one PR merges: Git addition status against the merge base distinguishes those
newly preserved snapshots from edits to pre-existing history. Their own
revision-directory files must retain the referenced hashes; they cannot cover
unlinked changes to live design inputs or shared output locations. Only the
pointer-selected revision receives live readiness validation. The same
assembly must have a valid current pointer selecting that live revision;
omitting registration cannot turn a new package into exempt history.
Historical-only references do not activate live checks,
and old revisions are not retroactively required to have new artifacts.
A missing manifest, unlinked physical change, malformed status, stale
revision/hash or unsupported readiness claim fails loudly.

Unrelated docs, agents, skills and policy/checker-only PRs receive explicit
**NOT APPLICABLE**, while checker regression tests still run. This does not
modify the existing hardware gate's diff-aware exemption or severity checks,
does not change branch protection, and cannot make a hardware gate pass.
An unusable PR diff is an error, never an automatic exemption.

For a current revision, independently of PR context:

```sh
python3 tools/check_assembly_evidence.py --manifest hardware/mechanical/assembly-evidence/<assembly>/<revision>/manifest.json
python3 tools/check_assembly_evidence.py --manifest hardware/mechanical/assembly-evidence/<assembly>/<revision>/manifest.json --require-approved
PYTHONPATH=tools python3 -m unittest discover -s tools/tests -p 'test_assembly_evidence.py'
```

A structurally valid WIP record returns success **with NOT ASSEMBLY READY
and all PENDING/BLOCKED items displayed**; `--require-approved` rejects it.
This allows preparation and early fault-finding without granting final
readiness. Hashes/file extensions/producer strings do not establish geometry,
authenticity, video playability or safety: those require the independent
evidence review. No actual assembly, animation, approval or historical
safety evidence is delivered by the policy-only PR introducing this contract.
