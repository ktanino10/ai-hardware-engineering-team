# プロジェクトダッシュボード

[English](../visualization/dashboard/README.md) | [日本語](dashboard.ja.md) | [Pages ガイド](pages.ja.md)

Chief Engineer 向けに、人間の判断待ち、工程、品質、活動、電気・機械の概要を読むページです。
**読み取り専用で、承認・台帳更新をしません。**
この版は現行の操作・解析規則・限界を説明し、開発当時の件数・全検証履歴は英語原本に残します。

## 開く・更新する・言語を切り替える

[日本語で開く](https://ktanino10.github.io/ai-hardware-engineering-team/dashboard/index.html?lang=ja)／
[English](https://ktanino10.github.io/ai-hardware-engineering-team/dashboard/index.html?lang=en)。
ローカル表示は [Pages 手順](pages.ja.md)を使います。
有効な URL の `lang` を初期値として優先し、なければ保存済み `dashboardLang`、その次に英語です。
EN/JA ボタンは保存済み表示データを再描画し、再取得はしません。
Refresh は fetch・parse・render を再実行します。Back は表示中の言語の紹介へ戻ります。

## なぜ static viewer と異なるか

回路・組立は人手で生成・レビューした `circuit-data.js` / `assembly-data.js` を使います。
dashboard は変化する要件・指摘・BOM 等を public `main` から毎回取得します。
`dashboard-live.js` が公開 raw Markdown を読み、
`dashboard-render.js` が section 別に描画し、失敗部分は source link 付き fallback にします。
事前生成済みデータを「live」と表示するものではありません。

raw content と directory listing は別経路です。
agent、skill、prompt、instruction、workflow の5 directory を Contents API で列挙し、
その後の個別 frontmatter・workflow・CODEOWNERS は raw 経路で読みます。
Contents API は認証なしの rate limit を受け、該当 metric が失敗しても他 section を空にしません。
原本にある取得 byte 数・件数は当時値で、今の性能測定ではありません。
CDN の cache があるため「毎回 fetch」は即時最新の保証でもありません。

## 8つの表示

| 表示 | 読み方 |
|---|---|
| Pending Human Decisions | Chief Engineer の Approval 行の Date が厳密に PENDING、OPEN CRITICAL/HIGH、限定した要件の未確認質問 signal |
| Phase / Process Pipeline | `docs/workflow.md` の `### Phase N — Name` から抽出。単一の「現在の版/工程」を捏造せず各文書の Status をそのまま表示 |
| Findings & Quality | severity × status、ECO/finding/Evidence の件数、ゲート条件1–3の live 計算。FMEA 等の条件4–5はリンクだけ |
| Recent Activity | ECO の文書順末尾12行 |
| Electrical & Mechanical | 既存 viewer へのリンク、interface の board outline・mounting-hole 数 |
| Requirements | Must/Should/Could/Won't と Rev tag 別の数 |
| AI Agent Organization | 実 agent frontmatter と関係行。既知 group は curated、未知 role は Other に表示 |
| GitHub Feature Map | live の file 数・workflow trigger・CODEOWNERS と、日付付き static 設定事実を分離 |

何も blocking signal がない表示も、必須5条件の完全な受け入れや実機許可ではありません。

## live と static

認証付きで過去に確認した branch protection、security、Dependabot、CodeQL、Pages 設定は、
`STATIC_FACTS_CONFIRMED_DATE` の**固定日付**と値を表示します。
毎回 `new Date()` を付けて「今日確認した」と見せません。
設定が変われば担当が値・日付を実確認して更新し、その場で読む人には実 Settings へのリンクを示します。
PR/Issue の design convention は認証制限とは違う理由の static note として区別します。
この言語対応では設定の再確認・変更を行いません。

## 翻訳するもの・しないもの

dashboard 自身の title、heading、button、template sentence、badge、
label、footnote、error fallback は `dashboard-i18n.js` の `{en, ja}` 辞書で翻訳します。
parameterized function は語順に対応し、`t` / `setLang` / `applyStaticChrome` で適用します。
回路・組立の UI は既存英語のままで、紹介文・ガイドだけに日本語を加えます。

次は翻訳しません。

- source から取得した decision、finding title、ECO、Status、phase、
  agent role/description/relationship、workflow name/trigger。
- `CRITICAL` / `HIGH` / `MEDIUM` / `LOW`、
  `OPEN` / `RESOLVED` / `ACCEPTED-RISK`、
  `Must` / `Should` / `Could` / `Won't`。
- ID、path、Rev/Phase の識別子、GitHub product/feature 名、
  設定された required-check の正確な文字列。

これらは定義済みの契約・出典データです。訳語から元記録と異なる意味を作らないために原文を維持します。

## parse 規則

共通 `extractAllTables` は column index の決め打ちではなく実 header 名で表を識別します。
直近の意味のある heading へ帰属させ、途中の空行・malformed row は skip、
次 heading / EOF で表を終えます。独立した component Approval 表も section 別に扱います。

- **承認**: Chief Engineer の Date cell が大文字小文字を無視した厳密 `PENDING` の場合だけ。
  他 cell がその語に言及しているだけでは対象にしません。
- **指摘**: `ISS-` / `MISS-` ID の行と、厳密な Severity/Status を数えます。
  長い Notes 等は表示用に解析せず、文中の偶然の状態語を count しません。
  一部 source の code span 内 `|` は利用 column より後という原本の制約があります。
- **traceability**: bold を除去した cell の先頭で Verified/Pending/Waived/Failed を判定します。
  文中の「pending physical build」等で bucket を変えません。
- **priority**: Won't → Must → Should → Could の順で、昇格説明の Should を誤採用しません。
- **要件質問**: `## <N><letter>. ... (new, pending confirmation)` に対し、
  同じ番号の後続 letter section があれば抑制します。後続がないことも確実な未解決の証明ではなく soft signal です。
- **frontmatter / YAML**: 当時の実ファイル形状に合わせた line parser で、完全な YAML library ではありません。
  省略可能 field を許し、workflow は無 indent の top-level `name:` を読みます。
  source が block scalar 等へ変われば別途対応が必要です。

shape 不一致は section 単位の `{ok:false, error}` です。
件数は全履歴を含むため特定 revision の指摘・traceability だけとは限りません。
各文書の Rev は別々の意味を持ち、1つの全体カウンターに統合しません。

## 限界

UI が日本語でもデータは原文です。curated grouping は新 role を正しい分野へ自動分類しません。
認証なし API rate limit、CDN cache、手書き Markdown の形状変化、部分ゲート表示の限界があります。
static facts は日付付きの過去確認、parse は best-effort で、
エラー時は原本を読むことが必要です。
feature branch の preview でも fetch は public main で、未マージのローカル差分ではありません。
