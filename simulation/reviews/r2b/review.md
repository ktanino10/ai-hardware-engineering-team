# R2b — Final parent-transform closure

**Verdict: PASS for this bounded implementation/evidence closure.**
**SIM-R2A-001 is RESOLVED.** No previously reported concrete implementation
finding remains open in the reviewed numerical/evidence pipeline. This is
not physical feasibility/safety, resolved flight, capture or Fusion approval.

## Boundary

- Independent reviewer: GitHub Copilot, continuing the independent
  Simulation Reviewer context; not the implementation author.
- Date: **2026-09-06 JST**.
- Frozen HEAD: `7512042dcdf773935a0a528ee9d4617787317da3`.
- Checker/test correction: `1e871634f126de7aa9286954e1761d8bb7979837`.
- Rechecked only the small checker/negative-test change, good native file,
  existing saved 10 mm counterexample and current v6 receipt bindings.
- R1/R2/R2a are preserved. No implementation edits, agents, commits,
  live-scene access, dynamics rerun, ROOT/startup reinvestigation or new
  physical/model assumptions.

## Fix and independent results

The checker now explicitly rejects nonidentity parent inverses on display
edges, rotor pivots/meshes and markers. It additionally constructs and checks
every fixed display edge's expected **complete world matrix at every
recorded frame**. Thus acceptance no longer relies only on local edge
position/rotation/scale. The production negative test includes the saved
edge-parent-inverse mutation.

Using my own [`witness.py`](witness.py), in isolated Blender 5.1.1 with
`--background --factory-startup --threads 2 --python-exit-code 1`:

1. **GOOD:** the delivered v6 native file passed all **250 frames** with
   `NATIVE_REOPEN_TRANSFORMS_GEOMETRY_AND_SOURCES_MATCH`. My fresh receipt
   matches the delivered receipt exactly.
2. **Existing counterexample:** I changed one `Visual_cube_edge` parent
   inverse by +10 mm X, saved a separate scratch `.blend`, reopened it and
   invoked the current checker. Measured world displacement was
   **0.009999999873689375 m**. It now rejects with
   **`Visual_cube_edge unsupported parent inverse`**, with **no success
   receipt written**.
3. **Bindings:** the shared encoder contract accepts the v6 source/native/
   provenance/check/render-receipt chain and all 250 PNG hashes. It rejects
   the older v5 checker receipt as current: “Native file/checker/source
   receipt changed; recheck before encoding.”

## Receipt-only evidence verification

Native `.blend`, provenance, render receipt, preview, MP4 and all raw frames
are byte-identical between v5 and v6. Only the new checker receipt and bound
manifest change. ffprobe confirms **250 frames, 25 fps, 10 seconds**.
No new geometry, camera, motion or startup result was introduced.

Principal SHA-256 bindings:

| Artifact | SHA-256 |
|---|---|
| Current checker | `03ad0b7dbc49d14f6b0169127bc6d727e08f50400e1ba7435002d4c2211d71a1` |
| Native file, unchanged | `b8f10b344627ebeb214caac4a2b816e5cd71d8be9d42b157199366f635e5838f` |
| MP4, unchanged | `183b8cf349dddd528758ac8635274125b324a605d13b84cae7ba664bc587b9e8` |
| New native-check receipt | `5d80f131a7cf5332e1dec8e7225a1f598b1df0b5d3384057a24b4ec009ca68f8` |
| v6 manifest | `a990ed1628ec07fc88280c1d0c257fc0df5d5d67bb1e7a80d26fe1723ceaf1be` |

GitHub CI [33979993468](https://github.com/ktanino10/ai-hardware-engineering-team/actions/runs/33979993468)
is independently verified **success** for this exact `7512042…` HEAD.

## Reproduce and retain qualifications

```sh
# Repository root; all generated experiments stay in reviewer-r2b scratch.
PYTHONDONTWRITEBYTECODE=1 simulation/.venv/bin/python \
  simulation/reviews/r2b/witness.py
```

[`witness.json`](witness.json) preserves the positive/negative results, hashes,
prior-review preservation checks and CI binding. No live unsaved scene is
opened or modified.

The prior R2 qualifications remain: the tiny contact gap is unresolved
against contact/envelope uncertainty; stable capture and a second jump are
not demonstrated; real motor/brake/source and hardware safety are
unqualified. Blender remains recorded MuJoCo replay, not native dynamics;
ROOT retains its previously documented operation-specific limits. Requested
Fusion assembly storyboards/video and all physical-action gates remain
separate.
