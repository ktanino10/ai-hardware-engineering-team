# ドキュメント

[English](README.md) | [日本語](README.ja.md)

[プロジェクト紹介](../README.ja.md)と[参加者向け案内](../AGENTS.ja.md)から始めてください。
説明文を言語ごとに分け、設計情報の原本は分岐させません。

| ガイド | 内容 |
|---|---|
| [構成](architecture.ja.md) | 役割、証拠、ツールの境界、人間の承認、設計ゲート |
| [開発フロー](workflow.ja.md) | 各段階の開始・終了条件、引き継ぎ、変更の波及 |
| [作業実行契約](work-execution.ja.md) | 固定入力、予約、進捗、終了状態 |
| [設計を始める](commands/make-circuit.ja.md) | 範囲を限定した開始プロンプトと応用 |
| [組立証拠](assembly-evidence.ja.md) | WIP 証拠、マニフェスト、承認後の資料 |
| [剛体シミュレーション](simulation.ja.md) | モデル・証拠・独立レビューの契約 |
| [評価](evaluation.ja.md) | 単一エージェントとマルチエージェントの比較 |
| [Pages ガイド](pages.ja.md) | 紹介ページ、ビューアーの限界、ダッシュボードの言語動作 |
| [言語対応範囲](language-coverage.ja.md) | 入力リビジョン、対応表、共通のまま維持する資料 |

## 各分野の入口と操作手順

`docs/` 外の読者入口も次の表で選べます。
source/hash と結び付いた記録へナビゲーションだけの変更を加えないため、
言語選択はここに集約しています。

| 対象 | English | 日本語 |
|---|---|---|
| データシート | [Policy and template](../datasheets/README.md) | [方針・テンプレート](datasheets.ja.md) |
| firmware | [Overview](../firmware/README.md) | [分野の入口](firmware.ja.md) |
| Bench-IMU-01 firmware | [Build and behavior](../firmware/bench-imu-01/README.md) | [build・実装の説明](bench-imu-01-firmware.ja.md) |
| 回路・PCB・製造 export | [Reading and regeneration](hardware.md) | [読み方・再生成](hardware.ja.md) |
| 機械・STL・図面 | [Source guides](hardware.md#mechanical-source-stl-and-drawings) | [全再生成手順](mechanical-artifacts.ja.md) |
| simulator | [Run and interpret](simulator.md) | [実行・解釈](../simulation/README.md) |
| 始動試験 | [Ten-second trials](startup.md) | [始動試験](../simulation/STARTUP.md) |
| Blender replay | [Commands and evidence](../simulation/blender/README.md) | [再描画・証拠](blender-replay.ja.md) |
| ROOT exchange | [Compiled adapter](../simulation/root/README.md) | [解析データ交換](root-analysis.ja.md) |
| 現在のRev5 v3・Blender動画6本 | [Visual release scope](rev5-v3-media-release/README.md) | [操作・動画・公開範囲](pages.ja.md#現在の-rev5-wip-参照図) |
| 回路 viewer | [Modes and PDF regeneration](../visualization/circuit-viewer/README.md) | [操作・PDF 再生成](circuit-viewer.ja.md) |
| 組立 viewer | [Controls and limitations](../visualization/assembly-viewer/README.md) | [操作・限界](assembly-viewer.ja.md) |
| dashboard | [Data and parsing](../visualization/dashboard/README.md) | [操作・解析規則](dashboard.ja.md) |

## 読者向け版と共通記録

英語ガイドは従来のパスを維持し、エージェントの指示、パーサー、節参照を壊しません。
日本語版は同じ場所の `.ja.md` ファイルです。
構成・開発フローの日本語読者向け版では現行の運用規則を説明し、過去の個別事例は英語原本にリンクします。
古いレビューを日本語の別台帳として複製しません。
対応表では翻訳と読者向け編集版を区別しており、リポジトリの全ファイルが翻訳済みという意味ではありません。

役割、スキル、パス別指示、スキーマ、コマンド、コード、設計記録、Evidence ID、指摘、
承認、過去資料は共通です。識別子や状態語を翻訳して意味を変えません。
説明文は設計値、レビュー判定、人間の意思決定、ゲートを変更しません。
版間に不一致があれば文書上の不具合として扱い、正本を確認して両方を整合させます。
