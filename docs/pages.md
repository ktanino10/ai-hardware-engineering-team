# Using the public visualizations

[English](pages.md) | [日本語](pages.ja.md) | [Guide index](README.md)

Open the [English landing page](https://ktanino10.github.io/ai-hardware-engineering-team/)
or its [Japanese edition](https://ktanino10.github.io/ai-hardware-engineering-team/index.ja.html).
Both route to the same viewers and the same engineering data.

## Run locally

From the repository root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory visualization
```

Open `http://127.0.0.1:8765/` or `http://127.0.0.1:8765/index.ja.html`.
Stop with Ctrl+C. There is no build step. HTTP is preferable to `file://`
for the assembly viewer's ES modules and model loading. Three.js is loaded
from its existing CDN; the dashboard needs access to public GitHub data.
This is not an offline guarantee for those historical viewers.

## Current Rev5 WIP reference

[Open whole-assembly v2](https://ktanino10.github.io/ai-hardware-engineering-team/rev5-full-assembly-v2/index.html).
The Japanese UI shows 399 nominal meshes from the frozen 2026-09-15 snapshot:
explosion, play/pause/reset, translucent edges, triangle-based hover and
reference three-view SVGs for every ID. Its self-contained runtime works
offline, including `file://`, without the historical viewer's CDN dependencies.
See its [operation guide](../visualization/rev5-full-assembly-v2/README.md)
and the [curated release scope](rev5-public-release/README.md).

**WIP / NOT ASSEMBLY READY; REF / NOT FOR FABRICATION.** These are installed-axis
mesh envelopes and presentation motions, not toleranced drawings, assembly-path
proof, physical simulation, or a complete purchased-parts BOM. Later geometry
and electronics epochs are not mixed in. The bench examples below remain
historical; neither they nor the dashboard certify current Rev5 readiness.

The [software follow-up](rev5-public-release/software.md) publishes an offline
synthetic IMU CLI and a source-only N8R8 evaluation closure, plus a C1
summary rather than its private production inputs. The landing page links
to their GitHub guides; these command-line tools do not run in the viewer.
The original v2 data, geometry epoch and physical holds remain unchanged.

## Circuit viewer

The English UI has three modes: power distribution, implemented open-loop
bench behavior, and explicitly **NOT IMPLEMENTED** closed-loop attitude
control. Click a box or wire for its role, net name and available source.
The pulse animation is explanatory, not a current measurement.
The schematic PDF is the literal drawing; block-diagram routes and
multi-node nets are simplified for readability.

Read the [maintainer guide](../visualization/circuit-viewer/README.md)
for derivation and exact PDF regeneration commands
([Japanese edition](circuit-viewer.ja.md)). Checked-in data is not live
schematic parsing; source changes require deliberate regeneration.

## Assembly viewer

Drag to orbit, scroll to zoom, use **Explode View / Assemble View**, and
click a part to open the sidebar/modal with source links, available 2D
drawings and an orbitable part view. Missing drawings or vendor data are
shown as explicit N/A rather than invented.

The English UI uses source-derived OBJ meshes and simplified purchased
parts. Its assembled view is a contact-stack presentation, not an exact
global-frame reconstruction; lids/caps are not fully nested, screw
positions are approximate and explode interpolation is not insertion-path
proof. It is neither physical assembly acceptance nor genuine Fusion
Animation. See the [maintainer guide](../visualization/assembly-viewer/README.md)
and [Japanese reading edition](assembly-viewer.ja.md).

## Dashboard

Open [English](https://ktanino10.github.io/ai-hardware-engineering-team/dashboard/index.html?lang=en)
or [Japanese](https://ktanino10.github.io/ai-hardware-engineering-team/dashboard/index.html?lang=ja).
`?lang=en|ja` selects the initial UI language; without a valid parameter,
the saved `dashboardLang` preference applies, then English. Use the
EN/JA buttons to change UI language, and Refresh to fetch records again.
Changing language alone does **not** fetch again. Back follows the displayed
language. Storage being unavailable does not prevent an explicit language link.

Titles, buttons, explanatory templates and fallback messages are bilingual.
Fetched source prose, component decisions, findings, ECOs, phase names,
agent descriptions, workflow names, IDs, paths, severity/status/priority
terms and configured GitHub feature names remain verbatim. This avoids a
second translated source of truth.

The dashboard reads public `main`, including during a feature-branch
preview. It does not show unmerged local design changes. CDN caching and
best-effort Markdown parsing can delay or limit sections; errors link back
to source. Dated static security/Pages settings are historical observations,
not fresh authenticated checks. No single project-wide revision is inferred
from different documents' revision numbers. The gate display is partial,
read-only and cannot authorize fabrication, power-on or flashing.

Details: [English dashboard guide](../visualization/dashboard/README.md) /
[日本語](dashboard.ja.md).

## Publication and scope

The existing Pages workflow uploads **only `visualization/`** on the
configured main-branch trigger. Repository documentation therefore uses
absolute GitHub links from Pages, not broken `../../docs/` URLs.
Opening a draft PR does not deploy these changes. The publication state
must be checked separately.

Language work does not change viewer datasets, models, trajectories,
manufacturing files, live-fetch configuration, review records or approval
gates. See [coverage](language-coverage.md) for the full reader-surface map.
