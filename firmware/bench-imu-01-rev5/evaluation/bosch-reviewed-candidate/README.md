# Selected Bosch HIGH corrections

**MODIFIED / NOT_FOR_FLASH / NOT WHOLE-DRIVER APPROVAL**

This candidate addresses report-local A1, A2 and C1. It retains the previously
selected C2 initial-feature error gate. **C3 remains OPEN / MEDIUM**, deliberately
unmodified: immediate-ready callbacks do not validate the retained tail-handshake
predicate. General Aux long-read indexing and broader APS/status recovery remain
outside this correction.

Only three functions change from the earlier bounds-plus-C2 derivative:
`bmi2_write_aux_man_mode` uses a full-width data index and explicit byte-address
wrapping; `set_if_aux_not_busy` returns a failed status read; `read_aux_data`
returns an operation failure before advancing its destination/address counters.
The original headers, configuration blob and license are unchanged.

The selected `bmi2.c` is 376033 bytes with CRLF line endings, SHA-256
`4ad4f91eb09f380df678e2bf1098e4140092337a442390e98915f43b9b302204`.
[candidate.json](candidate.json) binds the ordered source/patch chain and all
test inputs. [bmi2-selected.patch](bmi2-selected.patch) is the combined
upstream-to-selected LF-view patch; [bmi2-aux-selected.patch](bmi2-aux-selected.patch)
is only the additional A1/A2 change.

## Host-only checks

Use Python 3.9+, an installed Clang with AddressSanitizer/UndefinedBehaviorSanitizer,
and a POSIX host. No SDK, Git history, device, network or package installation is
needed. Delays and bus responses are synthetic.

From a public checkout whose measurement vendor source has been explicitly
rebound to this candidate:

```sh
scratch="$(mktemp -d)"
scratch="$(cd "$scratch" && pwd -P)"
python3 -B firmware/bench-imu-01-rev5/evaluation/bosch-reviewed-candidate/run_host.py \
  --bmi2 firmware/bench-imu-01-rev5/measurement/vendor/bosch/bmi2.c \
  --expected-sha256 4ad4f91eb09f380df678e2bf1098e4140092337a442390e98915f43b9b302204 \
  --output-root "$scratch" --output "$scratch/host"
```

In the private candidate checkout, omit `--bmi2` and `--expected-sha256` to use
the adjacent candidate source. The public export needs no second driver copy.
An original, unmodified measurement source is rejected rather than silently
treated as the selected source.

The frozen matrix has **965 executions / 895 distinct declared input tuples**:
73 retained regressions, 652 expanded CRT cases, 136 Aux-write cases and 104
directly affected Aux-read cases. It covers both public CRT entry points, SPI
and I2C, length normalization and extents, selected error paths, Aux lengths
through 65535, address wrapping, guarded destinations and relevant APS/busy
states. Repeated legacy/new tuples are not counted as independent scenarios.

The runner requires the unchanged Bosch headers, `bmi270.c` and license plus
the two exact C fixtures listed in `candidate.json`. Historical patch/source
locations in its provenance chain are not hidden runtime dependencies.
`case-matrix.json`, `legacy-oracles.json` and the current fixture/runner hashes
are enforced before compilation. Explicit source selection enforces the exact
derivative hash. Existing outputs, symlinks and malformed selections fail
without a success-shaped result; diagnostics and failed-run logs are retained.

The original 25 bounds / 36 state / 12 early-error oracles are used on the new
source, not by rerunning their old campaigns. Old BLOCKED and NOT_RUN records
remain unchanged. A completed host report is author evidence, not independent
acceptance, target compilation, protocol qualification, merge or physical approval.

The private measurement/recording defaults and historical source locks remain
on their original source. Public measurement/N8R8 rebinding is a separate,
explicit PR operation; it does not approve the full Rev5 hardware or resolve
the FG35/36/37 conflict.

See [NOTICE.md](NOTICE.md) for the unchanged upstream license.
