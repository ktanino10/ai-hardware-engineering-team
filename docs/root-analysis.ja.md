# CERN ROOT 解析データ交換

[English](../simulation/root/README.md) | [日本語](root-analysis.ja.md) | [ガイド一覧](README.ja.md)

ROOT は**列指向の解析・データ交換**に使い、剛体・接触 solver ではありません。
一次参照は [RDataFrame](https://root.cern/manual/data_frame/) と
[TTree](https://root.cern/manual/trees/) です。

公開原本は、当時の host の ROOT 6.38.04 で Cling が macOS C++ header/module-map の不整合に失敗、
local venv に PyROOT は不在、native canvas/PNG も失敗した一方、
compiled TTree は数値の書き込み・再読込に成功したと記録しています。
これは操作別の過去観測で、今回の host の成功・失敗を保証しません。

adapter は compiled / non-JIT TTree を意図的に使い、
global ROOT/SDK を変更したり別 toolchain を導入したりしません。
RDataFrame、PyROOT、ROOT graphics を実行済みと主張しません。

```sh
# repository root。既存 root-config と c++ が必要です。
simulation/.venv/bin/python simulation/root/export.py \
  simulation/evidence/startup-v4/startup-mechanism-fixture \
  --output simulation/runs/my-root-analysis
```

出力は native `trajectory.root`、`summary.json`、無加工の `native-runtime.log`、
source/output hash の `manifest.json` です。
実行ファイルは無視対象 `simulation/runs/root-build/` でコンパイルします。
元の全数値列を double branch として書き、再読込で完全比較します。
追加した時間重み `sample_dt_s` も対象です。

2つ目の tree `time_weighted_wheel_x_rpm` は bin 境界とシミュレーション秒数を保持し、
単なる行数は数えません。密な brake window が過大評価されるのを防ぎます。
重みは次の記録までの時間、最終行はゼロです。
これは記述用の left-hold histogram で、solver 評価点の機械仕事・力積積分の代替ではありません。

健全な ROOT 環境なら `ROOT::RDataFrame("trajectory", "trajectory.root")`、
filter、重み付き histogram で利用できます。
原本の host では compiled adapter と Matplotlib を使い、interpreter/graphics の阻害を明示しています。
数値 branch が一致しても ROOT metadata/UUID は export ごとに異なり得ます。
