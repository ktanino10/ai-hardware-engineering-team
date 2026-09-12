# ハードウェア成果物の読み方と再生成

[English](hardware.md) | [日本語](hardware.ja.md) | [ガイド一覧](README.ja.md)

回路、PCB、機械、製造ファイルの正本は元のパスに維持します。
ここでは形状、承認、データ、過去の tool 結果を変更しません。
コマンドは派生成果物の再生成であり、製造発注・購入・通電の指示ではありません。
担当範囲、実行時 tool preflight、[組立証拠契約](assembly-evidence.ja.md)を先に確認し、
探索中に古い証拠を上書きしないでください。

## 回路

[directory 規約](../hardware/schematic/README.md)／
[Bench-IMU-01 project](../hardware/schematic/bench-imu-01/README.md)が原本です。
実 `.kicad_pro` / `.kicad_sch` に加え、project-local `.kicad_sym`、`.pretty`、
`sym-lib-table`、`fp-lib-table` を一緒に保持して開きます。
`generate_schematic.py` は生成方法、別の schematic design 文書は net ごとの理由の原本です。
Rev2 capture、Rev3–5 extension は過去の適用範囲で、現行全要件の新承認ではありません。

重要な設計判断には理由と Evidence ID を付け、修正を無記録の手編集にせず ECO を残します。
KiCad CLI/MCP は毎回確認し、過去の障害を永久的な不在としません。
CLI ERC と ERC 用 MCP wrapper は別の能力です。
同梱 library だけで自動 SPICE があると推測せず、回路作業で機械・firmware の所有権を取得しません。

## PCB

[PCB 規約・履歴・再生成](../hardware/pcb/README.md)が原本です。
基板ごとに `hardware/pcb/<board>/` を使い、`generate_pcb.py` が実回路の netlist/BOM から再構築します。
作成前に同梱 Python/`pcbnew` を確認します。
CLI export・DRC・render があることは対話 routing 能力ではありません。
zone fill の失敗・後の成功は状態依存の過去観測で、普遍的な障壁ではありません。

製造前 review に実 DRC、整合した BOM、visual snapshot が必要です。
accepted-risk や未解決 violation を DRC-clean と呼びません。
独立 Hardware Review と人間のゲートを維持し、過去の iteration の数を現在 DRC としません。

### 再生成を比較する

UUID と footprint 出力順は、設計が不変でも変わり得ます。
DRC の単純差分、raw hash、Gerber D-code 番号だけで形状一致を判定しません。
segment/via の座標・幅・径・drill・layer・net の multiset、
footprint 集合、pad 数、top-level zone 頂点、aperture を解釈した Gerber primitive を比較します。
`%ADDnn` を形状・parameter に解決し、footprint 内の `zone_connect` を top-level zone と間違えません。
固定したファイルからの export と board の再構築では byte 一致の性質が異なります。

root からの記録済み PNG 再生成コマンド:

```sh
kicad-cli pcb render hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb \
  --side top --width 1568 --height 984 --quality high --floor \
  --background opaque -o hardware/pcb/bench-imu-01/bench-imu-01-3d.png
```

原本の KiCad 10.0.1 host では実出力が1544×952だったと開示しています。
要求寸法を実出力と同一視せず、画像・camera・形状を検査します。

## 製造用 export

[package guide](../hardware/pcb/bench-imu-01/fab/README.md)が原本です。
ZIP は copper、paste、silkscreen、mask、outline、job metadata、
別々の PTH/NPTH drill と map を含み、別 CSV が placement 情報です。
PCB source を変更したら、同じ限定変更で**この系列と公開 viewer PDF の両方**を更新します。
export を直接修正しません。

元の DRC・accepted-risk・BOM 調達履歴は正本と共有台帳に残します。
提出可能なファイル形式と、発注許可、DRC-clean、全体 Design Complete は別です。
root から `<staging-dir>` を新しい scratch directory に置き換えて実行します。

```sh
kicad-cli pcb export gerbers \
  --output <staging-dir> \
  --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb
kicad-cli pcb export drill \
  --output <staging-dir> \
  --format excellon --excellon-separate-th --generate-map \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb
kicad-cli pcb export pos \
  --output hardware/pcb/bench-imu-01/fab/bench-imu-01-positions.csv \
  --format csv --units mm --side both \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb
cd <staging-dir> && zip -X -j bench-imu-01-gerbers.zip ./*
```

ZIP は wrapper folder なしの flat 構成とし、個別 staging file はコミットしません。
RS-274X/Excellon header、copper layer 数、outline と stroke 込み job 寸法、
PTH/NPTH 数、mounting hole 除外と position 行数の整合、
ZIP 完全性、転送後一致、意図しない source 変更がないことを確認します。
過去の測定数は過去の結果であり、新 export は自分の実結果を必要とします。

## 機械 source・STL・図面

[機械規約](../hardware/mechanical/README.md)／[STL](../hardware/mechanical/stl/README.md)／
[図面](../hardware/mechanical/drawings/README.md)が原本です。
parameter 化した `.scad` と読める寸法表・理由が source で、
寸法は interface / Evidence ID または明示的 ASSUMPTION/ESTIMATE に結びます。
可視化のついでに形状を直さず、所有者と ECO を通します。
過去の「CAD なし」や成功記録は現在の可用性ではありません。
現在の契約では設計中から WIP 証拠を作り、APPROVED 公開は別のゲート後です。

5種類の STL は base assembly、PCB lid、containment cap、stand plate、
同形を4個使う pinch-guard quadrant です。pointer と cable anchor は base の一体 job に含まれます。
export や manifold の確認は、slicer、造形、嵌合、強度、封じ込めの適格性ではありません。
寸法・リスク表は版付き工学記録として原本に残します。

[日本語の機械成果物再生成手順](mechanical-artifacts.ja.md)に STL・2D の全コマンド列、
drafting sheet と過去の Blender pipeline を掲載しています。
図面 Method 2/3/5/6 は古い形状を描くと原本が開示しています。
Fusion-style は Fusion native ではなく、旧 physics/concept demo は
[現在の自由剛体 simulator](../simulation/README.md)でもありません。
