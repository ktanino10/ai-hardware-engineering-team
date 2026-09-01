# Infineon (International Rectifier) IRLZ44N Datasheet — Rev UNKNOWN

- **Manufacturer**: Infineon Technologies (part originated under
  International Rectifier, since acquired by Infineon; also widely
  second-sourced, e.g. by Vishay — this record cites the Infineon/IR
  lineage specifically, the "IRLZ44NPBF" Pb-free orderable variant).
- **Part Number**: IRLZ44N (orderable as **IRLZ44NPBF**, TO-220AB,
  through-hole, Pb-free).
- **Datasheet Title**: "IRLZ44N HEXFET Power MOSFET" (title as commonly
  printed on this part family's datasheet; not independently
  re-transcribed from a primary PDF this session).
- **Revision / Version**: UNKNOWN.
- **Publication Date**: UNKNOWN.
- **Official URL**: https://www.infineon.com/part/IRLZ44N (Infineon's own
  product page).
- **Retrieved Date**: 2026-09-08.
- **Local cache note**: not committed; content read this session via
  Infineon's own product page and a Mouser-hosted datasheet mirror
  (`mouser.com/catalog/specsheets/international%20rectifier_irlz44n.pdf`)
  — the Mouser-hosted PDF link itself was not independently
  text-extracted this session (same binary/non-text-extractable
  limitation as other parts in this evidence set); figures below are
  drawn from the search-engine-surfaced summary of that document plus
  Infineon's own product page.
- **Used for Evidence IDs**: DS-PROT-019.

## Key extracted figures

| Parameter | Value | Note |
|---|---|---|
| Drain-source voltage (VDS max) | 55 V | paired with LM5069 (9–80 V range) for this design's ≤13 V envelope — large margin |
| R_DS(on) | 22 mΩ max @ VGS = 10 V; 35 mΩ max @ VGS = 4.5 V | LM5069's gate charge-pump drives the gate to ≈12 V above the source node regardless of VIN, so the ≈22 mΩ figure is the realistic operating point, comfortably under this design's ≤35 mΩ target; even the worst-case 4.5 V-drive figure (35 mΩ) sits right at the target, not over it |
| Continuous drain current (ID) | 47 A @ 25°C (package/thermal-limited in practice; this design's ≤3 A worst-case current is a small fraction of this rating) | |
| Logic-level gate | Yes — fully enhances from a logic-level (as low as ~4.5 V) gate-source voltage, not requiring a full 10 V+ drive to reach low R_DS(on) | relevant given LM5069's charge pump target, though the charge pump already exceeds logic-level drive requirements with margin |
| Package | TO-220AB, through-hole | the easiest of any candidate/sub-component in this entire comparison to hand-solder — arguably easier than any of the leaded SMD packages (HTSSOP, VSSOP) also considered, since through-hole leads need no fine-pitch SMD technique at all |
| Price | ≈$1.80 (DigiKey, qty 1); volume pricing as low as ≈$0.60 | checked 2026-09-08 |
| Lifecycle / availability | Active/current, widely available, not obsolete, per Infineon's own product page and DigiKey listing | |

## Why this part / why not an alternative logic-level MOSFET

Selected as an extremely well-proven, long-lived, widely-second-sourced
logic-level N-channel power MOSFET for the discrete Candidate C
combination (paired with LM5069, `texasinstruments_lm5069mm-1_unknown-
rev.md`). Its voltage (55 V), current (47 A), and R_DS(on) (22–35 mΩ)
ratings are all far in excess of this design's actual ≤3 A / ≤13 V need
— this is intentional headroom, not a close-fit selection, since the
part's main selection criteria here were (a) logic-level gate
compatibility with LM5069's own gate-drive output, (b) an easy-to-hand-
solder through-hole package, and (c) extremely well-established
availability/pedigree (this is one of the most widely used hobbyist/
prototyping logic-level MOSFETs in existence) rather than a tight
electrical optimization. No competing MOSFET candidates were separately
researched for this sub-role, since Candidate C as a whole was not the
final recommendation (see the parent BOM section) — if Candidate C were
later selected instead, a more tailored FET comparison (e.g. optimizing
R_DS(on) or package size further) would be a reasonable follow-up, not
performed here.

## Known gaps (honestly flagged, not guessed)

- No independent primary-datasheet PDF read this session — figures above
  come from Infineon's own product page and a search-engine-surfaced
  summary of a Mouser-hosted datasheet mirror, not a direct page-numbered
  read.
- Gate charge (Qg), thermal resistance (RθJC/RθJA), and safe-operating-
  area (SOA) curves — all relevant to a full thermal design for this
  application — are **UNKNOWN this session**, deferred to Circuit
  Engineer's detailed design phase if Candidate C is ever selected.
