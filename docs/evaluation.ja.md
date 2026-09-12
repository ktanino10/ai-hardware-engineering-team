# 開発品質の評価

[English](evaluation.md) | [日本語](evaluation.ja.md) | [ガイド一覧](README.ja.md)

担当分離によって単一 AI より誤りが減り、追跡可能性が増すかを測るための
[evaluation.md](evaluation.md) の日本語版です。比較可能な複数サイクルができてから評価し、
役割数だけで効果を主張しません。

## 1. 実験

同じ `requirements/requirements.md`、部品候補群、利用可能なデータシートを使い、
MCU + IMU + 電源など比較可能な対象で以下を比べます。

- **A — 単一エージェント**: 役割分離・独立レビューなしで要件、部品、回路を扱う。
- **B — マルチエージェント**: 要件、選定、資料確認、回路、独立レビュー、検証、差し戻しのフレームワークを使う。

プロセス以外の条件をそろえます。

## 2. 指標

| 指標 | 定義・記録 |
|---|---|
| データシート違反 | 絶対最大・推奨動作条件に反する判断の総数。自己点検、独立評価、後日発見を含む。open-issues / design-review |
| ERC error | 回路の electrical rule error。実際に利用できたツールの出力を使用 |
| DRC error | PCB design rule error。実際の DRC 出力・履歴 |
| レビュー指摘 | 全重大度の独立指摘数。open-issues |
| CRITICAL 指摘 | CRITICAL の数。open-issues |
| 人間が先に見つけた誤り | `found-by: human` の指摘 |
| revision 数 | 対象設計の ECO 数。change-log |
| simulation failure | 原本では将来の SPICE 統合後の指標。剛体試験の失敗数へ無断で読み替えない |
| 実機問題 | bring-up 中・後の `phase: bring-up` 指摘 |
| Design Complete までの時間 | 要件承認からゲート通過まで。ECO timestamp |

原本の ERC 行には「将来統合」という古い説明が残っています。
ツール可用性は[構成 §5.2](architecture.ja.md#52-kicad)の実行時確認を優先し、
この翻訳は新たな ERC 実行成功を主張しません。

### 2.1 追加指標

| 指標 | 定義・意味 |
|---|---|
| Evidence Coverage Rate | 有効な Evidence ID を引用する判断・指摘の割合 |
| Unknown Resolution Rate | 当初 UNKNOWN の値が Design Complete 前に一次引用付きで解決した割合 |
| Reopen Rate | RESOLVED 後に再開した指摘の割合。表面的修正の検出 |
| FMEA Predictive Validity | 実機問題のうち bring-up 前の FMEA が予見した割合 |
| Requirement Coverage Rate | Design Complete 時の traceability の Verified 割合。Waived は含めない |
| Change Churn | 設計リビジョンサイクルごとの ECO 数 |

## 3. 追加台帳を作らない

必要なデータは既存の指摘、FMEA、ECO、traceability にあります。
別の並列ログを作らず、設計サイクル後に既存表を集計します。
機械可読に出力できるようになればスクリプト化し、それまではサイクルごとに手で計算します。

## 4. 報告

各条件・各設計サイクル後に指標を埋め、そのサイクルの closing ECO に添付します。
比較の根拠を監査可能な1か所に保ちます。
