#!/usr/bin/env python3
"""CI lint for .github/agents/*.agent.md and .github/skills/*/SKILL.md frontmatter.

Enforces the GitHub Copilot custom-agent and agent-skill spec's required
frontmatter fields, so a future contributor can't silently regress into the
same mismatch this repo's PR #2 and PR #3 had to fix by hand:
  - docs.github.com/en/copilot/reference/custom-agents-configuration
    (.agent.md requires a non-empty `description`)
  - docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/
    customize-cloud-agent/add-skills
    (SKILL.md requires non-empty `name` + `description`; `name` must be
    lowercase/hyphenated and match its directory name)

This is a repo-hygiene guard, not a Mechanical-domain-specific check --
it covers every current and future agent/skill file equally, regardless of
which discipline added it.
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _read_frontmatter(path: pathlib.Path) -> dict | None:
    """Return the parsed YAML frontmatter dict, or None if none is present."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML frontmatter: {exc}") from exc
    return data if isinstance(data, dict) else None


def check_agents() -> list[str]:
    violations: list[str] = []
    if not AGENTS_DIR.exists():
        return violations
    for path in sorted(AGENTS_DIR.glob("*.agent.md")):
        try:
            data = _read_frontmatter(path)
        except ValueError as exc:
            violations.append(f"{path.relative_to(REPO_ROOT)}: {exc}")
            continue
        if data is None:
            violations.append(f"{path.relative_to(REPO_ROOT)}: missing YAML frontmatter")
            continue
        description = data.get("description")
        if not description or not str(description).strip():
            violations.append(
                f"{path.relative_to(REPO_ROOT)}: missing/empty required 'description' "
                "field (docs.github.com/en/copilot/reference/custom-agents-configuration)"
            )
    return violations


def check_skills() -> list[str]:
    violations: list[str] = []
    if not SKILLS_DIR.exists():
        return violations
    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        path = skill_dir / "SKILL.md"
        if not path.exists():
            violations.append(f"{skill_dir.relative_to(REPO_ROOT)}/: missing SKILL.md")
            continue
        try:
            data = _read_frontmatter(path)
        except ValueError as exc:
            violations.append(f"{path.relative_to(REPO_ROOT)}: {exc}")
            continue
        if data is None:
            violations.append(f"{path.relative_to(REPO_ROOT)}: missing YAML frontmatter")
            continue

        name = data.get("name")
        if not name or not str(name).strip():
            violations.append(f"{path.relative_to(REPO_ROOT)}: missing/empty required 'name' field")
        else:
            name = str(name).strip()
            if name != skill_dir.name:
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}: 'name: {name}' does not match "
                    f"its directory name '{skill_dir.name}'"
                )
            if not NAME_PATTERN.match(name):
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}: 'name: {name}' must be lowercase "
                    "with hyphens for spaces"
                )

        description = data.get("description")
        if not description or not str(description).strip():
            violations.append(f"{path.relative_to(REPO_ROOT)}: missing/empty required 'description' field")
    return violations


def main() -> int:
    violations = check_agents() + check_skills()

    if violations:
        print("Agent/skill frontmatter lint FAILED:")
        for v in violations:
            print(f"  - {v}")
        print(
            "\nSee docs.github.com/en/copilot/reference/custom-agents-configuration "
            "and docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/"
            "customize-cloud-agent/add-skills for the required frontmatter, and this "
            "repo's PR #2/#3 history for why this check exists."
        )
        return 1

    agent_count = len(list(AGENTS_DIR.glob("*.agent.md"))) if AGENTS_DIR.exists() else 0
    skill_count = len([p for p in SKILLS_DIR.iterdir() if p.is_dir()]) if SKILLS_DIR.exists() else 0
    print(
        f"OK: {agent_count} agent profile(s) and {skill_count} skill(s) have valid "
        "required frontmatter."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
