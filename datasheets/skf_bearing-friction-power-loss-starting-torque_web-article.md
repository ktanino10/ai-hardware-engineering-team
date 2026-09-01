# SKF — "Bearing friction, power loss and starting torque" (Rolling Bearing Selection Guide)

- **Manufacturer**: SKF Group
- **Part Number**: N/A — this is a general engineering reference page (part
  of SKF's own online "Principles of rolling bearing selection" guide), not
  a specific product's datasheet.
- **Datasheet Title**: "Bearing friction, power loss and starting torque"
- **Revision / Version**: UNKNOWN (live web page, not a versioned PDF)
- **Publication Date**: UNKNOWN (page not dated)
- **Official URL**: https://www.skf.com/group/products/rolling-bearings/principles-of-rolling-bearing-selection/bearing-selection-process/operating-temperature-and-speed/bearing-friction-power-loss-and-starting-torque
- **Retrieved Date**: 2026-09-01
- **Local cache note**: Not cached locally; content summarized via an
  AI-assisted web search this session that cited this page directly,
  cross-checked against the same simplified-friction-model figure
  (μ≈0.0010–0.0015 for deep-groove ball bearings) independently reported by
  Koyo/JTEKT's own "Basic Bearing Knowledge" reference page
  (https://koyo.jtekt.co.jp/en/support/bearing-knowledge/8-4000.html) and
  American Roller Bearing's friction-calculation page
  (https://www.amroll.com/friction-frequency-factors.html).
- **Used for Evidence IDs**: DS-BRG-003

## Context

Used in `bom/component-selection.md`'s Free-Rotation Support Mechanism
section (Rev 4) to estimate friction torque for Candidates A and B via the
industry-standard simplified bearing-friction model **M = 0.5·μ·P·d**
(M in N·mm, μ = coefficient of friction, P = load in N, d = bore/bearing
diameter in mm). Coefficient of friction used: μ≈0.0013, the mid-value of
the commonly-cited 0.0010–0.0015 range for deep-groove ball bearings under
normal lubrication/light-to-moderate load — flagged explicitly as a generic
engineering rule-of-thumb (radially-loaded model applied to what is
primarily a thrust/axial load in this application), not a manufacturer-
published friction figure for either specific candidate bearing; see the
Open UNKNOWNs in `bom/component-selection.md`'s new section.
