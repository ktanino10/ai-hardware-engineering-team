# Rev5 public host smoke CI

The dedicated [workflow](../.github/workflows/rev5-public-host-smoke.yml)
exercises the unchanged [public host package](rev5-public-2026-09-10/README.md)
on Ubuntu with Python **3.10** and **3.14**, using only the standard library.
It runs on ordinary pull requests changing the package, workflow or this
document, and declares `workflow_dispatch` for manual runs once the workflow
is available on the default branch. Each matrix job has a ten-minute timeout,
read-only repository permissions and no persisted checkout credentials.

## Coverage and local commands

From the repository root:

```sh
python3 -B -m unittest discover -s docs/rev5-public-2026-09-10 -p 'test_*.py' -v
python3 -B docs/rev5-public-2026-09-10/cli.py all
```

Each matrix job also copies the **entire** package, including `_bootstrap.py`
and `source-context/`, into a temporary path containing spaces outside the
checkout. It repeats both commands against that copy from a separate working
directory. The existing portability tests exercise foreign imports, binding
mismatches, missing files and runtime side effects; no replacement tests or
weakened assertions are introduced. The temporary directory is removed on
normal completion or an exception. No dependency installation is needed.

The matrix declares intended CI coverage, not proof that either interpreter
has already passed. Consult the actual workflow run for each interpreter's
result; local execution only establishes coverage for the interpreter used.

## Scope and unchanged holds

Success means host-software tests and synthetic scenario assertions passed.
It is not hardware acceptance, independent engineering review, deployable
firmware, source adoption, or permission for any physical operation.
**NO-GO / P1 conditional / 3C8H / REQ409 and all physical/adoption holds remain.**
Existing workflows, required-check names and Design Complete gates are
unchanged. No model, scenario, test, binding hash, manifest, engineering
threshold, native CAD, SDK/device, flash or manufacturing change is included.

This is a separate CI addition dependent on the public-package work in
[PR #73](https://github.com/ktanino10/ai-hardware-engineering-team/pull/73).
