# データシートのメタデータ方針

[English](../datasheets/README.md) | [日本語](datasheets.ja.md) | [ガイド一覧](README.ja.md)

**公開リポジトリにメーカーの著作権付きデータシート本体（PDF 等）をコミットしません。**
`datasheets/` 以外に置いても同じです。`.gitignore` は補助であり、最初から登録しないことが原則です。

## 保存する情報

資料1つにつき、次の名前でメタデータを記録します。

```text
datasheets/<manufacturer>_<part-number>_<revision>.md
```

例: `datasheets/stmicroelectronics_stm32f103c8t6_rev14.md`。
共通のフィールド名は機械・人間の参照を保つため英語のままです。

```markdown
# <Manufacturer> <Part Number> Datasheet — Rev <revision>

- **Manufacturer**: <name>
- **Part Number**: <part number>
- **Datasheet Title**: <exact title as printed on the document>
- **Revision / Version**: <e.g. Rev 14>
- **Publication Date**: <date printed on the document, or UNKNOWN>
- **Official URL**: <manufacturer's own URL for this datasheet>
- **Retrieved Date**: <date this was fetched/reviewed>
- **Local cache note**: <cached locally, not committed>
- **Used for Evidence IDs**: <IDs in datasheets/evidence-log.md>
```

Publication Date が確認できなければ `UNKNOWN` とします。
local cache は存在・非コミットの説明だけにし、個人の disk path を repo path のように示しません。
Evidence ID の利用一覧はログと手動で整合させます。

## 理由

著作物を再配布せず、公式 URL から人間が同じ版・節・表・ページを確認できるようにします。
`Parameter | Min | Typ | Max | Unit | Source` の制約表は必要最小限の事実抽出で、
原文や図の大量複製ではありません。これは実務上の方針で法的意見ではなく、
正式な法的判断は所有者・法務に確認します。

## 引用

ファイル名・ページを毎回書き直す代わりに Evidence ID を使います。

```text
[Source: DS-IMU-003]
```

完全な引用は共通の [evidence-log.md](../datasheets/evidence-log.md) で確認します。
正規 ID の確保・公開は[実行契約](work-execution.ja.md)の直列公開に従います。
詳細は[構成 §6](architecture.ja.md#6-証拠モデル)と
[対象パスの共通指示](../.github/instructions/datasheets.instructions.md)を参照してください。
