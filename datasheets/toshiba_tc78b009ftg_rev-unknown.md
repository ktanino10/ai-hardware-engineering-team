# Toshiba TC78B009FTG Datasheet — Rev UNKNOWN

- **Manufacturer**: Toshiba Electronic Devices & Storage Corporation
- **Part Number**: TC78B009FTG
- **Datasheet Title**: Believed to be "Toshiba Original CMOS 3-Phase Full
  Wave Sine-Wave PWM Driver" family style title, per Toshiba's usual
  naming convention for this device family — **not independently
  confirmed this session** (the literal cover page was not read).
- **Revision / Version**: UNKNOWN this session. A secondary web-search
  source describes a 62-page English datasheet dated approximately June
  2022, but this was **not independently verified against the primary PDF**
  this session.
- **Publication Date**: UNKNOWN this session (see above — approx. June 2022
  per secondary source only, not confirmed).
- **Official URL**: Toshiba's own product page for TC78B009FTG (JS-rendered;
  this session's tooling could not extract its content directly) and a
  `docget`-style Toshiba PDF URL pattern (returned HTTP 404 for the exact
  path attempted this session — may be a stale/incorrect literal path, not
  proof the document doesn't exist; the part is confirmed real and
  in-production via simultaneous live distributor stock at DigiKey, Mouser,
  and Arrow).
- **Retrieved Date**: 2026-08-31 (attempted; not successfully retrieved as
  primary source text — see Confidence flag below)
- **Local cache note**: not committed; nothing cached (nothing was
  successfully retrieved from the primary document this session).
- **Used for Evidence IDs**: DS-MTR-049, DS-MTR-050, DS-MTR-051

## Confidence flag — read this before relying on any fact below (IMPORTANT)

**This record's underlying claims are secondary-source-verified, not
primary-source-verified, and materially lower confidence than every other
metadata record in this directory added for the Rev 3 Motor Driver
candidate comparison.** This session:

1. Attempted a direct `web_fetch` of a Toshiba `docget`-pattern datasheet
   URL — returned HTTP 404.
2. Attempted a direct fetch of a Mouser product page for this part — timed
   out.
3. A dedicated research sub-agent attempted the JS-rendered Toshiba product
   page directly — could not extract content (JS rendering not supported by
   this session's tooling).
4. Fell back to `web_search`, which returned an AI-synthesized answer citing
   an alldatasheet.jp mirror of the datasheet plus Toshiba's own (JS-
   rendered, unreadable-to-this-session) product page as its sources. The
   specific claims in DS-MTR-050 (FG output pin, ALERT pin, sensorless BEMF
   commutation, PWM/analog/I2C control) come from that synthesized answer,
   **not from this session directly reading the primary PDF or product
   page**.

The part itself and its datasheet's real-world existence are **not** in
doubt — it is confirmed in stock and actively sold at 3 independent major
distributors (DigiKey, Mouser, Arrow) simultaneously, which would not be
true of a fictitious/discontinued part. This is therefore **not** treated
as a "no datasheet can be found" Human-in-the-loop escalation
(`docs/architecture.md` §10) — the datasheet demonstrably exists and is
findable, just not fully readable by this session's tooling this cycle.
It **is** treated as a real, disclosed evidence-quality gap: this part is
presented in `bom/component-selection.md` as a worthwhile candidate on
paper, but **not** the recommended driver, in part *because* TI DRV10983's
equivalent facts were confirmed via a directly-fetched, live TI HTML
product page this same session (still one step below a literal PDF-table
citation, but a meaningfully stronger evidence chain than this record's).
Anyone revisiting this candidate should independently retrieve and read
the actual Toshiba PDF (or request it from a Toshiba/distributor FAE)
before treating any number here as final.
