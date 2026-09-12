# 回路・電流経路ビューアー

[English](../visualization/circuit-viewer/README.md) | [日本語](circuit-viewer.ja.md) | [Pages ガイド](pages.ja.md)

公開 Bench-IMU-01 の回路・firmware を説明するブロック図です。UI は既存の英語版を保持します。
[ローカル HTTP または Pages](pages.ja.md)で開き、部品と配線をクリックします。
source は実回路ですが、アニメーションを電流の測定値と解釈しません。

## 3つの mode

1. **Power Distribution**: USB から logic rail、外部 DC から保護・eFuse・motor driver・motor への経路。
2. **Current Behavior (implemented)**: IMU→UART は一方向 telemetry、
   host の UART 指令で motor を開ループ駆動し、FG は overspeed 安全 cutoff に使います。
3. **Future: Closed-Loop Attitude Control**: 明示的 **NOT IMPLEMENTED**。
   IMU に反応して motor を駆動する経路は現在の bring-up code に含まれません。

部品には役割・型番・存在する一次資料リンク、配線には net 名、接続元・先、用途・理由が表示されます。
FG の安全停止と速度・位置制御を混同しないため、net 名だけでなく実コード由来の説明を持ちます。

## 生成と保守

`circuit-data.js` は実 netlist / BOM / README から人手で導出したコミット済みデータです。
live query ではなく、source 変更時に担当者が更新します。
`index.html` / `circuit-render.js` は vanilla JS と SVG で build・runtime library 依存はありません。
線の見た目とは別の広い click hit-path を持ち、stroke と pulse がその click を奪わないようにしています。
クリック検査の旧測定数は原本の実装履歴で、今回再検証した結果ではありません。

`reference/bench-imu-01-schematic.pdf` と `reference/bench-imu-01-pcb.pdf` は実 KiCad からの export で、
source を修正すると古くなります。同じ変更で以下を再実行し、PDF を手修正しません。
root からの正確な command は次の通りです。

```sh
kicad-cli sch export pdf \
  -o visualization/circuit-viewer/reference/bench-imu-01-schematic.pdf \
  hardware/schematic/bench-imu-01/bench-imu-01.kicad_sch

kicad-cli pcb export pdf --mode-single \
  --layers F.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts \
  -o visualization/circuit-viewer/reference/bench-imu-01-pcb.pdf \
  hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb
```

KiCad 10 の PCB export には layer 指定が必要です。5 layer は既存出力の条件を維持します。
旧・新 PDF を `pdftoppm -r 150` で画像化し、変更領域が source 変更に対応するか比較します。
実行時の KiCad・画像化能力を確認し、共有証拠の版更新を担当範囲内で行います。

## 限界

配線経路は読みやすいブロック配置で、実 schematic の wire path そのものではありません。
`/3V3`、`GND` など多点 net は説明に必要な一部 edge を描きます。
J1 を出る2本の VBUS_5V が短い区間で重なり、重なりをクリックすると手前側を選ぶ場合があります。
どちらも実 net ですが、厳密に意図した sibling を選べるとは限りません。
この言語対応で layout data・回路・firmware・その limitations は変更しません。
