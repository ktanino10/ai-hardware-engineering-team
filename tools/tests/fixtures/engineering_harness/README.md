# Synthetic KiCad fixtures

These are test-only connectivity and geometry witnesses, not component
recommendations, a manufacturing design, or a three-axis Rev5 board.
`generate.py` deterministically creates our own source files and
`manifest.json` hashes. No vendor symbol/footprint library or production
artifact is copied or opened.

| Case | Actual bounded content | Expected native result |
|---|---|---|
| Clean ERC | Two custom passive terminals connected by one on-grid wire | Zero reported violations |
| Failing ERC | The same two terminals without the connecting wire | `pin_not_connected` errors, not a parse/load error |
| Clean DRC | Closed rectangular outline, four embedded test pads, two separated tracks on distinct nets | Zero reported violations |
| Failing DRC | Two pad-anchored nets crossing on the same copper layer | `tracks_crossing` error |
| Invalid outline | The same pad/track fixture with a single open edge instead of a closed boundary | `invalid_outline` error |

ERC uses the committed `sym-lib-table` and custom `Harness.kicad_sym`;
each operation copies only its declared native inputs to an isolated runtime.
PCB footprints are embedded. The matching `.kicad_pro` files freeze the
test rules and have no added exclusions. `--severity-all` includes errors,
warnings and exclusions, but **does not enable checks KiCad defaults to
ignore**; those default ignored-check lists are frozen in the experiment
plan and checked by the parser. No native `--schematic-parity` claim is made.
The schematic and PCB witnesses are independent, not a matched product.

`dependency.json` and `approval.json` are explicitly synthetic fixtures.
The final comparison uses the **native** invalid-outline PCB. Historical-only
dependency integrity cannot establish current freshness. Approval JSON
cannot enable a physical action or a manufacturing export.

Regenerate only in a new admitted implementation task, before freezing an
experiment candidate:

```sh
python3 tools/tests/fixtures/engineering_harness/generate.py
```

Do not regenerate fixtures or loosen thresholds during final measurements.
