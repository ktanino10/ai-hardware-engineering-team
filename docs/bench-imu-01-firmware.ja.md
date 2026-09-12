# Bench-IMU-01 ファームウェア

[English](../firmware/bench-imu-01/README.md) | [日本語](bench-imu-01-firmware.ja.md) | [分野の入口](firmware.ja.md)

公開された[基板 README](../firmware/bench-imu-01/README.md)の読者向け日本語版です。
以下はその記録する実装仕様であり、今回新たに実機動作や数値を検証した主張ではありません。
全設計理由・Evidence ID は共通の
[firmware design](../firmware/bench-imu-01/bench-imu-01-firmware-design.md)にあります。
同じ基板に、互いを制御しない IMU と motor の2 subsystem を持ちます。

## IMU 初期立ち上げ

I2C2 は **PA11 (SCL) / PA12 (SDA)** です。
旧 PB10/PB11 は実 package に存在しない誤りとして訂正された履歴があり、
同じ I2C2・AF6・400 kHz を使い GPIO だけを修正したと原本が記録しています。
根拠は ISS-027 と design §3 のメーカー資料です。
BMI270 の address 0x68、メーカー必須初期化と約8 KBの configuration blob を使います。
加速度・角速度は生 register count のまま100 Hzで読み、
USART2（PA2/PA3、115200 8N1）から `millis,ax,ay,az,gx,gy,gz` を出します。
boot 時には `RCC_CSR` の reset cause を1回報告します。

## Motor / reaction wheel の開ループ bring-up

U5 DRV10983、M1 T-Motor MN2206-13、U6 TPS26631PWPR の公開された
bench characterization 用実装で、閉ループ controller ではありません。
原本の pin contract は PA8 / TIM1_CH1（20 kHz PWM）→ SPEED、
PA6 / TIM3_CH1（interrupt input capture）← FG、PB1 → DIR、
PB6/PB7 / I2C1 → U5 commissioning/status、PA9 → U6 SHDN です。
SHDN は R11 pulldown により既定 OFF と記録されています。

次の表は**コードの command grammar の説明**であり、実機に送信する許可・実行手順ではありません。
実機の初回通電・flash・回転は人間の各承認と共通 bring-up procedure を先に満たす必要があります。

| ASCII command | 実装上の意味 |
|---|---|
| `SPD <0-100>` | PWM duty %。armed でなければ拒否 |
| `DIR <0|1>` | 0 forward / 1 reverse。armed かつ duty 0 のときのみ |
| `STOP` | 即座に duty 0。常に受理するが disarm はしない |
| `REARM` | U6 SHDN の power-cycle、I2C1 による U5 再 commissioning、latched fault を clear。最初の SPD と REQ-405/406 trip 後に必要。自動再開しない |

1行1 command で、終端は `\r`、`\n`、`\r\n`、`\n\r` に対応します。
Motor CSV は5 Hzで、IMU の非タグ行と区別します。

```text
MOTOR,millis_ms,armed,fault_latched,duty_pct,dir_reverse,fg_valid,rpm,mtrlck,lock_event_count
```

REQ-405 は FG 測定が **6000 RPM** を超えると SPEED 0・SHDN low にする latched trip です。
armed 中は STOP 後の coast-down も監視します。これは実装 threshold の引用で、
実機の安全保証ではありません。
旧 README の無負荷回転数と倍率には、[開発フローの古い引用事例](workflow.md)でも説明される
過去値が含まれます。この版ではそれを現在の安全余裕として再宣伝せず、
design §4.3 と現行の担当付き根拠・指摘を確認します。

REQ-406 は30秒 rolling window 内の3連続 Lock-Detection event で latched trip にし、
意図的な REARM を必要とします。設計理由は §4.4 です。
BEMF/FG の注意として原本は約500–1500 RPM の信号劣化・nuisance trip を記録し、
boot banner で開示しています。約103 RPM の open/closed-loop commutation transition は別の意味で、
firmware control loop と混同しません。詳しくは ECO-008 と design §4.6 を参照します。

## 実装しないこと

USB data/enumeration、wireless、PID/姿勢制御、sensor fusion、物理単位変換をしません。
**IMU を読んで motor を動かす経路、またはその逆はありません。**
共有するのは MCU、UART、main superloop です。REQ-405/406 は限定的安全 cutoff で、
姿勢・速度の制御ループではありません。

## build と過去の tooling 記録

原本は物理基板がなく、実機試験・flash をしていないと記録しています。
当時は `arm-none-eabi-gcc` 16.2.0 を確認し、PlatformIO と STM32CubeIDE/MX は不在でした。
両 subsystem の build は `-Wall -Wextra` で警告ゼロ、
`.text/.rodata` 14,752 bytes、`.bss` 108 bytes、`.data` 0 bytes と記録されています。
TIM3 vector の disassembly 確認も当時の結果です。今回の翻訳で build し直した結果ではありません。

toolchain がある場合の build は次です。まだない場合だけ、環境に適した方法で導入します。

```sh
# macOS で未導入の場合のみ。ほかの OS は適切な package を使用。
brew install arm-none-eabi-gcc
cd firmware/bench-imu-01
make
```

出力は `build/bench-imu-01.elf` / `.bin` / `.hex` です。
コンパイル成功は実機確認、独立受け入れ、flash 許可ではありません。
