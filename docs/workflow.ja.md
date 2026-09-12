# 開発フロー

[English](workflow.md) | [日本語](workflow.ja.md) | [ガイド一覧](README.ja.md)

[workflow.md](workflow.md) の**日本語読者向け編集版**です。
各段階の開始・終了条件と現行の引き継ぎ規則を説明します。
過去の個別事件の全文は正本の対応節に残し、設計履歴・判定を翻訳台帳として複製しません。
重大度、Evidence ID、承認条件の正本は `docs/architecture.md` です。

## 0. 実行境界

専門担当の起動・追加作業指示の前に[作業実行契約](work-execution.ja.md)を適用します。
`tools/agent_workflow.py start` が成功してから起動します。
ガードは固定入力・設定、過去試行、完了依存、linked worktree の範囲競合を調べ、
エージェント起動や設計承認はしません。

具体的な問いに答える、または依存を解消する次の成果物を選びます。
`done_when` / `stop_when` で部分成果を保存して終了します。
工程の差し戻しは依存関係の説明であり、不変の BLOCKED 入力を無期限に再実行する許可ではありません。
タスク `DONE` / `BLOCKED`、独立受け入れ、Design Complete、実機操作の許可を分けます。

## 1. 段階のつながり

要件 → 部品 → 資料確認 → 回路 → 独立レビュー → 検証 → 共通ゲートが基軸です。
レビュー・検証の欠陥は設計へ戻します。
機械の Phases 8–10 は物理情報が分かった Phase 4 から分岐し、
Design Complete を待たず WIP 証拠を作り、同じゲートへ戻ります。
PCB 情報が不足すれば Phase 4a で限定的に準備します。

Firmware の Phase 11 もピン・インターフェース確定後に分岐しますが、ハードウェアのゲートに合流しません。
Power の Phase 12 は実負荷が分かる Phase 2 から分岐して、電源回路設計の前に人間承認を得ます。
Simulation の Phase 4b は承認された物理の問いがあれば要件段階でも開始でき、
独立レビュー後の知見を元の設計担当へ返します。物理承認にはしません。

## 2. 各段階

### Phase 1 — 要件整理

**担当**: Hardware Lead と人間。requirements-engineering スキルを使います。
目標が提示されたら、曖昧さ、測定可能性、優先度、環境・安全・インターフェースの不足を整理します。
`requirements/requirements.md` を人間が承認し、traceability の行を `Pending` で初期化したら引き継ぎます。
単一の承認なので並列化しません。

### Phase 2 — 部品選定

**担当**: Component Engineer。承認済みの対象要件から、可能なら3候補以上を調査し、
各資料確認を Phase 3 で行い、電気仕様、package、EOL、供給、参照設計、開発環境を比較します。
`bom/component-selection.md` の推奨をまとめ、主要部品・構成判断は人間承認を得ます。
真剣に検討する候補の資料が見つからなければ推測せず停止・エスカレーションします。
候補調査は並列可、最終推奨は直列です。

### Phase 3 — データシート確認

**担当**: 選定中は Component Engineer、設計前・中は Circuit Engineer。
資料のメタデータだけを登録し、必要制約を `Parameter | Min | Typ | Max | Unit | Source` で抽出します。
絶対最大、推奨、代表を分け、Evidence ID の提案を引き継いで正規ログへ公開します。
設計依存値のすべてが Evidence ID または明示的 `UNKNOWN` になれば次へ進めます。
資料ごとの独立抽出は並列化できます。

### Phase 4 — 回路設計

**担当**: Circuit Engineer。承認済み部品と抽出制約が入力です。
Power Engineer 起用時は電源サブブロックだけが Phase 12 の人間承認を先に必要とし、
非電源ブロック全体をそれだけで止めません。
電源・接地・ピンを直列で固定後、スキルとプロファイルの全 checklist に沿って設計し、
Evidence ID と設計理由、power budget、自己点検をまとめて引き継ぎます。
独立ブロックは固定後に並列可、統合は直列です。

### Phase 4a — WIP PCB 物理インターフェース準備

**担当**: Lead が範囲を定めた PCB Engineer。回路接続は Circuit Engineer、筐体形状は Mechanical Lead のままです。
特定の回路入力リビジョンと承認済み部品で限定した物理の問いに答えます。
Design Complete や最終 board outline は開始条件ではありません。
package / footprint、両面の搭載 envelope、嵌合済み connector、暫定外形・穴・配置、
挿入・工具余裕、実際の routing / DRC 状態を記録します。
不明値には調査担当を付け、完成して見せるために部品や接続を発明しません。

出力は出典・リビジョン付き **WIP - NOT ASSEMBLY READY** の証拠と不明点です。
未配線基板は未配線のまま明示し、初期阻害レビューへ渡せます。
全配線、製造リリース、自己承認、実機操作は禁止です。
全 PCB 設計は Design-Complete 回路、独立 Hardware Review、人間の各ゲートを保ちます。
入力が変わったら影響する形状と下流証拠を更新し、ラベルだけを更新しません。
1人の PCB 形状担当と固定引き継ぎを維持すれば回路レビュー・機械計画と並行できます。

### Phase 4b — 早期 WIP 剛体シミュレーション

**担当**: Simulation Engineer と別の Simulation Reviewer。
人間が承認した限定物理の問いと、固定した出典入力または別の合成 fixture が開始条件です。
Phase 4 完了も電子回路全体も Design Complete も不要です。
ツールを確認し、rotor の質量二重計上を避け、内部反力・接触・受動試験・反応試験・feedback、
数値 witness、時刻付き図・動画を作ります。
実行可能なモデル・runner、入力信頼度、実際の出力とハッシュ、
独立判定・残る再現性の限界を引き継ぎます。

モデル・コードの `CRITICAL` / `HIGH` は実装者へ戻し、再レビューします。
入力変更は影響する結論を無効化し、古い証拠を保存して新版を生成します。
制御はシミュレーション内だけ。FEA/SPICE、実機操作、部品採用、強度・安全認定、
ハードウェア指摘の自動閉鎖はしません。
辺・頂点に最初から置いた試験を自由接触からの遷移成功と呼びません。
指摘は `simulation/reviews/` に置き、計算動画を Fusion 組立動画の代わりにしません。

### Phase 5 — 独立レビュー

**担当**: Hardware Reviewer と必要な別視点の前提確認。
回路の固定引き継ぎを受け、全 checklist と実在する KiCad 検査で確認します。
Evidence ID 付き重大度を分類し、レビュー報告と共有 backlog への提案を返します。
最終判定は1つの `PASS` / `FAIL` / `CONDITIONAL` です。
`CRITICAL` / `HIGH` は Phase 4 へ戻し、修正・影響範囲を再評価します。
独立した走査は並列可でも、判定は直列です。

### Phase 6 — 検証

**担当**: 現段階では Lead と人間。将来は必要に応じ Test/Validation Engineer。
レビュー PASS（open CRITICAL なし）を入口に、bring-up procedure と該当する検証を使います。
実通電前は人間の承認が必要です。実測を traceability と推奨動作条件に照合し、
行を `Verified` または `Failed` にします。失敗は設計へ戻します。
剛体シミュレーションの判定は物理検証ではなく、SPICE は別の将来統合です。
独立テストは並列可、最終検証判定は直列です。

### Phase 7 — Design Complete ゲート

**担当**: Hardware Lead。[構成 §8](architecture.ja.md#8-design-complete-ゲート)の5条件すべてを確認し、
不足があれば該当段階へ戻します。電子回路・機械は同じ backlog と同じゲートです。
成功は人間へ報告し、組立の APPROVED 公開には同じリビジョンの独立受け入れも要求します。
早期 WIP や CI はゲート・実機許可を免除しません。

### Phase 8 — 電子回路から機械への引き継ぎ

**担当**: Mechanical Lead が抽出、Hardware Lead が分野間完成と不足調査を調整。
真の分野間トレードオフは Systems Engineer が評価します。
必要な物理 interface が特定されれば開始でき、Phase 7 は前提ではありません。
外形、穴、部品高さ、connector は最終値として扱う前に安定した一次入力が必要ですが、
それを解決する WIP 証拠の作成を待たせません。

`hardware/mechanical-interface.md` を実 KiCad または設計担当・人間の出典付き入力で埋め、
各欄を `CONFIRMED` / `ASSUMPTION` / `ESTIMATE` / `UNKNOWN` とします。
搭載・嵌合状態、全 board/sensor/driver/power、支持・絶縁・保持 harness を含めます。
必須欄に暫定値または具体的な UNKNOWN 調査担当・次の対応があれば WIP を進められますが、
不明点があるまま最終受け入れにはしません。
上流形状変更時は該当欄を再抽出します。Phases 5–7 と並行できます。

### Phase 9 — 機械設計

**担当**: 唯一の形状所有者 Mechanical Lead。
Phase 8 の引き継ぎから筐体、基板支持、connector access、高さ・内部余裕、
締結、壁、組立順、基本造形公差・製造性を設計します。
実行時確認したツールで形状・寸法表を出し、WIP 手順、部品・座標対応、
全搭載・各工程証拠、要求された Fusion native/video を自己点検して渡します。
可視化で形状や最終搭載姿勢を黙って変更しません。
初期阻害レビューは不足を明示した WIP でも可、最終受け入れは完全なパッケージが必要です。
interface が変われば Phase 8 へ戻します。形状状態は1つなので並列設計しません。

### Phase 10 — 独立機械レビュー

**担当**: Mechanical Reviewer。WIP 阻害確認か最終受け入れかを明示して証拠を受け取ります。
全反証 checklist、マニフェスト、搭載状態、各工程、必要な Fusion native storyboard と動画を独立検査します。
共有 backlog の `Source=mechanical-reviewer` とレビュー報告への提案を出します。
アニメーションを衝突・連続経路・支持材除去・強度・安全の証明にはしません。
単一判定に範囲と正確な source/artifact hash を記録します。
`CRITICAL` / `HIGH` は Phase 9 と再レビューへ戻し、WIP 判定を最終承認と呼びません。

### Phase 11 — ファームウェア初期立ち上げ

**担当**: Firmware Engineer、独立評価は Firmware Reviewer。
対象周辺機器のピン、peripheral instance、mode strap が回路で確定したら始めます。
Design Complete は前提ではありません。
回路文書から実契約を抽出し、未決定の MCU clock は先に直列で固定します。
メーカーの register-level 一次資料と必要な初期化順序を守り、
必要な opaque data は許される条件と attribution を守って使用します。
コード、Evidence ID 付き設計理由、自己点検、実際の compile 状態を引き継ぎます。

独立レビュアーが固定ソース・ビルドを評価し、指摘は
`firmware/<board>/<board>-firmware-review.md` に記録します。
`CRITICAL` / `HIGH` は実装者へ戻して再レビューします。
レビュー阻害を自己レビューで置き換えません。
回路の pin/interface が変われば該当 driver を更新します。
これはハードウェア Design Complete の追加条件ではなく、将来の実機 bring-up の準備です。
実装は入力確定後に他分野と並行可、独立判定と初回 flash の人間承認は別の直列段階です。

### Phase 12 — 電源構成

**担当**: Lead が複雑さに応じて起用した Power Engineer。
単純な単一レールでは省略し、Circuit Engineer が予算を維持します。
Phase 2 の実際の候補の電流・電圧・熱データから既存・追加負荷を集計し、
新レールや入力源が必要なら少なくとも2つの具体的構成案と得失を示します。
sequence/coupling を評価し、人間の構成判断を `hardware/power-architecture.md` に残し、
承認案の multi-rail budget を更新して回路担当へ渡します。
新たな部品調達は Component Engineer に戻します。
後続追加で余裕を超えれば電源回路を進める前に戻ります。
候補調査の既存並列を利用できても、別の無用な fan-out を増やさず、推奨と人間判断は直列です。

## 3. 対立とエスカレーション

各側が Evidence ID・要件 ID で立場を示し、Lead が一次資料と照合します。
資料不足や伝達誤りを解決したうえで、真の Electrical/Mechanical/Firmware トレードオフを
Systems Engineer に渡します。検証済み制約と未確認前提、変更コスト・リスク、
独立評価済み成果への影響、波及を比較します。
推奨は自己実行されず、構成・安全・事業・日程など人間に留保された判断は Chief Engineer に渡します。
解決は ECO・指摘に根拠とともに記録します。

## 4. 引き継ぎ

永続的 Source of Truth は Git 管理された設計・証拠ファイルです。
終了条件はチャットの言葉だけでなくファイルの具体的な状態です。
repository-local の guard は試行、入力・設定、出力ハッシュを保存しますが、ライブ監視・設計承認ではありません。
session SQL `todos` / `todo_deps` は計画用であり、共有実行の権威ではありません。
新 todo で完了済み・阻害済み仕事をやり直しません。

機械は必要に応じ Phase 4a → interface → design → WIP evidence → independent review →
共通ゲートへ進みます。firmware は実装 → independent firmware review の別経路、
power は candidate → proposal → human gate → power circuit と先行します。
組立の永続引き継ぎは[リビジョン manifest](assembly-evidence.ja.md)であり、「見た目は大丈夫」ではありません。
Simulation は独自の model/run manifest と実軌道を使い、組立用 `current.json` を作りません。

### 4.1 共有 ID の衝突

予防策は Lead による直列公開です。専門担当は提案を返し、兄弟ブランチで別々に正規 ID を確保しません。
既存 branch・別 clone の衝突は Git が clean merge でも発生します。復旧時は次を守ります。

1. `python3 tools/check_id_uniqueness.py` で早期検出します。
2. レビュー済み・参照が多い・閉じた記録など影響を比較し、どちらを維持するか判断します。
   他方は両 namespace の和集合で未使用の番号へ移します。機械的な「+1」や常に main 優先ではありません。
3. 定義行だけでなくリポジトリ全体の旧 ID 引用を更新します。
4. 移動した旧→新 ID と理由を専用 ECO に残します。
5. チェックを再実行します。

Git にまだ記録されていないメッセージ内予約は静的検索では見えません。
予約を永続的に公開し、Git の「次に空いている番号」は進行中の調整と照合するまで確定値にしません。
過去の実衝突と不完全な置換事例は[原本 §4.1](workflow.md#41-cross-branch-id-collision-resolution-shared-namespace-files)を参照します。

### 4.2 重要数値の古い引用

導出元を修正しても引用側が自動更新されるとは限りません。単一ブランチの編集でも起こります。
指摘・ECO を閉じる前に、旧数値の単位、範囲、丸め、別表記を含めて全体を検索し、
各引用を修正するか、当時値との比較であることを明記します。
何を検索してどこを修正したかを closing ECO に記録し、それから波及完了とします。
値の表記が多様なので汎用 grep だけで完了を保証する CI は追加しません。
過去の熱・回転・質量等の具体的事例は[原本 §4.2](workflow.md#42-stale-load-bearing-figure-propagation-cross-document-citations)に残し、
当時の open/resolved を現在の状態として再掲しません。

### 4.2.1 分野間 snapshot のずれ

interface ファイルは upstream の live query ではなく、一度抽出した snapshot です。
上流がその後変われば各分野が内部整合していても組立が成立しなくなります。
機械可読の上流がある場合は外形・穴などの必要構造値を再導出して直接比較します。
`tools/check_mechanical_pcb_sync.py` は対応する実 PCB と SCAD の寸法・穴配置を比較する例です。
全機械形状の受け入れではありません。
機械可読原本がない人間要件・仮定はこの方法では検査できず、§4.2 の調査と担当レビューを使います。

### 4.3 1行記録の監査

台帳では1物理行に日時と長い Notes が同居します。
期待する日付・語だけを grep すると、同じ変更で追加された根拠を見落とせます。
変更行の before/after 全文を読み、人間判断に触れる場合は原文を確認します。
未確認・取得不能と「承認が存在しない」を混同しません。

人間の記録は、一方的な revert より可逆的な blocking review を優先します。
`PENDING` / `NOT AI-approved` と書いて自分でマージする二重基準を避け、
人間を待つか、許される範囲の自身の権限と理由を正直に示します。
誤った公開指摘は同じ可視性で訂正します。
これは読み方・判断順序の規則であり、「全文を読んだか」を保証する新 CI・役割を作りません。
実例の全文は[原本 §4.3](workflow.md#43-audit-method-failure-on-single-line-records-pattern-grep-vs-whole-line-diff)に保存します。

## 5. 設計サイクルを始める

[make-circuit](commands/make-circuit.ja.md)の限定プロンプトを使います。
実在する起動方法と該当プロファイル・スキルを使い、同じ実行契約に従います。
