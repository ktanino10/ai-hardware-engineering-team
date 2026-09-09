# Portable host-only output sequencer

**WIP — HOST-ONLY — NOT DEPLOYABLE FIRMWARE.**
This is a standalone, standard-library Python derivative of a stopped host
ordering model and its corrected CLR/CLK/OE sequencer. It issues no device I/O.
Useful synthetic service is exercised before and after an event; this is not
an always-OFF demonstration. Every actual-operation and actual-bus permission
remains **false**.

## Run without the original repository

Use Python **3.10 or later**. Copy this entire directory, including
`source-context/` and `_bootstrap.py`, into any ordinary working directory.
No installation, Git history, SDK, environment variables, network, original
worktree, datasheets or additional dependencies are needed.
Author validation used Python **3.14.3**; other interpreters were not executed.

From the copied directory:

```sh
python3 -B cli.py normal
python3 -B cli.py all
python3 -B -m unittest discover -s . -p 'test_*.py' -v
```

From a different current directory, pass the CLI's quoted path:

```sh
python3 -B "export copy with spaces/cli.py" stale-high-return
python3 -B -m unittest discover -s "export copy with spaces" -p 'test_*.py' -v
```

`-B` suppresses interpreter bytecode caches. The runtime itself only reads
eleven package files plus Python's standard library; it writes no files.
Tests create and remove small `.portability-work-*` directories **inside**
the copied package, so testing requires write access there. No system
temporary directory is used. Existing scratch directories are not overwritten.
Relocation tests copy only the public allowlist, run from a foreign working
directory, fence Git discovery at the scratch root, and audit runtime reads to
reject access outside the copied runtime files and standard library. This
checks independence from the repository; it is not a security sandbox.

CLI exit **0** means the selected scenario assertions held, not permission or
an independent verdict. A missing, modified or symlinked bound dependency
fails with exit **2**, a short package-relative error and no success JSON.
Do not edit hashes to conceal a mismatch. Any intentional source revision
requires a new manifest and a new review.

Each invocation generates **this public derivative's own current execution**,
marked `PUBLIC_DERIVATIVE_CURRENT_EXECUTION`. There are no rebound historical
results or stored success traces. The ten choices are:

| Choice | Demonstration |
|---|---|
| `normal` | Fresh hold/rejoin, useful transaction, planned event, genuinely fresh useful service |
| `held-request` | Retained/unqualified manual contact is not a new request |
| `stale-high-return` | An OE-return receiving history contradicting LOW commands is refused, not physically contained |
| `cancel`, `evidence-loss` | Stale tickets/proof refused; later newly qualified synthetic recovery remains possible |
| `unknown-C`, `unknown-local` | Missing independent/local power qualification denies progression |
| `unknown-output`, `unknown-ACK` | UNKNOWN receiving states and software ACKs cannot advance receiving fences |
| `bad-order` | Retained HIGH at OE return gives qualified symbolic HIGH/LOW or UNKNOWN according to the assumed order |

## What is included, excluded and bound

| Material | Treatment and dependency |
|---|---|
| `model.py` | **Exact bytes**, SHA-256 `ce496b2806b21966d68cec789ae85ec5dbdd4cf1eb7762a8d0b29fac172af447`; no request/epoch/proof/recovery edits |
| `sequencer.py` | Only loader/path/hash adapter changed. Everything from `base = _load_existing_model()` onward is byte-identical to corrected source `f15c6017…`, including FR-SEQ-01 correction |
| `scenarios.py` | Only the import becomes namespace-relative; all ten definitions and fixture data unchanged |
| `cli.py`, `_bootstrap.py` | Checked local loading in a fresh module namespace, explicit derivative label, bounded failure diagnostics |
| `test_sequencer.py` | All 29 existing tests retained. Imports and the exact model-file-location assertion are adapted, not weakened |
| Six project-authored [context files](source-context/README.md) | One exact diagram copy and five provenance-redacted JSON derivatives. Together with the model, **all seven** original dependency roles remain hash-checked using explicit public hashes |
| [Manifest](manifest.json) and [selection record](source-selection.json) | Exact original/public path and hash mapping; classifications and deleted JSON pointers; no claim of independent source acceptance |
| Manufacturer originals, attachments, private coordination, source receipts, old raw outcomes, environment/credentials, caches, SDK/native/embedded artifacts | **Not exported or required at runtime** |
| Upstream graph, SDK paths, historical reviews and Git commits mentioned inside context | Archive identifiers, not necessarily publicly reachable. Full upstream engineering/history reproduction is **not** supplied |
| Selected canonical source dependencies | Supplied by the [source supplement](../rev5-public-sources-2026-09-10/README.md). Its fixed row operations must be imported and actually enumerated by the public-tree checker; the [integration entry](../rev5-publication-2026-09-10/README.md) separates this from runtime portability |

The technical firmware-authority map is project-authored dependency context,
not an operator authorization record. Parameter annotations preserve existing
source conditions, categories, UNKNOWNs and provisional IDs; they are not
manufacturer document extracts, new datasheet interpretations or registrations.

The unchanged model's `SOURCE`, `CONFIG`, `A1_SHA`, `B_SHA` and `REVISION`
remain **historical model identity tokens**. They do not claim that redacted
public context is byte-identical to those originals. Current public binding
hashes are explicit in `sequencer.BINDINGS` and the manifest. Context hashes
check saved bytes, not their engineering truth. Original statuses in context
remain source-epoch statuses; use the package status below for the frozen
export baseline. Source-supplement manifests describe their own earlier frozen
preparation, including its then-unchanged 18-file package; this package's
current manifest and the global export manifest identify the later
administrative documentation update. No Python or bound-context byte changed.

## Frozen review status at integrated export

Stopped results were integrated after the initial `2fd6730` preparation.
The [source-assessment summary](../rev5-publication-2026-09-10/source-assessments.json)
records exact original/reviewed hashes and distinct verdict scopes:

- Old model **F1** remains independently **RESOLVED** in the limited `42cdc`
  review. It is not the sequencer finding.
- Original sequencer review `ef6ce6c3…` remains historical **FAIL**,
  **FR-SEQ-01 HIGH / OPEN**. The independent correction review `42265d02…`
  is **PASS**, resolving that HIGH finding on the exact original `5ba5889d…`
  code with SHA-256 `f15c6017…`. This is not a transfer of that verdict to
  changed public adapters.
- Built-in read-only Code Review reported **“No significant issues found in
  the reviewed changes.”** for the public adapter delta through `2fd6730`.
  It checked copies, bindings and transformations and executed CLI cases;
  it did not repeat the domain review or independently execute the writing
  unittest suite/outside-Git relocation. Author and Lead results remain
  separately attributed.
- The option-comparison `fa0abfb0…` review is a **limited semantic PASS**,
  **NO_SELECTION**, not component/electrical acceptance.
- G031's original source review remains **CONDITIONAL**. The changed-source
  disposition `88b3a544…` is limited **PASS**: one corrected effective-view
  condition and two acceptable legacy source clauses. Those two canonical
  clauses and document-only metadata were serially applied/read back at
  `256c931e…`. This is source-only closure, not board, firmware, candidate
  selection or physical acceptance. The full numeric proposal packet and
  uploaded PDF are not exported.
- This is a frozen public-safe export, not a claim that push or PR already
  occurred. Actual public import/remote results belong to the designated
  publisher's separate receipt. See [publication-status.json](publication-status.json).

## Important limits

Logical indexes/steps are **not ns or ms**. A commanded LOW is not proof of
pin LOW; HIGH_Z is not LOW; symbolic FF Q is not proof of physical
disconnection. Already-issued HIGH effects are UNKNOWN and not recalled.
ACKs, Python object identity and the synthetic journal are neither physical
evidence nor a security/authentication boundary. The loader prevents ordinary
cached-module substitution by loading checked bytes afresh; it does not defend
against an attacker controlling Python, the package, or standard-library imports.

No numerical B/X budget, capacitor maximum, settling interval or physical
margin is added. No independent C implementation, actual enforcer, part,
topology, risk, driver pin, power source or source interpretation is changed.
**NO-GO / P1 conditional / 3C8H / REQ409 and every physical/human gate remain.**
No first flash, energization, probe access, motion, manufacturing or physical
cut approval follows. SDK/toolchain/device work is **out of scope**, not
claimed unavailable. This package is host logic, not rigid-body simulation,
deployable firmware, electrical qualification or an independent review.
