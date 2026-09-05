"""Static local report: computed motion beside its recorded evidence."""

import html
from dataclasses import replace
import json
from pathlib import Path

from .model import ROOT, load_config
from .numerics import write_witnesses
from .braking import derive_startup_config
from .runner import run, sha256, write_json
from .scenarios import scenarios, startup_scenario
from .visualize import plot, plot_startup, render, source_label, verify_current

STARTUP_CASES = ("startup-reference", "startup-rev5-proxy", "startup-mechanism-fixture")


def build_gallery(directory):
    directory = Path(directory)
    cards, navigation, files = [], [], {}
    for model_dir in ("reference", "rev5-proxy"):
        for name in scenarios():
            relative = f"{model_dir}/{name}"
            path = directory / relative
            manifest, _ = verify_current(path)
            result = json.loads((path / "summary.json").read_text(encoding="utf-8"))
            scenario = result["scenario"]
            slug = f"{model_dir}-{name}"
            classification = html.escape(manifest["classification"])
            outcome = result["outcome"]
            label = {"NO_CONTROL_GOAL": "応答を観測（制御目標なし）",
                     "DEPARTED_TARGET": "目標姿勢を維持できず",
                     "TARGET_NOT_REACHED": "目標姿勢に到達せず",
                     "TARGET_ATTITUDE_REACHED_ONLY": "最終角度のみ目標帯内（遷移成功の証明ではない）",
                     "WITHIN_TRIAL_BAND": "この試験の角度帯内"}[outcome]
            navigation.append(f'<a href="#{slug}">{html.escape(model_dir)} / {html.escape(name)}</a>')
            cards.append(f"""
<article id="{slug}">
  <header><span class="model">{classification}</span>
  <h2>{html.escape(name)}</h2><p>{html.escape(scenario["description"])}</p></header>
  <video controls playsinline preload="metadata" poster="{relative}/preview.png"
         aria-label="{html.escape(model_dir + ' ' + name)} 計算軌道の動画">
    <source src="{relative}/motion.mp4" type="video/mp4">
    <a href="{relative}/motion.mp4">MP4を開く</a>
  </video>
  <div class="result {'failed' if outcome in {'DEPARTED_TARGET', 'TARGET_NOT_REACHED'} else ''}">
    <strong>{label}</strong>
    <span>最終姿勢誤差 {result["final_attitude_error_deg"]:.2f}° / {scenario["duration_s"]:.1f} s</span>
  </div>
  <p class="caption">{html.escape(source_label(manifest))}</p>
  <p class="links"><a href="{relative}/motion.mp4">動画</a>
    <a href="{relative}/trajectory.csv">CSV</a><a href="{relative}/trajectory.npz">全状態</a>
    <a href="{relative}/model.xml">MJCF</a><a href="{relative}/manifest.json">版・ハッシュ</a></p>
  <details><summary>グラフ・入力条件を見る</summary>
    <a href="{relative}/plots.png"><img loading="lazy" src="{relative}/plots.png" alt="姿勢・速度・トルク・接触・エネルギー・運動量の時系列"></a>
    <p><a href="{relative}/input.json">全モデル入力・未モデル化事項</a> /
       <a href="{relative}/scenario.json">初期条件・制御ゲイン</a> /
       <a href="{relative}/video-frames.csv">動画フレームと状態の対応</a></p>
    <pre>{html.escape(json.dumps(scenario, indent=2))}</pre>
  </details>
</article>""")
            files[f"{relative}/manifest.json"] = sha256(path / "manifest.json")
    page = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cube dynamics — WIP 計算結果</title>
<style>
:root{color-scheme:light;--ink:#173148;--paper:#eaf0f4;--line:#c4d3de;--teal:#12606c;--warn:#996100;--bad:#b13926}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 system-ui,"Hiragino Kaku Gothic ProN",sans-serif}
main{max-width:1440px;margin:auto;padding:32px 24px}h1,h2{font-family:"Avenir Next",system-ui,sans-serif;line-height:1.15}
h1{font-size:clamp(2rem,4vw,3.5rem);margin:14px 0}h2{font-size:1.6rem;margin:8px 0}
a{color:var(--teal);text-underline-offset:3px}a:focus-visible,summary:focus-visible,video:focus-visible{outline:3px solid var(--warn);outline-offset:4px}
.eyebrow,.model,.caption,.result span{font-family:ui-monospace,"SFMono-Regular",monospace}.eyebrow{letter-spacing:.1em;font-size:.8rem}
.intro{max-width:1000px}.warning{padding:16px 20px;border-left:5px solid var(--warn);background:#fff8e9}
.axes{display:flex;gap:24px;margin:18px 0;font-weight:650}.axes span{padding-left:10px;border-left:4px solid}.x{border-color:#d64735!important}.y{border-color:#209756!important}.z{border-color:#357bcc!important}
nav{display:flex;flex-wrap:wrap;gap:8px 18px;margin:24px 0;font-size:.85rem}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}
article{background:white;border:1px solid var(--line);border-radius:8px;overflow:hidden;scroll-margin-top:16px}
article header{padding:20px 24px}.model{font-size:.78rem;color:var(--teal)}header p{margin-bottom:0;font-size:.9rem}
video,img{display:block;width:100%;height:auto}video{background:#142636;aspect-ratio:4/3}
.result{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;padding:16px 24px;border-bottom:1px solid var(--line)}
.result span{font-size:.8rem}.failed{color:var(--bad);background:#fff0eb}.caption{font-size:.75rem;overflow-wrap:anywhere;padding:0 24px}
.links{display:flex;gap:18px;flex-wrap:wrap;padding:0 24px}details{border-top:1px solid var(--line);padding:16px 24px}summary{cursor:pointer;font-weight:650}
pre{overflow:auto;font-size:.8rem;padding:12px;background:var(--paper)}footer{margin:32px 0;color:var(--ink);font-size:.85rem}
@media(max-width:800px){main{padding:24px 12px}.grid{grid-template-columns:1fr}.result,article header{padding:16px}}
</style></head><body><main>
<header class="intro"><div class="eyebrow">RIGID-BODY LAB / WIP / 計算された運動</div>
<h1>Cube dynamics</h1><p>剛体キューブと3つのリアクションホイール。姿勢・接触・トルクを、同じ記録時刻の動画とグラフで追います。</p>
<div class="axes"><span class="x">+X wheel</span><span class="y">+Y wheel</span><span class="z">+Z wheel</span></div>
<p class="warning"><strong>実機の成立性・安全性を承認する結果ではありません。</strong>
基準モデルとRev5の部分的な固体CAD質量プロキシを分離しています。実ドライバー・完全な質量/CG・床特性は未確定です。
辺・頂点バランスは事前配置した試験です。失敗や飽和を隠していません。Fusionの組立工程動画とは別物です。</p>
<p><a href="numerics.json">刻み・ソルバー感度の数値記録</a> /
<a href="index-manifest.json">この一覧の証拠ハッシュ</a></p></header>
<nav aria-label="計算ケース">""" + "\n".join(navigation) + '</nav><section class="grid">' + "\n".join(cards) + """
</section><footer>動画は25 fpsで、100 Hz記録の該当行をそのまま再描画しています。ホイールマーカーには標本化による見かけの逆回転があります。
値の根拠はCSV/入力JSONです。5°帯は表示上の基準であり、実機の合否判定ではありません。</footer></main></body></html>
"""
    (directory / "index.html").write_text(page, encoding="utf-8")
    files["index.html"] = sha256(directory / "index.html")
    files["numerics.json"] = sha256(directory / "numerics.json")
    write_json(directory / "index-manifest.json", {
        "state": "WIP_SIMULATION_NOT_ASSEMBLY_EVIDENCE", "files": files,
        "interpretation": "Nested run manifests bind actual outputs; no physical/Fusion approval.",
    })


def suite(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    for model_name in ("reference", "rev5-proxy"):
        model_path = ROOT / "models" / f"{model_name}.json"
        config = load_config(model_path)
        for scenario in scenarios().values():
            scenario = replace(scenario, duration_s=max(10.0, scenario.duration_s))
            output = directory / model_name / scenario.name
            print(f"Computing/rendering {model_name}/{scenario.name}", flush=True)
            run(config, scenario, output, config_path=model_path)
            plot(output)
            render(output)
    write_witnesses(directory / "numerics.json")
    build_gallery(directory)


def write_startup_models(directory):
    directory = Path(directory)
    paths = [directory / f"{name}.json" for name in STARTUP_CASES]
    if any(path.exists() for path in paths):
        raise FileExistsError("Do not replace versioned startup inputs; use a new output directory.")
    directory.mkdir(parents=True, exist_ok=True)
    for i, path in enumerate(paths):
        base = ROOT / "models" / ("rev5-proxy.json" if i == 1 else "reference.json")
        write_json(path, derive_startup_config(base, mechanism_fixture=i == 2))


def startup_suite(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    cards = []
    hashes = {}
    for name in STARTUP_CASES:
        path = ROOT / "models" / f"{name}.json"
        config = load_config(path)
        output = directory / name
        scenario = startup_scenario(config)
        if scenario.duration_s < 10:
            raise ValueError("Published startup videos require at least ten simulated seconds.")
        print(f"Computing ten-second {name}", flush=True)
        run(config, scenario, output, config_path=path)
        plot(output)
        plot_startup(output)
        render(output)
        render(output, detail=True)
        report = json.loads((output / "summary.json").read_text())
        study = report["startup"]
        text = ("Synthetic small annular-wheel fixture; NOT Rev5" if name.endswith("fixture")
                else "Partial WIP design proxy" if name.endswith("proxy") else "Original mathematical reference")
        cards.append(f"""<article><h2>{html.escape(name)}</h2><p><strong>{text}</strong></p>
<p>Result: {report['outcome']} / max body rotation {study['max_body_rotation_from_initial_deg']:.3f} deg /
max lowest-corner clearance {study['max_minimum_corner_height_m'] * 1000:.4f} mm. NO captured balance.</p>
<p>Flight assessment: <strong>{study['flight_assessment']['status']}</strong>.
Tiny contact gaps are not a resolved jump; compare contact/geometry uncertainty and convergence.</p>
<video controls playsinline preload="metadata" poster="{name}/preview.png" src="{name}/motion.mp4"></video>
<details><summary>100x slow brake detail (10-second video, only 0.1 simulated seconds)</summary>
<video controls playsinline preload="metadata" poster="{name}/brake-detail-preview.png" src="{name}/brake-detail.mp4"></video></details>
<p><a href="{name}/startup-plots.png">Spin / brake / XYZ floor reaction / momentum / clearance plots</a> |
<a href="{name}/trajectory.csv">CSV</a> | <a href="{name}/input.json">Parameters and assumptions</a> |
<a href="{name}/manifest.json">Hashes</a></p>
<a href="{name}/startup-plots.png"><img loading="lazy" src="{name}/startup-plots.png" alt="Actual time histories"></a></article>""")
        hashes[f"{name}/manifest.json"] = sha256(output / "manifest.json")
    write_witnesses(directory / "numerics.json")
    page = """<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Spin-up and finite braking — 10 second WIP trials</title><style>
body{font:16px/1.6 system-ui,sans-serif;color:#163247;background:#eaf0f4;margin:0}main{max-width:1200px;margin:auto;padding:28px}
h1{font-size:2.4rem}article{background:white;padding:24px;margin:28px 0;border:1px solid #bfd0dc;border-radius:8px}
video,img{display:block;width:100%;height:auto;max-width:960px}video{background:#142636}a{color:#12606c}
.warning{border-left:5px solid #a06b13;background:#fff4dd;padding:18px}summary{cursor:pointer;padding:16px 0}
a:focus-visible,summary:focus-visible{outline:3px solid #a06b13}p{max-width:1050px}</style><main>
<h1>高速回転 → 有限制動：10秒の計算</h1>
<p>すべて静止状態から10秒間を実際に積分しています。XYZの外力で持ち上げず、内部ホイールトルクと床反力から運動を計算します。</p>
<p class="warning"><strong>WIP / 実機の成立性・安全性・制動性能の証明ではありません。</strong>
3000 rpmは既存の解析用目標で、定格ではありません。独立した仮想ブレーキの遅延・立ち上がり・トルク容量も仮定です。
100 mmの合成機構モデルは240 mmのRev5部分質量モデルと別物です。辺付近の通過や微小離床を倒立維持・頂点捕捉と呼びません。
ROOTはデータ解析、Blenderは計算軌道の再描画に使い、Fusion組立工程とは区別します。</p>
<p>通常動画は実時間10秒。拡大動画は<strong>100倍スロー</strong>で、0.1秒の計算区間を10秒で表示します。
<a href="numerics.json">刻み・ソルバーと補正済み仕事積分の数値記録</a></p>
""" + "\n".join(cards) + "</main></html>"
    (directory / "index.html").write_text(page, encoding="utf-8")
    hashes.update({name: sha256(directory / name) for name in ("index.html", "numerics.json")})
    write_json(directory / "index-manifest.json", {"state": "WIP_NOT_HARDWARE_APPROVAL", "files": hashes})
