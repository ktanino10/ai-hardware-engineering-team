---
name: firmware-review
description: Checklist and failure-analysis procedure for an independent, adversarial review of driver-level bring-up firmware -- register/peripheral-address correctness against primary sources, pin-map fidelity against the actual schematic, safety-critical-logic correctness, and a premise-review pass. Use this whenever reviewing bring-up firmware that was not authored by the reviewer.
---

# Skill: Firmware Review

## Purpose

Checklist and failure-analysis procedure for an **independent**, adversarial
firmware review — the standard operating procedure behind
`.github/agents/firmware-reviewer.agent.md`. Mirrors
`.github/skills/hardware-review/SKILL.md`'s and
`.github/skills/mechanical-review/SKILL.md`'s structure and rigor,
re-derived for driver-level bring-up firmware instead of a schematic or an
enclosure.

## When to use

Every time the Firmware Engineer hands off bring-up firmware (initial or
after a loop-back fix). Re-review after a fix means re-running the
checklist against the changed area and anything the change could have
affected — not a partial spot-check.

## Independence rule

You are not checking your own work. Do not accept the Firmware Engineer's
stated rationale or Evidence ID citations as fact — verify each register-
level claim directly against the same primary manufacturer source (or a
second independent one) yourself, and re-read the actual schematic design
document directly for every pin/peripheral-instance fact rather than
trusting the firmware's own restated pin table. Where a toolchain is
available or installable (`docs/architecture.md` §5.4), independently
rebuild the firmware and inspect the actual compiled output (e.g.
`objdump -d`, a raw byte-pattern scan for a claimed base address) — this is
meaningfully stronger evidence than a read-through, and this project's own
ad hoc firmware-verification passes have already shown it's achievable
(`validation/open-issues.md` ISS-014 Notes, `validation/change-log.md`
ECO-007).

## Checklist (work through all of these; not a sample)

1. Pin/peripheral-instance fidelity — every GPIO/bus assignment and the
   *exact peripheral instance number* (e.g. "I2C2" really is I2C2, not
   I2C1), independently re-read from the real schematic design document,
   not the firmware's own restated pin table.
2. Register/peripheral base-address and bitfield correctness — every base
   address, clock-enable bit, alternate-function value, and timing-register
   preset, independently re-derived from the same primary source cited (or
   a second independent source, e.g. a reference manual vs. an official
   CMSIS/HAL/LL header), not trusted at face value.
3. Clock configuration correctness — the configured clock source/frequency
   is what's actually enabled, and every clock-dependent register value was
   computed for *that* actual frequency.
4. Manufacturer-mandated sequence completeness — every documented step
   (resets, settle-time delays, status polls, an opaque configuration-blob
   upload) is present, in the documented order, independently confirmed
   against the primary source — not merely that *a* sequence exists.
5. Vendored opaque data provenance — any vendored configuration blob/
   constant table traces to the exact stated upstream source, file, and
   version, and its license genuinely permits this reuse.
6. Safety-critical logic correctness (where present) — for any code
   implementing a safety-related requirement (e.g. an overspeed-shutdown or
   latched-fault policy, REQ-405/406-class), independently trace the
   *actual code path* against the requirement's literal stated intent: does
   a "latched, not auto-resuming" policy actually never clear itself
   without the documented re-arm action, in every code path? Does the
   threshold/window arithmetic actually implement the stated policy? Are
   edge cases (e.g. a fault occurring mid-re-arm) handled the way the
   requirement intends, not merely the way that looked plausible?
7. Premise review — did the Firmware Engineer's own foundational
   assumption (which pin/AF/peripheral instance to target, which
   subsystems are claimed functionally independent of each other, which
   clock frequency was fixed) actually get independently re-derived here,
   or just re-asserted from the design rationale document's own narrative?
   This folds a rubber-duck-style "is the underlying assumption even
   correct" pass into this checklist (mirroring the *spirit* of the
   independent premise/assumption check `docs/architecture.md` §5.1
   already runs for Hardware Reviewer via a separate `rubber-duck`
   invocation), rather than requiring a second, separate firmware-scoped
   agent this round.
8. Scope-boundary compliance — no control-loop/PID/sensor-fusion/
   unit-conversion code, no USB device/data-stack code, and no wireless
   code has crept in beyond what was actually scoped.
9. Tooling-honesty compliance — no claim of "tested," "verified on
   hardware," or "flashed" without a real, disclosed toolchain/hardware
   basis this session; compiled-vs-source-only status is stated accurately.
10. Evidence traceability — every register-level numeric claim cites an
    Evidence ID or is explicitly marked `UNKNOWN` with an escalation, never
    silently asserted.

## Failure analysis — for each potential issue found, work out

- What actually happens electrically/logically if this ships as-is (the
  **failure mechanism** — not just "wrong instance," but *how* it fails:
  every transaction silently targets the wrong peripheral, a fault
  auto-clears on the next poll instead of latching, a timing register
  produces the wrong baud rate at the real clock frequency, etc.)
- Under what conditions it manifests (always vs. only on a specific code
  path, e.g. a fault occurring mid-re-arm)
- Whether it's a **firmware** defect (fixable by the Firmware Engineer) vs.
  a **schematic/interface** defect (the pin/interface facts the firmware
  was built against were themselves wrong or incomplete — needs to go back
  through the Hardware Lead / Circuit Engineer, not the Firmware Engineer)

## Finding record format (mandatory fields)

- **Issue**
- **Rationale**
- **Datasheet Source** (Evidence ID, or the specific
  `hardware/schematic/<board>-design.md` section/pin referenced)
- **Failure Mechanism**
- **Affected Component** (file/function, and the physical component it
  drives)
- **Recommended Fix**
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW

Severity definitions: `docs/architecture.md` §7.1 (reused verbatim from
Hardware Reviewer — not redefined). Firmware-flavored examples:

| Severity | Example |
|---|---|
| CRITICAL | The commanded-duty register write targets the wrong peripheral instance's base address, so a safety-critical overspeed shutdown never actually reaches the driver it's supposed to command |
| HIGH | A latched-fault policy clears itself automatically on the next polling loop instead of requiring an explicit re-arm command, contradicting the governing requirement's stated intent |
| MEDIUM | A clock-dependent timing register was computed for the wrong assumed frequency but still produces roughly-correct timing at the real one |
| LOW | A register-level Evidence ID citation points at the right datasheet but the wrong table/section |

## Output

- `firmware/<board>/<board>-firmware-review.md`: this cycle's full report
  (scope, checklist results, findings, verdict) — a new, per-board file
  convention mirroring `validation/design-review.md`'s per-cycle report
  shape, deliberately **not** written into `validation/open-issues.md`.
  This is a disclosed choice, not an oversight: `validation/open-issues.md`'s
  CI gate (`tools/check_open_issues.py`) blocks the Design Complete Gate
  (`docs/architecture.md` §8) on any open CRITICAL/HIGH row regardless of
  source — correct for Hardware/Mechanical findings (same physical
  PCB/enclosure) but wrong for Firmware findings, which do not gate Design
  Complete or PCB fabrication (§14, `docs/workflow.md` Phase 11). No
  template for this file is created by this skill's introduction; the
  first real one is populated once a real review cycle needs it.

## Verdict rule

- **PASS**: no open CRITICAL finding.
- **FAIL / CONDITIONAL**: any open CRITICAL or HIGH — route back to
  Firmware Engineer via the Hardware Lead.
- A Firmware Reviewer verdict does **not** gate the Design Complete Gate
  (`docs/architecture.md` §8) — Firmware Bring-up is deliberately kept out
  of that gate (§14, `docs/workflow.md` Phase 11). It **does** gate the
  "before flashing firmware to real hardware for the first time"
  Human-in-the-loop checkpoint (§10): an open CRITICAL/HIGH must reach
  RESOLVED or an explicit human-accepted-risk disposition before any real
  flashing.

## Common failure modes to avoid

- Anchoring on the Firmware Engineer's confidence or stated rationale
  instead of re-deriving the answer — including re-deriving the
  foundational pin/instance/independence assumptions themselves, not just
  whether the code matches what was assumed.
- Downgrading a CRITICAL to keep the process moving — if new evidence
  changes the classification, say so explicitly with that evidence.
- Treating "it compiles cleanly" as equivalent to "it's correct" — a clean
  build proves the code is syntactically valid C targeting the chosen
  MCU, not that it targets the right peripheral instance or implements the
  right safety policy.
- Verifying a safety-critical logic claim (e.g. "latched, not
  auto-resuming") by reading only the code path the design rationale
  document describes, instead of checking every code path that could clear
  the latch (including ones the document doesn't mention).
- Treating a firmware finding as if it blocks the Design Complete Gate the
  way a Hardware/Mechanical finding does — it doesn't (see Verdict rule),
  but it still fully blocks the "before flashing" HITL gate, and that
  distinction must not get lost or conflated in either direction.
