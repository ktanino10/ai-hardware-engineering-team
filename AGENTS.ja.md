# 参加者・エージェント向け入口

[English](AGENTS.md) | [日本語](AGENTS.ja.md)

このリポジトリにはハードウェア開発フレームワーク、設計成果物、Python チェック、
組み込み C、範囲を限定したシミュレーターがあります。すべてに共通する単一のビルドコマンドはありません。
このページは [AGENTS.md](AGENTS.md) の日本語案内です。実行に用いる指示の正本は元のパスのままです。

## 必要な文脈だけを読む

1. [共通方針](.github/copilot-instructions.md)と対象パスの `.github/instructions/*.instructions.md` を読みます。
   この案内は索引であり、役割や安全規則を別に定義するものではありません。
2. 工学作業では担当の `.github/agents/` プロファイルと必要なスキルを読み、
   [作業実行契約](docs/work-execution.ja.md)に従って専門担当を起動します。
   小さなツール・文書の直接編集で開発チーム全体を起動する必要はありません。
3. 実際に固定された入力と[開発フロー](docs/workflow.ja.md)の該当節を読みます。
   経緯は共通の `docs/architecture-evolution.md` にあり、毎回の事前読み込み対象ではありません。

## 原本の場所

| 作業 | 入口 |
|---|---|
| 目標、要件、追跡 | `requirements/` |
| 部品の事実と候補判断 | `datasheets/` のメタデータ・証拠ログ、`bom/` |
| 回路、PCB、電源、機械モデル | `hardware/`。担当と入力リビジョンを維持 |
| ドライバーレベルのファームウェア | [firmware/README.md](firmware/README.md)、対象基板の README |
| 剛体シミュレーション | [実行手順](simulation/README.md)、[適用範囲](docs/simulation.ja.md) |
| レビュー、指摘、設計変更 | `validation/`。ECO は `validation/change-log.md` に集約 |
| エージェント・開発フローのツール | `tools/`、`tools/tests/`、`.github/workflows/` |

## 既存コマンド

対象の worktree から実行します。Python と Git が必要です。
メタデータ・指示チェックには既存 CI と同じ PyYAML が必要です。
現在の環境を使い、不足が判明してから依存関係を導入してください。

| 変更範囲 | コマンド |
|---|---|
| エージェント・スキルのメタデータ | `python3 tools/check_agent_frontmatter.py` |
| 実行契約・指示・導入案内 | `PYTHONPATH=tools python3 -m unittest discover -s tools/tests -p 'test_*workflow*.py'` |
| 共通 Python チェック・証拠処理 | `PYTHONPATH=tools python3 -m unittest discover -s tools/tests` |
| Rev5限定ソフトウェア公開 | `python3 -B -m unittest discover -s tools/tests -p 'test_rev5_public_software.py'`。IMU・SDK不要のCMake確認は[公開手順](docs/rev5-public-release/software.ja.md) |
| Evidence・Issue・ECO の識別子 | `python3 tools/check_id_uniqueness.py` |
| 対応している機械・PCB 寸法ペア | `python3 tools/check_mechanical_pcb_sync.py` |
| 公開オフライン IMU の source・fixture 依存一式 | `python3 -B -S -m unittest discover -s tools/tests -p 'test_rev5_offline_publication.py'` |
| 元の合成 IMU 不一致解析の動作 | `python3 -B -S -m unittest discover -s simulation/imu_disagreement/tests` |

最小の適切な範囲を選びます。これらは記録・ソフトウェアのチェックであり、
ネイティブ CAD の検査、電気的適格性、物理的な承認ではありません。
ファームウェア、シミュレーション、CAD は各分野の指示と実際のツール可用性に従います。
開発フローだけの編集でレンダリングや実機ツールを実行しません。
CI は既存の個別 workflow を使い、別の汎用 `ci.yml` を追加しません。

## 提出

[保守対応表](.github/copilot-instructions.md#maintenance-matrix)に沿って影響する利用側だけを更新し、
無関係な作業や古い証拠を維持します。[PR テンプレート](.github/PULL_REQUEST_TEMPLATE.md)で
実際の結果と残る阻害要因を報告します。
ローカルコミット、push 済みブランチ、マージ済み PR、タスク `DONE`、設計・実機承認は別の状態です。
CI を通すためだけに本当の指摘を消してはいけません。
