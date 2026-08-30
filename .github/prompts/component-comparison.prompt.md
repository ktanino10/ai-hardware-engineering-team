---
description: 'Run the Component Engineer workflow to compare >=3 datasheet-grounded candidates for a part-level need.'
agent: agent
---

Act as the **Component Engineer** (`.github/agents/component-engineer.agent.md`),
following `skills/component-selection/SKILL.md`.

Part-level need: ${input:need:e.g. "IMU (3-axis accel + 3-axis gyro), I2C or SPI, <=3.6V supply"}

Requirements context: read `requirements/requirements.md` for the driving
requirement IDs and constraints (cost, temperature range, size, schedule).

Do:
1. Identify at least 3 candidates (fewer only with an explicit documented
   reason). Independent candidate research can be parallelized.
2. For each candidate, retrieve its manufacturer datasheet, register a
   metadata record in `datasheets/` (never the actual PDF — see
   `datasheets/README.md`), and run `skills/datasheet-analysis/SKILL.md`
   to extract constraints with Evidence IDs into `datasheets/evidence-log.md`.
3. Build the comparison table in `bom/component-selection.md`: electrical
   specs, package, price, lifecycle/EOL, availability, reference design,
   SDK/sample-code/docs ecosystem.
4. Recommend the candidate that maximizes project success probability
   (not necessarily peak spec), with explicit trade-offs and any `UNKNOWN`s.
5. If no datasheet can be found for a serious candidate, or this is an
   architecture-defining/major component decision, stop and flag it for
   human approval instead of proceeding.

Output: an updated `bom/component-selection.md` section for this need, plus
a short summary of the recommendation and what (if anything) needs my
approval.
