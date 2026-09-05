# キューブ剛体シミュレーター — WIP

自由な剛体キューブ、床接触、独立した3軸のリアクションホイールを
MuJoCoで計算します。**実機の成立性・安全性・Design Completeの承認ではありません。**
初期コントローラーはシミュレーション専用です。Fusionの組立工程アニメーションとは別物です。

## ローカル実行

リポジトリのルートから実行します。Python 3.14、ffmpegが必要です。
依存関係はこのディレクトリの仮想環境だけにインストールします。

```sh
python3 -m venv simulation/.venv
simulation/.venv/bin/python -m pip install -r simulation/requirements-lock.txt
cd simulation
.venv/bin/python -m cube_sim preflight
.venv/bin/python -m cube_sim run --scenario three-wheel --output runs/my-three-wheel --video
```

`runs/my-three-wheel/` の `motion.mp4`、`plots.png`、`trajectory.csv` を開いてください。
出力ディレクトリは毎回新しい名前にします。既存証拠を上書きしません。
`trajectory.npz` は状態記録、`model.xml` は実行したMJCFモデル、
`input.json`・`scenario.json`・`manifest.json` は入力と版・ハッシュ情報です。

macOSのネイティブ再生には通常のPythonではなく、MuJoCo同梱の `mjpython` を使います。

```sh
.venv/bin/mjpython -m cube_sim replay runs/my-three-wheel
# Linuxでは通常の .venv/bin/python を使用
.venv/bin/python -m unittest discover -s tests -v
```

再生は記録状態のリプレイであり、リアルタイム制御・ハードウェア接続ではありません。
ホイールの白マーカーも計算角度のまま描画するため、高速時に標本化による逆回転・静止に
見える場合があります。速度の真値はグラフとCSVで確認してください。

## 初期モデルの境界

`models/reference.json` は **SYNTHETIC_REFERENCE** です。
1 kgの均質キューブ相当の本体慣性と、各100 gの円柱ローターを明示的に与えます。
本体1 kgに3ローターの質量を含めず、合計1.3 kgです。これは実機の重量ではありません。
全単位はSI、世界座標はZ上向き、本体中心がローカル原点、ホイール軸は本体の+X/+Y/+Zです。
クォータニオンは `w,x,y,z`、本体→世界の回転です。
床接触は柔らかいbox/planeモデル、摩擦係数や剛性は未同定の仮定です。
刻み2 msのRK4を使います。比較したimplicitfastでは自由空間の並進運動量誤差が
刻みに比例して残り、RK4では同じ試験の誤差が約6×10^-16 kg m/sまで減ったためです。
この選択は数値精度のためで、物理的な接触特性を同定したことにはなりません。

モーターは本体と子ローター間のhingeに対する `motor joint=... gear=1` です。
本体への外力トルク、固定ピボット、姿勢の補正書き込みはありません。
逆トルクも理想的な双方向トルクであり、DRV10983の実際のBRAKE動作ではありません。
速度しきい値で同方向トルクを止めますが、速度を直接クランプせず、実機RPM上限も保証しません。

`rest`、`fall`、`one-wheel`、`three-wheel`、`edge-balance`、
`vertex-balance`、`face-to-vertex-attempt` を選択できます。
辺・頂点試験の初期姿勢はあらかじめ与えたものです。転倒、滑り、飽和は有効な結果であり、
成功に見えるよう調整しません。完全な面→辺→頂点遷移はまだ証明していません。

## 根拠

- [MuJoCo Python / macOS passive viewer](https://mujoco.readthedocs.io/en/stable/python.html#passive-viewer)
- [Actuation, transmission and generalized forces](https://mujoco.readthedocs.io/en/stable/computation/index.html#actuation-model)
- [Explicit inertial tensors](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial)
- [No inertia inference from render geometry](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-inertiafromgeom)
- [Soft contact and friction](https://mujoco.readthedocs.io/en/stable/computation/index.html#soft-contact-model)
- [Subtree angular momentum about COM, world coordinates](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom)

2026-09-05に公式資料とローカルAPIを確認。旧
`hardware/mechanical/drawings/physics-demo/` は規定回転のBlenderアニメーション、
`concept-demo/` は理想化したキーフレームです。過去の開示形式だけを参考にし、
現在の3軸動力学軌道としては再利用していません。
