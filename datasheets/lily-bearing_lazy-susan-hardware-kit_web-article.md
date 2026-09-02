# LILY Bearing — "Lazy Susan Hardware Kit: What's Inside and How to Install"

- **Manufacturer**: LILY® Bearing (a bearing manufacturer/retailer, not BC
  Precision — this is a **cross-industry generic-convention** source, not a
  citation from the actual DS-BRG-001 manufacturer)
- **Part Number**: N/A — this is a general how-to/buying-guide article, not
  a specific product's datasheet
- **Datasheet Title**: "Lazy Susan Hardware Kit: What's Inside and How to
  Install"
- **Revision / Version**: UNKNOWN (live web page, not a versioned PDF)
- **Publication Date**: UNKNOWN (page not dated)
- **Official URL**: https://www.lily-bearing.com/resources/blog/lazy-susan-hardware-kit-guide
- **Retrieved Date**: 2026-09-01
- **Local cache note**: Not cached locally; content fetched directly this
  session (full article text retrieved, not summarized secondhand).
- **Used for Evidence IDs**: DS-BRG-007

## Context

Used in `hardware/mechanical-interface.md` Part C1/C2 and
`hardware/mechanical/bench-imu-01-dimensional-spec.md` §18.1/§18.1.1/§18.2
(Rev 4, free-rotation support mechanism) as the **ASSUMPTION** basis for the
new mounting-flange/stand-plate bolt pattern for the BC Precision 4LS-3
lazy-susan turntable bearing (DS-BRG-001), whose own product page does not
publish a mounting-hole count, spacing, or size for either plate.

**Relevant table from the article ("Screw Specifications and Load Ratings by
Bearing Size"):**

| Bearing | Load Capacity | Pilot Hole | Screw | Countersink? | Detent |
|---|---|---|---|---|---|
| 3" | 200 lbs | 5/32" | #6 | If flat-head | No |
| **4"** | **300 lbs** | **5/32"** | **#6** | If flat-head | **No** |
| 6" | 500 lbs | 5/32" | #6 | If flat-head | No |
| 9" | 750 lbs | 3/16" | #8 | If flat-head | Yes (1 or 8) |
| 12" | 1,000 lbs | 3/16" | #8 | If flat-head | Yes (4) |

**Why this is treated as a valid cross-industry convention for DS-BRG-001,
not an unrelated citation**: the article's own "4-inch" row states a 300 lb
load capacity — an exact match to DS-BRG-001's own stated 300 lb capacity for
its 4in bearing. This independent agreement (two different
manufacturers/sources both associating "4-inch lazy-susan bearing" with
"300 lb load capacity") is used as evidence that the article's 4-inch row
(5/32in pilot hole, #6 screw) describes the same general bearing class
DS-BRG-001 belongs to, not a coincidentally-similar but unrelated product
line.

**Mounting-hole count** (used as the Evidence-ID basis for
`n_bmount_bolts`=4 in the `.scad` file): the article's own "Two Plates,
Explained" section describes each plate's holes as a fixed set used to
align/attach to the tray or base; separately, other generic lazy-susan
installation guides cross-checked during this session's research
consistently describe **4 evenly-spaced mounting holes per plate** as the
standard pattern for bearings in the 3"–6" class (this article does not
give an explicit numeric hole-count table itself, so the "4 holes" figure is
recorded here as the generic convention this session found consistent across
sources for this bearing-size class, not a number this specific article
states in as many words — flagged for precision).

**One precise, important nuance found on full-text fetch (not present in an
earlier, less precise summary of this same source used earlier in this
project's Rev 4 task)**: the article explicitly states that **"large access
holes (outer ring)"** — a separate, larger set of holes used to reach through
and drive the *opposite* plate's screws after assembly — apply only to **"9"
and 12" bearings"**, not to the 3"/4"/6" class. For a 4" bearing specifically
(DS-BRG-001's own size), the article's own "Step-by-Step Installation — For
3", 4", and 6" Bearings" section describes a simpler sequence: mount the top
plate first (using its own small holes as a drilling template against the
tray), then flip and mount the bottom plate to the base — with **no**
separate large access-hole feature involved at this size. **This project's
own new mounting flange/stand-plate design (§18.2/§18.4 of the dimensional
spec) does not rely on or model any access-hole feature** — it uses a solid
annular band with a single generic 4-hole bolt-circle pattern precisely
*because* the real hole positions (and, per this more precise reading, even
whether an access-hole feature exists at all at this bearing's actual size)
are not confirmed for this specific SKU — so this nuance does not require
any correction to already-written Rev 4 geometry, only a more precise record
here of what the source actually says.

**Also relevant, not currently used by this project but recorded for
completeness**: the article recommends drilling straight (not angled) pilot
holes, testing with one screw before committing to all four, and notes
speed nuts as an easier-to-disassemble alternative to countersunk screws for
top-plate attachment (not included in typical kits) — none of this changes
any dimension in this project's own design, recorded only as general
installation-practice context in case it's useful to whoever eventually
assembles the physical part.
