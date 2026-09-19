# Rev5 v3 — outside-first presentation

[English/source](README.md) | [日本語読者向け版](https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/docs/pages.ja.md)

**WIP / PRESENTATION ONLY / NOT ASSEMBLY READY / REF**

Open `index.html` with the complete29-file runtime bundle, including `media/`.
No server, network,
installation, sibling directory or browser security change is required.
The gallery contains **six actual Blender MP4s and six PNG posters**, copied
without changing their bytes. Browser rendering and recorded Blender CG are
distinct; neither is Fusion assembly output, a physical disassembly procedure
or a fabrication approval.

## 操作

初期表示は外装あり・停止状態です。進行スライダー、5段階のボタン、
「外側から段階再生」で次の表示を確認できます。戻り再生は同じ表示を逆に
たどります。「停止・組立0%へ」は元の配置へ正確に戻します。

| 進行 | 表示用の段階 |
| --- | --- |
| 0–15% | 外装締結の名目外形（24個のALLOC_panel_screw。調達済み実部品の意味ではない） |
| 15–35% | 外装パネルと同伴するインサート外形 |
| 35–50% | 一体のフレーム形状と同伴する接合外形 |
| 50–75% | 内部の名前付きユニット。小物を個別に散らさず同伴させる |
| 75–100% | 選択したユニット内の、別メッシュとして存在する構成形状のみ |

関連付けは保存ID／種別に基づく**表示用推定**です。実際の締結関係、
取り外し順序、干渉、重力、工具アクセス、保持や安全は検証していません。
100個の予約・ゲージ・経路参照は静止し、実部品として分解しません。
モーター／ホイールも元の名目REFERENCE表現を維持します。
外装ねじの描写はまず表示用に22 mm移動し、次の段階ではパネルの移動に
同伴します。先に遠くへ散らさず相対位置を保つ見せ方であり、22 mmは
必要な抜去量・クリアランスなどの設計値ではありません。

「ユニットを中心に見る」で25の名前付き表示グループを選び、
「ユニット表示・自動フィット」を押します。XYZは各22メッシュです。
最終段階の対象もこの選択に連動します。「単体表示・自動フィット」は
選択IDだけを元の姿勢で大きく表示します。一体形状や基板の積層／実装を
架空の部品に分解せず、単体では分解再生を無効にします。

7視点、ドラッグ／矢印、ホイール／＋−、Home／視点リセットに対応。
「ターンテーブル」は選択対象の中心の周りを**カメラが旋回**するもので、
部品／モーターの実動作ではありません。非表示・動きを減らす設定で
連続動作は停止し、自動再開しません。

ホバーは現在の可視三角形を正確にピックし、名前、不変ID、元のXYZ外接寸法、
参照状態を表示します。クリック／タップで選択固定。ID検索と選択欄も
キーボードで利用できます。透過時も最前面の三角形を選ぶため、奥の形状は
グループ切替・単体表示で確認してください。寸法ラベルは画面上で分離し、
寸法値そのものは変更していません。

全399 IDの参考三面図・SVG保存を維持。元のグローバル軸の外接寸法で、
解析的穴径・材質・公差・製造工程・印刷縮尺を補っていません。
隠線除去／ネイティブCAD図面ではありません。

## Six recorded native clips

Select a poster, then use the single native player's controls. Playback never
starts automatically, switching clips pauses the previous clip, and hiding
the page pauses playback without an automatic restart. Posters and metadata
are loaded from this bundle; no CDN, package or cross-origin request is needed.

| Clip | Original timing | Camera / displayed scope |
| --- | --- | --- |
| Whole exterior | 6 s / 72 frames / 12 fps | Perspective52 mm, fixed framing,360-degree camera orbit;299 visible meshes |
| Whole interior | 6 s / 72 frames / 12 fps | Same original perspective camera;293 visible meshes, six panels hidden |
| Outside first | 12.083333 s / 145 frames / 12 fps | Orthographic, fixed isometric direction, dynamic bounds; shared stages and X-unit detail |
| Unit X / Y | 12.083333 s each / 145 frames / 12 fps | Orthographic dynamic bounds,180-degree camera turn;22 source members per axis |
| Unit Z | **12.083008 s observed** / 145 frames / 12 fps | Same unit convention; original stream/container metadata retained |

The four sequenced clips sample source-clock **0–12 s** inclusive; encoded
playback also includes the final frame's display time. Z's stream end is
148476 ticks at1/12288 s, four ticks shorter than packet end148480
(exact145/12 s). All145 frames decoded; no re-encoding or rounding was used
to manufacture equality. Two original Z camera-radius readbacks also differed
by one binary64 ULP; this is retained as an observation, not a changed
engineering tolerance.

`media-manifest.json` is portable **DERIVED_PUBLIC_MEDIA_METADATA**, not a copy
of private process receipts. `media-data.js` carries its exact text and hash
for file-URL loading. Each clip is Blender5.1.1 / Cycles CPU4,
H264/yuv420p960×640 with original WIP captions. PNG posters are native stills
with caption borders; material colors/finish are illustrative, not physical
specifications. No Blender/native operation runs in this publication.

「関連CG」は選択形状を実際に含む動画への案内です。XYZの各22メッシュは
対応するユニット動画へ、他の可視形状は全体内部／外装動画へ案内します。
専用ユニット動画がない場合は明示し、非表示の予約・ゲージ100件には動画を
捏造しません。399個それぞれにネイティブ動画があるという意味ではありません。
個別のブラウザー表示とSVG参考図は全399 IDで利用できます。

## One authoritative plan for browser and sequenced CG

`presentation-plan.json` is the single choreography contract. It records:

- Scene/payload SHA-256, immutable source revision,399 IDs/794132 triangles,
  millimetres and right-handed cube-centred global XYZ.
-31 explicit display groups and25 units, exact source member IDs/hashes,
  each group's presentation association, offset and stage.
-5 contiguous stage ranges, smoothstep easing, constant holds outside a
  stage, additive global translations, selected-unit member offsets,
  exact zero, stationary references and single-part semantics.
-12-second one-way timeline; reversible24-second cycle; camera-only
  turntable rate; pause/stop/reduced-motion/hidden behavior.
- Orthographic camera directions, screen-right/up conventions including
  exact poles, dynamic visible-bound framing, near/far planes and explicit
  standard exterior/interior/drive visibility memberships.
-6 named native clip slots. Their original producer-time pending status is
  preserved in this immutable plan; `media-manifest.json` supplies completed
  media availability without changing choreography or geometry.

`plan-data.js` carries **the exact JSON text and its SHA-256** for file-URL
loading without fetch. Runtime integrity/source/membership validation runs
before drawing. Do not edit the wrapper or maintain separate offsets in
native scripts: consume the committed JSON and verify its hash.

For a member of the selected detail unit, displacement is the sum of its
whole-group translation, an optional one-level `carry_with` group
translation, and its detail-group translation. Each term uses
`t=clamp((amount-start)/(end-start),0,1)` and `t*t*(3-2*t)`. Other units use
only their whole-group term. Native consumers must retain the same source
poses, selections and view mode; an individual-part view has zero offset.
No rotation, scaling, remeshing or reapplication of installed transforms.

The immutable scene file remains
`8f55ba45dcd688c0253ec7c81628ce0ccedf7cedd79e7752191f2d8978eeedd0`.
Snapshot:2026-09-15 nominal, source
`a4a6382f0b80802cf3e22aa1f824d679784c6325`.
Public v2, inventory, original edge projections and historical evidence are
unchanged. `runtime-assets.json` records the byte-exact inherited assets.

## Reproduction and acceptance boundary

From repository root, with installed Python3.9+, Node22+, Chrome/Chromium
and optional existing ffprobe/ffmpeg for full media decode:

```sh
python3 visualization/rev5-full-assembly-v3/release_test.py
node --test visualization/rev5-full-assembly-v3/features_test.mjs visualization/rev5-full-assembly-v3/media_test.mjs
node visualization/rev5-full-assembly-v3/browser_test.mjs --entry PATH/TO/ISOLATED/BUNDLE/index.html --evidence-dir .agent-work/NEW-EVIDENCE-DIRECTORY
```

Use `--browser /path/to/existing/chrome` if Chrome is not at the standard
macOS location. Add `--url https://HOST/BASE/rev5-full-assembly-v3/index.html`
for HTTP/Pages-root mode: all29 runtime files are compared by HTTP hash
before actual controls, GPU pixels,399 SVGs and six native video controls
are exercised. Each evidence directory must be new. Browser profiles are
temporary and never use the user's existing profile.

These portable tests require no private history. Original source-generation,
native render recipes and private receipts are deliberately not included;
this public bundle cannot regenerate native scenes or historical geometry.
The installed headless browser is not an embedded-host app confirmation:
**HOST_APP_CONFIRMATION_PENDING** remains separate.

New integration evidence and the positive export manifest live in
[the visual release record](https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/docs/rev5-v3-media-release/README.md).
Original producer receipts are not rewritten or presented as fresh tests.

All WIP/NO-GO/3C8H/REQ409/strict-pro/39UNKNOWN, P1/C1/D1,
sidecar/ICD/control, original44=2closed42unfinished and N8R8 NOT_FOR_FLASH
holds remain. This is the separate visual-only, public-main-based lane.
Inherited first-party geometry was compared with the prior public provenance;
new project presentation code/materials and original render outputs were
traced separately. No new license or third-party permission is asserted.
Firmware/Bosch/C1/IMU/N8R8 work, private ancestry, raw uploads, native editor
files and scratch/process logs are not part of this release.
