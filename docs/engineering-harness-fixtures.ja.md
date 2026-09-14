# 合成 KiCad fixture の使い方と範囲

[English / 正本](../tools/tests/fixtures/engineering_harness/README.md) |
[MVP の日本語版](engineering-harness-mvp.ja.md) |
[日本語索引](README.ja.md)

これは fixture の日本語 reading edition です。正確なファイル、
ハッシュ、JSON/CLI 文法は正本と
[manifest](../tools/tests/fixtures/engineering_harness/manifest.json) に従います。
部品選定、製造用回路、Rev5 の三軸基板やその承認を表す資料ではありません。

## 何を実際に確認する fixture か

| ケース | 内容 | 期待する実 native の結果 |
|---|---|---|
| clean ERC | 自作の passive test terminal 2個を、grid 上の wire で接続 | 報告された違反0 |
| 故障 ERC | 同じ terminal の接続 wire をなくす | `pin_not_connected`、読み込み失敗を代用しない |
| clean DRC | 閉じた外形、埋め込み test pad 4個、異なる net の離れた配線2本 | 報告された違反0 |
| 故障 DRC | pad に結び付いた異なる net の配線を同一層で交差 | `tracks_crossing` |
| 不正な外形 | 同じ pad/配線を使い、閉じた境界の代わりに一本の開いた edge | `invalid_outline` |

symbol はこのテストのために作った `Harness.kicad_sym` です。
project-local `sym-lib-table` を使い、外部メーカーの部品やライブラリ、
本番プロジェクトをコピーしません。PCB footprint は埋め込みです。
ERC の回路図と DRC の基板は別々の witness で、対応する製品ペアではありません。

各 `.kicad_pro` と manifest がテスト用のルール・入力を固定します。
追加の除外はなく、`--severity-all` で error/warning/exclusion を含めますが、
KiCad が既定で無視するチェックまで有効化する引数ではありません。
既定の ignored-check 一覧も計画に固定し、parser が照合します。
`--schematic-parity` の実行や、温度・定格・実装・製造性の合格を主張しません。

## 生成と固定の順序

生成する必要があるときは、先に実装作業の正常予約を取り、
所有範囲と終了・停止条件を明示してください。新しい候補を固定する前だけ、
次の既存 generator を使用します。

```sh
python3 tools/tests/fixtures/engineering_harness/generate.py
```

generator はテスト用 source と SHA-256 manifest を決定的に作成します。
実験中に再生成、手直し、閾値緩和をしてはいけません。
コミット済み fixture があるだけでは、実行可能ファイルやライブラリの存在、
実 domain command の成功を証明できません。
実験の reservation とコマンドは
[MVP 正本](engineering-harness-mvp-2026-09-14/README.md#frozen-matched-experiment)
で確認してください。

実行時は manifest に宣言した入力だけを所有された一時領域へコピーします。
HOME/config/cache/temp を分け、本番入力を直接開きません。
snapshot/restore の対象は操作所有のテスト出力だけです。
他の書き込みや symlink/hardlink、所有場所の変化、cleanup 未確認なら
復旧を断定せず停止します。試験の後片付けは本番復旧の成功と数えません。

## 合成の証拠・失敗注入

`dependency.json` は実 simulation の再計算ではありません。
直接参照するモデル識別を変更して stale 判定を試し、fresh な正例も置きます。
historical-only は履歴の完全性だけであり、現在の freshness は
`UNKNOWN` / not checked のままです。

`approval.json` は架空の actor と `SYNTHETIC_ONLY`、
`usable_for_real_action: false` を持つ非現実の承認 fixture です。
入力ハッシュや要求に一致していても、実 export、fabrication、purchase、
power、flash を有効化しません。禁止要求は共通の無害な recorder より前で
拒否し、実 Gerber 等を生成しません。

不足・復元されたログ、truncated JSON、timeout、partial write、
復旧競合、ツール不足も合成注入として区別します。
中断回帰では短命の所有子プロセスだけを使い、SIGINT/KeyboardInterrupt 後に
回収または未確認 cleanup を記録して停止することを確認します。
この中断回帰は、既存 A/B の20ケースには追加しません。

## 測定結果を過大に読まない

元の候補と中断修正後の候補は別々の120件のキャンペーンを持ち、
両方とも強い scripted-reference と wrapper の結果は同等でした。
**NO_DEMONSTRATED_RELIABILITY_IMPROVEMENT** が結論です。
実 native では clean ERC/DRC の違反0、故障 ERC 2件、故障 DRC 1件、
不正外形1件という意図した結果を得ましたが、実 Rev5 の問題を解消した
証拠ではありません。

結果のハッシュ・レポート・所有プロセスの事後照合は決定的な整合性確認であり、
独立した engineering review、OS sandbox、全プロセス停止保証ではありません。
必要ツール不足や必須 native ケース未実施は `PARTIAL` とし、再実行や追加依存は
新しい関連入力・判断と正常予約へ戻します。本番採用・製造・実機許可は別です。
