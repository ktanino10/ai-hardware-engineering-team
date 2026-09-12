# 機械成果物の再生成手順

[English: STL](../hardware/mechanical/stl/README.md) /
[English: drawings](../hardware/mechanical/drawings/README.md) |
[日本語](mechanical-artifacts.ja.md) | [入口](hardware.ja.md)

公開された STL・図面 README の**操作手順を保持した日本語読者向け版**です。
寸法表、個々の判断、古い review 数値は版付き原本に残し、現在の承認として再発行しません。
以下は source の読み取りから派生物を生成する方法で、造形・実機操作の許可ではありません。
実行可能なツールを毎回確認し、指定された source と担当範囲、manifest の更新・独立レビューを守ります。
保存済み証拠の再生成は新しい版で行い、探索目的で元成果物を上書きしません。

## STL

5つの固有 piece に別 STL があり、pinch guard は同一 quadrant を4個使います。
base、flange、pointer、2つの cable anchor は1つの combined print job です。
wrapper は元 `.scad` を include し、`show_mode` を既存 assembled/print_layout のどちらでもない
`export` にすることで元の自動出力を止め、指定 module だけを出します。
source 寸法・module body は変更しません。

原本の再生成コマンド（root から移動）:

```sh
cd hardware/mechanical/stl/export
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-base-assembly.stl        export-base-assembly.scad
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-pcb-lid.stl               export-pcb-lid.scad
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-containment-cap.stl       export-containment-cap.scad
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-stand-plate.stl           export-stand-plate.scad
openscad -D 'show_mode="export"' --backend=manifold --export-format binstl -o ../bench-imu-01-pinch-guard-quadrant.stl  export-pinch-guard-quadrant.scad
```

binary STL を使います。原本の `NoError` / manifold 記録は当時の export の結果で、
今回の print・fit-check ではありません。base 内部支持材、cap の未実証 containment、
guard の bed 適合などは原本の版付き注意を確認します。
`trimesh` と OpenSCAD の manifold 評価が異なった過去事例も、
同じ理由があらゆる新形状へ適用されるとは仮定しません。

## 図面の状態と座標

`drawings/scad/` は搭載座標の wrapper、`stl/export/` は造形配置の wrapper です。
同じ piece でも座標・向きが違うことを隠しません。
図面原本では PCB resize 後に Method 1/4 を更新、
Method 2/3/5/6 は古い PCB bay と guard を描くと開示しています。
古い Blender 接続失敗はこの実行の能力判定ではありませんが、
古い動画を現行 geometry の証拠と呼ぶこともできません。

### Method 1: 正投影2D図

root から実行します。5 piece の top/front/side と assembled unit の4方向を出力します。

```sh
cd hardware/mechanical/drawings/scad
for name_script in "base-assembly:assembled-base-assembly" \
                   "pcb-lid:assembled-pcb-lid" \
                   "containment-cap:assembled-containment-cap" \
                   "stand-plate:assembled-stand-plate" \
                   "pinch-guard:assembled-pinch-guard"; do
  name="${name_script%%:*}"; script="${name_script##*:}"
  openscad -D 'show_mode="export"' --backend=manifold --projection=ortho --render \
    --autocenter --viewall --imgsize=1400,1050 --camera=0,0,0,0,0,0,300 \
    -o ../2d/${name}-top.png   ${script}.scad
  openscad -D 'show_mode="export"' --backend=manifold --projection=ortho --render \
    --autocenter --viewall --imgsize=1400,1050 --camera=0,0,0,90,0,0,300 \
    -o ../2d/${name}-front.png ${script}.scad
  openscad -D 'show_mode="export"' --backend=manifold --projection=ortho --render \
    --autocenter --viewall --imgsize=1400,1050 --camera=0,0,0,90,0,90,300 \
    -o ../2d/${name}-side.png  ${script}.scad
done

cd ../../
openscad --backend=manifold --projection=ortho --render --autocenter --viewall \
  --imgsize=1600,1200 --camera=0,0,0,0,0,0,400   -o drawings/2d/assembled-unit-top.png   bench-imu-01-enclosure.scad
openscad --backend=manifold --projection=ortho --render --autocenter --viewall \
  --imgsize=1600,1200 --camera=0,0,0,90,0,0,400  -o drawings/2d/assembled-unit-front.png bench-imu-01-enclosure.scad
openscad --backend=manifold --projection=ortho --render --autocenter --viewall \
  --imgsize=1600,1200 --camera=0,0,0,90,0,90,400 -o drawings/2d/assembled-unit-side.png  bench-imu-01-enclosure.scad
openscad --backend=manifold --projection=ortho --render --autocenter --viewall \
  --imgsize=1600,1200 --camera=0,0,0,55,0,25,400 -o drawings/2d/assembled-unit-iso.png   bench-imu-01-enclosure.scad
```

### Method 2: 過去の分解図 pipeline

`exploded/build_exploded_view.py` の header に従って搭載座標の8 STL を export します。
中間 STL は重複 binary としてコミットしません。
script 冒頭の `STL_DIR` / `OUTPUT_PATH` を設定して Blender 内で実行します。
実在する Scripting、background CLI、確認済み MCP のいずれかを使い、
他の未保存 scene を破壊しない独立環境で行います。
次に通常の Python で `exploded/build_exploded_view_annotations.py` を実行し、
8行の凡例と3つの締結具注記を加えた最終 PNG を生成します。

### Method 3: 過去の組立 animation pipeline

先に Method 2 の scene を生成し、`animation/build_assembly_animation.py` で keyframe と PNG frame を作ります。
原本の段階は lid、cap、stand plate + guard、bearing で、base は動きません。
180 frame / 24 fps の7.5秒は**過去の Blender 表示**で、現在要求される Fusion package ではありません。
script の header と出力 directory を確認したうえで、次の encoding を使います。

```sh
ffmpeg -y -framerate 24 -i "frames/f_%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart \
  bench-imu-01-assembly-animation.mp4

ffmpeg -y -framerate 24 -i "frames/f_%04d.png" \
  -vf "fps=12,scale=640:-1:flags=lanczos,palettegen=stats_mode=diff" \
  /tmp/anim-palette.png
ffmpeg -y -framerate 24 -i "frames/f_%04d.png" -i /tmp/anim-palette.png \
  -filter_complex "fps=12,scale=640:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \
  -loop 0 bench-imu-01-assembly-animation.gif
```

上記は原本の再現 command です。共有環境では出力と palette 用 scratch を
自分の作業範囲に確保してから使い、既存他作業のファイルを上書きしません。
PNG sequence は再生成可能な中間物で、最終 MP4/GIF と区別します。

### Method 4: drafting sheet

`Fusion-style` は見た目の表現で、Fusion native 保存・Animation の証明ではありません。
原本は OpenSCAD の DXF 投影と matplotlib で stand plate、cap、lid の sheet を作ります。
`<part>` は対象名へ置換し、`hardware/mechanical/drawings/` から実行します。

```sh
cd drafting-sheets/scad
openscad -D 'show_mode="export"' --export-format dxf \
  -o /tmp/<part>.dxf projection-<part>.scad
cd ..
python3 build_drafting_sheet.py --part <part> --dxf /tmp/<part>.dxf \
  --out bench-imu-01-<part>-drafting-sheet.png \
  --out-pdf bench-imu-01-<part>-drafting-sheet.pdf
```

scratch の衝突を避ける扱いは Method 3 と同じです。

### Methods 5/6: 履歴としての physics / concept demo

Method 5 は既存 ESTIMATE の運動量比を使った規定回転の表示で、
実測でも現在の自由接触3軸計算でもありません。高速 wheel の表示速度を意図的に変更した箇所を
on-screen に明示する原本の境界を保持します。
`build_physics_demo_animation.py`（Blender）→
`annotate_physics_demo_frames.py`（Pillow）→ Method 3 と同じ MP4/palette GIF pipeline です。
Method 6 は idealized CONCEPT で、
`build_concept_attitude_hold_animation.py` → `annotate_concept_demo_frames.py` → ffmpeg の順です。
実 controller・姿勢維持の実証とは呼びません。

これらを再生成しても、[組立証拠契約](assembly-evidence.ja.md)の Fusion native/video や
[現在の simulator](../simulation/README.md)の計算軌道にはなりません。
元の寸法理由、製造条件、組立手順、Evidence ID、ECO は共有の工学記録から確認してください。
