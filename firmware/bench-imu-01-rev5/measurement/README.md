# Frozen Rev5 measurement source dependency

[Public guide](../../../docs/rev5-public-release/software.md) |
[日本語](../../../docs/rev5-public-release/software.ja.md) |
[N8R8 evaluation](../evaluation/n8r8/README.md)

**NOT_FOR_FLASH / SOURCE DEPENDENCY ONLY / NOT HARDWARE APPROVAL**

This is the unchanged minimum measurement component required by the N8R8
evaluation profile. `main/main.c` is the corrected application at source
`962ce7e977c25263ca58429a62e61beb8b12a9ec`, SHA-256
`bc835654d70d8f422f190cd00b135ad2f50f85b61d91a763b9641a2024f20e05`.
The export is bound to `3db7ea5e74bfaf7c286383d6ee29926f347a2297`.

The C source, component registration, defaults, measurement profile and pin
header are not edited. `measurement/CMakeLists.txt` remains the historical
N8R2 baseline; choosing it is not choosing the N8R8 opt-in project.
The six-BMI270 application emits uncorrected raw counts with `REV5B1` /
`rev5-m1`, not SI, calibration, fusion, control or reset-unique clock mapping.
The original guards and all full-header FG conflicts remain.

Only the required source/profile/pin/vendor/license closure is public.
Original `source-lock.json`, build reports, fix receipts, host regression
tools and private tool installations are not copied. References to them in
unchanged source are historical provenance, not files fetched by public tests.
The public [source notes](../../../docs/rev5-public-release/software-source-notes.json)
provide selected manufacturer/evidence metadata without republishing raw
documents or inventing canonical IDs. The profile's pin projection does not
replace the complete native design.

This publication does not build or run firmware. See the evaluation guide
for SDK-free tests and exact external SDK prerequisites. Historical author
build claims are not new independent execution. All physical holds remain;
no flash or device instructions are provided.

Read [NOTICE.md](NOTICE.md) and the genuine vendor licenses before reuse.
Owner-authorized first-party publication does not create a project license.
