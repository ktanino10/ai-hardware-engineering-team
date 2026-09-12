# AI Hardware Engineering Team

[English](README.md) | [日本語](README.ja.md)

GitHub Copilot 上で動く、再利用可能な**マルチエージェント型ハードウェア開発フレームワーク**です。
1つの AI がすべてを設計するのではなく、専門エージェントが要件整理から独立レビューまでを分担します。
重要な技術的主張はメーカーの一次資料に結び付け、主要な意思決定には人間の明示的な承認を必要とします。

「もっともらしい回路を AI に書かせる」ことが目的ではありません。設計者とは別のレビュー担当が誤りを探し、
何を、なぜ、どの根拠で決め、誰が承認したかを後から追跡できる開発プロセスを提供します。

## はじめに

- **ドキュメントを読む**: [日本語ガイド一覧](docs/README.ja.md)／[英語ガイド一覧](docs/README.md)。
  説明文は言語別に分け、設計記録とエージェントの実行規約は共通の原本を参照します。
- **最初に確認**: [参加者向け案内](AGENTS.ja.md)で、対象作業の入口と既存コマンドを確認します。
- **今回の作業を区切る**: [作業実行契約](docs/work-execution.ja.md)で、入力の固定、担当範囲、
  進捗、共有ファイルの公開、停止条件を確認します。
- **必要な箇所だけ読む**: [構成ガイド](docs/architecture.ja.md)と[開発フロー](docs/workflow.ja.md)で、
  役割、証拠、ゲート、各段階の前提条件を確認します。毎回すべての過去記録を読む必要はありません。
- **設計を始める**: [make-circuit](docs/commands/make-circuit.ja.md)の開始プロンプトを使います。
- **組立を扱う**: [組立証拠](docs/assembly-evidence.ja.md)で、早期 WIP 証拠、Fusion の
  ネイティブ成果物と動画、承認後に公開する組立資料を区別します。
- **Cube の物理シミュレーション**: [実行・表示手順](simulation/README.md)と
  [シミュレーション契約](docs/simulation.ja.md)を参照します。
- **ブラウザーで見る**: [日本語の紹介ページ](https://ktanino10.github.io/ai-hardware-engineering-team/index.ja.html)。
  ダッシュボードの UI は EN/JA 切り替えに対応します。設計記録の本文は自動翻訳しません。

## エージェント（14役）

| 分野 | エージェント | 担当 |
|---|---|---|
| 電子回路 | [Hardware Lead](.github/agents/hardware-lead.agent.md) | 調整、依存関係、ゲート判断 |
| 電子回路 | [Component Engineer](.github/agents/component-engineer.agent.md) | 一次資料に基づく候補比較 |
| 電子回路 | [Circuit Engineer](.github/agents/circuit-engineer.agent.md) | 承認された部品による回路設計 |
| 電子回路 | [Hardware Reviewer](.github/agents/hardware-reviewer.agent.md) | 回路・PCB の独立レビュー |
| 電子回路 | [Power Engineer](.github/agents/power-engineer.agent.md) | 必要に応じたシステム電源構成 |
| 電子回路 | [PCB Engineer](.github/agents/pcb-engineer.agent.md) | WIP 物理インターフェース準備と承認後の PCB 設計 |
| 機械 | [Mechanical Lead](.github/agents/mechanical-lead.agent.md) | 形状設計と組立証拠 |
| 機械 | [Mechanical Reviewer](.github/agents/mechanical-reviewer.agent.md) | 形状・組立・製造条件の独立レビュー |
| 機械 | [Manufacturing Engineer](.github/agents/manufacturing-engineer.agent.md) | 構造上の前提を実現する製造条件 |
| ファームウェア | [Firmware Engineer](.github/agents/firmware-engineer.agent.md) | 実際のピン割り当てに沿ったドライバー実装 |
| ファームウェア | [Firmware Reviewer](.github/agents/firmware-reviewer.agent.md) | ドライバーの独立レビュー |
| 分野横断 | [Systems Engineer](.github/agents/systems-engineer.agent.md) | インターフェースと技術的トレードオフ |
| シミュレーション | [Simulation Engineer](.github/agents/simulation-engineer.agent.md) | 剛体モデル、計算、計算結果からの可視化 |
| シミュレーション | [Simulation Reviewer](.github/agents/simulation-reviewer.agent.md) | モデル・数値・実際の出力の独立レビュー |

最初の電子回路4役を基盤として、実際に必要になった責務だけを追加しています。
Power Engineer と Manufacturing Engineer は、電源の複雑さや構造部品の要件に応じて起用します。
PCB 専用の別レビュアーは作らず、Hardware Reviewer が独立評価を担当します。
シミュレーション内の制御は実機向け制御の実装ではなく、Control Engineer の新設も意味しません。
追加経緯は共通の [architecture-evolution.md](docs/architecture-evolution.md) に保存されています。

## リポジトリ構成

| パス | 内容 |
|---|---|
| `.github/` | 共通指示、パス別規則、役割、スキル、プロンプト、CI、CODEOWNERS |
| `requirements/` | 要件とトレーサビリティ |
| `datasheets/` | メーカー資料のメタデータと Evidence ID。著作権のある資料本体は含めない |
| `hardware/` | 回路、PCB、電源予算・構成、機械インターフェース、機械設計 |
| `bom/` | 部品候補の比較・選定記録 |
| `firmware/` | 基板別のドライバーレベル初期立ち上げコード |
| `simulation/` | 剛体モデル、固定入力、数値テスト、出力証拠、独立レビュー |
| `validation/` | レビュー、未解決課題、FMEA、ECO、変更影響、実機立ち上げ手順 |
| `docs/` | 構成、開発フロー、実行契約、評価方法、言語別の読者向け説明 |
| `tools/` | CI と証拠・実行契約のチェック |
| `visualization/` | GitHub Pages の紹介、回路・組立ビューアー、ダッシュボード |

## 原則

**一次資料優先**: 部品仕様を推測しません。数値の根拠をメーカー資料と Evidence ID で示し、
確認できない値は `UNKNOWN` とします。絶対最大定格、推奨動作条件、代表特性を混同しません。

**独立レビュー**: 自分の設計を自分だけで承認しません。
**完了を偽らない**: 未解決の `CRITICAL` がある設計を Design Complete としません。
全条件は[構成ガイドのゲート説明](docs/architecture.ja.md#8-design-complete-ゲート)を参照してください。

**人間の承認**: アーキテクチャ、主要部品、安全に関わる変更、大きな BOM 変更、
製造前、初回通電前などは人間が明示的に承認します。AI は開発支援者、人間が Chief Engineer です。

## ベンチマーク

最初の題材は **MCU + IMU + 電源**です。モータードライバー、リアクションホイール、
1軸・3軸の姿勢制御、立つ Cube へ向かうロードマップがあります。
現在の公開 WIP には3軸 Cube の設計と実行可能な独立したシミュレーターが含まれますが、
製作済み・実機認定済みという主張ではありません。フレームワーク自体は
組み込み、ロボティクス、IoT など別の開発にも再利用できます。

## 貢献する

他のセッションの worktree を妨げず、対象を限定したブランチで作業します。
[参加者向け案内](AGENTS.ja.md)、共通の[保守対応表](.github/copilot-instructions.md#maintenance-matrix)、
[PR テンプレート](.github/PULL_REQUEST_TEMPLATE.md)を使って、実際の結果と未実施事項・阻害要因を分けて報告します。
資料の体裁を整えるためだけに不要なツールや設定を導入しません。
独立レビュー、一次資料との対応、人間の承認、実機操作のゲートは翻訳後も変わりません。
