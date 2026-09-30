"""Behavioral tests for reversible, project-scoped Matt invocation policy."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/configure_codex_matt.py"
SPEC = importlib.util.spec_from_file_location("configure_codex_matt", SCRIPT)
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


class CodexMattConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.original = "interface:\n  display_name: Test\npolicy:\n  allow_implicit_invocation: false # upstream\n"
        names = (*adapter.POLICIES, *adapter.DEPENDENCIES)
        for name in names:
            for platform in (".agents", ".claude"):
                skill = self.root / platform / "skills" / name
                (skill / "agents").mkdir(parents=True)
                (skill / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Test\n---\nOriginal instructions.\n")
                (skill / "agents/openai.yaml").write_text(self.original)
        (self.root / "skills-lock.json").write_text(json.dumps({
            "version": 1, "skills": {name: {"source": "mattpocock/skills"} for name in names},
        }))

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def test_apply_check_restore_preserve_originals_and_are_idempotent(self):
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "adaptation needed"):
            adapter.configure(self.root, check=True)
        self.assertEqual(before, self.snapshot())
        adapter.configure(self.root)
        applied = self.snapshot()
        adapter.configure(self.root)
        adapter.configure(self.root, check=True)
        self.assertEqual(applied, self.snapshot())
        for path, content in before.items():
            if path.startswith(".claude/") or path.endswith("SKILL.md"):
                self.assertEqual(content, applied[path])
        for name in adapter.DEPENDENCIES:
            relative = str(adapter.policy_path(name))
            self.assertEqual(before[relative], applied[relative])
        for name, enabled in adapter.POLICIES.items():
            self.assertIn(f"allow_implicit_invocation: {str(enabled).lower()} # upstream",
                          (self.root / adapter.policy_path(name)).read_text())
        adapter.configure(self.root, restore=True)
        adapter.configure(self.root, restore=True)
        self.assertEqual(before, self.snapshot())

    def test_missing_skill_refuses_without_partial_writes(self):
        (self.root / ".agents/skills/research/SKILL.md").unlink()
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "Missing skill"):
            adapter.configure(self.root)
        self.assertEqual(before, self.snapshot())

    def test_wrong_source_name_collision_refuses(self):
        lock = self.root / "skills-lock.json"
        data = json.loads(lock.read_text())
        data["skills"]["implement"]["source"] = "someone/other-skills"
        lock.write_text(json.dumps(data))
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "name collision"):
            adapter.configure(self.root)
        self.assertEqual(before, self.snapshot())

    def test_absent_metadata_and_policy_are_restored_exactly(self):
        missing = self.root / adapter.policy_path("grill-with-docs")
        missing.unlink()
        default = self.root / adapter.policy_path("implement")
        default.write_bytes(b"interface:\r\n  display_name: Test\r\n")
        before = self.snapshot()
        adapter.configure(self.root)
        adapter.configure(self.root, check=True)
        self.assertIn("allow_implicit_invocation: false", missing.read_text())
        self.assertIn(b"\r\npolicy:\r\n", default.read_bytes())
        adapter.configure(self.root, restore=True)
        self.assertEqual(before, self.snapshot())

    def test_symlink_into_claude_is_refused(self):
        target = self.root / adapter.policy_path("implement")
        target.unlink()
        target.symlink_to(self.root / ".claude/skills/implement/agents/openai.yaml")
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "Symlinked"):
            adapter.configure(self.root)
        self.assertEqual(before, self.snapshot())

    def test_skill_body_symlink_is_refused_before_metadata_changes(self):
        target = self.root / ".agents/skills/implement/SKILL.md"
        target.unlink()
        target.symlink_to(self.root / ".claude/skills/implement/SKILL.md")
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "Symlinked"):
            adapter.configure(self.root)
        self.assertEqual(before, self.snapshot())

    def test_post_apply_edit_is_preserved_on_restore_failure(self):
        adapter.configure(self.root)
        target = self.root / adapter.policy_path("retro")
        target.write_text(target.read_text() + "# later user change\n")
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "changed after configuration"):
            adapter.configure(self.root, restore=True)
        self.assertEqual(before, self.snapshot())

    def test_policy_with_other_members_is_preserved(self):
        original = "policy:\n  products: [CODEX]\ninterface:\n  display_name: Test\n"
        changed = adapter.with_policy(original, False)
        self.assertEqual(changed, "policy:\n  allow_implicit_invocation: false\n  products: [CODEX]\ninterface:\n  display_name: Test\n")

    def test_unsupported_or_duplicate_policy_is_refused(self):
        for original in (
            "policy: {allow_implicit_invocation: false}\n",
            "policy:\npolicy:\n",
            "policy:\n  allow_implicit_invocation: false\n  allow_implicit_invocation: true\n",
            "policy:\n  allow_implicit_invocation: maybe\n",
        ):
            with self.subTest(original=original):
                with self.assertRaises(adapter.ConfigurationError):
                    adapter.with_policy(original, True)


if __name__ == "__main__":
    unittest.main()
