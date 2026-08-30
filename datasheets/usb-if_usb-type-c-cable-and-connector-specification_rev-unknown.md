# USB-IF Universal Serial Bus Type-C Cable and Connector Specification — Rev UNKNOWN

- **Manufacturer**: USB Implementers Forum (USB-IF) — standards body, not a component manufacturer
- **Part Number**: N/A — this is a connector/protocol specification, not a component part number
- **Datasheet Title**: "Universal Serial Bus Type-C Cable and Connector Specification"
- **Revision / Version**: UNKNOWN (specific revision, e.g. 2.3, not independently confirmed this session)
- **Publication Date**: UNKNOWN (not confirmed this session)
- **Official URL**: https://www.usb.org/document-library/usb-type-cr-cable-and-connector-specification (USB-IF's own document library; exact spec text not independently re-fetched this session — corroborated via secondary technical summaries during this session's search)
- **Retrieved Date**: 2026-08-31
- **Local cache note**: not committed; content (CC1/CC2 Rd=5.1kΩ pull-down requirement for a UFP/sink to enable VBUS from a compliant DFP/source) verified via live web search this session
- **Used for Evidence IDs**: DS-CONN-001

## Why this citation

Directly supports the USB-C vs. Micro-USB-B connector trade-off decision
in `hardware/schematic/bench-imu-01-design.md` §2 (Power block) — a
compliant USB-C source will not enable VBUS to a sink that does not present
the required Rd pull-down on CC1/CC2, even for a power-only (no data)
sink. This is why USB-C requires 2× 5.1kΩ CC-to-GND resistors that
Micro-USB-B does not need.
