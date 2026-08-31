# STMicroelectronics STPS3L60 Datasheet — DS2134 Rev 7

- **Manufacturer**: STMicroelectronics
- **Part Number**: STPS3L60 (60V/3A power Schottky rectifier; part family
  also includes STPS3L60U/STPS3L60S variants in different packages, not
  used here)
- **Datasheet Title**: "STPS3L60 — Power Schottky rectifier" (as printed
  on the document's own header)
- **Revision / Version**: DS2134, Rev 7
- **Publication Date**: January 2020 (printed on the document itself)
- **Official URL**: https://www.st.com/resource/en/datasheet/stps3l60.pdf
  (manufacturer-hosted datasheet PDF, confirmed reachable and
  text-extractable this session via an `r.jina.ai` reader proxy — full
  17-page document read)
- **Retrieved Date**: 2026-09-04
- **Local cache note**: not committed; content read live via the
  `r.jina.ai` text-extraction proxy this session, full Absolute Maximum
  Ratings / thermal / electrical characteristics tables captured directly
  from the primary document; not cached to any local disk.
- **Used for Evidence IDs**: DS-PROT-005

## Why this part

Selected as the series reverse-polarity-blocking diode for the new
~12V-class motor power input on Bench-IMU-01 Rev 3 (see
`bench-imu-01-design.md` §7.5.2). This design's own Rev 2 explicitly
identified a barrel-jack-style connector as the contrasting example for
why reverse-polarity protection matters ("...genuinely can be reversed by
a user", §3.3) — since Rev 3's new motor input is exactly that connector
type (PJ-102AH, DS-CONN-005), a discrete blocking diode is added here,
unlike the keyed USB-C input which does not need one.

A Schottky rectifier (not a standard silicon diode) was chosen for its
lower forward voltage drop (VF), reducing both conduction power loss and
the voltage "tax" subtracted from the already-modest motor-rail headroom
before the DRV10983's VCC pin. 60V/3A rating provides comfortable margin
above the DRV10983's absolute-maximum 3A startup/lock current
(**DS-MTR-056**, Table 10 Recommended Application Range — corrected
citation; DS-MTR-063 is a different fact, the `Op2ClsThr` open/closed-loop
register threshold, not the 3A current figure) without becoming a current
bottleneck at the motor's real worst-case operating current (§7.5.2,
§17/power-budget.md).

## Known gaps (honestly flagged, not guessed)

- The datasheet documents several package options for this same die
  (DO-201AD, DO-15, SMB, SMBflat, SMBflat Notch) with slightly different
  thermal resistance figures; this design specifies the **SMB** package
  variant specifically (Rth(j-l) = 20°C/W in that package) for SMT
  consistency with the other new protection part on this board (SMBJ16A,
  also SMB) — the other package options' thermal figures were noted but
  are not relied upon here.
- VF is characterized at a handful of discrete test points in the
  datasheet's typical-curve figures (graphical, not fully tabulated at
  every current); this design uses the closest tabulated points (0.53V
  typ @ IF=3A/Tj=100°C, 0.62V max @ IF=3A/Tj=25°C) as conservative
  bounds for the §7.5.2/power-budget thermal and voltage-drop
  calculations, rather than interpolating the graphical curve at this
  design's exact ~1-2A nominal operating current (which would show a
  somewhat lower VF than the 3A figures used) — this makes the design's
  own power/margin numbers conservative (an overestimate of diode loss),
  not optimistic.
