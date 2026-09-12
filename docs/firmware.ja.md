# ファームウェアの入口

[English](../firmware/README.md) | [日本語](firmware.ja.md) | [ガイド一覧](README.ja.md)

`hardware/` の基板に対応するドライバーレベルの初期立ち上げコードです。
Firmware Engineer と firmware-bringup スキルが担当します。
導入の経緯は共通の `docs/architecture-evolution.md` §32 に残し、
ここでは現在の利用方法と境界を説明します。

## 範囲

実際の回路のピン・interface 判断に対応した register-level の周辺初期化と driver が対象です。
制御ループ、PID、sensor fusion、校正・物理単位変換、要件が除外する USB data・wireless は含めません。
実機向け制御は将来の別責務で、シミュレーション内制御とは別です。

## 構成

基板ごとに `firmware/<board>/` を設けます。
README は build・tooling 状態、`<board>-firmware-design.md` は Evidence ID 付き設計理由、
`Makefile`、`linker/<part>_FLASH.ld`、`src/*.c` / `*.h` が実装です。
基板名は回路の名前に合わせます。

## ツールと検証

`arm-none-eabi-gcc`、PlatformIO、vendor IDE、物理基板・flash tool は毎回確認します。
基板 README の「この session で成功」は当時の記録で、現在の host への保証ではありません。
実コンパイル、独立 Firmware Reviewer の固定入力評価、初回実機 flash の人間承認は別の段階です。
自己点検を独立受け入れにせず、firmware の指摘でハードウェア Design Complete の条件を改変しません。

基板別: [Bench-IMU-01 の日本語ガイド](bench-imu-01-firmware.ja.md) /
[English](../firmware/bench-imu-01/README.md)。
