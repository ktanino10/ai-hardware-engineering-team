# GCT (Global Connector Technology) USB4105-GF-A Datasheet — Rev UNKNOWN

- **Manufacturer**: GCT (Global Connector Technology)
- **Part Number**: USB4105-GF-A
- **Datasheet Title**: "USB4105 — USB 2.0 Connector Type C Horizontal Receptacle (socket)" (per manufacturer drawing/product page)
- **Revision / Version**: UNKNOWN (not confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://gct.co/files/drawings/usb4105.pdf (manufacturer drawing, directly cited by the real KiCad footprint's own `descr` field already used on this board — `hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb`, footprint `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`); product page https://gct.co/connector/usb4105
- **Retrieved Date**: 2026-09-02
- **Local cache note**: not committed; content verified via live web search/fetch this session (the PDF's own encoded content stream could not be parsed as text by this session's fetch tool — corroborated instead via Mouser's own mirrored datasheet page and DigiKey/Mouser product listings, cross-checked against the footprint's own embedded tags)
- **Used for Evidence IDs**: DS-CONN-007

## Why this citation

**J1's real, currently-orderable MPN — resolves the design doc's own
explicitly-disclosed open item** (`bench-imu-01-design.md` §14 item 8:
"J1's exact USB-C receptacle MPN... not formally selected this cycle").
The real KiCad footprint already placed on the board
(`USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`) carries its own
`tags` metadata listing exact compatible real MPNs:
`USB4105-15-A`, `USB4105-15-A-060`, `USB4105-15-A-120`, `USB4105-GF-A`,
`USB4105-GF-A-060`, `USB4105-GF-A-120`. Of these, `USB4105-GF-A` (the base
part, no `-060`/`-120` thin-board suffix — this board is a standard 1.6mm
thickness, confirmed via the fab package's own Gerber job file) is
genuinely in stock at both DigiKey (108,586 units, live-checked this
session) and Mouser, while `USB4105-15-A` is not normally stocked (9-week
factory lead time, 50,400-unit minimum order quantity at Mouser) —
confirmed via live distributor search this session, not assumed.
Electrically/mechanically the two variants are identical (16-pin, USB 2.0,
5A VBUS rating, 48V DC max, 20,000 mating cycles, top-mounted/horizontal);
the `-15-A` vs. `-GF-A` difference is a contact-plating/packaging
designation, not a pinout or footprint difference — independently
cross-checked pinout (VBUS/GND/D+/D-/SBU1/SBU2/CC1/CC2 at the standard
16-contact USB2.0-only Type-C assignment) against the design's own
requirement that D+/D- exist on the physical part but are deliberately
left unpopulated/unrouted (REQ-105).
