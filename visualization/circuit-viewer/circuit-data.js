/*
 * circuit-data.js — Real component + net data for Bench-IMU-01, extracted from:
 *   - hardware/schematic/bench-imu-01/bench-imu-01.kicad_sch (kicad-cli sch export netlist)
 *   - bom/bench-imu-01-fab-bom.csv
 *   - firmware/bench-imu-01/src/main.c, motor.h, bmi270.h (actual implemented behavior)
 * No fabricated nets or behavior — every wire below corresponds to a real net name
 * in the exported netlist. Where a "future" concept is shown (Mode 3), it is
 * explicitly labeled NOT IMPLEMENTED, matching main.c's own scope-fence comment.
 */

// ---- Components (boxes) --------------------------------------------------
// x,y,w,h are SVG coordinates. category drives box accent styling (hub = MCU).
const COMPONENTS = [
  { id:'J1', x:30,  y:55,  w:100, h:85, ref:'J1', hub:false,
    nameEn:'USB-C Receptacle', nameJa:'USB-C レセプタクル', part:'USB4105-GF-A (GCT)',
    roleEn:'Power-only 5V input from a USB-C cable. D+/D- are deliberately left unconnected — this board has no USB data stack (REQ-105).',
    roleJa:'USB-Cケーブルからの電源専用5V入力。D+/D-はあえて未接続（このボードにUSBデータ機能はない, REQ-105）。',
    datasheet:null },
  { id:'U4', x:165, y:70,  w:70,  h:55, ref:'U4',
    nameEn:'ESD Protection', nameJa:'ESD保護IC', part:'USBLC6-2SC6 (ST)',
    roleEn:'Clamps ESD transients on the USB VBUS/D+/D- lines before they reach the LDO or MCU.',
    roleJa:'USBのVBUS/D+/D-ラインのESDサージをLDOやMCUに届く前にクランプ保護する。',
    datasheet:'https://www.st.com/resource/en/datasheet/usblc6-2sc6.pdf' },
  { id:'U3', x:265, y:70,  w:80,  h:55, ref:'U3',
    nameEn:'3.3V LDO Regulator', nameJa:'3.3V LDOレギュレータ', part:'TLV75533PDBVR (TI)',
    roleEn:'Regulates USB 5V down to the 3.3V logic rail (/3V3) that powers the MCU and IMU.',
    roleJa:'USBの5Vをロジック用3.3Vレール（/3V3）に降圧し、MCUとIMUに供給する。',
    datasheet:'https://www.ti.com/lit/ds/symlink/tlv755p.pdf' },
  { id:'U1', x:530, y:35,  w:210, h:300, ref:'U1', hub:true,
    nameEn:'STM32G031K8T6 (MCU)', nameJa:'STM32G031K8T6（MCU）', part:'STM32G031K8T6 (ST)',
    roleEn:'Central microcontroller. Reads the IMU over I2C2 and streams telemetry out UART; independently accepts UART speed commands and drives the motor driver — the two subsystems are deliberately NOT cross-wired yet (see main.c top comment).',
    roleJa:'中央のマイコン。I2C2でIMUを読みUARTへテレメトリ送信する系統と、UARTコマンドでモータードライバを制御する系統を持つが、両者は意図的にまだ接続されていない（main.c冒頭コメント参照）。',
    datasheet:'https://www.st.com/resource/en/datasheet/stm32g031k8.pdf' },
  { id:'U2', x:895, y:70,  w:120, h:90, ref:'U2',
    nameEn:'BMI270 (IMU)', nameJa:'BMI270（IMU）', part:'BMI270 (Bosch Sensortec)',
    roleEn:'6-axis accel+gyro sensor. Sampled at ≥100Hz over I2C2 (REQ-001); raw counts only, no unit conversion or fusion on this MCU.',
    roleJa:'6軸加速度・ジャイロセンサ。I2C2経由で100Hz以上でサンプリング（REQ-001）。生のレジスタ値のみで、単位変換やセンサフュージョンはこのMCU上では行わない。',
    datasheet:'https://www.bosch-sensortec.com/products/motion-sensors/imus/bmi270/' },
  { id:'SW1', x:165, y:400, w:55, h:55, ref:'SW1',
    nameEn:'Reset Button', nameJa:'リセットボタン', part:'SW_PUSH (generic 6mm THT)',
    roleEn:'Momentary push-button tied to NRST — manual MCU reset.',
    roleJa:'NRSTに接続されたタクトスイッチ。MCUを手動リセットする。', datasheet:null },
  { id:'D1', x:235, y:400, w:55, h:55, ref:'D1',
    nameEn:'Heartbeat LED', nameJa:'ハートビートLED', part:'LTST-C191KRKT (Lite-On)',
    roleEn:'PA5-driven status LED: 1Hz blink when the IMU is healthy, faster blink if BMI270 init failed (bmi_ok flag in main.c).',
    roleJa:'PA5で駆動されるステータスLED。IMU正常時は1Hz点滅、BMI270初期化失敗時は高速点滅に切り替わる（main.cのbmi_okフラグ）。',
    datasheet:null },
  { id:'J2', x:320, y:400, w:95, h:55, ref:'J2',
    nameEn:'UART Header', nameJa:'UARTヘッダ', part:'PREC004SAAN-RC (Sullins), 4-pin 2.54mm',
    roleEn:'USART2 TX/RX breakout — the only host communication link on this board (bench telemetry out, motor commands in).',
    roleJa:'USART2のTX/RXを引き出すヘッダ。このボード唯一のホスト通信経路（テレメトリ出力とモーターコマンド入力の両方）。',
    datasheet:null },
  { id:'J3', x:430, y:400, w:95, h:55, ref:'J3',
    nameEn:'SWD Header', nameJa:'SWDヘッダ', part:'PREC004SAAN-RC (Sullins), 4-pin 2.54mm',
    roleEn:'SWCLK/SWDIO/NRST/3V3 — programming &amp; debug only, not part of runtime data flow.',
    roleJa:'SWCLK/SWDIO/NRST/3V3。書き込み・デバッグ専用で、実行時のデータフローには関与しない。', datasheet:null },
  { id:'HOST', x:895, y:400, w:170, h:65, ref:'—',
    nameEn:'Host PC (bench operator)', nameJa:'ホストPC（ベンチ操作者）', part:'not a board component',
    roleEn:'A laptop/terminal connected via the UART header. Receives IMU CSV telemetry and sends ASCII speed-setpoint commands (see motor.h command grammar).',
    roleJa:'UARTヘッダに接続されるPC/ターミナル。IMUのCSVテレメトリを受信し、ASCII形式の速度指令を送信する（motor.hのコマンド文法参照）。',
    datasheet:null },

  { id:'J4', x:30,  y:640, w:90,  h:80, ref:'J4',
    nameEn:'DC Barrel Jack', nameJa:'DCバレルジャック', part:'PJ-102AH (Same Sky)',
    roleEn:'External motor-rail power input (VM_MOTOR_RAW). Tip/sleeve mapping is a disclosed ASSUMPTION pending mechanical-drawing verification.',
    roleJa:'外部モーター電源入力（VM_MOTOR_RAW）。チップ/スリーブの極性割当は仮定であり、実物の機械図での検証待ち。',
    datasheet:'https://www.sameskydevices.com/product/resource/pj-102ah.pdf' },
  { id:'F1', x:150, y:625, w:55, h:45, ref:'F1',
    nameEn:'PTC Fuse (power leg)', nameJa:'PTCヒューズ（電源側）', part:'30R500UF (Littelfuse)',
    roleEn:'Resettable fuse in series with the raw motor-rail input, before reverse-polarity protection.',
    roleJa:'モーター電源入力に直列で入る自己復帰型ヒューズ。逆接保護の手前に位置する。',
    datasheet:'https://www.littelfuse.com/assetdocs/littelfuse_ptc_30r_datasheet?assetguid=46bd151a-f029-4cec-aeef-2614869244f4' },
  { id:'F2', x:150, y:680, w:55, h:45, ref:'F2',
    nameEn:'PTC Fuse (GND leg)', nameJa:'PTCヒューズ（GND側）', part:'30R500UF (Littelfuse)',
    roleEn:'Second fuse added in the J4 GND return leg (ISS-032 fix) — protects against an internal J4 pin-mapping error that the power-leg diode alone cannot cover.',
    roleJa:'J4のGND側に追加された2本目のヒューズ（ISS-032対応）。J4内部の極性割当ミスに対し、電源側ダイオードだけではカバーできない経路を保護する。',
    datasheet:'https://www.littelfuse.com/assetdocs/littelfuse_ptc_30r_datasheet?assetguid=46bd151a-f029-4cec-aeef-2614869244f4' },
  { id:'D2', x:225, y:625, w:55, h:45, ref:'D2',
    nameEn:'Reverse-Polarity Protect', nameJa:'逆接保護ダイオード', part:'STPS3L60 (ST) Schottky',
    roleEn:'Series Schottky diode — blocks conduction if the barrel jack is wired with reversed polarity.',
    roleJa:'直列接続のショットキーダイオード。バレルジャックが逆極性で配線されても電流を遮断し保護する。',
    datasheet:'https://www.st.com/resource/en/datasheet/stps3l60.pdf' },
  { id:'D3', x:225, y:680, w:55, h:45, ref:'D3',
    nameEn:'TVS Surge Clamp', nameJa:'TVSサージ保護', part:'SMBJ16A (Littelfuse)',
    roleEn:'Unidirectional TVS diode across VM_MOTOR/GND — clamps voltage transients/surges on the motor rail.',
    roleJa:'VM_MOTORとGND間の単方向TVSダイオード。モーター電源ラインの電圧サージをクランプする。',
    datasheet:'https://www.littelfuse.com/products/tvs-diodes/automotive-and-commercial-vehicle/smbj/smbj16a' },
  { id:'U6', x:335, y:600, w:140, h:135, ref:'U6',
    nameEn:'eFuse / Load-Switch Supervisor', nameJa:'eFuse／ロードスイッチ監視IC', part:'TPS26631PWPR (TI)',
    roleEn:'Gates the entire motor rail. MCU (U1, U6_EN net) can arm/disarm it; internally protects on OVP/UVLO/ILIM (resistor-divider set).',
    roleJa:'モーターレール全体を開閉するゲートIC。MCU（U1、U6_ENネット）からアーム/ディスアーム可能。抵抗分圧で設定したOVP/UVLO/ILIMで内部保護も行う。',
    datasheet:'https://www.ti.com/lit/ds/symlink/tps2663.pdf' },
  { id:'U5', x:555, y:575, w:165, h:165, ref:'U5', hub:true,
    nameEn:'Sensorless BLDC Motor Driver', nameJa:'センサレスBLDCモータードライバ', part:'DRV10983PWPR (TI)',
    roleEn:'Drives the 3-phase reaction-wheel motor open-loop from the MCU\'s SPEED_PWM/DIR pins; reports back over I2C1 and a tachometer (FG) pulse.',
    roleJa:'MCUのSPEED_PWM/DIRピンからの指令でリアクションホイールモーターを3相・オープンループ駆動する。I2C1とタコメータ（FG）パルスでMCUへ状態を返す。',
    datasheet:'https://www.ti.com/lit/ds/symlink/drv10983.pdf' },
  { id:'M1', x:755, y:615, w:75, h:75, ref:'M1',
    nameEn:'Motor Phase Terminal Block', nameJa:'モーター相端子台', part:'MX126-5.0-03P (MaiXu)',
    roleEn:'3-position 5.0mm terminal block carrying the U/V/W phase wires to the off-board motor.',
    roleJa:'U/V/W相の配線をボード外のモーターへ渡す3極5.0mmピッチ端子台。', datasheet:null },
  { id:'MOTOR', x:900, y:600, w:150, h:120, ref:'(off-board)',
    nameEn:'Reaction-Wheel BLDC Motor', nameJa:'リアクションホイール用BLDCモーター', part:'T-Motor MN2206-13 KV2000',
    roleEn:'Off-board sensorless BLDC motor spinning a flywheel — the actuator for the (future) attitude-control loop; today driven purely open-loop for bring-up/characterization.',
    roleJa:'フライホイールを回すボード外のセンサレスBLDCモーター。将来の姿勢制御ループのアクチュエータだが、現時点では立ち上げ・特性評価のためオープンループで駆動されるのみ。',
    datasheet:null },
];

// virtual "future" ghost box (Mode 3 only)
const FUTURE_BOX = { id:'CTRL', x:895, y:230, w:170, h:70, ref:'—',
  nameEn:'Attitude Control Law (PID etc.)', nameJa:'姿勢制御則（PID等）',
  part:'NOT IMPLEMENTED / 未実装',
  roleEn:'Would read IMU orientation error and compute a corrected motor speed/torque command. Explicitly out of scope for the current firmware (main.c: "no control loop / attitude control / sensor fusion... Control Engineer territory, not yet triggered").',
  roleJa:'IMUの姿勢誤差を読み取り、補正後のモーター速度／トルク指令を計算する想定の機能。現行ファームウェアでは明示的にスコープ外（main.c: 「制御ループ・姿勢制御・センサフュージョンは実装しない、Control Engineer領域で未着手」）。',
  datasheet:null };

// ---- Wires ----------------------------------------------------------------
// category drives color + which mode tab shows/animates it.
// dir: 1 = animate from -> to, -1 = animate to -> from, 0 = no motion (static/debug)
const WIRES = [
  // ---- power: USB 5V / 3V3 logic rail ----
  { from:'J1', to:'U4', fromSide:'right', toSide:'left', category:'power5v', net:'VBUS_5V', dir:1 },
  { from:'J1', to:'U3', fromSide:'right', toSide:'top',  category:'power5v', net:'VBUS_5V', dir:1 },
  { from:'U3', to:'U1', fromSide:'right', toSide:'left', category:'power5v', net:'/3V3', dir:1, yoff:-15 },
  { from:'U3', to:'U2', fromSide:'right', toSide:'left', category:'power5v', net:'/3V3', dir:1, yoff:10 },

  // ---- power: external motor rail ----
  { from:'J4', to:'F1', fromSide:'right', toSide:'left', category:'powervm', net:'VM_MOTOR_RAW', dir:1 },
  { from:'F1', to:'D2', fromSide:'right', toSide:'left', category:'powervm', net:'VM_MOTOR_F1', dir:1 },
  { from:'D2', to:'U6', fromSide:'right', toSide:'left', category:'powervm', net:'VM_MOTOR', dir:1 },
  { from:'D3', to:'D2', fromSide:'top',   toSide:'bottom', category:'powervm', net:'VM_MOTOR', dir:0 },
  { from:'J4', to:'F2', fromSide:'bottom',toSide:'left', category:'powervm', net:'J4_GND_RAW', dir:1, yoff:20 },
  { from:'U6', to:'U5', fromSide:'right', toSide:'left', category:'powervm', net:'U5_VCC', dir:1 },
  { from:'U5', to:'M1', fromSide:'right', toSide:'left', category:'motorphase', net:'MOTOR_PHASE_U', dir:1, yoff:-18 },
  { from:'U5', to:'M1', fromSide:'right', toSide:'left', category:'motorphase', net:'MOTOR_PHASE_V', dir:1, yoff:0 },
  { from:'U5', to:'M1', fromSide:'right', toSide:'left', category:'motorphase', net:'MOTOR_PHASE_W', dir:1, yoff:18 },
  { from:'M1', to:'MOTOR', fromSide:'right', toSide:'left', category:'motorphase', net:'phase wires', dir:1 },

  // ---- data / control (bench mode) — corridor below U1 (x 560-895) is kept clear
  // of every other box specifically so these vertical runs never cross another part.
  { from:'U2', to:'U1', fromSide:'left', toSide:'right', category:'i2c', net:'I2C2_SCL/SDA', dir:1, yoff:-20 },
  { from:'U1', to:'HOST', fromSide:'right', toSide:'top', category:'uart', net:'UART_TX', dir:1, yoff:125, xoff:-45 },
  { from:'HOST', to:'U1', fromSide:'top', toSide:'right', category:'uart', net:'UART_RX', dir:1, yoff:145, xoff:15 },
  { from:'U1', to:'U6', fromSide:'bottom', toSide:'top', category:'ctrl', net:'U6_EN (SHDN)', dir:1, xoff:-70, toXoff:0 },
  { from:'U1', to:'U5', fromSide:'bottom', toSide:'top', category:'ctrl', net:'SPEED_PWM / DIR', dir:1, xoff:-15, toXoff:-30 },
  { from:'U1', to:'U5', fromSide:'bottom', toSide:'top', category:'i2c', net:'I2C1_SCL/SDA', dir:1, xoff:15, toXoff:0 },
  { from:'U5', to:'U1', fromSide:'top', toSide:'bottom', category:'feedback', net:'FG_TACH', dir:1, xoff:30, toXoff:45 },

  // ---- debug / static (all modes, dim, no motion) ----
  { from:'SW1', to:'U1', fromSide:'top', toSide:'left', category:'debug', net:'NRST', dir:0, yoff:80 },
  { from:'U1', to:'D1', fromSide:'left', toSide:'top', category:'debug', net:'LED_CTRL', dir:0, yoff:100 },
  { from:'U1', to:'J2', fromSide:'left', toSide:'top', category:'debug', net:'UART hdr', dir:0, yoff:120 },
  { from:'U1', to:'J3', fromSide:'left', toSide:'top', category:'debug', net:'SWD hdr', dir:0, yoff:140 },

  // ---- future (mode 3 only) ----
  { from:'U2', to:'CTRL', fromSide:'bottom', toSide:'top', category:'future', net:'orientation error (future)', dir:1 },
  { from:'CTRL', to:'U1', fromSide:'left', toSide:'right', category:'future', net:'corrected speed cmd (future)', dir:1, yoff:-60 },
];

const LEGEND = [
  { cat:'power5v',    en:'USB 5V / 3.3V logic power', ja:'USB 5V／3.3Vロジック電源' },
  { cat:'powervm',    en:'External motor-rail power (DC in)', ja:'外部モーター電源（DC入力）' },
  { cat:'motorphase', en:'3-phase motor current (U/V/W)', ja:'3相モーター電流（U/V/W）' },
  { cat:'i2c',        en:'I²C data (sensor / motor-driver)', ja:'I²Cデータ（センサ／モータードライバ）' },
  { cat:'uart',       en:'UART telemetry &amp; commands', ja:'UARTテレメトリ・コマンド' },
  { cat:'ctrl',       en:'Control signal (PWM / enable)', ja:'制御信号（PWM／イネーブル）' },
  { cat:'feedback',   en:'Safety feedback (tachometer)', ja:'安全フィードバック（タコメータ）' },
  { cat:'future',     en:'Not implemented yet (future work)', ja:'未実装（将来課題）' },
];

const BANNER = {
  power: { en:'<b>Mode 1 — Power Distribution:</b> USB 5V feeds the 3.3V logic rail (MCU + IMU). The external DC jack feeds a separately fused/protected motor rail through an eFuse supervisor into the motor driver and out to the 3-phase reaction-wheel motor.',
           ja:'<b>モード1：電源系統</b> USBの5Vはヒューズ保護された3.3Vロジックレール（MCU＋IMU）を供給。外部DCジャックは別系統でヒューズ・逆接保護されたモーターレールとなり、eFuse監視ICを経てモータードライバ、そして3相リアクションホイールモーターへ流れます。' },
  bench: { en:'<b>Mode 2 — Current behavior (Rev 3 firmware, as implemented):</b> The IMU path and the motor path are deliberately independent superloops sharing only this MCU. IMU→UART is one-way telemetry; Host→UART→PWM drives the motor open-loop; the FG tachometer feeds back for overspeed <i>safety</i> shutdown only — not for position/attitude control.',
           ja:'<b>モード2：現在の動作（Rev 3ファームウェアの実装通り）</b> IMU系統とモーター系統はこのMCUだけを共有する、意図的に独立した2つのループです。IMU→UARTは一方向のテレメトリのみ。ホスト→UART→PWMでモーターをオープンループ駆動。FGタコメータは過速度時の安全シャットダウンにのみ使われ、姿勢・位置制御には使われていません。' },
  future:{ en:'<b>Mode 3 — Future closed-loop attitude control:</b> This dashed path is <b>NOT implemented</b> today. main.c\'s own top comment explicitly fences it out: "any code path that reads the IMU and reacts by driving the motor... Control Engineer territory, not yet triggered." Shown here only to illustrate the eventual goal.',
           ja:'<b>モード3：将来の閉ループ姿勢制御</b> この破線経路は<b>現時点では未実装</b>です。main.c冒頭コメントで明示的にスコープ外とされています：「IMUを読み取りモーター駆動で反応するコードパスは実装しない…Control Engineer領域、未着手」。将来の目標を示すためだけに表示しています。' },
};
