# Rev5 v3 visual-only public release

[English/source](README.md) | [日本語読者向け版](../pages.ja.md)

**DERIVED_PUBLIC_EXPORT / WIP / REF / NOT ASSEMBLY READY**

[Open v3](https://ktanino10.github.io/ai-hardware-engineering-team/rev5-full-assembly-v3/index.html)
for the approved outside-first browser presentation and six actual Blender
movies. [Public v2](https://ktanino10.github.io/ai-hardware-engineering-team/rev5-full-assembly-v2/index.html)
and its original release receipts remain unchanged.

## Delivered scope

The self-contained v3 bundle retains all399 source meshes,794132 triangles,
five display stages,31 groups,25 named units, seven camera angles, exact
triangle picking and399 individual reference SVGs. Ten inherited core files,
including the scene, plan, renderer and drawings, are byte-identical to the
frozen v3 input. Only gallery integration, local-media metadata, public
documentation/navigation and portable tests are added or adapted.

One native player, six selectable posters and `preload="metadata"` avoid six
simultaneously autoplaying movies. The selected part links to an actual
containing XYZ-unit clip where one exists, otherwise a containing whole view.
The100 hidden reference volumes have no invented movie. Individual browser
views are not misrepresented as native per-part movies.

| Movies | Actual original timing and camera |
| --- | --- |
| Exterior / interior | Two6-second,72-frame,12-fps perspective52 mm,360-degree turntables with fixed framing |
| Outside first |145 frames at12 fps; source-clock0–12 s, observed12.083333 s; orthographic, fixed isometric direction with dynamic bounds |
| X / Y units |145 frames at12 fps; source-clock0–12 s, observed12.083333 s; orthographic dynamic bounds,180-degree camera turns |
| Z unit |145 frames at12 fps, observed **12.083008 s**; same unit convention; all frames decoded |

Z's stream/container end is148476 ticks at1/12288 s while exact packet end
is148480 ticks (145/12 s). The four-tick discrepancy is preserved, not hidden
or re-encoded away. The producer also retained two one-binary64-ULP Z
camera-radius readback differences. Neither changes source geometry,
physical tolerances or engineering acceptance.

All six MP4s and six native-derived PNG posters are copied byte-for-byte.
The producer was Blender5.1.1 / Cycles CPU4. Captions and illustrative
materials remain WIP/reference only. The runtime contains no native scene,
render worker, source STL, raw frame, process argv/log, external font or
supplier binary. No native render, transcoding or physical operation was
performed by this publication.

## Frozen intake and first-party provenance

[intake.json](intake.json) records the sanitized owner commission and public
base `ca07ba11bf3347ff467671606c00a6e2b5a70c02`.
[intake-audit.json](intake-audit.json) binds exact source Git blobs, all
MP4/poster hashes, producer DONE records and publication eligibility.
The viewer came from `c5349740bb240ed600df8e4b056921067a102c1d`; combined
media from `382345807899333ecfc47a2a7e4948d937ff3993`, retaining base
`66266f553d49cc54bfe2462f7045a5258ec70c78`.

The packed scene, edges, inventory, triangle-picking implementation and SVG
implementation were byte-compared with the already cleared
[v2 first-party provenance](../rev5-public-release/README.md).
New project-authored presentation code was traced separately. The Blender
recipe builds the same packed triangles and procedural Principled BSDF
colors, lights and a non-product studio floor; it imports no supplier mesh,
image texture or HDRI. Sequenced rendering reuses those materials and the
unchanged shared plan, hiding only the non-product floor. Materials are
illustrative appearance, not validated manufacturing properties.

The owner's explicit public-publication request covers this original
project work. **No new project license or third-party redistribution
permission is invented.** References to immutable private producer commits
are provenance metadata, not private ancestry included in the public branch.
The original recipes and full receipts are not exported, so native
regeneration is deliberately unavailable from this release alone.

## Integration evidence and publication boundary

[manifest.json](manifest.json) positively enumerates every runtime/test and
navigation/documentation delta, its bytes/hash and source disposition.
[verification.json](verification.json) records this integration's actual
software/browser observations. Media metadata is separately published as
[DERIVED_PUBLIC_MEDIA_METADATA](../../visualization/rev5-full-assembly-v3/media-manifest.json),
not an altered producer receipt.

The portable browser regression retains isolated file loading, source-bound
GPU/picking/choreography checks and all399 SVGs. HTTP mode compares every
runtime asset's bytes before exercising the same controls and all six actual
movie players/posters. Python checks additionally decode all724 frames and
retain the exact observed timing. See the [operation and test guide](../../visualization/rev5-full-assembly-v3/README.md).
These are author software checks, not a new independent engineering review
or embedded-host confirmation.

New reader paths are classified in the existing EN/JA inventory before
tracked-file checks. Existing required CI and the positive Git-object
publication audit must pass before a normal merge. No workflow, gate,
finding, branch protection or administrator bypass is changed.
The existing Pages workflow uploads **`visualization/` as the site root**.
Commit, PR, merge, deployment and verified live acceptance are distinct;
the terminal publication handoff records their actual SHAs and URLs rather
than claiming deployment from this document's existence.

## Exclusions and unchanged holds

The release excludes all firmware/Bosch/C1/IMU/N8R8 source changes associated
with the separate PR80 lane. Its unresolved alerts are not bypassed or
concealed by this visual release. No private branch ancestry, raw upload,
account receipt, private path, SDK, `.agent-work` file, native editor file,
original source STL or raw frame is published.

**WIP / REF / NOT ASSEMBLY READY / NO-GO / 3C8H / REQ409 / strict-pro /
39UNKNOWN; P1/C1/D1; sidecar/ICD/control; original44 = 2 closed /
42 unfinished; N8R8 NOT_FOR_FLASH** all remain. Source, human and physical
gates are unchanged. This is not Fusion assembly evidence, Design Complete,
fabrication/assembly acceptance, power-on, flash, purchase or control
permission. Rollback uses a normal reviewed revert, required checks and
the existing Pages deployment; v2 remains available independently.
