# Blender — 計算状態の再描画

[English](../simulation/blender/README.md) | [日本語](blender-replay.ja.md) | [ガイド一覧](README.ja.md)

任意の追加経路として Blender 5.1.1 / Cycles CPU または Workbench で、
記録済み MuJoCo 姿勢を描画します。**Blender/Bullet の独立物理計算ではなく**、
実機 CAD、実機承認、Fusion 組立動画でもありません。成功して見せるために軌道を変更しません。

起動中 Blender の未保存 scene を reset・保存してはいけません。
まず独立した background process で native file を作成・再読込します。
利用者が表示を求めたときだけ名前付き replay scene を live application に append し、
既存 scene・object をすべて維持します。

## 実行

リポジトリ root から、実行時 preflight で確認した Blender binary を使います。
以下は原本の macOS パスです。他環境に同じパスがあるとは仮定しません。

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --threads 4 --python-exit-code 1 \
  --python simulation/blender/render_replay.py -- \
  --run simulation/evidence/startup-v4/startup-mechanism-fixture \
  --output simulation/runs/my-blender-replay --engine workbench --animation

/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup simulation/runs/my-blender-replay/replay.blend \
  --threads 4 --python-exit-code 1 --python simulation/blender/check_replay.py -- \
  --run simulation/evidence/startup-v4/startup-mechanism-fixture \
  --output simulation/runs/my-blender-replay/native-check.json

simulation/.venv/bin/python simulation/blender/encode_replay.py \
  --run simulation/evidence/startup-v4/startup-mechanism-fixture \
  --render simulation/runs/my-blender-replay
```

`replay.blend` または `blender-motion.mp4` を開きます。
`preview.png`、`provenance.json`、`native-check.json`、`manifest.json` が
元記録、script、native、frame 対応、output hash を結びます。
`frames/` は再生成可能な描画中間物なので PR に入れずローカルに保ちます。

schema 3 の provenance は表示 CSV だけでなく、source manifest に束ねられた
`model.xml`・`trajectory.npz` 等の全ファイルを検証します。
注記・設定に使った内容と hash 対象は同じ内容です。source と Blender 出力は別 directory にし、
出力が自分自身の source になる循環を作りません。

## native・動画の検査

encoding 前に全 frame hash、source binding、現行 native-check receipt を検証します。
body/rotor/marker の world transform、中心、parent、scale、mesh 軸、
表示 mesh の頂点・topology・winding を検査し、半径の最大最小だけで済ませません。
実効 frame rate は `render.fps / render.fps_base` で、整数 FPS だけの一致は不十分です。
marker delta、折れた half-annulus、fps_base 変更、rotor 移動は保存物の拒否例です。
古い receipt は履歴であり現行受け入れに使えません。

`negative_native.py` は独立した保存ファイル変更による regression を提供します。
出力は `simulation/runs/` とし、live scene に入れません。
新しい公開 clip は最低10秒の記録済み運動が必要です。
Workbench は軽い表示レンダラーで、異なる物理 engine ではありません。
以前の3秒 Cycles 比較は履歴です。小さい合成 annular fixture を Rev5 と誤認させないよう、
model identity、寸法、数学的質量を表示します。

Blender frame 1 は記録時刻0で、整数 frame は source video map の正確な姿勢を使います。
中間 keyframe 補間は物理証拠ではありません。
再読込は描画した body/wheel 姿勢を 1e-6 の位置・quaternion 成分余裕で比較します。
これは float32 表示精度用で実機適格性ではありません。
marker は alias し得るため速度は元 CSV を使います。
edge/cylinder は質量のない表示 proxy で、新しい機械 Source of Truth ではありません。

公式参照: [render](https://docs.blender.org/api/5.1/bpy.ops.render.html)、
[native libraries](https://docs.blender.org/api/5.1/bpy.types.BlendDataLibraries.html)、
[transforms](https://docs.blender.org/api/5.1/bpy.types.Object.html)。
既存 Blender 5 layered F-curve 方法を使います。
material/world の `use_nodes` は5.1では対応していますが6での削除警告があるため、移行前に再確認します。
これらは公開原本の実績・注意事項であり、翻訳中に Blender を実行した主張ではありません。
