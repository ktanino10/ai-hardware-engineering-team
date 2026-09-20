# Changed-scope independent review — selected scope PASS

> Public reading edition: technical verdict, findings and results are unchanged. Source links are pinned to the reviewed public commit; four private evidence links are withheld. Original response SHA-256: `b0e2573f3232e1edfba20dcba0fb1dcb3d1501e55b19d9cd45c4f255d6e68981`.

**A1, A2 and C1 are RESOLVED for public commit `31031c25d421ad0f793c746a0bf47d356e7ac433`, without reducing their original HIGH severities. C2 is preserved and verified. No new concrete blocker was found in the reviewed changed/affected scope.**

**Overall firmware release acceptance remains CONDITIONAL. C3 remains OPEN/MEDIUM, explicitly unselected and unrepaired.** This verdict does not authorize publication, merge, target execution, flashing or physical use.

## Reviewed identity and scope

| Item | Independently verified value |
|---|---|
| Task/run | `rev5-bosch-selected-public-review` / `1f29d75b-88bb-43fc-9058-993dbecababd` |
| Public source and configuration commit | `31031c25d421ad0f793c746a0bf47d356e7ac433` |
| Actual selected source | [Measurement vendor `bmi2.c`][source] |
| Source SHA-256 | `4ad4f91eb09f380df678e2bf1098e4140092337a442390e98915f43b9b302204` |
| Encoding/size | 376,033 bytes; 11,765 CRLF line endings; no bare LF or CR |
| Final preservation check | All 37 snapshotted public inputs unchanged; tracked worktree clean at the same HEAD |

I read the current reviewer profile, firmware-review skill and applicable instructions; the new patches, fixtures, runner, matrix declaration, validation tests, public correction records and consumer bindings. Unchanged headers, blob and reused fixtures were checked by exact identity rather than repeating the previous baseline investigation.

The Aux-only patch reverses **in memory** to the previously reviewed pre-Aux hash:

`8ce40c9da0ec462e0ea8700ba702be303faa4803d762de2105ded5d3dc4c39ed`.

Only the three declared Aux functions differ from that source. The combined patch reconstructs the original upstream hash:

`c3f912bc3033b411fa8df67dbdf66f5b3d74cf203b2e8aa4a8c834821116c2b3`.

Reconstruction was an integrity check, not compilation or execution of an old source campaign.

## Finding dispositions

All line references below identify the exact selected [public driver][source].

| Finding | Disposition | Source and independent reasoning |
|---|---|---|
| **A1 — Aux write-counter wraparound** | **HIGH / RESOLVED** | `bmi2_write_aux_man_mode`, lines 4047–4102, particularly 4053 and 4076–4079. The index is now `uint16_t`; only the register address is explicitly converted to `uint8_t`. Data indexing therefore progresses through the full public length domain while register addresses retain modulo-256 behavior. |
| **A2 — Aux error propagation and affected read consumer** | **HIGH / RESOLVED within selected scope** | `set_if_aux_not_busy`, lines 6095–6138, now returns a failed status operation immediately at 6109–6113. `read_aux_data`, lines 6589–6655, returns an operation failure before address/count/remaining-length progression. This closes the previously identified short-buffer recovery path, rather than fixing the shared helper alone. |
| **C1 — CRT configuration-buffer bounds** | **HIGH / RESOLVED** | `write_crt_config_file`, lines 10181–10287, retains the validated endpoint, full-width remainder, even-word constraints and per-transfer remaining-extent checks. The supported public-entry normalization remains in `do_gtrigger_test`, lines 10380–10466. New execution covers both public APIs and both transports. |
| **C2 — Initial feature error gate** | **Preserved and verified** | The immediate return following `get_maxburst_len`, lines 10420–10424, remains intact. Initial feature failures return through both public entry points without subsequent trigger/upload activity. This is not a broader APS/status-error repair. |
| **C3 — Tail-finality/readiness logic** | **OPEN / MEDIUM, unchanged** | The retained predicate at line 10273 is unchanged. No C3 correction or delayed-readiness qualification was performed. |

Both CRT function bodies are byte-identical, after consistent LF normalization, to the previously reviewed bounds+C2 candidate. Their current manifest hashes include the terminating newline; removing that newline reproduces the earlier review’s function hashes. This is a hashing-convention difference, not a source change.

For A1, all four maximum-length combinations—SPI/I2C with APS initially enabled/disabled—completed exactly **65,535 bytes**. Their transport callback counts were respectively 196,605 without APS transitions and 196,609 with them. The tests also exercised lengths 255, 256 and 257 and register-address boundary crossings.

## Oracle assessment

I inspected the new [Aux fixture][aux], [CRT fixture][crt], [matrix declaration][declare] and [runner][runner], rather than accepting aggregate PASS labels.

The Aux model checks operation order, expected register addresses, byte values, completed prefixes and exact error-stop behavior. Its pattern is not 256-byte periodic, so replaying the first 256 bytes cannot masquerade as correct progression. Sixteen-byte destination guards and checks of the untouched suffix supplement ASan, including the one-byte and partial-final-burst read cases.

A2 failure coverage includes data, status and address operations; failures before and after the 255/256 boundary; status failure following busy polls; and first/later read transactions. The callback sentinel is `-7`, while the expected public result is the driver’s mapped error—not an assumed identity between callback and API return codes. Subsequent I/O after the injected failure is rejected.

CRT checks validate normalization before the first entry callback, encoded word offsets, ordered coverage, invalid extents, null inputs, first-feature suboperations and full/tail transfer failures. Their immediate-ready model remains unsuitable for qualifying C3, as explicitly documented.

I also regenerated the declaration **in memory** and matched the committed matrix. Case identifiers are suite-scoped. An initial reviewer-only assertion incorrectly assumed global uniqueness of bare IDs; checking `(suite, ID)` established all 965 execution identities correctly. No source, fixture or acceptance assertion was changed to obtain a pass.

## Independent execution results

I independently ran the complete suite **once against the actual public vendor path**, using explicit `--bmi2` and `--expected-sha256` arguments. No adjacent candidate driver copy exists or was compiled.

| Executed group | Result |
|---|---:|
| Retained scenarios on the selected source: bounds 25, controls 36, initial-error 12 | **73 PASS** |
| Expanded CRT cases | **652 PASS** |
| Aux-write cases | **136 PASS** |
| Directly affected Aux-read cases | **104 PASS** |
| **Total** | **965 executions PASS / 895 distinct declared tuples** |
| Runner guard unit tests | **5 PASS** |
| Public source/provenance/rebinding unit tests | **5 PASS** |
| Unchanged N8R8 profile/source-guard tests | **5 PASS** |

Actual tools were Python **3.9.6**, Apple Clang **21.0.0**, and the supplied session-local CMake **3.31.6**. Host compilation used `-Wall -Wextra -Werror`, ASan, UBSan and stack-use-after-return detection.

Every compiler/host execution command returned zero, with **empty compiler/runtime stderr**. I separately read back the raw case outputs, completion counts, command receipts and hashes. The 15 unit tests also completed without failures or skips.

The unchanged runner retains its `AUTHOR_HOST_ONLY` labels. Those labels were not edited; this report separately attests my independent execution and verdict. The 73 retained scenarios exercised the **new selected source**, not original or historical candidate binaries.

## Consumer and provenance conclusions

**The public rebinding is effective at the source-selection and guard level.**

The unchanged [measurement component registration][component] compiles the actual vendor source tested here. N8R8 still selects that same measurement component through `EXTRA_COMPONENT_DIRS`; it has no forked C implementation.

I verified that the [eleven-input source contract][guard] changed only the selected driver hash and measurement-profile hash. The profile change is limited to the driver description, binding and scope disclosure. Application, pin definitions, SDK defaults, wire identity and acquisition settings remain unchanged.

The CMake tests accepted the exact frozen inputs and rejected modified driver, profile, application, pin-header and component-registration bytes. These were **SDK-free script-mode checks**, not an ESP-IDF configure/build.

Current [vendor provenance][provenance] truthfully marks `bmi2.c` as modified, records the selected hash/size, and separately preserves the upstream original hash, size and URL. The other five vendor files remain identical. The extracted 8192-byte blob remains:

`2d75e68e343a13ff99be98261dfbd99d9e8c6f267da9e3c5aeb883276ad178db`.

The public correction record distinguishes current bindings from immutable producer/historical locators. I did not interpret the absent adjacent derivative path as the compiled source, or globally adopt private recording/defaults.

## Evidence and remaining limits

Raw host, unit-test, input-snapshot and readback receipts are retained privately; they are not distributed with this public reading edition.

The host report SHA-256 is:

`a8fe9e30be911394e054adec3e06d1a6db09525d8ad055dabaa03a36ebbb7dd8`.

**Selected-scope PASS does not close C3 or the excluded general Aux long-read indexing and broader APS/status-recovery issues.** Buffer guarantees still require truthful caller allocation/extent information and valid callback contracts.

Target/SDK build, ELF/BIN qualification, device access, physical timing, current CI/CodeQL, publication and merge were **NOT_RUN**. Original 3C8H, REQ409, NOT_FOR_FLASH and all human/physical gates remain unchanged. No sources or historical records were modified, no additional actor was spawned, and no coordinator start/finish operation was performed.

[source]: https://github.com/ktanino10/ai-hardware-engineering-team/blob/31031c25d421ad0f793c746a0bf47d356e7ac433/firmware/bench-imu-01-rev5/measurement/vendor/bosch/bmi2.c
[aux]: https://github.com/ktanino10/ai-hardware-engineering-team/blob/31031c25d421ad0f793c746a0bf47d356e7ac433/firmware/bench-imu-01-rev5/evaluation/bosch-reviewed-candidate/aux_selected.c
[crt]: https://github.com/ktanino10/ai-hardware-engineering-team/blob/31031c25d421ad0f793c746a0bf47d356e7ac433/firmware/bench-imu-01-rev5/evaluation/bosch-reviewed-candidate/crt_selected.c
[declare]: https://github.com/ktanino10/ai-hardware-engineering-team/blob/31031c25d421ad0f793c746a0bf47d356e7ac433/firmware/bench-imu-01-rev5/evaluation/bosch-reviewed-candidate/declare_matrix.py
[runner]: https://github.com/ktanino10/ai-hardware-engineering-team/blob/31031c25d421ad0f793c746a0bf47d356e7ac433/firmware/bench-imu-01-rev5/evaluation/bosch-reviewed-candidate/run_host.py
[component]: https://github.com/ktanino10/ai-hardware-engineering-team/blob/31031c25d421ad0f793c746a0bf47d356e7ac433/firmware/bench-imu-01-rev5/measurement/main/CMakeLists.txt
[guard]: https://github.com/ktanino10/ai-hardware-engineering-team/blob/31031c25d421ad0f793c746a0bf47d356e7ac433/firmware/bench-imu-01-rev5/evaluation/n8r8/source-contract.cmake
[provenance]: https://github.com/ktanino10/ai-hardware-engineering-team/blob/31031c25d421ad0f793c746a0bf47d356e7ac433/firmware/bench-imu-01-rev5/measurement/vendor/bosch/provenance.json
