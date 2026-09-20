# Rev5 ソフトウェア公開追補

[English](software.md) | [日本語](software.ja.md) | [元のv2公開](README.md)

**DERIVED_PUBLIC_EXPORT / WIP / NOT_FOR_FLASH**

独立レビュー済みの限定ソフトウェアを公開する追補です。Rev5全体の完成ではありません。
[全体モデルv2](https://ktanino10.github.io/ai-hardware-engineering-team/rev5-full-assembly-v2/index.html)
と元の公開manifestは変更しません。現在の公開baseには別途公開済みのv3、
Blender動画6本、オフラインIMUツールもあります。その実行用データは保持し、再生成しません。

元のsoftware・offline-tool manifestは当時の記録として保持します。
[software-continuation.json](software-continuation.json)が、意図して更新する補助ファイルを
元manifestのhashと現在のbytesへ結び付けます。共通検査は履歴の改変・重複path・
由来のない上書きを拒否します。不変のcode/data検査を省略したり、過去レビューを再発行したりしません。

## 選択された修正と残るfirmware制限

今回の修正対象はHIGHの3件、Aux書込みcounterの折返し、Auxエラー伝播と直接影響する
読出し経路、CRT configuration bufferの範囲超過です。既存の初回featureエラー修正は保持します。
修正の証拠と採用対象sourceは、下記の過去36テストのレビューとは別に結び付けます。

**C3はOPEN / MEDIUMのままで、修正対象に選ばれていません。**
残存するCRT末尾判定は、最後ではないtail chunkのready待機を省略したり、
1つだけの最終tail後に待機したりします。即時readyを返すhost modelでは、このprotocolを
受容できません。一般的なAux長文読出しのindex問題と、広範なAPS/statusエラー復旧も対象外です。

選択されたhost caseやCodeQLが成功しても、**firmware全体のrelease受容にはなりません**。
全体レビューは条件付きであり、このPRはmerge・flash・sensor実動作や物理操作の許可ではありません。

## 公開した範囲と保留

| 対象 | この追補 | 残る境界 |
|---|---|---|
| C1 readiness | [派生要約](software-c1-summary.json)。正確な型番候補10、製品UNKNOWN要件2、gap23、出典観測103 | **採用0・数量UNKNOWN・購入readiness CLOSED・発注不可**。CLI、元の生産用dataset、封印された私有電源入力は非公開。要約を代替入力として使わない |
| synthetic IMU | [CLI/API](../../simulation/imu_disagreement/README.md)、不変の最小estimator/helper、元の14テスト、正確な合成one-bias fixture | オフラインの合成SI・body座標・既知の合成時計だけ。実データ、健全性判定、自動除外、重み付け、校正・制御の適格性は含まない |
| N8R8評価 | [明示opt-in profile](../../firmware/bench-imu-01-rev5/evaluation/n8r8/README.md)、不変のapplication/pin/blob、明示選択した修正Bosch source、ライセンス、移植したtest | **NOT_FOR_FLASH**。C3はOPEN/MEDIUM。PSRAM無効でも全Rev5の**FG35/36/37競合は未解消**。SDK、tool snapshot、ELF/BIN、実機証拠は含まない |

元44件は **2 closed / 42 unfinished**、complete BOM・motor powerは **NOT_DONE**。
NO-GO / 3C8H / REQ409 / strict-pro / 39UNKNOWN、P1/C1/D1、RRT、
sidecar/ICD/controlとすべてのhuman/physical holdsを維持します。
購入・配線・組立・通電・初回flash・回転・製造・安全承認を与える公開ではありません。

## 公開checkoutだけで実行する

リポジトリのルートでPython 3.9以上を使います。今回のPythonコードは標準ライブラリだけで動き、
既存の大きなシミュレーターの依存パッケージは不要です。
私有Git object、元review受領記録、隠れた入力ファイルも不要です。

```sh
python3 -B -m unittest discover -s simulation/imu_disagreement/tests -v
python3 -B -m unittest discover -s tools/tests -p 'test_rev5_public_software.py' -v

out="$(mktemp -d)"
python3 -B -m simulation.imu_disagreement \
  --config docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/config.json \
  --samples docs/rev5-six-imu-fault-study-2026-09-13/author/run-001/one-bias/samples.jsonl \
  --output-dir "$out/report"
```

fixtureは元の1,201件の合成recordです。新しい出力先に`report.json`と`report.md`を作り、
既存directoryは拒否します。exit0は合成前提の下で全recordを比較できたという意味で、
**健康・正確という意味ではありません**。exit2は入力不適合、連続性異常、空入力、
比較対象不足などを示します。書込みエラーと部分出力は成功にしません。
メモリー上で処理する有限入力用であり、無制限streamや資源枯渇攻撃への適格性は未評価です。

gyro spreadは既存estimatorの等重みbody平均からの**最大ユークリッド距離**で、
標準偏差ではありません。2台未満ではspread/residualはnullであり、0や正常ではありません。
共通biasなら誤差があってもspread0になり、3対3では正しい側を決められません。
集計はrecord単位で時間重みではなく、truth/fault-label sidecarは読みません。
内部の姿勢値を出力したり制御へ接続したりしません。

## SDKを使わないN8R8確認

source/profileの5テストには**既存のCMake 3.16以上**と新規scratchが必要です。
ESP-IDF configure、firmware compile、実機アクセスは行いません。
CMake不足は実行前提の不足であり、skipしたPASSではありません。

```sh
cmake --version
REV5_EVAL_CMAKE="$(command -v cmake)" \
REV5_EVAL_TEST_SCRATCH="$(mktemp -d)" \
  python3 -B firmware/bench-imu-01-rev5/evaluation/n8r8/tests/test_profile.py -v
```

動的CMakeテストの本体は不変です。固定11入力を受け入れ、main・pin header・component登録を
改変した際に拒否することを検査します。元test fileの移植変更はpin参照のファイル名だけです。
assertionやCMakeテストを減らしたり、失敗を抑えたりしていません。

[U201参照](../../firmware/bench-imu-01-rev5/evaluation/n8r8/reference/u201-pin-reference.xml)は
**派生したソフトウェアテスト用の抜粋**で、完全なnative netlistではありません。
元native XMLから測定11pinと競合するFG3pinのnet/node属性をそのまま保持し、
端末パスと無関係な回路を除外しました。元hash・生成方法・全14行は
[source notes](software-source-notes.json)にあります。
ゲートの適用範囲を変えるためにhardware設計を移動・変更・承認していません。

生成pin header全体は競合するFG割当も含め不変です。元sourceのN8R2表記、
raw recordの`REV5B1` / `rev5-m1`、当時のreview-status欄も残しています。
実moduleのsuffixを特定する値ではなく、別ファイルの新しい限定レビュー要約を取り消しません。
N8R8測定subsetの評価profileであり、全Rev5の正式代替ではありません。

[選択したBosch sourceのhost確認](../../firmware/bench-imu-01-rev5/evaluation/bosch-reviewed-candidate/README.md)
は、別コピーではなく実際に選択したvendor sourceを対象にします。
POSIX hostのPython 3.9以上と既存Clang sanitizerを使い、965回の実行・895種類の入力tupleを
定義しています。bus応答とdelayは合成です。元のN8R8 5テストと動的CMakeテスト本体は保持し、
追加のsource/provenance 5テストで実byte・逆patchによる原版復元・driver/profile改変時の拒否を、
runner guard 5テストで不正入力の拒否を検査します。C3の修正・protocol受容にはなりません。

ESP-IDF buildは別の作業で、**今回の公開担当は実行していません**。
official SDK v5.5.2 commit `30aaf64524299d3bde422ca9a2848090d1bc5d0f`と対応toolchainが必要です。
installer、SDK本体、flash手順は追加せず、SDK不足のためにsource guardを緩めません。

## 独立レビューと今回の確認を区別

[software-review.json](software-review.json)は独立レビュー
`5d70e3126a5008904ff3d32ccdcda28cd26f1e29`
（技術結果`7b033d9fb7675ac1d2a6847cfc73b40422d52568`）のhash付き派生要約です。
限定した3つのsource scopeは**PASS、新しい具体的欠陥0、unit test 36件RUN/PASS**でした。
内訳はC1 18、IMU 14、N8R8 4です。

そのレビューのN8R8動的CMake 1件はhostにCMakeがなく**NOT_RUNのまま**です。
SDK/build/ELF/BIN/deviceは**対象外**、作者の過去build記録は**AUTHOR_REPORTED**であり、
独立した再実行ではありません。元の私有review/tool logは公開しません。

[software-checks.json](software-checks.json)は最初の公開担当の記録であり、
後続のBosch修正結果ではありません。continuation記録と現在のPRチェックを別に扱います。
CIでCMakeが成功しても過去NOT_RUNを上書きせず、公開包装の独立レビュー、firmware build、
実機受容とは扱いません。既存simulation workflowの元の数値回帰は変えず、
今回の有限チェックを追加します。必須check名・hardware gate・branch protectionは不変です。

## 生成元・ライセンス・再現できない範囲

[intake](software-intake.json)が固定sourceの許可リスト、
[manifest](software-manifest.json)が最初の公開snapshotのhashと変換区分です。
code/dataのbyte同一コピーと、説明・metadata・pin抜粋・test参照先の派生を区別します。
公開mainの祖先上に選択したblobだけを取り込み、私有branchはマージしません。
現在の意図した変更はcontinuation manifestに別記し、修正driverと対応する正確な
provenance/build metadataへ結び付けます。元のintake・review・check記録は書き換えません。

first-partyコードと合成fixtureはownerが公開を承認したプロジェクト成果です。
新たなproject/downstream licenseは作りません。BoschのBSD-3-Clause原文、通知、
出典、無変更のconfiguration blobを保持します。ESP-IDFは外部依存でlicenseだけを保持します。
[third-party notices](../../firmware/bench-imu-01-rev5/measurement/NOTICE.md)を参照してください。

不変のコード内のEvidence IDは**元source snapshotの意味**を保持します。
source notesの抜粋は新規DS採番や公開台帳の書換え、最新メーカー資料の再確認ではありません。
元のmeasurement source-lock、私有build/fix receipt、比較packet、完全なnative設計履歴は非公開です。
不変metadataに残る文字列は過去の参照先であり、実行時の隠れた依存や自動取得先ではありません。
公開testだけでこれらの過去監査を再現したとは主張しません。

非公開対象は、封印C1入力、raw upload/screenshot、メーカー原文document、
account/provider/reviewer/host log、SDK/tool snapshot、ELF/BIN、native CAD/media、
保留中のsidecar/control、進行中のv3/Blenderです。
過去の私有履歴の再構築、native CAD再生成、実機認定はできません。

## Pagesと公開状態

Pages artifact rootは従来どおり`visualization/`です。EN/JA入口からGitHub上のこの説明へ移動します。
CLIをブラウザー上で実行するサイトではありません。
PR CI、通常merge、remote file hash、Pages deploy・navigationは別々の実証であり、
実際のURLで記録します。ローカル文書の存在だけではmerge/deploy済みにはなりません。

戻す場合はこの追補だけを通常のreview付きrevertにし、同じ必須checkとPages deployを通します。
元v2は保持します。共有履歴reset、ゲート緩和、deploy未確認の「復旧済み」表示は行いません。
