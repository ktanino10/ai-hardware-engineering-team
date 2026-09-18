# 公開ビューアーの使い方

[English](pages.md) | [日本語](pages.ja.md) | [ガイド一覧](README.ja.md)

[日本語の紹介](https://ktanino10.github.io/ai-hardware-engineering-team/index.ja.html)または
[英語の紹介](https://ktanino10.github.io/ai-hardware-engineering-team/)から開きます。
紹介文を分けても、ビューアーと設計データは共通です。

## ローカルで開く

リポジトリのルートから実行します。

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory visualization
```

`http://127.0.0.1:8765/` または `http://127.0.0.1:8765/index.ja.html` を開き、
Ctrl+C で終了します。ビルドは不要です。組立ビューアーの ES module・モデル読み込みには
`file://` より HTTP を使ってください。Three.js は既存 CDN、dashboard は公開 GitHub にアクセスするため、
完全オフライン動作を保証しません。

## 現在の Rev5 WIP 参照図

[全体モデル v2](https://ktanino10.github.io/ai-hardware-engineering-team/rev5-full-assembly-v2/index.html)は、
2026-09-15時点の名目メッシュ399個を固定した日本語UIです。分解量、再生・停止・リセット、
透過線画、三角形に基づくホバー、全IDのSVG参考三面図を利用できます。
このv2単体は依存ファイルを同梱しており、`file://`でもオフライン動作します。
[操作ガイド](../visualization/rev5-full-assembly-v2/README.md)と
[公開範囲・保留項目](rev5-public-release/README.md)を参照してください。

**WIP / NOT ASSEMBLY READY、REF / NOT FOR FABRICATION**です。
寸法は設置軸のメッシュ外接寸法、動きは表示専用です。公差付き製造図、組立経路の成立、
物理シミュレーション、完成した購入部品BOMを意味しません。後日の形状・電子系は混在させていません。
以下のベンチ例は過去の成果物であり、ダッシュボードも現在のRev5の完成を認定しません。

分解量は0〜100%、停止で正確に0%へ戻ります。再生・一時停止とカメラ自動旋回は
表示専用で、非表示時は停止し、動きを減らす設定では連続再生を無効にします。
ホバーは可視三角形の最前面、クリック／タップは選択固定です。ID検索でも選択でき、
透過中に奥の部品を選ぶ場合はグループ非表示または単独表示を使います。
参考三面図は元の設置姿勢から投影し、分解移動、公差、材質、工程、解析的穴径、
隠線除去、印刷縮尺の保証を含みません。

任意のソフトウェア確認にはNode22以上、ブラウザー確認には既存のChrome/Chromiumを使います。
リポジトリのルートから実行し、証拠用フォルダーは毎回新しいものを指定します。

```sh
node --test visualization/rev5-full-assembly-v2/features_test.mjs
node visualization/rev5-full-assembly-v2/browser_test.mjs \
  --evidence-dir .agent-work/rev5-browser-local
```

macOSの標準Chrome配置以外は `--browser /path/to/existing/chrome` を追加します。
公開先の確認には `--url` で完全な `index.html` URLを指定します。
全12実行ファイルのHTTP hashをローカル公開版と比較してから、GPU描画、操作、ホバー、
399件のSVG、実ダウンロードを検査します。他アプリや既存ブラウザープロファイルは操作しません。

### Rev5限定公開の範囲と生成元

公開内容は利用者自身のプロジェクトコードと、Python/OpenSCADで生成した名目・参照形状です。
モーター・ホイール・機器・PCB部品は独自のプリミティブや外形参照であり、
メーカーCAD/PDF本体やアップロード画像は含みません。元STLと全399形状の座標列を
照合し、形状は変更していません。新しいライセンスやメーカーの転載許諾は作っていません。
出所・hashの詳細は[限定公開記録](rev5-public-release/README.md)と
[manifest](rev5-public-release/manifest.json)を正本として参照します。

実行は公開ファイルだけで可能ですが、元のCAD生成器・STL入力・履歴依存のpacker/testは
未公開です。**この公開版だけから過去のネイティブ形状を再生成することはできません。**
私有履歴、SDK、flash binary、ユーザー画像、私有受領記録を補って見かけ上成功にしません。

| 対象 | 今回の扱い・残る条件 |
|---|---|
| v2 viewer | 12実行ファイルと任意のテスト2本。全体の閲覧を公開するが、完成設計・発注BOMではない |
| C1 readiness | 状態要約のみ。10正確候補・製品UNKNOWN要件2・23gap・103出典観測、採用0。数量・用途UNKNOWN。封印された入力に公開対象外の私有電源履歴があり、実行版は別の公開可能な入力一式とレビューが必要 |
| synthetic IMU | CLIは保留。独立レビューとestimator/helper/fixtureの最小依存一式が必要。synthetic gyro不一致の報告のみで、健全性判定・自動除外・制御ではない |
| N8R8評価 | profile/code/buildは保留。独立レビュー、測定・pin・vendor依存と通知が必要。NOT_FOR_FLASH、測定subsetのみ。全Rev5の35/36/37との競合は未解消 |
| 過去のBlender/FreeCAD | geometry epochを混ぜず保留。native binaryやeditor実行は含めない |

全成果物の公開完了ではありません。必須CI後の通常マージとPages deploy成功は別に確認し、
実URLでの描画・操作を検査します。戻す場合も通常のreview付きrevertと同じ必須チェック・deployを使います。
NO-GO / 3C8H / REQ409 / strict-pro / 39UNKNOWN、P1/C1/D1、sidecar/ICD/control、
original44 = **2 closed / 42 unfinished**、**NOT_FOR_FLASH**を維持し、
製造・組立・通電・書込み・回転の許可は与えません。

## 回路ビューアー

UI は英語です。電源配分、実装済みの開ループ動作、**NOT IMPLEMENTED** の閉ループ構想を切り替えます。
部品・配線をクリックすると役割、net、出典が開きます。流れる点は説明で、電流の実測ではありません。
実配線図は schematic PDF を見てください。ブロック図の経路・多点 net は読みやすく省略しています。
[英語保守ガイド](../visualization/circuit-viewer/README.md)／[日本語版](circuit-viewer.ja.md)に、
生成方法と PDF 再生成の正確なコマンドがあります。source の変更は自動反映されません。

## 組立ビューアー

ドラッグで回転、スクロールで拡大し、**Explode View / Assemble View** で表示を切り替えます。
部品クリックで説明、出典、存在する2D図面、単体3Dビューを開きます。
存在しない図面や vendor 情報は N/A と表示し、補作しません。

UI は英語です。出典由来 OBJ と簡略購入部品を使いますが、搭載表示は contact-stack 型の説明配置で、
正確な global 座標再構成ではありません。蓋・cap の入れ子、ねじ位置、挿入経路は保証しません。
実組立受け入れでも Fusion Animation でもありません。
[英語保守ガイド](../visualization/assembly-viewer/README.md)／[日本語読者向け版](assembly-viewer.ja.md)を参照してください。

## ダッシュボード

[日本語](https://ktanino10.github.io/ai-hardware-engineering-team/dashboard/index.html?lang=ja)／
[English](https://ktanino10.github.io/ai-hardware-engineering-team/dashboard/index.html?lang=en)で開けます。
`?lang=en|ja` は初期 UI 言語を指定し、有効な指定がなければ保存済み `dashboardLang`、次に英語を使います。
EN/JA ボタンで表示言語、Refresh でデータを更新します。言語切り替えだけでは再取得しません。
Back は表示中の言語へ戻ります。保存領域が使えなくても明示的な言語リンクは機能します。

タイトル、ボタン、説明文、エラー表示を翻訳します。
取得した設計本文、部品判断、指摘、ECO、phase 名、agent 説明、workflow 名、
ID、パス、重大度・状態・優先度語、設定された GitHub 機能名は原文のままです。
翻訳された別の Source of Truth を作らないための境界です。

feature branch のプレビューでも読むのは公開 **main** です。未マージのローカル設計変更は表示しません。
CDN cache と Markdown の best-effort 解析には遅延・制限があり、エラーから原本へ移れます。
日付付きの security / Pages 設定は過去観測で、毎回の認証付き再確認ではありません。
各文書の独自 revision を1つのプロジェクト版へまとめません。
ゲート表示は部分的な読み取り専用表示で、製造・通電・flash を許可しません。

詳細: [English](../visualization/dashboard/README.md)／[日本語](dashboard.ja.md)。

## 公開と変更範囲

既存 Pages workflow は設定済み main trigger で **`visualization/` だけ**を公開します。
そのため Pages から docs へは GitHub の絶対 URL を使い、壊れる `../../docs/` を使いません。
draft PR を開いただけでは deploy されません。公開状態は別に確認します。

言語対応は共有 viewer data、モデル、軌道、製造ファイル、live-fetch 設定、
レビュー記録、承認ゲートを変更しません。[全対応表](language-coverage.ja.md)も参照してください。
