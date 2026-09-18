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
