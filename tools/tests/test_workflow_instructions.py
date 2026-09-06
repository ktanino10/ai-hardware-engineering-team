"""Keep active instructions consistent; historical evolution records are not policy."""
import pathlib
import re
import unittest


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


if __name__ == "__main__":
    unittest.main()
