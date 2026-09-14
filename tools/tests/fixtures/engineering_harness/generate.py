"""Generate our synthetic connectivity/clearance fixtures; no vendor parts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import uuid


ROOT = Path(__file__).resolve().parent


def uid(label: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "engineering-harness-test-only/" + label))


SYMBOL = """
  (symbol "Terminal"
    (pin_numbers hide)
    (pin_names (offset 0) hide)
    (in_bom no)
    (on_board no)
    (property "Reference" "J" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Terminal" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "Terminal_0_1"
      (rectangle (start -1.27 1.27) (end 1.27 -1.27)
        (stroke (width 0) (type default)) (fill (type background))))
    (symbol "Terminal_1_1"
      (pin passive line (at -3.81 0 0) (length 2.54)
        (name "1" (effects (font (size 1.27 1.27))))
        (number "1" (effects (font (size 1.27 1.27))))))
  )
"""


def schematic(name: str, connected: bool) -> str:
    root_uuid = uid(name)
    instances = []
    for number, x in ((1, 54.61), (2, 80.01)):
        instances.append(f"""
  (symbol (lib_id "Harness:Terminal") (at {x} 50.8 0) (unit 1)
    (in_bom no) (on_board no) (dnp no) (uuid "{uid(name + str(number))}")
    (property "Reference" "J{number}" (at {x} 48.26 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Terminal" (at {x} 53.34 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at {x} 50.8 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "" (at {x} 50.8 0) (effects (font (size 1.27 1.27)) hide))
    (pin "1" (uuid "{uid(name + 'pin' + str(number))}"))
    (instances (project "{name}" (path "/{root_uuid}" (reference "J{number}") (unit 1))))
  )
""")
    wire = f"""
  (wire (pts (xy 50.8 50.8) (xy 76.2 50.8)) (stroke (width 0) (type default))
    (uuid "{uid(name + 'wire')}"))
""" if connected else ""
    return f"""(kicad_sch (version 20250114) (generator "engineering_harness_fixture")
  (uuid "{root_uuid}") (paper "A4")
  (lib_symbols {SYMBOL.replace('(symbol "Terminal"', '(symbol "Harness:Terminal"', 1)})
  {wire}
  {''.join(instances)}
)
"""


def board(name: str, crossing: bool) -> str:
    second = "(start 25 15) (end 25 25)" if crossing else "(start 20 23) (end 30 23)"
    positions = [(20, 20, 1), (30, 20, 1)]
    positions += [(25, 15, 2), (25, 25, 2)] if crossing else [(20, 23, 2), (30, 23, 2)]
    pads = "\n".join(
        f'    (pad "{i}" smd circle (at {x} {y}) (size 1 1) (layers "F.Cu" "F.Mask") '
        f'(net {net} "TEST_{"A" if net == 1 else "B"}") (uuid "{uid(name + "pad" + str(i))}"))'
        for i, (x, y, net) in enumerate(positions, 1)
    )
    return f"""(kicad_pcb (version 20241229) (generator "engineering_harness_fixture")
  (general (thickness 1.6))
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (37 "F.SilkS" user)
    (39 "F.Mask" user)
    (47 "F.CrtYd" user)
    (44 "Edge.Cuts" user))
  (setup (pad_to_mask_clearance 0))
  (net 0 "")
  (net 1 "TEST_A")
  (net 2 "TEST_B")
  (footprint "HarnessTestPads" (layer "F.Cu") (at 0 0)
    (uuid "{uid(name + 'pads')}")
    (attr board_only exclude_from_pos_files exclude_from_bom)
    (property "Reference" "T1" (at 25 13) (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)) hide))
    (property "Value" "SYNTHETIC_ONLY" (at 25 12) (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)) hide))
    (fp_rect (start 18 13) (end 32 27)
      (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
{pads}
  )
  (gr_rect (start 10 10) (end 40 30)
    (stroke (width 0.05) (type default)) (fill none) (layer "Edge.Cuts")
    (uuid "{uid(name + 'outline')}"))
  (segment (start 20 20) (end 30 20) (width 0.5) (layer "F.Cu")
    (net 1) (uuid "{uid(name + 'track1')}"))
  (segment {second} (width 0.5) (layer "F.Cu")
    (net 2) (uuid "{uid(name + 'track2')}"))
)
"""


def generate() -> None:
    payloads = {
        "Harness.kicad_sym": '(kicad_symbol_lib (version 20241209) (generator "engineering_harness_fixture")\n' + SYMBOL + ")\n",
        "sym-lib-table": '(sym_lib_table (version 7)\n  (lib (name "Harness") (type "KiCad") (uri "${KIPRJMOD}/Harness.kicad_sym") (options "") (descr "Synthetic test terminals; no real component")))\n',
        "clean.kicad_sch": schematic("clean", True),
        "erc_violation.kicad_sch": schematic("erc_violation", False),
        "clean.kicad_pcb": board("clean", False),
        "drc_violation.kicad_pcb": board("drc_violation", True),
        "invalid_outline.kicad_pcb": board("invalid_outline", False).replace(
            "(gr_rect (start 10 10) (end 40 30)", "(gr_line (start 10 10) (end 40 10)", 1,
        ).replace('(fill none) (layer "Edge.Cuts")', '(layer "Edge.Cuts")', 1),
        "dependency.json": json.dumps({
            "scope": "SYNTHETIC_ONLY", "fixture": "not-a-real-simulation",
            "model_revision": "fixture-v1", "verification_mode": "CURRENT",
        }, indent=2) + "\n",
        "approval.json": json.dumps({
            "scope": "SYNTHETIC_ONLY", "actor": "fictitious-test-actor",
            "usable_for_real_action": False, "requested_action": "manufacturing-export",
        }, indent=2) + "\n",
    }
    project = {
        "meta": {"version": 1, "filename": ""},
        "board": {"design_settings": {
            "rules": {"min_clearance": 0.2, "min_track_width": 0.2},
            "drc_exclusions": [], "rule_severities": {},
        }},
        "erc": {"erc_exclusions": [], "rule_severities": {}},
        "libraries": {"pinned_symbol_libs": ["Harness"]},
    }
    for name in ("clean", "erc_violation", "drc_violation", "invalid_outline"):
        project["meta"]["filename"] = name + ".kicad_pro"
        payloads[name + ".kicad_pro"] = json.dumps(project, indent=2) + "\n"
    payloads = {
        name: "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
        for name, text in payloads.items()
    }
    for name, text in payloads.items():
        (ROOT / name).write_text(text)
    manifest = {
        "schema_version": 1, "scope": "SYNTHETIC_ONLY",
        "files": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in sorted(payloads.items())},
        "domain_inputs": {
            "clean-erc": ["clean.kicad_sch", "clean.kicad_pro", "sym-lib-table", "Harness.kicad_sym"],
            "failing-erc": ["erc_violation.kicad_sch", "erc_violation.kicad_pro", "sym-lib-table", "Harness.kicad_sym"],
            "clean-drc": ["clean.kicad_pcb", "clean.kicad_pro"],
            "failing-drc": ["drc_violation.kicad_pcb", "drc_violation.kicad_pro"],
            "invalid-outline": ["invalid_outline.kicad_pcb", "invalid_outline.kicad_pro"],
        },
        "rule_policy": {"reported_violations_allowed": 0, "severity": "all", "exclusions": []},
        "expected_domain_failure": {
            "failing-erc": "pin_not_connected", "failing-drc": "tracks_crossing",
            "invalid-outline": "invalid_outline",
        },
        "nonempty": {"erc": "Two custom passive test terminals, connected or disconnected",
                     "drc": "Closed outline, four embedded test pads and two copper tracks on distinct nets, parallel or crossing"},
        "external_symbol_or_footprint_libraries": [],
        "limitations": "No production components, parity, hardware feasibility, manufacturing or Rev5 blocker acceptance.",
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    generate()
