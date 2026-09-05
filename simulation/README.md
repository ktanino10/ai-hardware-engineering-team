# キューブ剛体シミュレーター — WIP

自由な剛体キューブ、床接触、独立した3軸のリアクションホイールを
MuJoCoで計算します。**実機の成立性・安全性・Design Completeの承認ではありません。**
初期コントローラーはシミュレーション専用です。Fusionの組立工程アニメーションとは別物です。

**最新の10秒始動試験**: [高速回転→有限制動の手順と条件](STARTUP.md)。
閲覧入口は `evidence/startup-v2/index.html`。合成機構モデルと不完全な実機プロキシを
別ケースにし、XYZ反力を内部制動と床接触から計算します。
Blenderの10秒再描画とCERN ROOT形式への解析出力も、それぞれ役割を分けています。

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

## まとめて実行・見る

両モデル×7シナリオの動画・グラフ・数値感度を一度に再生成できます。
`--allow-proxy` は不完全な設計プロキシと仮定した駆動/接触モデルを使うという確認であり、
実機の許可ではありません。

```sh
# simulation/ で実行。出力先は既存でないディレクトリを指定
.venv/bin/python -m cube_sim suite --allow-proxy --output runs/my-suite
.venv/bin/python -m http.server 8765 --bind 127.0.0.1
# ブラウザーで http://127.0.0.1:8765/runs/my-suite/index.html を開く
```

初回の短い収録結果（履歴）は `evidence/initial-v1/index.html` です。同じサーバーなら
`http://127.0.0.1:8765/evidence/initial-v1/index.html` で閲覧できます。
サーバーはCtrl+Cで終了します。外部CDNやクラウドへの設計アップロードはありません。

## Rev5入力の扱い

`intake/rev5-v1.json` は、設計統合担当から受け取った凍結WIP
`3633eb5d03d6db7c90b582e53180414087b33519` の数値抜粋とハッシュです。
元の21ファイル束のハッシュ/サイズと、抜粋した質量・CG・慣性の一致を確認しています。
そのコミットはmainや完成品の版ではありません。実機CADを複製・変更していません。

`models/rev5-proxy.json` は `cube_sim.intake.derive_proxy()` で決定的に導出します。
入力の **3.06427779784 kgには既に3ローターが含まれる** ため、同じ原点で質量・一次
モーメント・慣性を引いて本体を約2.76427779784 kgにし、各0.1 kgのローターを別DOFに
戻しています。別方法の「印刷物＋全モーター近似＋裸基板」加算とも照合します。
元の完全性を増やす操作ではありません。モーターの未知の回転子/固定子分割は推定せず、
全モーター近似を本体に固定した仮定を開示しています。

```sh
.venv/bin/python -m cube_sim run --config models/rev5-proxy.json --allow-proxy \
  --scenario vertex-balance --output runs/my-proxy-vertex --video
# 導出を再実行して元ファイルを上書きせず比較
.venv/bin/python -m cube_sim derive-proxy --output runs/rederived-proxy.json
```

実機全体の質量/CG、電池・実装済み基板・ハブ・配線・固定具、実モーターのトルク/速度/
電流曲線とDRV10983の制動応答、床の特性は未確定です。実ドライバーの忠実モデルは
まだ実行できません。代理モデルでは基準ケースと同じ理想トルク/接触仮定を明示的に使い、
成功に合わせた調整や3000 rpmを安全上限とみなす操作はしていません。
過去の固定辺モデルの運動量不足も、すべての軌道が不可能だという証明にはしていません。

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
本体速度は並進が世界座標・角速度が本体座標です。ホイール相対速度はhingeの
`qvel`、絶対軸速度はそれに本体角速度の同軸成分を加えた値です。

`rest`、`fall`、`one-wheel`、`three-wheel`、`edge-balance`、
`vertex-balance`、`face-to-vertex-attempt` を選択できます。
辺・頂点試験の初期姿勢はあらかじめ与えたものです。転倒、滑り、飽和は有効な結果であり、
成功に見えるよう調整しません。完全な面→辺→頂点遷移はまだ証明していません。

## 証拠と解釈

`verify` はCSV/NPZ/動画等のハッシュだけでなく現在のコード・入力モデル・凍結入力の
対応も調べます。古い結果を歴史的記録として開く場合だけ `--historical` を使います。
入力やコードが変わったら別名で再計算し、独立Simulation Reviewerの再評価を受けます。
古い計算を新しいレンダラーで再生成して元の証拠に上書きすることも認めません。

```sh
.venv/bin/python -m cube_sim verify evidence/initial-v1/reference/three-wheel --historical
.venv/bin/python -m cube_sim witnesses --output runs/my-numerics.json
```

CSV/グラフは100 Hz、動画はその記録の該当行を25 fpsで再描画します。
`video-frames.csv` の時刻と状態ハッシュで対応を追えます。接触点数、法線力、貫入量、
滑り速度、飽和・速度超過を記録しますが、サンプル間の衝撃ピークを保証しません。
エネルギーは剛体の位置/運動エネルギーと、モーター・受動・拘束力の仕事を比較します。
現在はRK4の実評価点に整合する仕事積分を使います。初回版の端点台形則の不足と
補正/残差の扱いは [STARTUP.md](STARTUP.md) に記録しています。
接触で散逸する試験に保存則を押し付けたり、拘束仕事を制動発熱/構造強度と読み替えたり
しません。

条件・単位・数値許容差・責任境界は [simulation contract](../docs/simulation.md) を参照。
2/1/0.5 ms、Newton/CGの比較は数値モデルの感度であり実測による同定ではありません。
この初期試行で姿勢維持/遷移が失敗しても、実機の普遍的不可能性は結論できません。

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
