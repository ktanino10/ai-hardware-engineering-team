"""Keep active instructions consistent; historical evolution records are not policy."""
import pathlib
import re
import unittest

import agent_workflow
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


class WorkflowInstructionTests(unittest.TestCase):
    def test_firmware_handoffs_require_the_existing_independent_reviewer(self):
        paths = (
            ".github/agents/firmware-engineer.agent.md",
            ".github/instructions/firmware.instructions.md",
            ".github/skills/firmware-bringup/SKILL.md",
            "docs/workflow.md",
        )
        stale = re.compile(
            r"(?:no independent firmware reviewer (?:agent )?exists yet"
            r"|until a firmware reviewer role exists|stands in for independent review)",
            re.IGNORECASE,
        )
        for name in paths:
            with self.subTest(path=name):
                text = " ".join((ROOT / name).read_text(encoding="utf-8").split())
                self.assertIsNone(stale.search(text))
                self.assertRegex(text, r"(?i)firmware[ -]reviewer")

    def test_independent_role_and_scoped_record_still_exist(self):
        text = (ROOT / ".github/agents/firmware-reviewer.agent.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("firmware-review", text)
        self.assertIn("firmware/<board>/<board>-firmware-review.md", text)
        self.assertIn("first", text.lower())

    def test_dispatch_entrypoints_use_the_same_execution_contract(self):
        paths = (
            "AGENTS.md",
            "README.md",
            ".github/copilot-instructions.md",
            ".github/agents/hardware-lead.agent.md",
            ".github/prompts/independent-review.prompt.md",
            "docs/architecture.md",
            "docs/workflow.md",
            "docs/commands/make-circuit.md",
        )
        for name in paths:
            with self.subTest(path=name):
                self.assertIn("work-execution.md", (ROOT / name).read_text(encoding="utf-8"))

    def test_documented_publisher_scopes_match_the_guard(self):
        text = (ROOT / "docs/work-execution.md").read_text(encoding="utf-8")
        for name in agent_workflow.SHARED_LEDGERS:
            with self.subTest(path=name):
                self.assertIn(f"`{name}`", text)

    def test_common_role_index_preserves_every_existing_specialist(self):
        text = (ROOT / ".github/copilot-instructions.md").read_text(encoding="utf-8")
        for path in (ROOT / ".github/agents").glob("*.agent.md"):
            role = path.name.removesuffix(".agent.md")
            with self.subTest(role=role):
                self.assertIn(f"| `{role}` |", text)

    def test_onboarding_links_resolve_without_duplicate_policy_files(self):
        paths = ("AGENTS.md", "README.md", ".github/copilot-instructions.md")
        for name in paths:
            path = ROOT / name
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#")):
                    continue
                with self.subTest(page=name, target=target):
                    self.assertTrue((path.parent / target.split("#", 1)[0]).exists())
        policy = (ROOT / ".github/copilot-instructions.md").read_text(encoding="utf-8")
        self.assertIn("## Maintenance matrix", policy)

    def test_documented_workflow_commands_match_the_existing_ci(self):
        workflow = yaml.safe_load(
            (ROOT / ".github/workflows/agent-frontmatter-lint.yml").read_text(encoding="utf-8")
        )
        job = workflow["jobs"]["frontmatter-lint"]
        guide = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        runs = {step["run"] for step in job["steps"] if "run" in step}
        for command in (
            "python3 tools/check_agent_frontmatter.py",
            "python3 -m unittest discover -s tools/tests -p 'test_*workflow*.py'",
        ):
            self.assertIn(command, runs)
            self.assertIn(command, guide)
        self.assertEqual(job["name"], "Check agent/skill frontmatter")
        self.assertEqual(workflow["permissions"], {"contents": "read"})


if __name__ == "__main__":
    unittest.main()
