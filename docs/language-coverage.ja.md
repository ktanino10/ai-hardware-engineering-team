# 公開文章の言語対応範囲

[English](language-coverage.md) | [日本語](language-coverage.ja.md) | [ガイド一覧](README.ja.md)

**公開 source/configuration 基準**:
`f259608bd6d4e673393bb6ed4924ea7dc892cb6d`。
入力はこの公開 checkout だけです。私有 branch、raw endpoint、素材束、履歴を取り込みません。
公開文中にすでにある参照は維持しますが、追加の私有設計情報を取得するために辿っていません。

後続の[Rev5限定公開](rev5-public-release/README.md)は別途明示承認された出力から
2件のREADMEを追加しています。[Pages日本語ガイド](pages.ja.md)に実行方法、
生成元・再現性の限界、個別の公開保留を記載しました。上の基準は元の言語対応作業を
指し、後続の公開取込みを同じ入力だったと主張するものではありません。

## 「対応済み」の意味

[機械可読対応表](language-coverage.json)は**既存26の読者入口**について
source、English、日本語、版の種類を1行ずつ記録します。
root README/AGENTS、active framework guides、各分野の README・手順が対象です。
regression は README の一覧漏れと未分類 Markdown を検出します。
後続のRev5ビューアー・限定公開のREADME 2件も、現在の対応表に明示登録しています。

`translation` は操作説明を別言語で提供し、command grammar と境界を保持するものです。
`reading-edition` は現行の説明・手順を読者向けに編集し、
長い経緯、設計数値表、個々の部品判断、元 review receipt を正本へリンクするものです。
**読者向け版は source 全文の逐語訳ではありません。**
未翻訳の履歴・工学記録を「すべて翻訳済み」と表示しません。

root と[分野別入口](README.ja.md#各分野の入口と操作手順)で、変更しない source-bound ファイルにも
EN/JA の導線を提供します。日本語の simulator/startup は、
英語見出しだけではなく実行・解釈・制限を含む英語版を用意しています。

## 対応表

| 対象 | 扱い |
|---|---|
| README / 参加者入口 | EN/JA 分離、相互リンク、全役割と既存コマンド |
| 構成・開発フロー | 英語正本の path/heading は導線以外維持。日本語は現行規則、過去事件は原本参照 |
| 実行契約・開始 prompt | 日本語の契約説明、JSON/CLI、限定 prompt。機械実行の正本は不変 |
| 組立契約 | 日本語で fields、状態、承認、coverage、失効、実行方法。schema/template は共通 |
| simulation 契約・評価 | 日本語で model/evidence/gate と指標。数値原本は共通 |
| datasheets | 日本語方針と全 metadata template。資料本体は追加しない |
| firmware 分野・基板 | 日本語の pin/command/telemetry/build 説明。古い余裕値を現在の安全値にしない |
| 回路・PCB・fab | EN/JA 読者ガイド、render/export command、比較方法、独立・人間ゲート。個々の旧設計判断は共通 |
| 機械・STL・図面 | EN/JA 導線、日本語 STL/2D 全 command と drafting/Blender pipeline。旧 demo の古さと座標差を開示 |
| simulator/startup | setup/run/replay/suite/verify、case 区分、始動・会計の注意を含む英語版 |
| Blender / ROOT | 日本語の command、native 検査、encoding/交換、操作別の tool 限界 |
| 3 viewer の説明 | 日本語の操作、導出、解析、再生成、限界。長い実装履歴は共通 |
| Pages landing | 別 EN/JA static page と共通 CSS。新 build/deploy 機構なし |
| dashboard UI | 既存 EN/JA と data 分離を維持。明示言語 URL と言語に沿う Back を追加 |
| 回路・組立 UI | 既存英語 UI・data のまま。日本語の紹介が runtime UI 全翻訳だとは主張しない |
| Rev5 v2・限定公開 | 日本語UI。Pagesの日本語読者向け版に操作・確認コマンド、第一者成果物の公開根拠、履歴からの再生成不可、ソフトウェアの個別保留を記載。詳細な出所・hashは原記録を維持 |

## 意図的に共通とする資料

残る tracked Markdown は対応表の明示 path/prefix で分類します。

- `.github/`: agent、skill、path 別 instruction、prompt、PR template は機械方針の正本。
  日本語説明を別の採用設定にしません。
- `requirements/`、`bom/`、`datasheets/`、各分野の設計・review、`validation/`:
  設計値、ID、判断、FMEA、ECO、物理 bring-up・組立手順、hash-bound 記録を共通にします。
  **安全に関わる実機手順そのものを新しく翻訳・再承認したわけではありません。**
  読者ガイドはその正確な決定を置き換えず原本へつなぎます。
- `docs/architecture-evolution.md` と `docs/reference-cases/`:
  歴史・出典限定の学習記録を原言語のまま保持し、現在の方針へ無断変換しません。
- code、schema、CAD、BOM CSV、binary/media、data、軌道、manifest は表示言語と独立した共通資産です。
  対応表の shared runtime paths はこの変更で更新しません。

元の分野 README は、言語 switch の追加だけで工学 provenance を失効させないよう元のまま残します。
対応する説明版を `docs/` に配置し、両言語 index を入口とします。

## 保守と確認

source と影響する説明版を一緒に整合させ、現行規則と日付付き過去観測を区別します。
ID、単位、command option、状態語、人間の引用を変えません。
不一致は文書の不具合であり、新たな工学判断ではありません。

```sh
PYTHONPATH=tools python3 -m unittest discover -s tools/tests -p 'test_*workflow*.py'
```

既存 workflow test に inventory、Markdown link/anchor、Pages の対、dashboard 言語動作を含めます。
dashboard は Node の標準 VM/assert で確認し、Node 不在は明示 skip します。
package 追加・live fetch は不要です。意味の完全一致、実機、native CAD を認定する検査ではありません。
公開・deploy・独立受け入れはローカル文書チェックと別です。
