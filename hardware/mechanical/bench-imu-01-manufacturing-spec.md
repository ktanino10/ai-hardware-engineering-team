# Bench-IMU-01 Rev 3 Manufacturing Specification — Flywheel Containment Parts

## 1. Scope

This document specifies the **manufacturing process** for Bench-IMU-01 Rev 3's two printed flywheel-containment parts: the `base()` piece's cylindrical `fw_bay_wall()` and the separate bolted `containment_cap()`, both already disclosed in `hardware/mechanical/bench-imu-01-dimensional-spec.md` §8 and modeled in `hardware/mechanical/bench-imu-01-enclosure.scad`. It does **not** redesign the geometry. It converts the CAD-geometric claim (`containment_wall_t` = 4.0 mm) into explicit FDM process recommendations so neither printed piece is silently produced with sparse default infill.

## 2. Safety-critical classification

- Parts: the 1st printed piece `base()` (specifically its cylindrical `fw_bay_wall()` containment wall) and the 3rd printed piece `containment_cap()`.
- Governing requirement: `requirements/requirements.md` **REQ-403**.
- Classification: **safety-critical** (`CONFIRMED`).
- Why: these parts' purpose is fragment/projectile containment for a detached 100 g flywheel or fragment thereof, not cosmetic closure or fit only.

## 3. Source geometry and disclosed load case

### 3.1 Geometry consumed, not re-derived

- `containment_wall_t` = **4.0 mm** (`ESTIMATE` in the source CAD/spec, not a validated ballistic rating), from `hardware/mechanical/bench-imu-01-enclosure.scad` and `hardware/mechanical/bench-imu-01-dimensional-spec.md`.
- `fw_bay_wall()` is part of the 1st printed piece `base()`: an annular cylindrical wall from `fw_bay_inner_r` = **39.5 mm** to `fw_bay_outer_r` = **43.5 mm** (therefore 4.0 mm radial thickness), spanning `fw_wall_h` = **43.0 mm**, with a top flange band from `fw_bay_outer_r` out to `fw_flange_or` = **52.5 mm** over `flange_band_h` = **8.0 mm** to host the 6 heat-set inserts. `base()` also bundles `pcb_bay_base()`, `motor_platform()`, and `motor_wire_bridge_solid()` before the global subtraction of `motor_wire_duct_void()`.
- `containment_cap()` is the 3rd printed piece with a 4.0 mm disk top and a downward skirt bolted by 6× M3 fasteners into the base flange. Its skirt is a slip-fit collar around the flange band, with outer diameter `fw_flange_dia + 2*fit_clearance + 2*wall_t` = **109.4 mm** and therefore a radial location well outside `fw_bay_wall()`'s 43.5 mm outer face.

### 3.2 Disclosed REQ-403 load case extracted from the existing design documents

The following values are copied from `hardware/mechanical/bench-imu-01-dimensional-spec.md` §8 and are **not re-derived here**:

| Quantity | Value | Confidence | Source |
|---|---:|---|---|
| Credible worst-case flywheel speed | 22,200 RPM no-load-high | ESTIMATE | `bench-imu-01-dimensional-spec.md` §8 table; per `datasheets/evidence-log.md` DS-MTR-018, this is this project's own derived no-load-speed estimate from the published KV constant at full-charge 3S (11.1 V), "not directly published by the manufacturer" |
| Angular velocity | 2324.8 rad/s | ESTIMATE | `bench-imu-01-dimensional-spec.md` §8 table; unit conversion of the RPM row above, so inherits the same ESTIMATE confidence |
| Stored kinetic energy | 121.60 J | ESTIMATE | `bench-imu-01-dimensional-spec.md` §8 table; depends on 100 g disk mass (`ESTIMATE`) and `fw_dia` = 60.0 mm (`ASSUMPTION`) inputs |
| Rim tip speed | 69.74 m/s (~250 km/h) | ESTIMATE | `bench-imu-01-dimensional-spec.md` §8 table; depends on `fw_dia` = 60.0 mm (`ASSUMPTION`) input |
| Threat mechanism | Hub collar retention failure releasing the entire 100 g disk as a rigid projectile | ESTIMATE | `bench-imu-01-dimensional-spec.md` §8 text; mechanism remains a reasoned hazard hypothesis because hub-collar retention strength is carried as `UNKNOWN`/unverified in the source design docs |

### 3.3 Why this is a containment problem, not merely a fit problem

Per `bench-imu-01-dimensional-spec.md` §8, the governing hazard is **not** bulk flywheel burst from disk stress; it is a **discrete coupling failure** in which the hub collar loses retention and releases the 100 g disk at up to ~250 km/h rim speed. The existing design document explicitly states that no datasheet exists for the assumed hub collar retention strength, so the failure mode cannot be bounded by calculation there and is instead being mitigated structurally. For a radial ejection from the disk rim (`fw_dia` = 60.0 mm, so launch radius ≈30 mm), the part first in that threat path is `fw_bay_wall()` in `base()`; `containment_cap()` is therefore a secondary/backup surface for that specific radial threat, not the primary one. That makes both printed pieces projectile-containment features, not merely geometric enclosure covers.

## 4. Manufacturing process specification

These values are process recommendations for FDM fabrication of the existing geometry. Because no physical test of the actual printed parts exists in this environment, the process values below are predominantly `ESTIMATE`, not `CONFIRMED`.

| Printed piece / parameter | Specified value | Confidence | Rationale |
|---|---|---|---|
| Both parts — Material | **Nylon (PA) or PA-CF only if the actual printer/process is already demonstrated capable of producing void-free, dimensionally stable parts; otherwise PETG as the fallback recommendation for prototype evaluation only** | ESTIMATE | General FDM literature consistently treats nylon as materially tougher and more impact-tolerant than PLA/PETG/ABS, while PETG is tougher and less brittle than PLA. For a fragment-containment role, toughness matters more than cosmetic printability. However, nylon's hygroscopicity and print sensitivity can degrade results if the process is not controlled, so PETG remains the more realistic prototype fallback where nylon process control is unavailable. Neither material choice constitutes validated containment certification. |
| Both parts — Infill percentage | **100%** | ESTIMATE | This containment structure exists to intercept a disclosed worst-case projectile-like event of 121.60 J / 69.74 m/s (`ESTIMATE`). Some published FDM impact-toughness results are more nuanced than a simple “maximize infill for impact-energy absorption” rule: the document's own cited MDPI Eng. Proc. 2024 reference reports a 40% infill sample outperforming both a Hilbert-pattern sample and a 100% solid sample for Charpy energy absorption. 100% infill is retained here anyway as a conservative default under deep load-case uncertainty (hub-collar retention strength remains `UNKNOWN`) and to preserve CAD-fidelity to the already-approved “solid 4.0 mm containment wall” design intent, not because the literature unambiguously proves 100% infill is always best for this exact goal. |
| Both parts — Infill pattern | **Gyroid or honeycomb; prefer gyroid if the slicer/toolchain supports it robustly, otherwise honeycomb** | ESTIMATE | Published and technical literature generally shows honeycomb/triangular-family patterns outperforming simple line/grid patterns for energy absorption. At 100% nominal infill the pattern matters less than at lower densities, but specifying a non-line pattern still helps avoid long straight weak planes in any locally non-solid regions the slicer may leave. Gyroid is widely used for isotropic energy distribution in modern slicers; honeycomb is the more directly literature-grounded fallback. |
| Both parts — Wall / perimeter count | **Minimum 6 perimeters** with a 0.4 mm nozzle equivalent (or shell thickness ≥2.4 mm before infill contribution) | ESTIMATE | Shell continuity has outsized influence on impact performance relative to infill alone. For a 4.0 mm containment wall, 6 perimeters drives most of the section toward continuous shell material rather than relying on interior pattern fill. This directly addresses the documented gap that a nominally 4.0 mm CAD wall can otherwise print mostly as air with only 2 default perimeters and sparse infill. |
| `base()` / `fw_bay_wall()` — Top/bottom solid layers | **100% solid where slicer settings distinguish floor/roof skins; no reduced-skin shortcut on the floor disc or flange band** | ESTIMATE | `base()` is the primary radial containment piece, but it is not an isolated ring: it also carries the PCB-bay base, motor platform, flange band, and wire-bridge geometry in one print. The floor disc beneath the wall and the flange band hosting inserts should therefore be printed as fully solid skins wherever the slicer exposes that control, so the annulus, floor, and flange do not rely on sparse bridging under an already safety-critical wall. |
| `base()` / `fw_bay_wall()` — Print orientation | **Print `base()` in its installed orientation, with the broad enclosure floor / motor-platform face down on the build plate and `fw_bay_wall()` rising upward** | ESTIMATE | This orientation keeps the large PCB-bay base and motor-platform surfaces flat on the bed, which best preserves the whole `base()` piece's competing functional needs (mounting-feature flatness, motor-platform flatness, flange concentricity). It also makes `fw_bay_wall()` a stack of continuous XY circumferential loops, which is the preferred orientation for a radial strike into the cylindrical wall. A sideways orientation might better reduce Z-axis exposure at isolated local surfaces, but it would sacrifice the broader `base()` part's datum flatness and would turn the cylindrical wall into layer-to-layer laminations loaded more directly across weaker interlayer bonds. |
| `containment_cap()` — Top/bottom solid layers | **100% solid; top/bottom thickness ≥4.0 mm where slicer settings express this separately** | ESTIMATE | The cap's flat top is itself part of the containment surface. Its material continuity should not depend on a low number of top skins bridging across sparse interior structure. A solid top/bottom setting is needed so the cap top approximates the 4.0 mm geometric material thickness the CAD implies. |
| `containment_cap()` — Print orientation | **Print with the cap installed orientation preserved: flange-contact face down on the build plate, cap top upward, so the cap's circular top and skirt are built concentrically in XY and the likely radial fragment impact into the sidewall/skirt is carried primarily in-layer rather than through Z-layer adhesion** | ESTIMATE | FDM anisotropy makes Z-direction interlayer strength the weakest direction. Printing the cap upright keeps the cylindrical skirt/perimeter load path predominantly in continuous XY loops, which is preferable to a sideways orientation that would turn the skirt into stacked laminae loaded across layer bonds. This orientation also best matches the modeled installed geometry and preserves flange/skirt concentricity. Residual limitation: the cap's own flat top still contains Z-axis-built layer interfaces through its thickness, so infill/perimeter/orientation choices cannot fully remove anisotropy from that top surface; they only avoid making the cylindrical skirt and bolt-circle region even worse. |
| Both parts — Nozzle / layer intent | **Use the largest nozzle/layer combination already qualified on the printer for strong functional parts; do not prioritize fine cosmetic layer height over interlayer fusion** | ASSUMPTION | No exact printer is specified in this repository. Larger extrusions commonly improve bead bonding and reduce void fraction, but without a named machine/process this remains a process assumption rather than a confirmed setting. |

### 4.1 Primary vs. secondary containment surfaces for the disclosed radial-ejection threat

- **Primary containment surface:** `fw_bay_wall()` within the 1st printed piece `base()` (`ESTIMATE` as a threat-path determination grounded in the disclosed geometry and load-case description). A fragment launched radially from the 30 mm flywheel rim reaches the 39.5–43.5 mm wall annulus first.
- **Secondary / backup containment surface:** `containment_cap()` (`ESTIMATE` as a threat-path determination). Its skirt sits radially outside the flange band and therefore behind `fw_bay_wall()` for the radial-ejection scenario; its top remains relevant for non-radial or ricocheted trajectories, but not as the first intercept surface for the disclosed radial threat.

## 5. Explicit exclusions and honesty about confidence

- The values above are **engineering recommendations**, not validated pass/fail limits.
- Confidence is mostly `ESTIMATE` because the literature characterizes coupons and generalized process trends, not this exact cap geometry, this exact printer, this exact filament lot, or this exact fragment-impact event.
- No physical/destructive testing capability is available in this environment. No FEA/simulation tool is verified connected in this session. No claim is made here that the specified process has been tested against a 121.60 J containment event.

## 6. Process adequacy assessment — is FDM actually adequate here?

### Conclusion

**FDM cannot be presented as an adequate, validated containment process for REQ-403 on the basis of this document alone.**

### Reasoning

1. The governing use case is genuine hazardous-energy containment: the existing design documents disclose a 100 g projectile hazard with up to **121.60 J** stored energy and up to **69.74 m/s (~250 km/h)** rim speed, both carried here honestly as `ESTIMATE` values because they depend on `ASSUMPTION`/`ESTIMATE` source inputs.
2. FDM mechanical performance is highly dependent on the exact printer, material, moisture condition, orientation, extrusion quality, shell bonding, and the specific print run.
3. Safety/certification practice for additive manufacturing is process-combination-specific; published certification pathways and UL additive-manufacturing programs require physical testing of the actual printer + material + process combination, not a paper transfer of generic material properties.
4. Machinery-safety risk-reduction practice (e.g. ISO 12100's guard/containment framing) expects containment capability to be verified appropriately for the identified ejected-part hazard; this repository's environment has **no physical test capability** to do that verification.

### Manufacturing Engineer disposition

- **Recommended process if an FDM prototype must be produced for evaluation:** Nylon/PA preferred where the printer process is already mature; otherwise PETG prototype only; 100% infill; gyroid/honeycomb; minimum 6 perimeters; print both `base()` and `containment_cap()` upright in their installed orientations, with `base()` bedded on its enclosure floor / motor-platform datum surfaces.
- **But:** this does **not** close REQ-403, does **not** certify containment, and does **not** resolve the fundamental adequacy question.
- **Escalation required (`CONFIRMED`)**: the adequacy of FDM for this containment-cap purpose must be escalated to the human Chief Engineer as a safety-critical human-in-the-loop decision, with an expectation that real destructive/containment testing or a different manufacturing/process strategy may be required before any claim stronger than "prototype recommendation" is made.

## 7. Source references for process claims

1. `hardware/mechanical/bench-imu-01-dimensional-spec.md` §8 — disclosed REQ-403 load case and containment rationale.
2. `hardware/mechanical/bench-imu-01-enclosure.scad` — `containment_wall_t`, `fw_bay_wall()`, `base()`, `containment_cap()`, and flywheel-bay geometry.
3. 3DMag, "3D Print Infill Percentage and Patterns for Maximum Strength" — general infill-density/pattern trends for structural FDM parts.
4. MDPI Eng. Proc. 2024, "Optimizing Impact Toughness in 3D-Printed PLA Structures Using Hilbert Curve and Honeycomb Infill Patterns" — pattern/toughness literature pointer supporting non-line infill preference and documenting that some sub-100% infill cases can outperform 100% solid prints for impact-energy absorption.
5. Technical reviews summarized via current web search on shell/perimeter dominance and FDM anisotropy, including The Virtual Foundry shells/infill analysis and anisotropy overviews from MLC CAD / Hotean; used only as general-process literature, not part-specific validation.
6. UL additive-manufacturing certification materials / Blue Card program references — used to justify that printer+material+process combinations require physical testing and certification-specific evidence.
7. ISO 12100 explanatory references on guards containing ejected materials/workpieces — used to justify that guard adequacy requires verification appropriate to the hazard.

## 8. Handoff

This document is **ready for the Mechanical Reviewer's independent cross-check**. It is **not** a final or approved manufacturing specification, and it does **not** self-certify REQ-403 containment adequacy.
