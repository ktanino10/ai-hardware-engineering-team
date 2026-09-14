# Engineering Harness MVP の使い方と実測結果

[English / 正本](engineering-harness-mvp-2026-09-14/README.md) |
[日本語索引](README.ja.md) |
[fixture の日本語版](engineering-harness-fixtures.ja.md)

これは運用上重要な内容をまとめた日本語 reading edition です。
コード、JSON、コマンドの文法と測定データは正本を参照します。
元の資料や全ログを逐語訳・再審査したという意味ではありません。

**承認されたのは実装・テスト範囲です。本番採用や実機操作の承認ではありません。**
対象は合成 fixture に対する一つの native KiCad ERC/DRC アダプターと、
テスト用の証拠・レビュー準備判断です。Rev5 の実設計、simulation/control、
製造用データや既存の判断記録は変更しません。

## 何を許可する状態なのか

`ALLOW_TEST_OUTPUT` は、操作が成功し、実レポートの検証が `PASS` で、
明示した入力・設定・ツール・ルールが現在も一致し、
レポートとログの証拠がそろった **テスト出力だけ**を意味します。
消えたログ、変わったレポート、古い入力や未確認の新しさでは許可しません。

操作 lifecycle、validation verdict、evidence freshness、gate decision、
recovery outcome は別項目です。元の検証結果を履歴として保存することと、
現在の判断に使えることも別です。historical-only の照合では現在の freshness は
`UNKNOWN` / not checked であり、自動的に `STALE` と断定しません。
既存 simulator の検証処理を呼び直したり置換したりするものではありません。

復旧は操作所有のテスト出力だけです。以前の bytes と書き込み後の期待ハッシュを
記録し、競合、symlink、hardlink、所有場所の変更があれば拒否します。
`ROLLBACK_OK` でも失敗した操作は失敗のままです。
元の失敗レポートやログは、戻した出力とは別に残します。

## 通常予約と実行

Python 3.11 以降の標準ライブラリを使い、今回の測定環境は
Darwin/arm64・CPython 3.14.3・KiCad 10.0.1 に固定しています。
他の環境・バージョンまで動作確認したとは主張しません。
自動インストール、MCP 導入、任意 shell 引数の実行はありません。

まず [通常の bounded-work 手順](work-execution.ja.md) で、
固定した入力コミット、設定コミット、書き込み範囲と停止条件を予約します。
task/run ID は納品追跡の情報であり、人の権限確認ではありません。

```sh
PYTHONPATH=tools python3 -m unittest discover -s tools/tests -p 'test_engineering_harness*.py'
```

このコマンドは合成 unit/regression を実行し、実 KiCad の完了証拠の代わりには
なりません。CLI request の完全な形は
[正本の Commands](engineering-harness-mvp-2026-09-14/README.md#commands-and-existing-reuse)
を参照してください。`scope` は `SYNTHETIC_ONLY`、
`operation` は `erc` または `drc`、入力は fixture manifest と固定 Git bytes に
結び付けます。設定、入力名、tool の version/SHA-256、timeout、
正常予約の task/run を含め、未知の追加引数は認めません。

```sh
python3 tools/engineering_harness.py <request.json> \
  --workspace .agent-work/<admitted-task>/<new-operation> \
  --kicad-cli <verified-native-cli>
```

終了コード **0** は現在有効なテスト出力、**2** は BLOCKED または人への判断経路、
**130** は利用者による捕捉可能な中断です。任意の製造/export/purchase/
power/flash や save-board/refill-zones は、承認らしい JSON が一致していても
`HUMAN_REQUIRED` / `OUT_OF_MVP_SCOPE` で実処理を行いません。

## 中断時の修正と限界

[中断 follow-up](engineering-harness-mvp-2026-09-14/cancellation-followup.md) では、
待機中の caller SIGINT で子プロセスが残り、process receipt が作られない
元の欠陥を、短命の所有テスト子プロセスで再現しました。
修正後は既知の所有グループを停止・回収し、receipt を残して中断を伝えます。
確認できない cleanup は未確認として扱い、後続ケースへ進みません。
部分状態は所有領域に保存されるため、勝手に削除して成功扱いしません。

これは catchable `KeyboardInterrupt` / caller SIGINT の対策です。
捕捉不能な SIGKILL、標準動作の SIGTERM、一般的な親プロセス死亡、
同一 UID の任意操作まで保証するものではありません。
wrapper 外から直接ツールを起動するクライアントも防げません。

## 固定した比較の結果

[元の結果](engineering-harness-mvp-2026-09-14/experiment/summary.md) と
[中断修正後の結果](engineering-harness-mvp-2026-09-14/experiment-cancellation-successor/summary.md)
は混ぜずに保存されています。後継コード候補は
`ad5542b43890980bc28c3e589c1a33eb2fdd7394` です。
元と同じ20ケース・各群3反復で、全11行の失敗クラスと正例を試しました。
中断 witness/regression を、A/B の有利な追加ケースとして分母に足していません。

| 後継比較の各群 | A | B |
|---|---:|---:|
| 予定 / 実行 / ケース成立 | 60 / 60 / 60 | 60 / 60 / 60 |
| 期待どおりの結果 | 60/60 | 60/60 |
| 正例の許可 | 12/12 | 12/12 |
| 正常出力の誤遮断 | 0/12 | 0/12 |
| 不正出力の受け入れ | 0/30 | 0/30 |
| 禁止された合成要求の拒否 | 12/12 | 12/12 |

A は既存方針に従う強い scripted direct-CLI/owner-inspection の参照手順で、
故意に危険な操作をさせた群ではありません。実際の人やモデルの働き方を
測定した実験でもありません。両キャンペーンの信頼性指標は同等で、
**NO_DEMONSTRATED_RELIABILITY_IMPROVEMENT** です。中断の具体的な修正成功と、
A/B で改善を実証できなかった結論を区別してください。

実 native の clean ERC/DRC は非空 fixture で違反0、
故障 ERC は `pin_not_connected` 2件、故障 DRC は `tracks_crossing` 1件、
開いた基板外形は `invalid_outline` 1件でした。残りは明示された合成注入です。
同じ severity/default ignored-check 条件であり、すべての物理チェックや
schematic/PCB parity を評価した意味ではありません。
実ツールの必須ケース不足は `PARTIAL` で、mock 成功で埋めません。

計測を再び実施する必要がある場合も、関連する変更・許可と別の正常予約、
新しい固定候補が必要です。後継出力先は
`docs/engineering-harness-mvp-2026-09-14/experiment-cancellation-successor`。
既存結果を上書きしたり、途中で fixture・ルール・反復順を変えたりしません。
請求額と backend-model identity は公開情報がなければ `UNKNOWN` のままです。

## 証拠と承認

公開するのは小さい sanitized reports/logs、入力・設定・tool のハッシュ、
実測値と制約です。raw private bytes のハッシュと公開用 bytes のハッシュは
別に記録します。出力・復旧・cleanup の照合は同じ担当者による
**決定的な事後整合性確認**で、独立した工程・設計レビューではありません。

新しい依存・権限、入力の変化、所有権や cleanup の不確実性があれば停止して
担当者へ戻します。直接宣言していない推移的な依存の失効は解決していません。
`DONE`、テスト成功、PR の push、マージ、Design Complete、本番採用、
実機の許可はすべて別です。人の本番採用判断と既存の物理ゲートは未解除です。
