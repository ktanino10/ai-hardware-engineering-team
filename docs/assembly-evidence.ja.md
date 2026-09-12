# 組立証拠の契約

[English](assembly-evidence.md) | [日本語](assembly-evidence.ja.md) | [ガイド一覧](README.ja.md)

複数部品の組立に使う、リビジョン付き引き継ぎ契約の日本語版です。
新しい設計分野でも Design Complete の5条件の代替でもありません。
早期に組立順序・干渉の証拠を検査可能にし、承認後までアニメーションを先送りしたり、
PCB の単一寸法チェックを統合組立レビューと同一視したりしないための契約です。

剛体計算は別の[シミュレーション契約](simulation.ja.md)です。
ハッシュ・版・失効の考え方は共通でも、計算動画は Fusion の native storyboard・組立動画を代替せず、
数値受け入れは物理・組立承認を与えません。

## 2つの状態と1人の形状担当

| 状態 | 必要な行動 | 許可しないこと |
|---|---|---|
| `WIP - NOT ASSEMBLY READY` | interface・筐体設計中から計画、形状証拠、動画を作り、不足・近似を表示して早期阻害レビューを受ける。入力変更後は更新する | WIP 表示だけで未解決を解消扱いしない。完成・製造・通電・安全・公開承認ではない |
| `APPROVED assembly documentation` | 全証拠を完成し、同一リビジョンを Mechanical Reviewer が独立受け入れ。Design Complete と名指しの安全判断を参照し、手順・native・動画を一緒に公開 | 製造・通電・flash・回転体操作の許可ではない。個別の実機ゲートは別途必要 |

WIP 表示は manifest だけでなく手順、storyboard の見出し・注記、出力図・動画にも付けます。
不完全な証拠でも早期阻害レビューは行えますが、最終受け入れとは言えません。
APPROVED は必須 interface と証拠が解決・レビュー済みであることを要求し、
従来の人間のリスク判断を正確に示します。新たな免責を与えません。

機械形状は Mechanical Lead、board layout は PCB Engineer が所有します。
可視化中に寸法、最終搭載姿勢、嵌合関係、組立順を都合よく変更しません。
欠陥は Lead 経由で出典担当へ戻し、修正後に該当証拠を再生成・独立再レビューします。

## 担当と不足の解決

Hardware Lead は条件付き報告の収集だけでなく、**全体の interface 完成**を調整します。
電気・connector・電源は Circuit、搭載 PCB・穴・配置は PCB、
形状・保持・挿入経路は Mechanical、製造依存の嵌合・支持・構造条件は Manufacturing に割り当てます。
Mechanical Lead が interface を記入し、真の技術境界対立は Systems Engineer が評価します。
Mechanical Reviewer が独立受け入れを判断します。

Phase 4a の PCB WIP 準備は Design Complete 前に出典付き envelope・暫定形状・不明点を提供できます。
これは組立証拠と基板形状の循環依存を解くためであり、全配線・製造・実機操作は許可しません。
`UNKNOWN` は正直な状態ですが、完成した成果物の代わりではありません。
出典を調査するか具体的な代替案を示し、調査可能な事実を無期限の「人間の承認待ち」にしません。
資料欠落は推測せず、構成・主要部品・BOM・安全の変更は意味のある選択肢を示して人間の判断を得ます。

## 必須成果物

[manifest template](templates/assembly-manifest.json)から
`hardware/mechanical/assembly-evidence/<assembly>/<revision>/manifest.json` を作り、
[current template](templates/assembly-current.json)で
`hardware/mechanical/assembly-evidence/<assembly>/current.json` に現行版を登録します。
古い manifest は変更せず保存します。テンプレートは不完全な雛形で、過去版の証拠ではありません。
実ファイルの配置は既存成果物領域でも構いませんが、正確なパス・ハッシュを列挙します。

| キー | 受け入れに必要な内容 |
|---|---|
| `tool_preflight` | 日付、操作ごとの可用性、公式資料、版・接続、実行経路、限界、正確な引き継ぎ |
| `component_map` | 要件・BOM・interface 由来の全 inventory。安定 part/instance ID → Fusion component/occurrence → source/hash、単位、軸、搭載変換 |
| `assembly_instructions` | 部品・締結具・工具、挿入・着座・締結・接続の番号付き実順序、保持と工具進入、取り外し・整備、storyboard 対応 stage ID、出典/配分/UNKNOWN、安全停止点 |
| `installed_assembly` | 全 inventory の搭載状態と測定、版、公差、未解決事項。裸 PCB 矩形や見栄えのよい図だけでは不可 |
| `assembly_stages` | 挿入・着座・締結・接続・取り外し各段階の移動物・固定物、治具・仮保持、工具・配線 access、経路方法、測定、sample と限界 |
| `drawings` | 読める組立・部品別の正投影図、必要な全体・分解図、寸法出典、版・WIP 表示。実ファイルをすべて列挙 |
| `native_animation` | 実際の Fusion `.f3d` / `.f3z`、名前付き物理部品と保存 storyboard。保存物を開き直し参照と持続性を検査 |
| `animation_video` | Fusion Animation から公開した再生可能な動画。範囲、storyboard、時間、形式、再生、provenance。別レンダーの改名・静止画代用は不可 |
| `independent_review` | Mechanical Reviewer の日付付き報告。早期阻害か最終受け入れか、入力版、検査 hash、範囲・限界・判定 |

全搭載状態と関係する**各工程の両方**で、両面の部品 envelope、嵌合 connector、
支持・締結・絶縁、全 sensor の位置・方向、daughterboard、driver、power、
motor bell・shaft・hub・wheel と回転包絡、bearing の着座、ねじ頭・nut・washer・insert と工具、
保持 harness・strain relief・曲げ余裕・panel 通過、挿入・取り外し・仮支持・支持材除去を扱います。

出典寸法、理由付き `ASSUMPTION` / `ESTIMATE` の設計配分、`UNKNOWN` を区別します。
保守的な簡略 envelope は省略箇所を示し、欠けた嵌合・支持設計を隠しません。
一体造形、bearing 接触、確認済み process interference と、不許可な別部品の重なりを区別し、
接触ペア、目的、適格性を記録します。「接触するものだから」で全干渉を免除しません。

アニメーションは衝突解析ではありません。連続経路、支持材除去、強度、安全、機能を証明しません。
離散検査は姿勢・間隔、公差、モデル忠実度、未検査区間を記録し、連続衝突証明と呼びません。
分解位置から home への補間は表示手法であり、組み立て可能な経路とは限りません。

## Manifest schema version 1

機械可読キーは翻訳しません。

- `schema_version: 1`、`assembly`、`revision`、`state: WIP | APPROVED`、
  `author`、完全な Git hash の `source_revision`。ディレクトリ名も一致させます。
- `sources` は実際に使った正規入力の非空 `{path, sha256}` リスト。
  先に source をコミットし、hash はその commit と現在 checkout の両方に一致させます。
- `retired_sources` は意図的に除去・置換したファイルの `{path, sha256, source_revision, reason}`。
  元 commit に一致するファイルがあり現在パスは不存在でなければなりません。古い manifest は削除しません。
- `animation` の既定は `{"workflow": "FUSION", "alternative_approval": null}`。
- `artifacts` は上表の9キーを正確に持ち、各項目に `owner` と状態を記録します。
- WIP は `approval: null`。APPROVED は下記の承認 object が必要です。

```json
{
  "status": "PRESENT",
  "owner": "mechanical-lead:<session>",
  "source_revision": "<same full source commit>",
  "files": [{"path": "<repository-relative file>", "sha256": "<64 hex digits>"}]
}
```

`PRESENT` はファイルの存在を意味し、完全性・独立受け入れではありません。
部分報告は不足を明記して WIP のままにします。
Fusion の native/video は `"producer": "Autodesk Fusion Animation"` も要求しますが、
文字列や拡張子だけを信じず実物の provenance を検査します。

```json
{
  "status": "BLOCKED",
  "owner": "mechanical-lead:<session>",
  "reason": "<specific missing source or capability, with investigation result>",
  "next_action": "<smallest actionable owner task or human handoff>"
}
```

`PENDING` は未実施の作業に同じフィールドを使い、どちらも `files` を提出済みと主張できません。
Fusion export が阻害されても別証拠の準備を止めず、スクリプト準備を native 成果物と呼びません。
人間が明示的に認めた代替のみ `APPROVED_ALTERNATIVE` とでき、
`alternative_approval` に `name`、ISO `date`、`rationale`、実 `workflow`、
判断位置の `record: {path, sha256, section}` が必要です。
producer はその workflow と一致させ、native と video の提出自体は免除しません。

APPROVED は9成果物すべて PRESENT にし、`approval` に次を含めます。

- `name`: author と異なる独立レビュアーで `independent_review.owner` と一致。
  `role: mechanical-reviewer`、ISO `date`、`rationale`、`verdict: PASS`、同じ `source_revision`。
- `evidence_sha256`: 最終レビュー前の完全な WIP package に対して checker が出す fingerprint。
  assembly/revision/author、入力参照、retirement、animation、review 以外の artifacts を
  sorted-key compact JSON と SHA-256 で束ねます。review 自身の除外で循環 hash を避けます。
  形状不変でも検査対象の出力再生成は受け入れを無効化します。
- `record: {path, sha256, section}`: `independent_review` の実ファイル内の判断。
- `design_complete: {path, sha256, section}`: 該当版の本当のゲート判断。
- `safety_decisions: {path, sha256, section}`: 該当する人間の構成・部品・BOM・安全判断と、
  PCB/機械製造、初回通電、初回 flash など継続して保留する実機ゲート。

レビュアーはファイルの存在だけでなく、元の判断と Design Complete 全5条件を確認します。
CRITICAL は accepted-risk にできず、既存 HIGH の判断は変わった構成へ自動延長しません。
共有 ID は Lead の直列公開で確保します。

## 自動チェックと実行

既存 CI は各 PR で stdlib unittest と `tools/check_assembly_evidence.py` を実行します。
新たな CAD・plugin は導入しません。PR 差分は merge-base を使い、rename で履歴削除を隠せないように扱います。
`hardware/**`、`bom/**`、`visualization/assembly-viewer/**` の変更には更新 manifest と
各ファイルの source/artifact/retirement 対応が必要です。
SCAD、KiCad、library table、BOM、interface は出力に偽装せず source として登録します。

current pointer が live manifest を選びます。参照された source、出力、独立報告、承認記録の変更は
物理 prefix 外でも検査を起動します。パスは全要素に symlink のない正規リポジトリ相対パスが必要で、
別名で変更を隠して N/A にしません。
pointer/manifest は削除せず新版へ移し、既存の inactive history は編集しません。
同じ PR 内で新たに保存した旧 snapshot も、その版ディレクトリの hash を保つ必要があります。
live inputs の未対応変更を履歴扱いで隠せず、current 登録省略でも免除されません。

欠落 manifest、未対応物理変更、不正状態、古い hash、根拠のない ready 主張は失敗します。
無関係な docs、agent、skill、policy/checker のみは明示的 `NOT APPLICABLE` ですが、
regression は実行します。hardware gate や branch protection は変わらず、
差分取得不能を自動免除にはしません。

```sh
python3 tools/check_assembly_evidence.py --manifest hardware/mechanical/assembly-evidence/<assembly>/<revision>/manifest.json
python3 tools/check_assembly_evidence.py --manifest hardware/mechanical/assembly-evidence/<assembly>/<revision>/manifest.json --require-approved
PYTHONPATH=tools python3 -m unittest discover -s tools/tests -p 'test_assembly_evidence.py'
```

構造が正しい WIP は `NOT ASSEMBLY READY` と全 PENDING/BLOCKED を表示して成功できますが、
`--require-approved` は拒否します。hash、拡張子、producer は真偽・形状・再生・安全の証明ではなく、
独立証拠レビューが必要です。この翻訳は実組立・動画・承認・過去安全証拠を生成しません。
