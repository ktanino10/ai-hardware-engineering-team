# Mechanical Design Files

This directory holds the Mechanical Lead's design artifacts for the
enclosure/mechanical structure (`docs/architecture-evolution.md` §10/§27).

## What goes here

- An OpenSCAD-syntax `.scad` text file — the primary parametric artifact,
  every dimension a named variable.
- A structured dimensional-spec Markdown table (`Parameter | Value | Unit |
  Source/Rationale`) — the always-readable fallback for anyone without
  OpenSCAD, and the artifact of record if no `.scad` file is produced for a
  given revision.
- A design rationale log (can be a section of the dimensional-spec file)
  recording the "why" for every dimension, per
  `.github/skills/enclosure-design/SKILL.md`.
- Once a revision reaches Design Complete, downstream documentation
  artifacts may also live here: `assembly-instructions.md` (a build
  procedure), `stl/` (print-ready exports), and `drawings/` (2D
  orthographic views + an exploded assembly view — see `drawings/README.md`
  for the tooling/regeneration convention). None of these edit the source
  `.scad` geometry; they are read-only-derived documentation.

## Conventions

- No CAD/3D modeling MCP tool is connected in this environment (verified —
  `docs/architecture.md` §5.3/§13): a live connection check against the only
  3D-capable tool surface present (`blender-get_addon_status`) returned
  "Could not connect to Blender," and no local `openscad`/`freecad` binary or
  `cadquery`/`solid`/`build123d` Python library is installed. Do not claim a
  rendered preview, an STL export, or a fit-check exists unless a
  verified-connected tool actually produced it — see
  `.github/agents/mechanical-lead.agent.md`.
  - **Addendum, later session (documentation-generation pass, `drawings/`
    directory)**: a fresh `blender-get_addon_status`/`blender-get_scene_info`
    check found Blender (v5.1.1) genuinely connected via the `blender-*` MCP
    tools that session, and it was used (read-only against this directory's
    `.scad` file) to build the exploded assembly view in `drawings/exploded/`.
    This does **not** retroactively change the historical record above (that
    was an accurate account of a prior session's own tooling state) or
    establish a standing guarantee — the same "no CAD/3D tool connected until
    verified this session" default still applies to any future session; check
    again rather than assuming Blender (or OpenSCAD, or any other tool named
    in this file) is still connected.
- Every dimension must trace to `hardware/mechanical-interface.md`, an
  Evidence ID (`datasheets/evidence-log.md`), or an explicit
  `ASSUMPTION`/`ESTIMATE` — never a silent guess
  (`.github/instructions/mechanical-design.instructions.md`).
- Do not hand-edit the design to "fix" a Mechanical Reviewer finding without
  logging the change in `validation/change-log.md` (ECO), mirroring the same
  rule already in place for `hardware/schematic/` and `hardware/pcb/`.
