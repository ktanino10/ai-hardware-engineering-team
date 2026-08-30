# Microchip MCP1700T-3302E/TT Datasheet — Rev UNKNOWN

- **Manufacturer**: Microchip Technology
- **Part Number**: MCP1700T-3302E/TT (MCP1700 family, fixed 3.3V / SOT-23-3, tape-and-reel option)
- **Datasheet Title**: UNKNOWN (exact printed title not independently re-confirmed against the literal PDF cover page this session). No document/literature number was surfaced in this session's research. Functional description: Microchip MCP1700-family low quiescent current LDO regulator datasheet, oriented toward battery/wearable applications.
- **Revision / Version**: UNKNOWN (not confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.microchip.com/en-us/product/MCP1700 (Microchip product page — stable/high-confidence URL pattern; the specific datasheet PDF itself was accessed this session via the product page's documentation tab / distributor-mirrored copies, not a single fixed PDF permalink independently re-verified byte-for-byte this session).
- **Retrieved Date**: 2026-08-30
- **Local cache note**: not committed; content verified via live web search this session, cross-checked across ≥2 independent sources per critical fact (mouser.com listing, lcsc.com C39051, microchip.com).
- **Used for Evidence IDs**: DS-PWR-012, DS-PWR-013, DS-PWR-014, DS-PWR-015, DS-PWR-016, DS-PWR-017, DS-PWR-018, DS-PWR-019, DS-PWR-020, DS-PWR-021, DS-PWR-022

## Status note (per this repo's evidence rules)

This part is **disqualified** for use in the Bench-IMU-01 design: its 250 mA
rated max output current is below REQ-103's 300 mA system current budget, and
its own package thermal budget (≈253 mW @ TA=40°C) is exceeded by actual
dissipation (425 mW) even at its own rated 250 mA — see
`bom/component-selection.md` "Power Regulator" section. Retained here only as
a documented comparison point.
