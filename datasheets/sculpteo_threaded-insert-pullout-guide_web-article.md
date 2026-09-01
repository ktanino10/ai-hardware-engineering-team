# Sculpteo — "Pull-out Resistance of Threaded Inserts: Testing and Results" (web article/design guide, Rev UNKNOWN)

- **Manufacturer**: N/A — Sculpteo (an industrial 3D-printing service
  bureau) technical design-guide/testing article, not a fastener
  manufacturer's own datasheet.
- **Part Number**: N/A — general M3 brass threaded-insert pull-out test in
  MJF (Multi Jet Fusion) PA12 nylon parts.
- **Datasheet Title**: "Pull-out Resistance of Threaded Inserts: Testing and
  Results" (sculpteo.com 3D-learning-hub design-guidelines article).
- **Revision / Version**: UNKNOWN (web article, not versioned).
- **Publication Date**: UNKNOWN
- **Official URL**: sculpteo.com/en/3d-learning-hub/design-guidelines/pull-out-resistance-of-threaded-inserts-testing-and-results/
  — this session directly fetched this URL and confirmed it is a real, live
  page describing this exact test; however, the page's actual numeric
  results table did not render as retrievable text through this session's
  fetch tool (likely client-side/JS-rendered), so **the specific ≈1258 N
  M3/MJF-PA12 figure used in this project's estimate was obtained via an
  AI-assisted web search that cited this article as its source, not by this
  session directly reading the table itself.**
- **Retrieved Date**: 2026-09-13
- **Local cache note**: not committed; page existence/topic confirmed via
  direct fetch this session, but the specific figure below is a
  second-hand (search-engine-mediated) transcription, honestly disclosed as
  such — see confidence marking in `bench-imu-01-dimensional-spec.md` §8.1.
- **Used for Evidence IDs**: DS-FAST-003

## Why this reference matters here

Used only as a **secondary, corroborating** cross-check for the primary
fastener pull-out figure (`datasheets/cnckitchen_petg-threaded-insert-pullout-test_web-article.md`,
DS-FAST-002): a different process (MJF, not FDM), different material (PA12
nylon, not PETG), and different insert vendor, yet reports a comparable
single-insert M3 pull-out capacity (**≈1258 N**) to the CNC Kitchen FDM/PETG/
Ruthex figure (≈1167 N average). This convergence across genuinely
independent process/material/source combinations is useful supporting
evidence that the ~1100-1300 N order of magnitude is a reasonable
real-world M3 heat-set/threaded-insert pull-out capacity in a plastic host
material generally — but this specific number carries a lower confidence
tier than DS-FAST-002 because of the search-engine-mediated retrieval path
disclosed above.

## Known gaps (honestly flagged, not guessed)

- Numeric results table not independently read by this session (see above)
  — treat the ≈1258 N figure as ESTIMATE-tier, not a directly-verified
  primary-source read, until a human re-fetches and confirms the table
  directly.
- MJF PA12 is a different manufacturing process (powder-bed-fusion) from
  this design's own FDM-printing assumption — not a strict apples-to-apples
  comparison, used only as an order-of-magnitude cross-check.
