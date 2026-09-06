"""Keep active instructions consistent; historical evolution records are not policy."""
import pathlib
import re
import unittest

import agent_workflow

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


if __name__ == "__main__":
    unittest.main()
