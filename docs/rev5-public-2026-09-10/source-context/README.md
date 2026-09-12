# Bound project context — public derivatives

These are **project-authored analysis records**, not manufacturer PDFs, PDF
text/image extracts, raw uploads or fresh source verification. Read them as
conditional, unadopted design context. Electrical requirements and their
UNKNOWNs remain as recorded. No component, pin, source or topology is changed.

| Public file | Original archive role | Export treatment |
|---|---|---|
| [acceptance-spec.json](acceptance-spec.json) | A1 acceptance specification | Provenance-redacted JSON; C1–C5, event ordering, envelope and evidence obligations unchanged |
| [firmware-authority-map.json](firmware-authority-map.json) | Technical B issuer/authority map | Provenance-redacted JSON, **not operator authorization**; routes, unimplemented enforcer and external-actor limitations unchanged |
| [driver-proposal.json](driver-proposal.json) | Conditional driver proposal | Provenance-redacted JSON; exact proposed pins, separate domains, conditions and UNKNOWN loads retained |
| [driver-schematic.md](driver-schematic.md) | Project-authored proposed connection diagram | Exact copy, not native CAD or manufacturer artwork |
| [source-proposals.json](source-proposals.json) | **Effective capacitance-corrected** source view | Provenance-redacted JSON; existing parameter annotations and provisional handles, not new canonical registration |
| [capacitance-correction.json](capacitance-correction.json) | Source-view correction rationale | Provenance-redacted JSON; before/after technical clause, conditions and unresolved independent disposition retained |

The schematic's `source-proposals.json` reference means the **effective**
public file above, never the old superseded driver source view. Capacitance
MAX, RC/settling/loaded-edge bounds and actual charging load remain UNKNOWN.
The historical `exact_change.before` clause is explicitly superseded, not a
current maximum guarantee.

Full original paths, SHA-256 values, export classifications, removed JSON
pointers and public hashes are in [selection](../source-selection.json) and
[manifest](../manifest.json). Original nested hash/path fields remain **archive
metadata**: the public replacement bindings are the manifest and
`sequencer.BINDINGS`, not those historical fields. JSON whitespace changed on
reserialization; apart from listed provenance operations every decoded value
is preserved. The one shortened `normal_first` string removes delegation/click
provenance only and retains the analysis boundary.

References such as `R.*`, `S.*`, `AUTH`, evidence IDs, original relative archive
paths and source-witness/checker filenames are **unresolved upstream archive
references**, not local links or runtime resources. Upstream ledgers, SDK,
graphs, manufacturer originals, old checkers and review records are omitted.
Thus this bundle reproduces host behavior and its *bounded supplied context*,
not the full source-acquisition, electrical-proof or independent-review chain.
Official manufacturer URLs retained as metadata are not fetched by the code.

The old per-file status remains its own source epoch. The package's frozen
review/publication status and all unchanged physical holds are described in
the [package README](../README.md); later independent conclusions cannot be
inferred from any earlier source record or passing author check.
