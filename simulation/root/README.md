# CERN ROOT analysis interoperability

ROOT is used as a **columnar analysis/data-exchange framework**, not as the
rigid-body/contact solver. The primary references are the
[RDataFrame workflow](https://root.cern/manual/data_frame/) and
[TTree storage contract](https://root.cern/manual/trees/).

This host has ROOT **6.38.04**. Its Cling interpreter fails on a macOS C++
header/module-map mismatch (`__type_traits/add_lvalue_reference.h` missing,
then unresolved `cling::runtime::gCling`); PyROOT is absent from the local
simulation environment. A compiled TTree program can nevertheless write
and read the numeric records successfully. Native canvas/PNG rendering
was attempted and failed. These are different operation-specific statuses,
not a blanket claim that ROOT works or is unavailable.

The adapter deliberately uses **compiled, non-JIT TTree operations**.
It does not modify the global ROOT/SDK installation, install another toolchain,
or claim to have exercised RDataFrame, PyROOT or ROOT graphics.

```sh
# Repository root; requires existing root-config and c++.
simulation/.venv/bin/python simulation/root/export.py \
  simulation/evidence/startup-v3/startup-mechanism-fixture \
  --output simulation/runs/my-root-analysis
```

Outputs: native `trajectory.root`, `summary.json`, the unfiltered
`native-runtime.log` and source/output hashes in `manifest.json`.
The executable is compiled in ignored `simulation/runs/root-build/`.
Every source numeric column is written as a double branch, then reopened
and compared exactly, including the added `sample_dt_s` time weights.

The second tree, `time_weighted_wheel_x_rpm`, stores bin edges and simulated
seconds, not a naïve count of rows. Dense brake-window sampling would
otherwise overrepresent a few milliseconds. Weights use the interval to
the next recorded row; the final row has weight zero. This is a descriptive
left-hold histogram, **not** a replacement for the solver-stage mechanical
work/impulse integration.

On a healthy ROOT installation the file can be consumed through
`ROOT::RDataFrame("trajectory", "trajectory.root")`, filters and weighted
histograms. On this host use the compiled adapter and the simulator's
Matplotlib plots; interpreter/graphics remain explicitly capability-limited.
ROOT file metadata/UUIDs can differ across exports even when all numeric
branches reproduce exactly.
