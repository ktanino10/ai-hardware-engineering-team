# Lessons from JAXA's triaxial attitude-control module

**Case ID: JAXA-TRIAXIAL-20260906 / Recorded by Copilot, 2026-09-06 JST.**
Follow the shared
[engineering-reference-learning](../../.github/skills/engineering-reference-learning/SKILL.md)
procedure. **CANDIDATE**: reuse the comparison questions below only after
independent review and human approval/merge of the introducing PR. This
does not approve a physical design or claim that model weights were trained.

## Takeaway and scope

The lesson is not "buy a higher-torque part." Compare body first moment and
inertia, wheel angular momentum, brakes, supports, control, power and wiring
as a coupled system. Self-righting, subsequent attitude capture and maintained
balance are separate success conditions.

The originating request on 2026-09-06 was to reconsider the build using these
references and improve the agents' skills, instructions and expertise. The
gap addressed here is the missing shared procedure that turns supplied
references into specialist comparisons and actual next work. Design concerns
were handed off by the requester; they are not hardware/simulation audit
results produced by this case. The record starts from main
`dd7e4b4a7f4ccd838edeb93b9cc9aac86dc1375d`.
Actual Rev5 design and the simulation in
[#70](https://github.com/ktanino10/ai-hardware-engineering-team/pull/70)
remain separate work with their existing owners. Do not import their unmerged
implementation or evidence here. Reconnect each application to the owner's
current revision and requirements.

Protected decisions at intake: retain the new A-board's 150 x 95 mm outline,
134 x 79 mm mounting pattern and current pose, `ESP32-S3-WROOM-1-N8R2`, and
the U-only exception for native USB programming/debugging + CDC. These are
recorded human instructions, not an implementation check against this base.
Do not change power, drivers, guards, fuses, tests or safety decisions.
Manufacturer inquiries were cancelled: no contact, email, account
authentication or new vendor request.

## Primary sources and immutable identity

Both pages were retrieved on 2026-09-06 JST. P1/P2 are case-local source keys,
not design Evidence IDs. Published page revision numbers are UNKNOWN. The
SHA256 values identify the fetched HTML bytes, not guaranteed future
retrievability. English link labels below describe the Japanese source
titles; they are not presented as official English titles.

| Key | Publisher, source and inspected scope | Retrieved HTML SHA256 |
|---|---|---|
| P1 | JAXA Research and Development Directorate, [Miniaturized triaxial attitude-control module](https://www.kenkai.jaxa.jp/research/automation/triaxial.html): research overview, detailed results, applications, publicity and patent list | `ae4a263939ad40a3982cc87f4fd7470d12812f16879aab510dbc4a3b71273751` |
| P2 | JAXA, [The miniaturized triaxial attitude-control module inside Int-Ball](https://fanfun.jaxa.jp/topics/detail/10792.html), 2017-10-13: large/small prototype distinction, integration, sensor fusion and brake function | `14060da8a8dd05ca034d23662299d6b8da7e725e921e97a236ea9de3c1998c03` |

The public videos were verified through P1's actual links:
[research introduction, labeled 2:01](https://www.youtube.com/watch?v=VamXKnQnrPg)
and [Endless applications?! Miniaturized triaxial control module](https://www.youtube.com/watch?v=ummojBgEVLo).
For the latter, P1's November 2017 publicity entry was cross-checked against
the YouTube page title. P2 embeds the former; do not attribute the latter's
link to P2. Full public-video byte hashes were not obtained. P1 also links
separate large/small experiment clips; the timestamps below are not their
playback times.

The supplied private screen recordings and existing extracted frames were
consulted. Do not publish originals, images, full captions or local paths.
Recording SHA256 values were checked; existing extracts were reused for
observations.

| Recording | Duration (handoff metadata, not physical-event duration) | Original SHA256 |
|---|---|---|
| V1 | 114.916 s | `5885da096d19621d9465f591147c0ebea4fa9a349fb7c815a07bf6d752042484` |
| V2 | 363.532 s | `a82585f2d8c2ffbc15bcec2b33234c761cea2408d6bacd4dcfc30300ff8e6df9` |

## Separate observations, published claims and inference

**The figures here are P1/P2's published claims about reference prototypes,
not our specifications, defaults or acceptance criteria.** Before adopting a
fact in a design, its owner verifies the applicable configuration/conditions
against primary documentation and registers an Evidence ID in the existing
`datasheets/evidence-log.md`. Film alone does not establish a manufacturer's
operating limits.

| Class | Source and configuration | Original summary and limitations |
|---|---|---|
| PUBLISHED CLAIM | P1's module overview, in the 100 mm-prototype context | Six MEMS inertial sensors at vertices, each measuring three-axis angular rate and three-axis acceleration. BLDC built-in Hall sensors measure wheel speed; newly developed thin electromagnetic brakes and PSoC measurement/control at 50 Hz are described. Do not generalize to the 31 mm version or our configuration. |
| PUBLISHED CLAIM | The same 100 mm overview | Energized braking torque of 2.1 N m; 6000 rpm to zero within 100 ms, including demagnetization time. This is not a speed/temperature/duty-dependent torque waveform, an allowable cycle count or evidence of safety in our hardware. |
| PUBLISHED CLAIM | P1's later applications section and P2's miniaturization account | Approximately 31 mm / 50 g describes a separate miniaturized module. Do not transfer the earlier braking/control figures to it. P1's mass heading and volume entry do not map clearly, so the missing 100 mm-prototype mass remains UNKNOWN. |
| OBSERVED / CG | V1 approximately 16 s | Distributed sensor markers and a six-unit label in CG. Actual mounting coordinates, axis calibration and fusion algorithms were not measured. |
| OBSERVED / apparent live action | V1 approximately 27-35 s and 40 s | Face-rest to inclined support to a corner-like stance, followed by 100 mm/31 mm labels. Editing and crossfades are present; this does not establish an uninterrupted, unconstrained test. |
| OBSERVED / CG; PUBLISHED CLAIM / captions | V1 approximately 48-64 s; V2 approximately 210-225 s and 135-150 s | Wheel/electromagnetic-brake explanatory CG, unfolding PCB/wheel CG, and captions describing integration of the structure and circuit boards. Actual joints, manufacturing process and load limits are not established. |
| OBSERVED / live action; PUBLISHED CLAIM / captions | V2 approximately 160 s, 165-175 s and 228-248 s | A small-module mass caption, an apparent corner-balancing pose and rapid self-righting. Leads and edits are visible. State histories, freedom from external constraint and capture time remain UNKNOWN. |
| INFERENCE | Applying the above to our comparison | Evaluate acceleration, finite braking, release/unload, capture and maintained balance separately. This is a proposed comparison procedure, not a control law reconstructed from film. |

All timestamps are **approximate positions in the screen recordings**, not
the original videos' clocks or calibrated braking durations. Space/flight
application CG illustrates possible uses, not flight qualification or
demonstration of the filmed prototype.

## Transferable questions and next work for existing owners

These are candidates for application to work already handed off. Hardware
Lead connects them to existing owners/artifacts without duplicating tasks.
Comparisons in this PR are **NOT RUN / no adoption into the actual design**.
Take numeric thresholds from current approved requirements. If absent, the
owner proposes them and does not claim success before the necessary human
decisions.

| Current concern and transferable question | Non-transfer and counterexample | Existing owner, concrete next action and comparison output |
|---|---|---|
| Are body first moment/inertia, wheel angular momentum, brake/support/controller/battery burden and the complete force/reaction path compared together, rather than only part torque or enclosure size? | A stronger motor or a larger enclosure alone does not demonstrate whole-system improvement. Reference compactness is not permission to adopt structural PCBs. | Mechanical states mass, inertia and support conditions for a baseline preserving the current pose and for alternatives. Route boundary conflicts via Lead to Systems' existing four criteria. Record comparisons and ripple effects in existing mechanical/interface artifacts and hand off to Mechanical Reviewer. |
| Are sensing purpose, frames, physical placement, time alignment and the distinction between actual Hall/speed feedback and FG output explained? | Six coplanar BMI270s do not automatically reproduce the distributed fusion architecture. That alone also does not disqualify them or require satellite boards. | Circuit/PCB records actual pin/function/frame/placement mappings in existing circuit/interface artifacts. Firmware stays within checking state/timestamp availability. Component compares primary evidence for required functions; route to each existing independent reviewer. |
| Are supply/energy boundaries during braking and restart, plus radio, connector and thermal burdens, accounted for? | An industrial brake's peak torque does not qualify repeated braking. Do not infer a part choice, permissible duty or safety from reference-prototype figures. | Component/Circuit/Power investigates speed/temperature/duty/energy conditions in available public primary documentation. If missing, compare documented candidates or run explicitly assumed sensitivity comparisons. Use existing component/power artifacts and Hardware Reviewer; do not change power or drivers without authorization. |
| Can release/unload, capture and maintained balance after self-righting be explained? | Crossing an angle, tumbling, a tiny gap or a video-like marker trajectory is not maintained balance. Do not fill gaps with hidden base impulses, pose resets or parameter fitting to film. | Pass acceleration -> finite braking -> release/unload -> capture -> maintained-balance comparisons to the existing simulation owner. Record state availability, saturation, remaining wheel momentum, contact dwell and attitude/angular-rate capture metrics in a separate study. Use that owner's independent review; do not rewrite #70's frozen audit/evidence. |
| Is integration CG distinguished from real parts that can be manufactured and assembled? | Markers or CG folding are not hardware/flight evidence; a fused print is not equivalent to joints between separate components. | Mechanical/Manufacturing compares parts, joints, insertion paths, tools, retention and material/process limits. Produce WIP evidence through the existing `mechanical-visualization` and `docs/assembly-evidence.md` procedures for Mechanical Reviewer. Fusion assembly sequencing, MuJoCo computation and Blender replay are not interchangeable. |

If evidence remains insufficient, do not stop at repeated UNKNOWN checklists.
The owner proposes an appropriate next step: functionally suitable candidates
with available primary sources, a model comparison with bounded assumptions,
or a constraint-preserving option alongside an architecture-change option
requiring human judgment. If constraints must change, return to the existing
`systems-integration` process and human decision, not unilateral adoption.

P1 lists patents; public film is neither permission to copy a mechanism nor
a substitute for manufacturing/IP investigation. Applicability of rights
and manufacturing conditions is unevaluated. No broad legal conclusion is
made here.

## Review and reuse boundaries

An independent reader checks source version/prototype/conditions, the
observation/inference distinction, counterexamples, owners and comparison
metrics. Record reviewer, reviewed commit, date, findings and disposition
in the introducing PR; remain CANDIDATE until human approval/merge. Readers
without the private recordings distinguish verified published claims from
unconfirmed recording observations. Viewing existing extracts alone does not
independently validate physical performance.

The shared skill's behavioral examples describe expected output, not executed
agent evaluations. Hardware/control changes, performance comparisons and
manufacturability/safety acceptance arising from this case have not been
performed. Re-review applicability when sources, requirements, parts or
placement change. Actual design changes return to existing ECOs, requirement
traceability, independent design review and human approval; merging a
knowledge PR does not substitute for them.
