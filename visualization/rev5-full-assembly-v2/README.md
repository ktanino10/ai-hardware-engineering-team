# Rev5 v2 — public interactive reference

[English/source](README.md) | [日本語読者向け版](https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/docs/pages.ja.md)

**WIP / NOT ASSEMBLY READY · REF / NOT FOR FABRICATION**

Open `index.html` in a current WebGL browser. Keep the entire runtime bundle
together: no server, installation, sibling directory, CDN or network is
required. Do not change browser security settings. A missing dependency is
reported by filename and leaves controls disabled.

## 操作

| 機能 | 操作と境界 |
| --- | --- |
| 全体・内部 | 「外装を表示」「内部を見る」「3軸駆動だけ」、グループ切替。ゲージ・予約領域は初期非表示。 |
| 視点 | ドラッグ／矢印キー、ホイール／＋−、4視点プリセット。「視点リセット」または Home。 |
| 分解量 | 0〜100%。「停止・組立0%へ」で移動量を正確にゼロへ戻す。分解中は240 mmの全体寸法線を表示しない。 |
| 動画 | 「分解↔組立を再生」「一時停止」「停止・組立0%へ」と独立した「カメラ自動旋回」。初期停止。非表示になると停止し、自動再開しない。動きを減らす設定では連続再生を無効化。 |
| 透過 | 「透過・エッジ表示」で半透明の面と稜線へ切替。隠線除去ではなく奥線も表示する。 |
| 部品識別 | 実際の可視三角形にホバーすると名前・不変ID・XYZ外接寸法・参照状態を表示。クリック／タップで選択固定。ID検索と選択欄はキーボードでも操作可能。 |
| 参考三面図 | 選択した全399 IDに正面・側面・上面を表示。「参考三面図へ」で移動し、「SVG参考図を保存」で単独表示できるSVGを保存。 |

透過中のホバーも最前面の三角形を選びます。奥の形状はグループ非表示、
検索または単独表示で選んでください。参照図は狭い画面では図の領域内で
横スクロールできます。

## Frozen source and presentation

- Nominal snapshot: **2026-09-15**, upstream commit
  `a4a6382f0b80802cf3e22aa1f824d679784c6325`.
- **399 meshes / 794,132 triangles**, already-installed global XYZ, millimetres.
  Source vertices, topology and installed poses are unchanged.
- Original `scene-data.js` SHA-256:
  `8f55ba45dcd688c0253ec7c81628ce0ccedf7cedd79e7752191f2d8978eeedd0`.
- `inventory.json` contains each original ID, mesh path, hash, dimensions and
  representation status. `runtime-assets.json` pins copied inputs.
- Explosion offsets are **PRESENTATION ONLY**: frames move along Z; other
  shapes move radially from their nominal centres. These are not source
  placements, assembly sequences, clearances or feasible physical motions.
- GPU triangle/depth picking uses the same visible geometry and presentation
  transforms as drawing; no AABB-only selection. GPU rasterization uses
  float32; the preserved source coordinate stream remains float64.
- Reference views use original installed axes: front X/Z from −Y, side Y/Z
  from +X, top X/Y from +Z. Source triangle boundary/crease edges and
  view-dependent mesh silhouette edges are projected without hidden-line
  removal. Smooth outlines are mesh approximations, not analytic curves.
- XYZ values are global-axis mesh envelopes, not measured manufacturing
  dimensions. No tolerances, material, process, analytic hole diameters,
  print-scale guarantee or fabrication approval are supplied.
- Every ID is supported, including reservations, gauges and nominal drive
  envelopes; this is not a399-item purchased-parts BOM.

No later clamp/battery/electronics epoch is mixed into this snapshot. All
NO-GO / 3C8H / REQ409 / strict-pro / 39UNKNOWN, P1/C1/D1, sidecar/ICD/control,
original44 = 2 closed / 42 unfinished, and N8R8 NOT_FOR_FLASH holds remain.
Browser motion is neither simulation nor motor actuation. No native CAD
operation, independent review or physical qualification was performed.

## Public runtime and checks

The 12-file runtime is self-contained. The two optional test scripts need
Node22+; the browser test also needs an existing Chrome/Chromium installation.
They do not need source STLs, CAD tools or historical Git objects.

```sh
node --test visualization/rev5-full-assembly-v2/features_test.mjs
node visualization/rev5-full-assembly-v2/browser_test.mjs \
  --evidence-dir .agent-work/rev5-browser-local
```

For non-macOS Chrome, pass `--browser /path/to/existing/chrome`. For a live
deployment, additionally pass `--url` with its full `index.html` URL. The
harness verifies downloaded runtime hashes against the local release,
then exercises rendering, controls, hover, all399 SVGs and SVG download in
a newly owned browser profile. It does not inspect another application.
Use a new evidence directory per run. Browser success is not embedded host
acceptance or physical qualification.

The original packer, source-history tests and native geometry generation
chain are **not included**: their pinned historical Git objects and source
mesh closure are not part of this public export. Historical reproduction
from those objects is unavailable in a clean public clone. Never fetch
private ancestry or substitute hashes to make those tests appear to pass.

## Publication provenance

This is an owner-authorized export of first-party project code and generated
nominal/reference geometry, not redistribution of supplier CAD or datasheet
files. The inherited WebGL helper, procedural mesh sources, and derived
edges/SVGs were traced before publication. No project license was introduced;
this publication does not invent a downstream reuse license or supplier
endorsement. Source dimensions retain their existing qualification limits.

The public README and navigation are derived publication edits; the packed
scene, edges, original inventory and runtime implementation remain unchanged.
Repository provenance, hashes, exclusions and software status:
[release record](https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/docs/rev5-public-release/README.md).
