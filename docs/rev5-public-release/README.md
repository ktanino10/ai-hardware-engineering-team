# Rev5 curated public release

[English/source](README.md) | [日本語読者向け版](../pages.ja.md)

**DERIVED_PUBLIC_EXPORT / WIP / NOT ASSEMBLY READY**

[日本語の公開入口](https://ktanino10.github.io/ai-hardware-engineering-team/index.ja.html) /
[whole-assembly v2](https://ktanino10.github.io/ai-hardware-engineering-team/rev5-full-assembly-v2/index.html).

この公開単位は **Rev5全体モデル v2の閲覧**を優先します。399個の名目メッシュ、
分解量、再生・停止、透過線画、三角形に基づくホバー、全IDのSVG参考三面図を含みます。
形状・配置は2026-09-15時点の固定値です。後日の形状変更や電子系を混在させず、
過去のベンチ例は別の履歴として案内します。全作業・全設計の公開完了を意味しません。

**Software follow-up:** the separately curated
[English guide](software.md) / [日本語](software.ja.md) now covers the C1
derived summary, synthetic IMU executable closure and N8R8 source-only
evaluation closure. The table and verification history below describe the
**original PR79 release** and remain preserved, not retroactively rewritten.
The follow-up has its own manifest, review summary and publication checks;
neither release changes engineering or physical approval.

## Included and deferred

| Candidate | This release | Boundary / next dependency |
| --- | --- | --- |
| Whole-assembly v2 | 12 self-contained runtime files; two portable test scripts; public navigation | Display/reference only. 399 meshes are not 399 purchased parts. |
| C1 readiness | Status only; executable/data not included | 10 exact catalogue candidates, 2 unknown-product requirements, 23 gaps and 103 source observations; zero adopted candidates. Quantities/application remain UNKNOWN. Its sealed input closure includes excluded private power-source history; needs a separately curated and reviewed public closure. |
| Synthetic IMU disagreement | Deferred; no CLI or claimed review acceptance in this release | Offline synthetic SI/body/exact-clock gyro reporting only. Requires independent review and the complete, cleared estimator/helper/fixture closure. No health classification, auto-exclusion or control. |
| N8R8 evaluation | Deferred; no profile/code/build artifacts in this release | NOT_FOR_FLASH; measurement subset only. Requires independent review, frozen measurement/pin dependencies and vendor notices. Not a full Rev5 replacement; reserved35/36/37 conflict remains. |
| Earlier Blender/FreeCAD presentations | Deferred | Different geometry epochs and native/media provenance need their own scoped export. No native binaries, source STLs or editor execution included. |

These are publication dispositions, not changed engineering verdicts. The
separately commissioned software reviews may produce frozen successors; they
are not silently imported into this release.

## Provenance and permission basis

The project owner explicitly requested public reflection and normal
main/Pages publication after required checks. The original candidate's
`UNKNOWN_NOT_CLEARED` rights note prompted a source trace, not a fabricated
license. The following first-party lineage was inspected at frozen objects:

| Surface | Inspected origin and derivation |
| --- | --- |
| Runtime code | V2 source `7a7924645042ae60386c14e38be4770bfcbfecac`. Plain project JavaScript/CSS/HTML; no runtime CDN, package, vendored renderer or telemetry. Inherited `interactive-viewer.js` originated in project commit `9e3f4076b0d158f347b9c75de79753fd96d091e5`, authored by the project owner with Copilot attribution. |
| Packed scene / inventory | V1 packer at `97a4e2157878bcbb4e717ddcb860549b08096d3f` serializes original STL triangle corners without changed poses/topology. Nominal upstream `a4a6382f0b80802cf3e22aa1f824d679784c6325`; 52 service-margin, 329 internal-layout correction-002 and 18 larger-cassette meshes. |
| Frame, cassette, supports and fasteners | Project Python/OpenSCAD generators, retained project surfaces and transformations. Panels/allocated hardware trace through current76 exports and rev5-pcb-wip wrappers to `bench-imu-01-enclosure.scad`; no downloaded supplier mesh. |
| Motors, wheels and equipment | `mount.scad::motor` constructs cylinders and holes; `build_check.py` constructs wheel/keep cylinders; internal-layout builder constructs nominal equipment boxes. These are original proxies, not vendor CAD or claims of exact manufactured shape. |
| PCB and component references | Project PCB contours and placements, `reference76.scad::rv76_body` rectangular envelopes, and source22 Yageo `bodies.scad` rectangular envelopes. Manufacturer dimensional facts were inputs, not copied drawings/PDFs/STEP assets. UNKNOWN marker geometry remains explicitly unqualified. |
| Edges and reference SVGs | V2 `build_edges.py` derives edges from the packed coordinate stream; `drawings.js` projects those edges on demand. No user-uploaded image is embedded. |

Publication is authorized for this original project work. **No new project
license or third-party redistribution permission is asserted.** Absence of a
repository license is not treated as a prohibition on the owner's publication,
nor as a downstream license for others. Dimensions and source qualifications
are unchanged; this is not supplier endorsement or manufactured-part acceptance.

## Integrity, redaction and reproduction

[manifest.json](manifest.json) records original and public file hashes.
The packed scene, edge data, inventory and runtime implementation are unchanged.
The entry navigation, empty inline favicon (avoiding a root favicon request)
and README are explicitly derived public edits. The
browser harness adds a live-URL mode, cross-platform browser argument and fresh
evidence directories; it still checks actual framebuffer pixels, controls and
all399 SVGs, rather than reporting an HTTP response as rendering success.

Only the allowlisted bytes were exported onto public `main` ancestry. The
release excludes private branch ancestry, raw source STLs, manufacturer
documents, raw uploads/screenshots, account/provider receipts, private
source/sink/brake history, `.agent-work`, host paths/profiles/endpoints, SDK
snapshots, flash binaries and native editor files. Original evidence remains
unchanged; this record is a derived public summary, not its replacement.

The runtime works from a clean public checkout. Node22+ feature tests and the
optional installed-Chrome browser harness use the included runtime, without
private Git objects. See the [viewer guide](../../visualization/rev5-full-assembly-v2/README.md).
The original geometry generators, packer and source-history test input closure
are deliberately not exported. **Historical native regeneration is unavailable
from this release alone.** Hashes are lineage records, not missing-source
fallbacks; no source IDs or verification hashes were spoofed.

## Verification and publication boundaries

Local feature tests: 3 passed, including every ID's reference projection and
corrupt-binding rejection. The isolated installed-Chrome file-mode run passed
19 browser checks, including actual GPU pixels, transformed hover/click/touch,
animation/reduced-motion/hidden lifecycle, four responsive widths and all399
SVGs. These are software observations, not independent mechanical acceptance
or confirmation of any embedded host application.

The initial HTTP-mode run exercised all19 checks but failed on the browser's
automatic missing `/favicon.ico` request. An explicit empty inline favicon
addresses that deployment-root defect; errors were not suppressed. The
corrected HTTP run passed all19 checks and compared all12 public-layout assets
against the local files. It is recorded separately from the original failure.

Required PR CI and the exact publication diff must pass before normal merge.
The initial required CI caught two unclassified new README paths: local tests
had preceded staging, while CI enumerated tracked files. The language inventory
and real Japanese reading coverage were corrected; tests and gates were not
changed. Final tracked-file CI, not that earlier local pass, controls merge.
Merge and Pages deployment are separate: the existing workflow publishes
`visualization/` as the site root. The live browser harness compares each
runtime file's public HTTP bytes with this checkout before testing controls.
The release handoff records the actual PR, merge and deployment result;
the existence of this document alone is not deployment evidence.

Rollback is a normal reviewed revert of this release's publication change,
followed by the same required checks and Pages deployment. No branch protection,
gate, workflow or engineering finding is changed. Until a revert deploys, do
not describe the site as rolled back.

**Unchanged holds:** NO-GO / 3C8H / REQ409 / strict-pro / 39UNKNOWN;
P1/C1/D1; sidecar/ICD/control; original44 = **2 closed / 42 unfinished**;
N8R8 **NOT_FOR_FLASH**. No fabrication, assembly, energization, first flash,
motor operation or safety permission is conveyed.
