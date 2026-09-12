# 剛体シミュレーション契約

[English](simulation.md) | [日本語](simulation.ja.md) | [ガイド一覧](README.ja.md)

[simulation.md](simulation.md) の日本語読者向け版です。
人間が承認した初期物理範囲は、自由 Cube、床の接触・摩擦、実際の3ローター自由度、
シミュレーション内だけの小さな姿勢制御です。
Simulation Engineer と独立 Simulation Reviewer が担当し、
Control Engineer、実機制御、FEA、熱/SPICE、大規模最適化、実機操作、認証済み digital twin は追加しません。
実行手順は[日本語](../simulation/README.md)／[English](simulator.md)です。

後続の始動試験では静止からの spin-up、有限の独立 brake、10秒以上の公開動画、
明確に別の小型環状ホイール fixture、Blender replay、CERN ROOT 解析交換を追加しています。
条件・provenance は [STARTUP.md](../simulation/STARTUP.md) を参照します。
Cube への直接 XYZ impulse や新しい実機アクチュエーター承認は追加しません。

## 開始、所有権、証拠状態

要件・interface・設計中、Design Complete 前に開始できます。
Lead が元の所有者から固定入力を得て不足を割り当てます。
simulation 側で別 CAD/PCB/回路/BOM を作らず、Systems Engineer が分野間判断を保ちます。

| ラベル | 意味と結論の限界 |
|---|---|
| `SYNTHETIC_REFERENCE` | 明示的な数学 fixture。数値実装とその fixture の挙動だけ |
| `WIP_DESIGN_PROXY` | 固定された設計事実・モーメントと省略・仮定。不完全 proxy の条件付き挙動だけ |
| 実 driver/system case の阻害 | 必須の質量・駆動・接触値が不明。証拠不足であり普遍的不成立の証明ではない |

実行可能な2ラベルも `WIP_SIMULATION_NOT_HARDWARE_OR_ASSEMBLY_APPROVAL` のままです。
レビューは数値実装の受け入れだけで、組立 APPROVED へ遷移しません。
コード・入力・テスト・`simulation/evidence/<version>/` は実装者、
`simulation/reviews/<review-id>/` は独立レビュアーが所有します。
指摘 ID は simulation-local とし、実設計への影響は Lead と既存所有者・Evidence ID・人間判断へ戻します。

## 最低モデル契約

SOURCE / DERIVED / ASSUMPTION / UNKNOWN を付け、入力 commit・hash・版、
world/body/inertial frame、SI、quaternion 順、正方向、質量 inventory・省略・COM、
名前付き点に関する対称正慣性、内部 joint・transmission、相対/絶対速度、
command/delivered torque、cutoff/delay、重力、接触、摩擦、solver、integrator、
初期状態、gain、目的、数値 witness・許容差・結論の限界を記録します。
主慣性は正で三角不等式を満たす必要があり、描画形状から暗黙に慣性を決めません。

固定入力のローター二重計上を防ぐため、同じ原点で分解します。
以下は原本の計算関係をそのまま保持したものです。

```text
P(r) = (r dot r) Identity - r r^T
I_O = I_C + M P(c)
M_base = M - sum(m_wheel)
first_base = M c - sum(m_wheel c_wheel)
I_O_base = I_O - sum(I_C_wheel + m_wheel P(c_wheel))
c_base = first_base / M_base
I_C_base = I_O_base - M_base P(c_base)
```

再合成で質量・COM・tensor を確認します。
公開された初期 proxy の別経路の加算検査も、部分的な解析入力との整合を示すだけで、
実質量、充填、CG、搭載成立、motor bell 慣性の実測ではありません。
個々の凍結数値と出典 hash は[英語正本](simulation.md)と共通 intake を参照し、
翻訳で別の設計数値台帳を作りません。

## 初期実装の選択

MuJoCo の freejoint body に3つの hinge-child rotor を持たせ、
`motor` / `gear=1` の内部一般化トルクを与えます。反作用は結合運動から生じます。
base への外力トルク、固定 pivot、床試験の接触無効化、初期化後の姿勢補正を使いません。
自由空間 witness は明示的に重力・接触を消した試験で、跳躍の実証ではありません。

基準立方体・円柱は閉形式慣性を使います。
Rev5 proxy は公開済みの固定入力を使い、未知の電池・電子部品・hub・harness・retention・
motor rotor/stator 分割を明示します。box collision proxy は CAD の代替ではありません。
理想双方向トルク、20 ms FIFO、基準トルク・速度 cutoff は仮定であり、
DRV10983 の実 brake、current、stop/hold/restart、regen を表しません。
一般的な runtime BRAKE bit を仮定しません。cutoff は外向きトルクを止めるだけで速度を消しません。

制御は quaternion 誤差の sampled PD で、推定器、重力・gyro feedforward、並進 capture、
desaturation、実時間 firmware はありません。辺・頂点は初期配置で、非対称 COM の支持整合も自動保証しません。
別の face-to-vertex attempt と区別し、成功に合わせて元ケースを黙って調整しません。
target visit、短い分離、capture、持続平衡は別の結果です。

初期 solver は Newton、elliptic cone、condim 3、転がり・ねじり抵抗なしです。
2 ms RK4 の選択は自由空間の数値比較に基づき、接触の実測校正ではありません。
soft-contact は未測定仮定であり、貫入、反発、衝撃荷重、変形、封じ込めの実機結論には使えません。

## 実行証拠と失効

各不変 run は `input.json`、`scenario.json`、`model.xml`、`trajectory.npz`、
`trajectory.csv`、`summary.json`、`plots.png`、`motion.mp4`、`video-frames.csv`、`manifest.json` を含みます。
manifest はコード・版、依存・engine、intake、model、各 output hash を結び、未コミットはその旨を記録します。
CSV と図は100 Hz、動画は記録行を25 fpsで使い、姿勢・時刻の補間をしません。
frame map は state hash を持ち、終端状態は軌道内にあります。
startup は brake 周辺10 kHzと0.1 ms積分を使います。
通常動画は10秒のシミュレーション、明示的100倍 slow 動画は0.1秒を10秒で再生します。
ループや水増しで時間を作りません。

姿勢、body/world angular rate、wheel relative/absolute rate、要求・遅延・実 torque、
saturation/cutoff/overspeed、contact 数・法線力・貫入・slip、energy、各 work、
全 COM angular momentum を記録します。sample 間のピークは保証しません。
非駆動自由空間の保存則を、駆動・散逸接触へ無理に適用しません。
motor work は相対速度を使い、contact work は発熱・強度認定ではありません。
有限 brake work は constraint work の部分集合で、二重加算しません。
床の work はその差です。床 XYZ force、外部 angular impulse、COM momentum residual は計算結果で、
任意の揚力を加えません。

初期端点台形則の不足は R1 の `SIM-R1-001` で記録されています。
現在は実 RK4 4評価点を読み取り、別 data object で力を再評価して 1:2:2:1 quadrature を使います。
主軌道は変えず、全 step・記録 grid・最終 residual を分けます。
未校正の誤差を物理散逸と呼びません。native control callback は step 内だけ所有して `finally` で復旧し、
既存 callback があれば上書きせず拒否します。

`verify` は現在の実装・model・intake と成果物 hash を照合し、
`verify --historical` は保存出力だけを確認します。
source、分解、contact、control、solver の変更は影響結論を再生成・再レビューまで無効にします。
古い証拠を維持し、upstream branch の進行を凍結 snapshot の自動更新にしません。
組立 manifest / `current.json` は simulation 用に作りません。

## 独立レビューと数値許容差

別レビュアーが式、信頼度、実コード、実軌道・動画を検査し、代表 run を再実行して限界を記録します。
open `CRITICAL` / `HIGH` は該当結果への依存を止め、修正・独立再評価が必要です。
条件付きモデル判断は実機リスク受容・操作許可にはなりません。

| witness | 原本の regression margin（実機の受け入れ値ではない） |
|---|---|
| 初期慣性・加速度・frame/質量再合成 | acceleration 1e-10、tensor/frame 1e-12–1e-14 |
| 自由空間の線・角運動量 | 1e-10 kg m/s または N m s |
| 駆動自由空間の energy − actuator work | 1e-7 J |
| quaternion / deterministic replay | norm 1e-12、同一 runtime 配列の一致 |
| 受動静止 | 重量差 1e-3 N、貫入 0.2 mm 未満 |
| step / solver 感度 | 2/1/0.5 ms、Newton 50/100・CG 100。自由空間 state 1e-8、静止/drop 高さ差 10 µm / 1 mm、drop 貫入 10 mm 未満 |
| 有限制動 startup | 0.1/0.05 ms と別の出力間引き。5e-5 J、1e-7 N m s |

これらは宣言済み fixture の数値 regression 値です。
不安定な辺・頂点では感度を報告し、すべての詳細接触軌道が収束したと主張しません。
短い試験の失敗を普遍的不可能性、最適化結果、新たな部品推奨に変換しません。
