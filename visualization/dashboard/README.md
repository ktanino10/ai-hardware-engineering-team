# Project Dashboard (Bench-IMU-01)

A bird's-eye status view for the human Chief Engineer: what phase things are
in, what's waiting on a human decision right now, findings/quality
snapshot, recent activity, and an electrical/mechanical snapshot. Open
`index.html` directly in a browser, or view it hosted on GitHub Pages.
Bilingual UI chrome (EN/JA toggle, top-right) — see "Bilingual UI, English
data" below for exactly what does and doesn't get translated, and why.

## Why this page works completely differently from the other two viewers

`circuit-viewer/` and `assembly-viewer/` are built from **static, checked-in
data files** (`circuit-data.js`, `assembly-data.js`) — hand-derived once
from the real KiCad netlist/BOM/STL exports, committed to git, and only
updated when someone re-runs that derivation by hand. That pattern is right
for them: a schematic or a 3D mechanical assembly doesn't change every few
minutes, and "generated once, reviewed, committed" is the more trustworthy
process for that kind of artifact.

This dashboard's job is the opposite: track `requirements/`, `validation/`,
and `bom/component-selection.md`, files that this project's own history
shows changing constantly (68+ ECOs and counting, many PRs merged per day).
A static data file for content that volatile would be stale within hours of
being generated, and — worse — would look authoritative while quietly
lying. So this page does the trade-off the other direction:

- **`dashboard-live.js`** fetches the real Markdown source files directly
  from `raw.githubusercontent.com` (not the GitHub API, no auth, no rate
  limit beyond the CDN's own — confirmed this endpoint sends
  `access-control-allow-origin: *`, so an unauthenticated browser `fetch()`
  from a GitHub Pages origin works for this public repo) **every time the
  page loads**, and parses them into plain data in the browser. Nothing
  here is pre-generated or committed — that's the whole point, and why this
  file is deliberately *not* named like `circuit-data.js`/`assembly-data.js`
  (those are static data; this is a live fetch-and-parse routine).
- **`dashboard-render.js`** turns that parsed data into the DOM, section by
  section, with a per-section fallback if a parse didn't work out.
- A **Refresh** button re-runs the whole fetch+parse+render cycle without a
  full page reload.

Trade-off accepted knowingly: ~1.4MB of Markdown is fetched across 8 files
on every load/Refresh (sizes at time of writing: `open-issues.md` 446KB,
`change-log.md` 266KB, `component-selection.md` 210KB, `evidence-log.md`
243KB, `requirements.md` 108KB, `mechanical-interface.md` 104KB,
`traceability-matrix.md` 46KB, `workflow.md` 45KB) — acceptable for an
internal status dashboard served off GitHub's own CDN, not something that
needs to be fast for a large public audience.

## What it shows

1. **⚠ Pending Human Decisions** (top, most prominent) — every
   `bom/component-selection.md` Approval-table row whose Chief Engineer
   line has a literal `PENDING` Date cell, every `validation/open-issues.md`
   finding that's `OPEN` **and** `CRITICAL`/`HIGH`, and a hedged secondary
   signal from `requirements.md`'s "Open Questions for the Human" headings
   (see "Parsing rules" below for exactly how that last one is qualified).
   Shows a clear "nothing blocking" state when all three are empty — that's
   a real, useful signal too, not just an edge case to paper over.
2. **Phase / Process Pipeline** — the process phases themselves are
   live-extracted from `docs/workflow.md`'s own `### Phase N — Name`
   headers (so this list can't go stale even if a phase is renamed or a new
   one is added), annotated with whatever concrete live signal exists for
   that phase. Deliberately does **not** assert one project-wide "you are
   here" phase/revision marker — see "A deliberate design decision" below
   for why — and instead surfaces each key document's own self-reported
   bold **Status:** line verbatim underneath.
3. **Findings & Quality Snapshot** — severity × status grid from
   `validation/open-issues.md`, ECO/finding/Evidence-ID scale counts, and a
   compact Design-Complete-Gate condition check (`docs/architecture.md`
   §8, conditions 1–3 computed live; conditions 4–5 linked, not tracked
   here — this dashboard doesn't fetch `validation/fmea.md`).
4. **Recent Activity** — the last 12 rows of `validation/change-log.md`'s
   ECO log, in document order.
5. **Electrical & Mechanical Snapshot** — links to `circuit-viewer/` and
   `assembly-viewer/` (this page doesn't try to duplicate their rendering),
   plus board outline size and mounting-hole count pulled live from
   `hardware/mechanical-interface.md`.
6. **Requirements Snapshot** — Must/Should/Could/Won't priority counts and
   a Rev-tag breakdown, tallied live across every requirement row in
   `requirements/requirements.md`.

## Bilingual UI, English data

An EN/JA toggle (top-right, styled after `circuit-viewer/`'s own dormant
`.lang-toggle` CSS pattern from before it was simplified to English-only)
switches this dashboard's **own UI chrome** — titles, section headings,
buttons, my own template sentences and badge labels, stat/fact labels,
footnotes, and error-fallback messages. The choice persists via
`localStorage` across visits. Toggling never re-fetches data — it re-renders
the already-loaded content from memory in the new language.

This is scoped to this dashboard only, per an explicit request: `circuit-viewer/`
and `assembly-viewer/` are untouched and stay English-only, matching their
own prior, explicitly-requested simplification.

**Deliberately never translated, in either language** — agreed with the
human Chief Engineer before implementing, given the same
mistranslation/meaning-shift concern that motivated the request in the
first place:

- Anything actually fetched and parsed from this repository's own files:
  component-selection.md decision text, finding titles, ECO revision/
  changed text, self-reported status lines, and phase names extracted live
  from `docs/workflow.md`.
- This project's own **defined governance vocabulary** — severity
  (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`), status (`OPEN`/`RESOLVED`/
  `ACCEPTED-RISK`), and priority (`Must`/`Should`/`Could`/`Won't`) — these
  are precise terms-of-art defined in `docs/architecture.md` §7.1/§8 and
  appear verbatim in the source files; a translated gloss (e.g. for
  `ACCEPTED-RISK`, which carries a specific governance meaning) risks the
  reader not recognizing the term when they go read the real English
  source documents, which is the opposite of what was asked for.
- IDs (`ISS-005`, `ECO-068`, `REQ-021`), file paths, and `Rev N`/`Phase N`
  designators.

Everything else — the actual majority of visible text on the page — is
genuine chrome I authored for this dashboard, and is fully bilingual.
`dashboard-i18n.js` owns this split: a `STRINGS` dictionary (`{en, ja}`
pairs, some parameterized as small functions so word order can differ
between the two languages around a number), a `t(key, ...args)` lookup, and
`setLang()`/`applyStaticChrome()` to apply it.

## A deliberate design decision: no single "Rev N / current phase" claim

The brief this page was built from assumed one project-wide revision
counter ("Rev 1 through Rev 5"). Reading the real files surfaced that this
isn't how the project's own documents actually work: `requirements.md`,
`hardware/schematic/bench-imu-01-design.md`, and
`hardware/mechanical-interface.md` each keep their **own** independent "Rev
N" for their own scope, and they don't line up — e.g. the schematic
document's own "Rev 5" (a motor-rail supervisory-controller addition)
predates and is unrelated to `requirements.md`'s "Rev 5" (the newly-approved
3-axis "Cube" scope expansion). Forcing these into one headline number
would have manufactured exactly the "stale figure propagation" failure mode
`docs/workflow.md` §4.2 already documents as a real, recurring hazard in
this project. So this dashboard deliberately shows each document's own
self-reported status **verbatim**, plus hard, unambiguous counts (PENDING
approvals, OPEN CRITICAL/HIGH, Verified/Pending traceability rows) instead.

## Parsing rules (validated against the real, live file content — not synthetic test data)

A single reusable table extractor (`extractAllTables` in
`dashboard-live.js`) is used for every Markdown table on this page,
philosophically mirroring this repo's own `tools/check_id_uniqueness.py`
(whose docstring documents a real incident where a naive parser silently
truncated a table for an entire session): it locates a table by its header
row's **real cell names** (never a hardcoded column index), tracks the
nearest Markdown heading while scanning (so `bom/component-selection.md`'s
~13 independent per-component Approval tables each get attributed to the
right section, walking past boilerplate sub-headings like "Approval" or
"Recommendation" to the nearest heading that actually names the
component/re-evaluation), and ends a table's data rows only at the next
heading or EOF — a stray blank line or malformed row in between is skipped,
not treated as the table's end.

Specific rules, each checked against this repo's real current content
during development:

- **Component approvals**: a row is "pending" only if its Chief Engineer
  line's Date cell is the literal string `PENDING` (case-insensitive,
  exact) — not merely mentioning the word anywhere. Verified against the
  real file: finds exactly the MCU/IMU/Motor/Motor-Driver-IC Rev 5
  re-evaluations plus the Electromagnetic Brake and Wireless
  Remote-Control-Link sections (6 today), correctly leaving the 7
  already-dated/approved sections alone.
- **Findings**: only rows whose ID starts `ISS-`/`MISS-` are tallied;
  Severity/Status are matched by exact value (`CRITICAL`/`HIGH`/`MEDIUM`/
  `LOW` × `OPEN`/`RESOLVED`/`ACCEPTED-RISK`), not substring, since a Notes
  cell can be 10,000+ characters and mention any of these words
  incidentally. Only ID/Severity/Status/Title are ever read — the Notes,
  Failure Mechanism, Recommended Fix, etc. columns are never parsed for
  display, both because they're enormous and because 2 real rows in this
  file (and 2 in `evidence-log.md`) contain a literal, non-delimiter `|`
  character inside a backtick code span; confirmed those occur only in
  columns past the ones this page reads, so they can't misalign the
  columns actually used.
- **Traceability status**: bucketed by matching `Verified`/`Pending`/
  `Waived`/`Failed` at the **start** of the (bold-marker-stripped) cell,
  not "contains anywhere" — an earlier draft of this parser used an
  unanchored substring check and mis-bucketed real rows like `"Verified —
  confirmed waived, not applicable"` (REQ-505) and `"Verified — ...
  hardware confirmation pending physical build"` (REQ-405/406) into the
  wrong bucket purely because those words appear later in the explanatory
  sentence. Caught by cross-checking the live parser's output against a
  manual count of the real file and fixed before this page shipped.
- **Requirements priority**: bucketed `Won't` > `Must` > `Should` > `Could`
  in that check order, so a cell like `"Must, upgraded from Should"`
  (a real value in this file) is correctly counted as `Must`.
- **"Possibly still open" requirements questions**: a heading shaped
  `## <N><letter>. ... (new, pending confirmation)` is only surfaced if no
  *later* lettered subsection exists under the same number (e.g. `§9i`
  after `§9h`) — a later letter existing is a strong, not certain, sign the
  question set was already addressed, so this dashboard doesn't flag it as
  live-pending. This generalizes to a future Rev 6 etc. without new code.
- Every parser above is wrapped so a shape mismatch returns
  `{ok:false, error}` for that section alone — verified this actually
  matters, not just a defensive nicety nobody will hit, given how much this
  project's own file formats have already shifted revision to revision.

## Known limitations (disclosed)

- **Bilingual UI, not bilingual data — by design, not oversight.** The
  original brief this page was first built from assumed the whole site
  uses `nameEn`/`nameJa` bilingual labels throughout; that turned out to be
  inaccurate for the *other two* viewers (`circuit-viewer/`'s own README
  states it went English-only "per explicit user preference"; neither it
  nor `assembly-viewer/` nor the landing page has a live Japanese variant,
  and this page doesn't touch them). This dashboard's *own* chrome, added
  in a follow-up request, is bilingual — see "Bilingual UI, English data"
  above for exactly what does/doesn't get translated and why.
- **GitHub raw-content CDN caching**: `raw.githubusercontent.com` can serve
  a cached response up to a few minutes stale after a very recent commit —
  "live" here means "fetched fresh every page load," not "guaranteed
  sub-second."
- **Design-Complete-Gate counts are cumulative across each file's whole
  history**, not scoped to one revision — `validation/open-issues.md` and
  `requirements/traceability-matrix.md` don't structurally separate
  "this revision's" rows from prior ones, so e.g. the traceability Pending
  count includes in-progress Rev 5 rows alongside any from earlier
  revisions that were never revisited.
- **Best-effort parsing, not a guarantee.** These are large, hand-authored
  Markdown tables with 10,000+ character prose cells and formats that have
  already shifted slightly across revisions. Every parser is defensive and
  fails gracefully per-section, but a future format change big enough could
  still degrade a section to its fallback link rather than silently
  showing wrong numbers — that's the intended failure mode.
- This page is **read-only and presentational** — it never writes anything
  back to the repository, and requires no authentication (this is a public
  GitHub Pages site reading a public repo).
