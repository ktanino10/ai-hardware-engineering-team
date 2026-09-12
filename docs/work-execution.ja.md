# 範囲を限定したエージェント作業

[English](work-execution.md) | [日本語](work-execution.ja.md) | [ガイド一覧](README.ja.md)

[work-execution.md](work-execution.md) の日本語版です。開発フローの実行契約であり、
新しい専門分野でも独立レビューの代替でもありません。調整担当を1つに定め、
次の依存関係を解消する成果物に必要な専門担当だけを起動します。
並列作業には独立した入力と重複しない書き込み範囲が必要です。役割が存在するだけで全員を起動しません。

## 専門担当を起動する前に

Hardware Lead は限定された目的ごとに安定したタスク ID を記録します。
関係する入力と採用する設定を変更不能な Git コミットで固定し、稼働中の書き手の checkout に
新設定をマージしません。契約、担当プロファイル、必要なスキル、一次資料への参照、対象範囲を渡し、
会話全体やすべての過去監査を渡しません。

セッション作業領域または無視対象の `.agent-work/` に JSON 契約を作成します。
フィールド名と状態値は共通の機械可読契約なので翻訳しません。

```json
{
  "schema_version": 1,
  "id": "example-interface",
  "owner": "circuit-engineer",
  "objective": "Resolve one explicitly commissioned interface",
  "source_revision": "<full source commit ID>",
  "config_revision": "<full adopted configuration commit ID>",
  "inputs": ["requirements/requirements.md"],
  "writes": [".agent-work/example-interface"],
  "deliverables": [".agent-work/example-interface/handoff.json"],
  "done_when": "Deliver the proposed interface, source basis and remaining limitations",
  "stop_when": "A required source, capability or human decision is unavailable",
  "depends_on": []
}
```

例の入力を、実際に判断を支える**すべての入力**に置き換えます。
必要に応じて対象範囲の意思決定・ツール可用性記録を含めますが、無関係な履歴は追加しません。
`writes` は glob ではなくリポジトリ相対の実ファイル・ディレクトリで、
すべての `deliverables` がその範囲内に必要です。
報告だけの担当は `.agent-work/<task>/` を使えますが、その一時報告は公開済み設計記録ではありません。

`depends_on` の各生成側が宣言した成果物は、利用側の `inputs` に同じ相対パスで含めます。
成果物をコミットしてから利用側の `source_revision` を選び、その snapshot に記録済みの内容が存在することを確認します。
ガードは生成側の保存出力と利用側の固定コピーを両方確認します。
依存名だけでは別 worktree や古いローカルコピーを読む権限になりません。
依存入力になる成果物は永続的なリポジトリパスを使い、無視対象の一時報告とは区別します。

調整担当は、担当者が使う予定の worktree から次を実行します。

```sh
python3 tools/agent_workflow.py start /absolute/path/task.json --session coordinator-id
```

終了コード **0** の後にだけ、現在の Copilot 環境で実際に使えるツールで専門担当を1回起動します。
返された `run_id` を保持します。スクリプトは予約するだけで、エージェントの起動・監視・停止、
フックの導入、App 設定の変更はしません。`handoff_to` などの frontmatter は役割説明でありスケジューラーではありません。

ガードは以下を拒否します。

- すでに `RUNNING` のタスクや書き込み範囲の重複。linked worktree 間も対象です。
  同じ worktree の読み書き競合も拒否し、別の固定 worktree の読者は宣言した snapshot を読めます。
  大文字小文字・Unicode の別名は保守的に同一扱いとし、symlink を拒否します。
- `DONE` 引き継ぎがない依存、保存出力の欠落・変更。
- 関連入力の内容と依存引き継ぎが同じままの、過去に `DONE` または `BLOCKED` となったタスク。
  日付、セッション、設定リビジョン、無関係なコミットを変えても新しい入力にはなりません。
- 入力 snapshot の欠落・未コミット変更、`config_revision` と異なる設定。
  `AGENTS.md`、`.github/`、構成・開発フロー・実行指示、開始プロンプト、ガード自体を確認します。

拒否を避けるためにタスクを改名したり、状態を消したり、無関係な入力を増やしてはいけません。
再作業には関係する証拠の変化か記録された人間の判断が必要です。
異なる問いには別タスクと明示的な依存を用意します。基盤修復も別の限定タスクで扱い、
同じ設計レビューのやり直しに見せかけません。

## 進捗と終了

成果物、判断、阻害要因が変わったときに短く記録します。

```sh
python3 tools/agent_workflow.py progress RUN_ID --session coordinator-id \
  --summary "Completed X; Y remains" --next-action "Owner/action for Y; estimate UNKNOWN"
python3 tools/agent_workflow.py status
```

利用者には**提出済みの結果、現在の作業、残る阻害と担当、次の停止境界・見積もり（不明なら UNKNOWN）**
を伝えます。重要な入力・設定リビジョンや安全上の保留も明示します。
メッセージやコミット、ツール呼び出しの数でなく、解決したインターフェース・指摘を数えます。
長いネイティブ操作の前には出力と停止境界を示し、架空の ETA や活動表示だけの監視担当を作りません。

限定作業の引き継ぎ時に、同じ調整担当が終了結果を1つ記録します。

```sh
python3 tools/agent_workflow.py finish RUN_ID --session coordinator-id --state DONE \
  --summary "Bounded result saved; independent acceptance remains separate" \
  --next-action "Hand this frozen result to its independent reviewer"
```

停止条件に達したら `--state BLOCKED` とし、部分成果を保存して、
**具体的にどの入力・判断が変わる必要があるか**を記録します。
`DONE` にはすべての宣言済み成果物の存在が必要です。
両終了状態は読み取り可能な通常ファイルのハッシュを保存します。
`BLOCKED` は欠落・不正・読み取り不能な出力のエラーを明示して試行を終了しますが、
それらを修復したり別パスを追ったりしません。`DONE` は不正出力を拒否します。
ファイルの存在だけでは工学的な受け入れを証明できず、Hardware Lead が `done_when` を判断します。

`BLOCKED` は今回の試行終了であり、同じ問い合わせ・再試行の継続指示ではありません。
依頼されたすべてのタスクが終了したら報告して終了します。
新しい依頼なしに研究、再レビュー、巡回を追加しません。

| 状態 | 意味 |
|---|---|
| `RUNNING` | 調整担当付きで予約された作業。プロセスが生きている証拠ではない |
| `DONE` | 限定された結果を提出した。レビュー結果が FAIL でもレビュー作業自体は終了し得る |
| `BLOCKED` | 明示された前提不足で今回の試行を停止した |
| Design Complete / APPROVED / 実機操作の許可 | 従来の独立レビューと人間のゲートのみが与える。ツールは与えない |

レビュー対象は固定した実装です。再レビューは変更箇所と影響範囲を既存スキルに従って扱い、
日付更新のためだけに同じ数値計算・描画・資料調査を繰り返しません。
古いレビューを変更後のパッケージに対する受け入れと表示しません。

## 共有記録の公開担当は1つ

技術的著者は専門担当のままです。担当は提案行、根拠、判定を自分の範囲の引き継ぎにまとめます。
Hardware Lead は次の更新前に、別の直列公開タスクを予約します。

`datasheets/evidence-log.md`、`validation/open-issues.md`、
`validation/design-review.md`、`validation/change-log.md`、
`requirements/traceability-matrix.md`、`bom/component-selection.md`。

統合作業の worktree で正規 ID を一度だけ確保し、レビュー担当の意味・判定を変えずに公開して、
既存の ID・ゲートチェックを実行します。他の担当はコミット済みの引き継ぎを待ち、
独自の ID 確保や台帳の同時編集をしません。公開担当へ技術的所有権やリスク判断権は移りません。
範囲内の形状・コードは元の担当が所有し、その他の共有ファイルにも書き込み範囲ガードが適用されます。

## 永続化・復旧・制限

状態は `<git-common-dir>/agent-workflow/state.sqlite3` に保存し、
同じマシンの linked worktree 間で共有します。コミット対象の設計ファイルや一時 todo ではありません。
`status --history` は過去試行も示し、通常の `status` は各タスクの最新試行を示します。
未予約の計画に session todo を使えますが、実行状態の根拠はこのツールです。
別 clone・別マシンとは DB を共有しないため、調整担当を1つに決め Git で永続的に引き継ぎます。

状態は**保存記録であってライブ監視ではありません**。
App が止まった場合は実際の担当と保存ファイルを先に確認します。
`RUNNING` 予約は自動失効しません。書き込み停止を確認した後、
記録済みの調整担当 ID と worktree から、復旧証拠・次の対応付きで `BLOCKED` にします。
再試行を通すために稼働中予約を消しません。DB の欠落・破損は完了の証拠になりません。

ガードは開始時の検査で、OS の権限制御ではありません。
新たな作業を開始する起動・追加指示の前に呼び出し、担当は範囲を守る必要があります。
任意の App 操作や管理外エージェントは横取りできず、既存セッションを自動移行もしません。
安全な引き継ぎまたは新セッションで設定を採用します。

時間・クレジット・同時実行上限は利用者と合意し、黙って設定したりモデルを変更しません。
実行環境が対応する制限は別途設定します。ソフト上限は確実なタイマーや工学的な完了条件ではありません。
ハードウェアゲート、必須チェック、マージ、製造、通電、初回 flash、回転・跳躍、リスク免責の権限は追加されません。
