# `make-circuit` — 設計サイクルを始める

[English](make-circuit.md) | [日本語](make-circuit.ja.md) | [ガイド一覧](../README.ja.md)

人間の Product Owner / Chief Engineer が新しいハードウェア設計を依頼するときの開始プロンプトです。
毎回、調整手順を最初から書き直す必要はありません。
これは [make-circuit.md](make-circuit.md) の日本語版であり、実行契約や承認ゲートは共通です。

## 1. 開始前

まず `requirements/requirements.md` を作成・更新します。
ラフな案でも構いません。Phase 1 の要件整理で具体化します。
ファイルがまだない場合はプロンプトにそう書き、Hardware Lead にそこから始めてもらいます。

## 2. 標準の開始プロンプト

山括弧部分を実際の依頼に置き換えて使います。コマンド、パス、状態語は変更しません。

```text
このリポジトリの Hardware Engineering Lead / Orchestrator として作業してください。
.github/agents/hardware-lead.agent.md と .github/copilot-instructions.md を参照してください。

要件は requirements/requirements.md にあります。今回の変更: <変更内容>。

docs/workflow.md に沿って、次の依存関係を解消する成果物を特定してください。
今回依頼するのは <1つの限定目的、または明示的に合意した目的の集合> のみです。
設計ライフサイクル全体を、無期限に作業する許可と解釈しないでください。

規則:
- docs/work-execution.md に従い、専門担当の起動や作業開始の追加指示の前に、
  契約を作り tools/agent_workflow.py start で予約を成功させてください。
  source/configuration コミット、関連入力、書き込み範囲、成果物、依存、
  done_when、stop_when を含めます。拒否時は起動せず、改名で回避しません。
- Lead 自身が詳細回路設計をせず、Component Engineer、Circuit Engineer、
  Hardware Reviewer へ必要な作業を委譲してください。
  現在の環境にあるネイティブ起動方法、または対応する task ツールを使い、
  .github/agents/*.agent.md と必要な .github/skills/*/SKILL.md を渡します。
- 部品仕様を推測しません。重要な数値は datasheets/evidence-log.md の
  Evidence ID で示し、未確認は UNKNOWN として私へエスカレーションしてください。
- docs/architecture.md の §4 に従い、独立した候補調査・サブブロックだけを並列化します。
  統合、要件承認、レビュー判定は直列に保ち、今必要な役割だけを起動してください。
- 下流証拠を仕上げる前に上流のインターフェース・資料の判断を解決してください。
  実際の修正後に変更・影響範囲を再レビューし、同じ未解決指摘だけを理由に反復しません。
- 専門担当は共有台帳への提案を返し、Hardware Lead が判定を変えずに直列公開します。
- docs/architecture.md §10 の全 Human-in-the-loop ゲートで停止し、
  私の明示的承認を得てください。アーキテクチャ、主要部品、資料欠落、
  安全に関わる変更、大きな BOM 変更、PCB 製造前、初回通電前などです。
  明示的な許可なしにゲートを越えません。
- docs/architecture.md §8 の全条件を満たすまで Design Complete としません。
  未解決 CRITICAL がゼロ、HIGH が解決済みまたは私の承認付き accepted-risk、
  traceability がすべて verified/waived、FMEA レビュー済み、ECO 記録済みが必要です。
- tools/agent_workflow.py で限定作業を DONE または BLOCKED として保存します。
  どちらも設計・安全承認ではありません。依頼作業が終了したら報告して終え、
  新たな研究・巡回を追加しないでください。

報告:
- 提出済み成果と現在の作業
- 残る阻害要因、その担当、必要な具体的判断
- 次の停止境界と見積時間（不明なら UNKNOWN）
- open CRITICAL/HIGH の実数が変わったときはその数
コメント量ではなく、記録済みタスク状態と根拠のある結果で報告してください。
```

## 3. スケジュール機能と組み合わせる場合

現在の Copilot 環境が保存 workflow・スケジュール機能を実際に公開している場合に限り、
上の限定プロンプトを設定できます。過去に `save_workflow` というツールがあったことは、
今回も使える保証ではありません。この文書自体はスケジュールを作りません。

定期起動も同じリポジトリ内ガードを確認します。
入力と判断が変わっていなければ新規起動なしと報告して終え、担当を起こしません。
合意した目的を達成したら定期作業を無効化し、無制限の再試行ループにしません。

## 4. 応用

**早期の Cube 剛体物理**: Hardware Lead から固定入力を Simulation Engineer に渡し、
`docs/simulation.md` に沿った Cube・床・3輪の限定 WIP 実験を依頼します。
Design Complete を待つ必要はありませんが、実アクチュエーターや質量の欠測を補作しません。
合成参照モデルと不完全な設計 proxy を分離し、実軌道・図・動画を出力して、
別の Simulation Reviewer が実装と出力を評価します。
シミュレーション内制御は実機コード、物理承認、Fusion 組立動画ではありません。

**レビュー差し戻しからの再開**: 冒頭を「対象要件の設計を再開してください。
前回判定は <PASS/FAIL/CONDITIONAL>、指摘は validation/open-issues.md、
変わった入力・判断は <根拠付き差分> です。<限定修正> とその変更・影響範囲の独立レビューを依頼します」
に置き換えます。§2 の規則と報告条件は維持します。

**サブシステム追加**: 回路設計の一部として `hardware/power-budget.md` を更新し、
供給能力と再比較することを明記します。大きな BOM 変更・アーキテクチャ判断に該当し得ます。
既存レールに収まらない場合は Hardware Lead が Power Engineer の先行起用を判断し、
`hardware/power-architecture.md` の人間承認後に電源回路を実装します。追加のたびに自動起用するわけではありません。

**既知インターフェースからの WIP 機械・組立計画**: 不足する PCB 情報は Phase 4a の限定準備に回し、
Design Complete や全配線を待たせません。出典付き暫定値と不明点を示し、
最終寸法には確認済み入力を要求します。Mechanical Lead がインターフェースと筐体を設計し、
Mechanical Reviewer の独立評価を受けます。
`docs/assembly-evidence.md` に沿って早期から全搭載状態・各工程の証拠と WIP 組立計画・動画を作ります。
操作ごとにツールを確認し、要求された Fusion ネイティブ storyboard と再生可能な公開動画を提出します。
不可能なら正確な機能阻害と準備済み引き継ぎを記録し、黙って別レンダラーに置き換えません。
APPROVED 資料の公開は独立受け入れ、Design Complete、名指しの安全判断後です。
