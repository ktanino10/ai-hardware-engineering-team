# HC1 CLR/CLK driver layer — 条件付き接続案

**NOT_INDEPENDENTLY_REVIEWED / 未採用 / 未実装。通電・操作許可ではない。**

これは既存 HC1 の最終出力段を具体化する**新しいドキュメント上の配線案**であり、
KiCad の回路変更ではない。以下の `TDRV_X/Y/Z` と `TREQ` は別途提案する
TXU0304PWR の候補別名で、既設部品番号ではない。条件付き部品比較
`7bfc4c7` の推奨を使用し、新しい部品を正式選定してはいない。

## 1. 最初に固定した電源・帰路・権限の境界

| ドメイン | 凍結ソースにある実体／今回の扱い |
|---|---|
| H | `LOGIC_3V3`、U202.5 → U201.2。暫定サービス電源、供給能力・イベント中の維持は未適合確認 |
| VX | `DRV_3V3_X`、U301.9。FF_X/TDRV_X B 側/LX の候補電源 |
| VY | `DRV_3V3_Y`、U302.9。FF_Y/TDRV_Y B 側/LY の候補電源 |
| VZ | `DRV_3V3_Z`、U303.9。FF_Z/TDRV_Z B 側/LZ の候補電源 |
| C | **`C_SUPPLY_UNIMPLEMENTED`。電源、デバイス、出力ピンとも存在を確認できない境界**。H や三つの local rail に置換しない |
| GND | 既存の共通論理 GND。実帰路インピーダンス・連続性・電位差・ノイズは UNKNOWN。非絶縁方式 |

三つの VM 入力は実装された供給元を持たない。**MCU がリセットされても
LOCAL が生き残る、という仮定は置かない。** C の有効電圧範囲も未指定である。
TXU の ROC が広いことは、C 電源が存在することを意味しない。

今回の提案範囲は、C 側の**未実装の独立出力**から FF 端子までの具体的な
ドライバ配線である。独立出力そのもの、全 issuer の排除、freshness、
物理切断の観測／証明は実装していない。

根拠: 凍結 `integrated-contract.json` の電源・ピン・gaps、
DS-IFACE-002/058、HC1 と B authority map。
`PROPOSED-TXU-GROUND-FIRST` は GND 先行の追加出版案で、登録済み条件ではない。

## 2. X 軸の具体的配線：二つの TXU 出力が唯一の FF 入力源

```text
     C 側: 実デバイス・出力ピン・電源が未実装
     -----------------------------------------
     C_CLR_RELEASE_X o-------------------------- TDRV_X.2 A1
                         |                         |
                      R_A_CLR_X ?                  | A1 -> B1Y
                         |                         |
                        GND                TDRV_X.13 B1Y
                                                   |
                                   CLR_N_X --------+-------- FF_X.6 /CLR
                                      |
                                   R_CLR_X ?              FF_X = SN74LVC1G74DCTR
                                      |                   .2 D    -- VX
                                     GND                  .7 /PRE -- VX
                                                          .8 VCC  -- VX
     C_FRESH_CLK_X o---------------------------- TDRV_X.3 A2
                         |                         |
                      R_A_CLK_X ?                  | A2 -> B2Y
                         |                         |
                        GND                TDRV_X.12 B2Y
                                                   |
                                 ARM_CLK_X --------+-------- FF_X.1 CLK
                                      |
                                   R_CLK_X ?              FF_X.5 Q -- C_LX
                                      |                                |
                                     GND                    +----------+----------+
                                                            |          |          |
                                                          LX.1       LX.4     R_OFF_LX ?
                                                          SEL1       SEL2         |
                                                                                 GND

     C_DRV_ENABLE_X o-------------------------- TDRV_X.8 OE
                         |
                      R_OE_X ?
                         |
                        GND

     C_SUPPLY_UNIMPLEMENTED ------------------- TDRV_X.1 VCCA
                         +-- C_DRV_A_X ? -- GND
     VX = U301.9 ------------------------------ TDRV_X.14 VCCB
                         +-- C_DRV_B_X ? -- GND
     GND -------------------------------------- TDRV_X.7 / FF_X.4 / LX.7

     TDRV_X.4 A3  -> GND            TDRV_X.11 B3Y -> NC 出力
     TDRV_X.10 B4 -> GND            TDRV_X.5 A4Y  -> NC 出力
     TDRV_X.6 / .9 -> NC (内部接続なし)
     FF_X.3 /Q -> NC 出力
```

`?` は抵抗値／有効容量／MPN／公差／実装位置が未決定の位置であり、
実部品の選定ではない。各抵抗の .2 は GND、.1 は示した信号ネット。
FF の C_FF_X は従来 HC1 の VCC–GND バイパス位置を維持する。

**配線の理由**

- PW14 の A1.2→B1Y.13 を clear-release、A2.3→B2Y.12 を clock に使用する。
  LOW の clear-release は /CLR を LOW にする。反転器を暗黙に追加しない。
  [DS-IFACE-002/040/075]
- FF /PRE、D、VCC は同じ VX。PRE HIGH と CLR LOW の条件下だけ Q LOW。
  PRE/CLR 同時 LOW は Q と /Q が HIGH になる非安定条件である。
  PRE の rail tie は電源ランプ中の HIGH 保証ではない。[075]
- Q は二つの local SEL のみへ接続する。**TXU 出力の負荷は FF 入力一つと
  bias/配線等**であり、Q の二つの SEL 負荷とは別の問題。[039/040/075]
- A3/B4 は入力なので GND 固定。A4Y/B3Y は出力なので NC。内部 NC6/9 も
  未接続。5 MΩ TYP を外部配線の確実な parking 抵抗として使わない。
  [002/018/055]
- CLR/CLK の唯一の能動出力はそれぞれ TXU.13/.12。外部 supervisor、
  オープンドレイン reset、別の push-pull 源を重ねない。
  R_CLR は能動 HIGH に勝つ veto ではない。

## 3. 全三軸の対応と要求入力 TREQ

### 三つのローカルドライバを複製し、電源を混ぜない

| 候補 | VCCA.1 | VCCB.14 | B1Y.13 → | B2Y.12 → | Q.5 → |
|---|---|---|---|---|---|
| TDRV_X | 未実装 C | U301.9 / DRV_3V3_X | FF_X.6 / CLR_N_X | FF_X.1 / ARM_CLK_X | LX.1 と LX.4 |
| TDRV_Y | 未実装 C | U302.9 / DRV_3V3_Y | FF_Y.6 / CLR_N_Y | FF_Y.1 / ARM_CLK_Y | LY.1 と LY.4 |
| TDRV_Z | 未実装 C | U303.9 / DRV_3V3_Z | FF_Z.6 / CLR_N_Z | FF_Z.1 / ARM_CLK_Z | LZ.1 と LZ.4 |

各 OE.8 は別の `C_DRV_ENABLE_X/Y/Z`、A1.2 は
`C_CLR_RELEASE_X/Y/Z`、A2.3 は `C_FRESH_CLK_X/Y/Z`。
各々の**供給元 device.pin は null**であり、同名ポートの存在を実装と見なさない。
一つの C が共通故障源になり得ることも残る。三軸構成は冗長性認証ではない。

### 要求を伝えるだけの別パッケージ

```text
未割当 H requester 出力                   未実装 C validator 入力
H_REQ_DATA   o-- TREQ.2 A1 -> B1Y.13 ------o C_REQ_DATA
H_REQ_STROBE o-- TREQ.3 A2 -> B2Y.12 ------o C_REQ_STROBE
                    TREQ.1 VCCA = H
                    TREQ.14 VCCB = C_SUPPLY_UNIMPLEMENTED
未実装 C enable o--- TREQ.8 OE
                    TREQ.7 GND
                    .4 A3 / .10 B4 = GND
                    .5 A4Y / .11 B3Y / .6 NC / .9 NC = 未接続
```

H 入力二本、C 出力二本、OE に各一つの GND 向き bias 位置
`R_REQ_HD/HS/CD/CS/OE` を置く候補。TREQ.1–.7 と .14–.7 にそれぞれ
`C_REQ_H/C_REQ_C` バイパス位置を提案する。値は UNKNOWN。
OE は C 側の独立源から駆動する候補で、TXU の either-rail reference
機能を使う。[002/055]

これは **DATA/STROBE の物理層候補だけ**である。新しい MCU GPIO を割当てず、
UART ログ線、GPIO42/47、SW201、既存 command/FG 経路を流用しない。
フレーム、レート、epoch 保管、parser、ACK 復路、通信完了検出は未実装。
fresh issuer/event/old∪new∪shared/configuration を検証するための内容は
この二本の電圧や strobe 一発では表現・検証済みにならない。

**TREQ.12/.13 から TDRV の A1/A2/OE へ直接つながる線はない。**
間に必要な C validator/authority は具体的に未実装と記録する。
もし後でそこを直結すれば、CPU 要求の level shifter にすぎず、独立権限という
前提は成立しない。部品 crossing 自体は C5 を供給しない。

## 4. Bias、負荷、エッジ、電源の閉じていない条件

### 登録済み事実で言える範囲

- 両 TXU rail が**ちょうど 3 V**の source point では、data HIGH は
  VT+ MAX 1.92 V より上、LOW は VT- MIN 0.89 V より下で判定する。
  [DS-IFACE-014]。同じ OE の追加行は `source-proposals.json` の
  PROPOSED handles であり、まだ canonically registered ではない。
- TXU の 100 µA source/sink **それぞれの試験点**では、
  3 V の VOH MIN 2.9 V、VOL MAX 0.1 V。FF の VIH 2 V/VIL 0.8 V との差は
  算術上 0.9 V/0.7 V。ただし実負荷、return/noise、信号品質込みの余裕は UNKNOWN。
  [015/056/075]
- 10 mA sink 試験の VOL MAX 0.8 V は FF LOW 上限と等しい。
  正の LOW noise allowance は残らない。この点を軽負荷の証明に流用しない。
  そもそも local の 5 mA 外部供給枠と無関係な自由負荷を設定しない。[056/MTR-116]
- C/H/VL の3.0～3.6 V全域、または異なる rail 電圧の data/OE threshold
  surface は、確認した p7 の離散同電圧行では埋まらない。**PDF は入手済みだが
  必要な連続範囲の保証はその表に記載されていない**。補間しない。
- TXU の Schmitt input は slow input に許容性がある一方、電流増加がある。
  出力は push-pull。軽負荷の ringing に注意という記述は、FF 入力での
  slew/monotonicity を保証する数値ではない。[055]

### 今回は値を選べない理由

high-Z 時は、正負の injection、初期電荷、実 C、R 公差、ground/noise によって
LOW 到達電圧と時刻が変わる。IOZ の rail/GND endpoint 試験と、
Ioff の片 rail=0 試験、Ioff-float の GND 入出力・外部 leakage≤10 nA 条件を
混ぜて一つの全状態 leakage 合計にしない。[016/056]

能動 HIGH 時の `V/R + receiver + wiring/protection` 負荷、能動 LOW 時の
sink/source の向き、disabled 時の放電を**同じ R で同時に満たす**必要がある。
今回の出力段は値未定のままなので、「bias あり → safe LOW」とは判定しない。

FF CLK と /CLR は ordinary LVC 入力であり、3.3 V±0.3 V の入力遷移要件
10 ns/V 以下は残る。[039]。TXU **入力**が Schmitt でも、TXU high-Z 化後の
R–C 放電で FF に入る遅いエッジは改善されない。
HOLD 入力容量の新しい 5 pF **TYP**を最大値に昇格して TXU の 5 pF fixture と
同一視しない。今回その HOLD 原本は再読していない。

### バイパス／電源のローカル提案

TDRV 三個×二電源と TREQ×二電源で **八つの新しい bypass 位置**。
原本の 0.1 µF 推奨は `PROPOSED-TXU-BYPASS` の application recommendation
で、最小有効容量でも、新規 capacitor MPN 採用でもない。可能な限り IC の
近くという指示に任意の mm 値を付けない。DTR12 の layout 図を PW14 に流用しない。

電源負荷は `proposal.json/local_power_proposal` に H、C、VX/VY/VZ ごとに記載。
四個の combined-static source test を足した **24 µA** は全デバイスの
両電源合計の**同条件試験上限**のみ。bias 駆動、動的電流、C controller 自体、
起動時容量充電を含まず、実消費や各 rail の残余枠ではない。[002]
実際の local 5 mA 枠には既存 pull/load、RA/TCA/TMUX/FF と新 TDRV を含める。
Q と CLR/CLK の出力が供給する bias 電流を二重計上しない。

`hardware/power-budget.md` は変更しない。このローカル提案を正式統合する場合の
未解決 load delta であり、実サブシステム追加や power architecture の採用ではない。

## 5. OE は rejoin clock ではない：具体的順序と失敗

| 状態／事象 | 必要な順序と、実際に残る失敗 |
|---|---|
| Cold start | GND/rail/入力が未適合なら Q は UNKNOWN。OE 内部 pull と FF の rail tie では POR を作れない |
| 初期化 | 有効 power/return/load を別途成立させ、A1=A2=LOW、OE=LOW → OE=HIGH、CLR/CLK LOW を成立させる。観測手段や保証遅延は未実装 |
| Normal ON から withdraw | 変更前の q と対象を凍結し、queue/ISR 等を disposition。OE=HIGH のまま A1 を LOW にして active clear、その間に A2 を LOW に戻す |
| Event hold | PRE HIGH、CLR LOW、有効供給・負荷の条件なら Q LOW。[075]。全六極・tail・B/X・権限成立前に event を開始しない |
| CLK が stale HIGH | CLR が有効 LOW の間だけ capture を抑止できる。解除前に必ず CLK LOW。CLR が stuck HIGH、または power invalid ならこの論拠は消える |
| OE が復帰 | A1=A2=stale HIGH なら CLR と CLK の到着順序は保証されない。CLR 先行→CLK rising で fresh request なしに Q HIGH、または recovery 違反。CLK 先行なら Q LOW が残る可能性もあり、どちらも service 証明ではない |
| C power が off | VL が有効で055条件を満たせば TXU high-Z。これは強制 LOW ではない。復帰時の retained HIGH は OE 復帰と同じ競合 |
| LOCAL power が off | FF は TXU の <100 mV 判定より前に使用した operating bin を外れる。Q/PRE/SEL/切断維持を保証できない。0 V の Ioff は Q LOW ではない |
| OE disable 中の電荷 | B 出力が high-Z になっても CLR/CLK の電荷・leakage により LOW 時刻と edge は UNKNOWN。CLR HIGH 中の ringing が clock になり得る |
| C/driver stuck HIGH | pull-down と別 push-pull HIGH を戦わせない。独立故障検出、veto、保持電源、故障被覆は未実装 |
| Partial transaction / cancel | 開く前に clocked write や reset が実行済みなら rollback されない。後から ACK、IDLE、timeout を返しても復元しない |
| Fresh useful rejoin | Event と遅延作用の終了、transaction disposition、新 epoch、rails/host/TCA/端子を再適合確認。CLR LOW 中に CLK LOW → clean CLR release → FF recovery/setup/hold → 新規の一つの適合 clock pulse → CLK LOW。その後実正常通信を別途適合確認 |

RX strobe の held HIGH に対しても同じ問題がある。TREQ の OE/電源復帰時に
**正しく HIGH を伝達すること**は、誤 glitch ではなくても C には rising edge に
見える。release-before-new-transition だけで fresh epoch や intent は証明できない。
未実装の validator はそれらを検証しない限り CLR/CLK を生成してはならない。

原本の glitch-free statement [018/055] を否定しているのではない。
**「本来 LOW のはずなのに誤 HIGH」と「以前の HIGH を復帰後に正しく伝達」は別**
であり、後者は fresh pulse の保証にならない。

FF の pulse MIN 2.7 ns、setup 1.3 ns、hold/recovery 1.2 ns [039] は
受信端の条件であり、生成済みの波形ではない。TXU 伝搬 0.5～11 ns [057]、
enable 6.6～29 ns [PROPOSED]、disable 18.5～42 ns [057] の marker は
FF の threshold と同じではない。CLR 解除と clock の差に任意の ns を決めず、
各 FF ピンでの最遅 release／最早 capture と誤差込みで条件を満たす必要がある。
**これらを足した event-completion timer は存在しない。**

## 6. 維持する A1／既存回路／全17 issuer 境界

`proposal.json/all17_issuer_boundary` は B の **17 keys を欠落なく個別に保持**。
現在の app entry、UART setup/progress、IMU pin/setup/reset、SPI route/transaction、
SDK restart/panic、I2C remap/reset/async、direct GPIO/mux/OE/pull/hold、
CPU debug、external debug、EN/boot/power、privileged/ISR/DMA/ROM のどれにも、
TREQ/TDRV だけでは enforceable gate を追加できない。

特に SW201.1 は `MCU_EN` に直結し U201.3 を reset する。
それを TREQ への request に読み替えない。SW202 の boot、J201 電源抜去、
noos/ROM/raw writer、CPU halt 後の probe access も残る。
GPIO39/40/41 と JTAG alias の問題、三つの 0x52 domain と二つの hardware I2C
resource、未割当 GPIO42/47 も変更しない。

今回追加する制御段の下流でも、local witness は次の六極である:
`LX.2-3 / LX.5-6 / LY.2-3 / LY.5-6 / LZ.2-3 / LZ.5-6`。
五つの TMUX の24 used S/D terminals、八つの unused channels、H0/H1、
TCA9517 の active release/tails、RA/RB、全 terminal/rail/return の ROC と
signed current/charge/transient は残る。

例えば3.6 V terminal と1.5≤TMUX VDD<1.8 V の組合せは powered signal ROC
を満たさない [071/074]。その TMUX が非 witness の host 側でも免除されない。
Q/CLR/SEL、request ACK、software success は物理導通の測定ではない。
A1 C1–C5、数値 B、実 X、維持時間／conformance が UNKNOWN なら event は
**NOT_AUTHORIZABLE**。永久 OFF を「正常 service 成功」と数えない。

九つの SPEED/DIR/FG endpoint 経路は一切流用しない。
本凍結 integrated graph 自体はこの新 control layer を実装しておらず、
既存文書の proposed path を as-built とも断定しない。
Bus permission は motor inhibit、no-motion、残存エネルギー排除ではない。

## 7. AXC 前提の狭い補正／設計義務／次の handoff

AXC 原本の section7.1/Table7-1 を必要な分だけ再確認した。
**DIR=HIGH、/OE=LOW が A→B**であり、固定方向なら DIR1/2 を
自身の VCCA に tie する候補を検討できる。追加の動的 GPIO/controller は必須ではない。
`PROPOSED-AXC-DIR` として記録し、「DIR が増えるから必ず追加 controller」
という強すぎる棄却理由は今回の案では使わない。
TXU は固定方向・既登録 disconnected-rail scope 等による条件付き選好のまま。
AXC の不可能性、部品変更、ISO 再評価、old RAW_NOT_REVERIFIED の修正ではない。

18 項目の設計義務と Hardware checklist の未解決点は `proposal.json` にある。
四個の package、八つの bypass は将来の面積／熱／帰路／保護／配置検討を増やす。
rotating-body 振動による solder/connector stress、局所加熱による IMU bias drift
も未適合確認である。geometry や PCB を更新していない。

新 `check.py` はこの新接続、17 key の対応、source bindings、
driver-specific な論理反例を確認するだけ。ERC/DRC/SPICE、analog simulation、
機器操作、完全回路検証、独立 review は実行していない。
既存 HC1 の CONDITIONAL/0 new findings は保存し、この新案へ引き継がない。

Sole Lead へ: C 実体と power、要求／freshness protocol、各 node の signed load・
bias・loaded edge、全 issuer の実排除、数値 B/実 X が最小の未解決入力。
必要な七つの PROPOSED 行を通常の serial publication で処理し、
停止済み同一 bytes の intake/commit の後に新しい独立 review を行う。
**NO-GO / P1 conditional /3C8H /REQ409 /oldfive /foreign.pro strict /
旧13 closed tasks /全 physical・human gates を維持する。**
