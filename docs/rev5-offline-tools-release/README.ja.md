# Rev5 オフライン解析の限定公開

[English](README.md) | [日本語](README.ja.md) | [公開入口](https://ktanino10.github.io/ai-hardware-engineering-team/index.ja.html)

**SYNTHETIC ONLY / NOT SENSOR HEALTH OR CONTROL APPROVAL**

既存の IMU 不一致解析 CLI、estimator/helper 4 ファイル、変更していない 14 テスト、
合成 one-bias 入力一式と、**C1 集計要約のみ**を独立した公開単位にします。
firmware や C1 の実処理ツールは含みません。保留中の
[PR #80](https://github.com/ktanino10/ai-hardware-engineering-team/pull/80)とは別であり、
その firmware alert の修正・抑制・解消を意味しません。

## 既存の例を実行する

公開 checkout のリポジトリルートで Python 3.9 以上を使います。
標準ライブラリだけで実行でき、追加 package、Git 履歴、ネットワーク、SDK、実機、
truth sidecar、私有ソースは実行時に不要です。

```sh
python3 -B -S -m unittest discover -s simulation/imu_disagreement/tests -v
out="$(mktemp -d)"
python3 -B -S -m simulation.imu_disagreement \
  --config docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/config.json \
  --samples docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/samples.jsonl \
  --output-dir "$out/report"
```

`-S` は site package を無効にし、標準ライブラリだけの実行を明確にします。
新しい出力ディレクトリへ `report.json` と `report.md` を保存します。
既存ディレクトリは拒否し、途中まで書かれたディレクトリを完成済みとは扱いません。
終了 **0** は合成入力契約の下で全 record が比較可能だったという意味で、
正常・正確の判定ではありません。終了 **2** は入力・比較の未解決または出力エラーです。
report と stderr を確認し、不完全な結果を成功として扱わないでください。
入力は規模を限定した信頼できるオフラインファイルで、メモリー内へ読み込みます。

元の fixture は **1,201 record が比較可能、未解決 0**、最大 spread は約
**0.1 rad/s**、record 平均は約 **0.08334721 rad/s** です。センサー仕様値ではありません。
[example-summary.json](example-summary.json)は大量の入力・record を複製せず、
実際の summary を既存 report と同じ形で保存します。完全版 report は入力と実装の
SHA-256、Python 版も含むため、全体 hash は Python 版や入力パス表記で変わり得ます。
異なる環境で byte hash が一致すると約束せず、入力・実装 hash と数値の意味を比較します。

## report の読み方

`records` は受理 ID、別に観測した存在・欠落、拒否理由、入力時刻ラベル、body 座標の
gyro 平均、Euclidean 残差ベクトルと norm を保持します。spread は
**既存の等重み平均からの最大 Euclidean 距離**で、標準偏差や姿勢誤差ではありません。

| 寄与数・入力の有効性 | 出力の意味 |
|---|---|
| 有効かつ受理 2 個以上 | `COMPARABLE_SYNTHETIC`。残差と spread を計算可能 |
| 有効かつ受理 1 個 | 平均だけを保持。spread・残差は `null`、比較は `UNRESOLVED` |
| 受理 0 個または入力・連続性無効 | 比較不能は `null` のまま。ゼロ誤差・正常へ変換しない |

存在しても受理されたとは限りません。不正 UTF-8 は有効な prefix を残したうえで
連続性無効を latch します。欠落・stale・重複・reset・逆順・gap の元の拒否方針を維持します。
集計は比較可能 record の等重みで、時間加重ではなく、補間で欠損を埋めません。
共通 bias なら spread がゼロでも誤差はあり得ます。3 対 3 の分裂から真値は選べません。

対応するのは宣言済みの合成 SI、body 座標変換、較正済み identity 入力、
正確な合成 clock だけです。実際の精度・遅延・較正は **UNKNOWN** のままです。
既存 helper は内部で従来の加速度・姿勢経路も実行しますが、この wrapper は姿勢を
出力せず制御へ接続しません。健全性閾値、自動除外、重み、較正、姿勢制御、
sidecar の動作は追加・変更していません。

## C1 は要約であり購入用データではない

同一 byte の [C1 JSON](../rev5-public-release/software-c1-summary.json)は
**候補 10、製品 UNKNOWN 要件 2、gap 23、出典観測 103、採用 0** を記録します。
数量は **UNKNOWN**、purchase readiness は **CLOSED**、実機許可は **NOT_GRANTED** です。
日付付き観測であり、最新 catalogue の再確認や代替候補を合算した部品数量ではありません。
封印済み私有入力、CLI、実処理用の依存一式は公開・再構成しません。
この JSON は代替の入力 dataset でも発注可能 BOM でもありません。

## 出典・確認・公開の境界

[intake.json](intake.json)は coordinator が選んだ目的と正の Git-object リストを固定します。
11 個の実装・テスト・fixture・要約は公開 commit
`6a86f5e71934c78435ca31f3f696da48de5ddd5a` と同一 byte です。
Python と fixture の元の authored revision も [provenance.json](provenance.json)に記録します。
[manifest.json](manifest.json)は限定した出力と派生文書・CI を束ね、manifest 自身の
hash は再帰計算せず所属 Git commit で固定します。元 branch 全体や私有履歴は merge しません。

元の独立した限定レビューは IMU wrapper と 14 テストを PASS としています。
元の担当・範囲、他の対象の過去件数、明示的 **NOT_RUN** は provenance とそこから
リンクする immutable 公開要約に保持します。今回の依存確認と例の実行は
**公開担当・CI の証拠で、新しい独立レビューではありません**。

```sh
python3 -B -S -m unittest discover -s tools/tests -p 'test_rev5_offline_publication.py' -v
```

hash、安全な限定パス、import、元の 14 テスト、公開ファイルだけの隔離実行、
helper 欠落時の失敗、合成入力の意味、C1 制限、EN/JA リンク、v2/v3/動画の保持を確認します。
既存数値 CI を残したまま、オフライン確認を追加します。
[checks.json](checks.json)は PR 作成前のローカル確認 snapshot であり、
その後の merge・Pages deploy の証明ではありません。それぞれ実際の remote readback が必要です。
Pages root は引き続き `visualization/` のため、文書へは実際の GitHub URL で案内します。

公開済みの [v3 と Blender 動画 6 本](../rev5-v3-media-release/README.md)、
[v2](../rev5-public-release/README.md)は同一 byte を維持します。
firmware、vendor/Bosch/CRT/N8R8/SDK、私有 C1 入力、raw source notes、native CAD、
media、実機・serial 作業は含みません。所有者の自作成果物公開許可を根拠とし、
新しいライセンスや第三者の許諾は作りません。戻す場合も、この限定変更の通常 review 付き
revert、既存必須 CI、既存 Pages workflow を使い、保護設定を回避しません。

**未変更の保留:** original44 = **2 closed / 42 unfinished**、WIP /
NOT ASSEMBLY READY / NO-GO / 3C8H / REQ409 / strict-pro / 39UNKNOWN、
P1/C1/D1、control/sidecar/ICD と全 source・human・physical gate。
有限のソフトウェア公開であり、組立・購入・製造・通電・flash・回転・安全の許可ではありません。
