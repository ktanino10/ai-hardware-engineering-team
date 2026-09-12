# 3D 組立・部品ビューアー

[English](../visualization/assembly-viewer/README.md) | [日本語](assembly-viewer.ja.md) | [Pages ガイド](pages.ja.md)

既存の英語 UI で公開 Bench-IMU-01 部品を閲覧します。
HTML、ES module、CDN からの Three.js で動作し、Unity・native plugin・build は不要です。
HTTP で開く手順は [Pages ガイド](pages.ja.md)を参照してください。
旧 Unity Editor 版の export 阻害は原本の導入履歴で、現在の Unity 可用性の判断ではありません。

## 表示内容と操作

印刷部品は公開 STL 由来 OBJ、PCB は KiCad GLB→OBJ、
購入部品4種（bearing、motor、hub collar、flywheel）は出典寸法に基づく簡略 primitive、
ねじはおおよその位置の cylinder/head です。実物をすべて忠実に形状再現しているわけではありません。
ドラッグで orbit、scroll で zoom、部品クリックで名称・寸法・役割・出典と modal を開きます。

初期表示は assembled です。右上の **Explode View / Assemble View** は交互に1ラベルを表示し、
camera を現在の配置へ fit します。
assembled は実 mesh の測定高さで並べる contact stack で、
stand plate → bearing → base を主軸、guard を stand plate の高さ、
PCB/lid と motor/hub/wheel/cap を分岐として配置します。
2つの bay を水平に離す量は公開 source 変数に由来しますが、
mesh centre を用いる近似なので source の global frame の厳密再構築ではありません。

exploded は横一列です。測定幅と説明用 gap で配置し、
`assembly-data.js` の従来 `y` は位置ではなく順序キーとして使います。
なめらかな補間は表示効果で、物理的な挿入経路の証明ではありません。

## 部品 modal

sidebar と同じ説明に加え、repo-relative path を実 GitHub リンクにします。
5印刷部品は存在する front/side/top と drafting sheet を表示します。
購入4部品には専用図がなく、PCB は印刷部品図の対象外なので、
理由付き N/A と実 board render を使います。部品総数は PCB を含め10です。
単体3Dはすでにロードした geometry を使い、再 network fetch しません。

printed part は実 SCAD module と存在する projection script へ、
PCB は実 KiCad source へリンクします。motor/hub/wheel の共通 `reference_motor_flywheel()` は
参照用 stand-in で、購入部品の実設計ではありません。
bearing/motor の購入 URL は metadata 由来です。
hub/wheel の vendor/MPN や Evidence ID がなければ、その欠落を明示して創作しません。

## 限界と保守

gap は説明用です。原本の旧 vertical-spacing 注記は旧表示履歴で、
現行 explode は横一列です。購入部品の stator/winding など詳細形状はありません。
ねじ位置は source と mm 単位で検査したものではありません。
assembled は単軸 contact stack なので、蓋・cap が内容物を囲んで下がる形を正確に再現せず、
bay offset にも中心仮定があります。全搭載・干渉・安全の受け入れではありません。

mini viewer は `Object3D#clone(true)` ではなく `cloneForMiniViewer()` で
transform と geometry/material を複製・共有し、循環参照を持つ `userData.rootWrapper` を避けます。
原本の不具合履歴を消したり、翻訳のために clone logic を変えたりしません。

Pages は `visualization/` だけを配信するため、外部 folder は
`raw.githubusercontent.com` / `github.com` の URL を使います。
`../../hardware/...` のようなローカルだけで通るリンクを Pages に追加しません。
motor の Evidence ID link は metadata の Used for Evidence IDs 由来で、
既存 assembly-data の BOM source field が以前から同じ ID を持っていたとは主張しません。

これは説明用のビューアーです。WIP/APPROVED 組立パッケージの
Fusion native storyboard、全搭載・各工程証拠、独立受け入れを代替しません。
data、mesh、配置、判定をこの日本語説明から変更しません。
