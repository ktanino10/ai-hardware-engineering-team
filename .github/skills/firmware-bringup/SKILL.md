---
name: firmware-bringup
description: 'Standard procedure for writing driver-level firmware bring-up code from a completed schematic: extracting the real pin/interface contract, sourcing register-level facts and any manufacturer-mandated initialization sequences from primary documentation, and honestly disclosing toolchain/compilation status. Use this whenever writing or revising bring-up firmware for a specific board design.'
---

# Skill: Firmware Bring-up

## Purpose

Standard procedure for going from a completed (or at least stable)
schematic design document to defensible, register-level driver-bring-up
firmware, with every decision's "why" recorded and every register-level
fact traced to a primary source -- the standard operating procedure behind
`.github/agents/firmware-engineer.agent.md`. Mirrors
`.github/skills/schematic-design/SKILL.md`'s and
`.github/skills/enclosure-design/SKILL.md`'s evidence-and-rationale
discipline, re-derived for firmware.

## Preconditions

- A schematic design document exists for the target board
  (`hardware/schematic/<board>-design.md`) with pin assignments, peripheral
  instances, and mode-select straps recorded -- read it in full, not a
  summary. If it isn't at least self-consistent, escalate rather than guess
  around the gap.
- The MCU and any sensor/peripheral ICs are already Component-Engineer-
  approved, with datasheet Evidence IDs in `datasheets/evidence-log.md`
  (`.github/skills/datasheet-analysis/SKILL.md`).

## Procedure

1. **Extract the real pin/interface contract from the schematic.** For
   every peripheral you'll touch, note the exact pin, the exact peripheral
   *instance* (e.g. "I2C2", not just "an I2C bus" -- getting the instance
   number right is exactly the class of fact a mislabeling defect hides
   in), any address/mode-select strap, and anything deliberately left
   unwired (e.g. interrupt lines NC in favor of polling). Never re-derive
   or assume a pin assignment independently -- if the schematic and a task
   description disagree, the schematic wins; report the discrepancy rather
   than silently picking one (see "Common failure modes" for a worked
   example of this happening in practice).
2. **Verify tooling honestly, this session, not from memory of a past
   session.** Check whether an embedded toolchain is installed or
   installable (e.g. `which arm-none-eabi-gcc`, `brew info`/`apt-cache
   search`, `pip show platformio`) before assuming a build is (or isn't)
   possible. Check whether a physical board exists to flash/power on
   (almost certainly not) -- if not, this is a source-code exercise, the
   same tooling-honesty convention `docs/architecture.md` Section 5.3/5.4
   already established for Mechanical's CAD tooling.
3. **Fix the MCU clock configuration first, serially**, with a recorded
   rationale, if the schematic leaves it open (it usually does -- board
   designs commonly fix "no external crystal" without fixing an exact
   target frequency). Other register values (timing registers, baud-rate
   registers) typically depend on this choice, so get it stable before
   anything else -- the firmware equivalent of fixing shared rails/ground/
   pins before sub-block circuit design
   (`.github/skills/schematic-design/SKILL.md` step 1).
4. **Gather register-level facts from a primary source before writing any
   register-poking code**: peripheral base addresses, clock-enable bit
   positions, alternate-function values, and timing-register presets from
   the MCU manufacturer's reference manual, or (often faster and just as
   authoritative) the manufacturer's own official CMSIS/HAL/LL header
   source, which you can fetch and grep directly. Cross-check a critical
   fact against a second independent source when practical (e.g. an
   established open-source project's register definitions) the same way
   this project's Hardware Reviewer cross-checks datasheet claims. Assign
   `DS-<CATEGORY>-<NNN>` Evidence IDs, reusing the existing category for
   that component (e.g. `DS-MCU-`) -- register facts are still facts about
   a component already in the evidence log, not a new evidence category.
5. **If a sensor/peripheral needs a manufacturer-mandated initialization
   sequence** (register pokes in a specific order, settle-time delays, or
   an opaque configuration blob/microcode upload): find and follow the
   manufacturer's own documented sequence exactly -- do not simplify,
   reorder, or omit a step because it seems unnecessary. If the sequence
   requires uploading opaque data you cannot derive, see "Vendoring
   opaque manufacturer data" below. Verify the sequence against the
   manufacturer's own official driver source code where one exists -- it
   is often more precise and less ambiguous than a prose description.
6. **Write one peripheral driver at a time**, each against the real pin/
   instance facts from step 1, each register-level claim tied to an
   Evidence ID from step 4. Keep each driver minimal and purpose-built --
   do not vendor an entire vendor HAL/LL package when a hand-written subset
   covering only the registers this board actually uses is sufficient and
   more auditable.
7. **State the host communication framing explicitly and simply**: baud
   rate (or equivalent), and a documented line/packet format. A simple,
   human-readable format (e.g. CSV text) is preferable to an invented
   binary protocol unless there's a concrete reason (bandwidth, parsing
   robustness) that the task actually needs one -- don't over-engineer this.
8. **Respect the scope boundary with future/adjacent disciplines.** Raw
   register-level sensor output (counts, not physical units) is a complete
   bring-up deliverable. Unit conversion, calibration, filtering, sensor
   fusion, and control loops belong to a future Control Engineer role
   (`docs/architecture.md` Section 14) whose trigger is almost certainly
   not met by a bring-up task -- do not creep into that scope "just to be
   more useful."
   The separately approved Simulation Engineer may implement simulated
   attitude feedback under `simulation/`; this does not authorize adding
   that controller to bring-up firmware or claiming control qualification.
9. **Self-check against the checklist below** before considering the work
   handed off -- until a Firmware Reviewer role exists
   (`docs/architecture-evolution.md` Section 32), this self-check stands in
   for independent review and must be done with matching rigor, not skipped
   or rubber-stamped.
10. **Attempt a real compile if a toolchain is available or installable.**
    A successful build (especially with warnings enabled, e.g. `-Wall
    -Wextra`) is meaningfully stronger evidence than uncompiled source --
    pursue it. Fix any real error the build surfaces (a genuine compile/
    link failure is *more* trustworthy evidence of a real bug than a
    plausible-looking but never-built source tree) and record what
    actually happened, honestly, either way.
11. **Produce a design rationale document** for the firmware (mirroring the
    schematic's own style: a "why" for every decision, Evidence IDs, an
    explicit tooling-honesty statement) and hand off to the Hardware Lead.

## Self-check / firmware-review checklist (work through all of these)

1. **Pin/peripheral instance fidelity** -- does the code actually target the
   schematic's real pins and the *correct peripheral instance* (e.g. "I2C2"
   really is I2C2's register base address, not I2C1's)? This is the single
   highest-value check: an instance-number mixup is exactly the kind of
   defect that looks completely plausible until checked against the real
   base address.
2. **Clock configuration correctness** -- the stated clock source/frequency
   is what's actually configured, and every clock-dependent register value
   (timing registers, baud-rate registers) was computed for *that* actual
   frequency, not a different assumed one.
3. **Manufacturer-mandated sequence completeness** -- every documented step
   (resets, settle-time delays, status polls) is present, in the documented
   order, not abbreviated for convenience.
4. **Vendored opaque data provenance** -- any vendored configuration blob/
   constant table traces to a verbatim, attributed manufacturer source, not
   an approximation, and its license permits this use.
5. **Register bitfield correctness** -- every clock-enable bit, mode/
   alternate-function encoding, and timing-register value traces to the
   Evidence ID cited for it, not "this looked right."
6. **Host communication framing consistency** -- the stated baud rate/
   format matches what's actually configured and actually transmitted.
7. **Scope-boundary compliance** -- no USB device/data-stack code, no
   wireless code, and no control-loop/filtering/unit-conversion code has
   crept in beyond what the task actually scoped.
8. **Tooling-honesty compliance** -- no claim of "tested," "verified on
   hardware," or "flashed" without a real, disclosed toolchain/hardware
   basis this session; compiled-vs-source-only status is stated accurately,
   not implied more favorably than what was actually exercised.
9. **Evidence traceability** -- every register-level numeric claim cites an
   Evidence ID or is explicitly marked `UNKNOWN` with an escalation, never
   silently asserted.
10. **Requirement-vs-schematic consistency** -- where a requirement's
    assumed wiring was checked against the actual schematic and found to
    differ, the firmware follows the real schematic and the discrepancy is
    documented, not silently reconciled by inventing behavior.

## Foundational Change Cascade Checklist (revising existing firmware after a schematic/interface change)

Added following MISS-034 (CRITICAL, resolved) and informed by **MISS-019 (LOW, still OPEN)** as Firmware's own already-documented instance of the same broader failure shape: a foundational upstream fact changed, the local artifact remained internally consistent, and stale downstream citations/comments were left behind. See `docs/workflow.md` §4.2 and especially §4.2.1. Firmware has the same risk even when the code still compiles cleanly: the schematic's live pin/interface contract can move after firmware was first written, leaving a plausible-looking but stale GPIO/peripheral/clock/address configuration in place. **Whenever you are revising existing bring-up firmware because the upstream schematic/pin-map/peripheral contract changed -- not writing first-pass firmware from scratch -- work through every category below before claiming the firmware still matches the board:**

1. **Re-read the current schematic design document from scratch, not just the prior firmware rationale.** Re-derive every touched pin, alternate function, peripheral instance number, strap-selected bus address, reset/default state, and any deliberately-unwired signal directly from `hardware/schematic/<board>-design.md`'s current text. Do not assume the old rationale is still mostly right and only patch the one changed line.
2. **Trace the change through every code location that snapshots that contract.** In firmware, the risk is not only the obvious register writes in one driver file; it also includes headers, inline comments, design-rationale prose, README/setup instructions, fault messages, and any duplicated pin tables. MISS-019 is the repo's own live evidence that these downstream firmware artifacts can remain stale even after the upstream correction is known.
3. **Distinguish what is genuinely unchanged from what only looks adjacent.** A pin move might leave the peripheral instance unchanged (e.g. same I2C block, different GPIO pins), or might leave a timing value unchanged while invalidating an AF selection, RCC enable set, EXTI route, or power-up sequencing assumption. Re-derive each dependent fact explicitly rather than inferring "same bus, so everything around it must still be right."
4. **Re-run the self-check specifically as a live upstream-consistency check, not merely an internal-consistency check.** A build that still passes, or code/comments that agree with each other, do **not** answer the MISS-034-shaped question from `docs/workflow.md` §4.2.1: *has the upstream Source of Truth moved since this firmware snapshot was last checked?* Your self-check must explicitly compare the current code against the current schematic, item by item.
5. **If a machine-readable upstream Source of Truth or derived check exists, use it; if not, say so honestly and do the manual re-derivation.** Firmware often depends on schematic facts recorded in human-readable markdown rather than a ready-made exported pin-map, so the narrower automated check described in `docs/workflow.md` §4.2.1 may not exist yet for every board. Do not pretend the absence of automation means the risk is absent; it means the manual comparison step is mandatory.
6. **When you find stale firmware-side citations or comments, treat them as real drift, not harmless polish.** Wrong source comments, stale margin rationales, or superseded pin-map prose can mislead the next bring-up/review cycle into trusting an outdated premise even if the executable code path was already corrected. Fix or explicitly flag that drift in the same handoff.

## Vendoring opaque manufacturer data

Some sensors require uploading manufacturer-supplied calibration/
initialization microcode you cannot derive or approximate. When this
happens:

- Locate the manufacturer's own official, redistributable driver source
  (check its license before reusing it -- BSD/MIT/Apache-style permissive
  licenses are generally fine with attribution; anything else, escalate
  rather than assume).
- Copy the opaque data verbatim into its own clearly-labeled file, with a
  header comment recording: source repository, source file, upstream
  version/date, byte count (independently counted, not trusted blindly),
  and the license text/notice the upstream project requires you to
  retain.
- This is a different regime from `datasheets/README.md`'s "never commit a
  datasheet PDF" policy, which is about copyrighted manufacturer PDF
  documents -- permissively-licensed, manufacturer-published *source code*
  is not that, and reusing it with attribution is standard open-source
  practice, not a new capability claim or a copyright risk.
- Never hand-derive, interpolate, or approximate the data itself, even
  partially -- if the exact upstream source can't be found, escalate
  (`docs/architecture.md` Section 10) rather than improvise a substitute.

## Output

Firmware source tree (drivers + main program) + a design rationale document
(Evidence-ID-cited, mirroring the schematic's own style) + a tooling-
honesty/compile-status disclosure + self-check results, referencing the
schematic design document it was built from.

## Common failure modes to avoid

- Trusting a task description's assumed wiring over the actual schematic
  document -- for example, assuming a "manual reset button" requirement
  means a GPIO firmware can poll, when the schematic actually wires that
  button directly to the reset pin. Always re-read the real schematic
  before writing the code that depends on it.
- Writing register-level code from memory of "how STM32/similar parts
  usually work" instead of confirming the exact base address/bit position
  for *this* part, *this* peripheral instance, this session.
- Approximating a manufacturer's opaque configuration blob instead of
  vendoring it verbatim from an official source.
- Excluding a compiler support library (e.g. `libgcc`, which supplies
  software integer-divide routines on cores without a hardware divide
  instruction) when trying to build a fully freestanding image, and only
  discovering this because the link fails -- treat a real build attempt's
  errors as valuable signal, not an annoyance to route around by weakening
  the build.
- Treating your own self-check as equivalent to actually having a second,
  independent reader try to break the firmware -- it is a documented,
  reversible stand-in for review (see the Firmware Engineer agent's
  "Out of scope"), not a permanent substitute.
- Implying "tested" or "verified" when only "compiles" (or worse, only
  "written") was actually true this session.
- Letting unit conversion, filtering, or a control loop creep in because it
  seemed like a small, helpful addition -- that is a scope boundary with a
  documented future trigger, not a judgment call to make ad hoc.
