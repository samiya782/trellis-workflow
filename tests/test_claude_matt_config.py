"""Behavioral tests for reversible, project-scoped Claude Code Matt invocation policy."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adapter = load("configure_claude_matt")
codex = load("configure_codex_matt")
BODY = "\nOriginal instructions.\n\nUse /tdd where possible.\n"


class ClaudeMattConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        names = {*adapter.POLICIES, *adapter.DEPENDENCIES, *codex.POLICIES, *codex.DEPENDENCIES}
        for name in names:
            # Upstream marks every stage in POLICIES user-only; dependencies are invocable.
            flag = "disable-model-invocation: true\n" if name in adapter.POLICIES else ""
            for platform in (".agents", ".claude"):
                skill = self.root / platform / "skills" / name
                (skill / "agents").mkdir(parents=True)
                (skill / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Test\n{flag}---{BODY}")
                (skill / "agents/openai.yaml").write_text("policy:\n  allow_implicit_invocation: false\n")
        (self.root / "skills-lock.json").write_text(json.dumps({
            "version": 1, "skills": {name: {"source": "mattpocock/skills"} for name in names},
        }))

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def skill(self, name):
        return (self.root / adapter.skill_path(name)).read_text()

    def test_apply_check_restore_change_only_the_downstream_field(self):
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "adaptation needed"):
            adapter.configure(self.root, check=True)
        self.assertEqual(before, self.snapshot())
        adapter.configure(self.root)
        applied = self.snapshot()
        adapter.configure(self.root)
        adapter.configure(self.root, check=True)
        self.assertEqual(applied, self.snapshot())
        changed = {path for path in before if before[path] != applied[path]}
        self.assertEqual(changed, {str(adapter.skill_path(name))
                                   for name, disabled in adapter.POLICIES.items() if not disabled})
        for name in ("to-spec", "to-tickets", "implement", "retro"):
            self.assertIn("disable-model-invocation: false\n", self.skill(name))
            self.assertTrue(self.skill(name).endswith(BODY))
        for name in ("grill-with-docs", "wayfinder"):
            self.assertIn("disable-model-invocation: true\n", self.skill(name))
        adapter.configure(self.root, restore=True)
        adapter.configure(self.root, restore=True)
        self.assertEqual(before, self.snapshot())

    def test_claude_and_codex_adapters_are_independent(self):
        before = self.snapshot()
        adapter.configure(self.root)
        codex.configure(self.root)
        adapter.configure(self.root, check=True)
        codex.configure(self.root, check=True)
        adapter.configure(self.root, restore=True)
        codex.configure(self.root, check=True)
        for path, content in before.items():
            if path.startswith(".claude/"):
                self.assertEqual(content, (self.root / path).read_bytes(), path)
        codex.configure(self.root, restore=True)
        self.assertEqual(before, self.snapshot())

    def test_missing_entry_field_is_added_user_only_and_restored(self):
        entry = self.root / adapter.skill_path("wayfinder")
        entry.write_bytes(b"---\r\nname: wayfinder\r\ndescription: Test\r\n---\r\nBody\r\n")
        before = self.snapshot()
        adapter.configure(self.root)
        self.assertEqual(entry.read_bytes(),
                         b"---\r\nname: wayfinder\r\ndescription: Test\r\ndisable-model-invocation: true\r\n---\r\nBody\r\n")
        adapter.configure(self.root, restore=True)
        self.assertEqual(before, self.snapshot())

    def test_user_only_dependency_is_refused(self):
        dependency = self.root / adapter.skill_path("grilling")
        dependency.write_text("---\nname: grilling\ndisable-model-invocation: true\n---\nBody\n")
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "user-only"):
            adapter.configure(self.root)
        self.assertEqual(before, self.snapshot())

    def test_missing_or_colliding_skill_refuses_without_partial_writes(self):
        (self.root / adapter.skill_path("research")).unlink()
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "Missing skill"):
            adapter.configure(self.root)
        self.assertEqual(before, self.snapshot())
        (self.root / adapter.skill_path("research")).write_text("---\nname: other\n---\nBody\n")
        with self.assertRaisesRegex(adapter.ConfigurationError, "name collision"):
            adapter.configure(self.root)

    def test_symlinked_skill_is_refused(self):
        target = self.root / adapter.skill_path("implement")
        target.unlink()
        target.symlink_to(self.root / ".agents/skills/implement/SKILL.md")
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "Symlinked"):
            adapter.configure(self.root)
        self.assertEqual(before, self.snapshot())

    def test_post_apply_edit_is_preserved_on_restore_failure(self):
        adapter.configure(self.root)
        target = self.root / adapter.skill_path("retro")
        target.write_text(target.read_text() + "later user change\n")
        before = self.snapshot()
        with self.assertRaisesRegex(adapter.ConfigurationError, "changed after configuration"):
            adapter.configure(self.root, restore=True)
        self.assertEqual(before, self.snapshot())

    def test_unsupported_frontmatter_is_refused(self):
        for original in (
            "name: x\n---\n",
            "---\nname: x\n",
            "---\ndisable-model-invocation: true\ndisable-model-invocation: true\n---\n",
            "---\ndisable-model-invocation: \"true\"\n---\n",
        ):
            with self.subTest(original=original):
                with self.assertRaises(adapter.ConfigurationError):
                    adapter.with_policy(original, False)


if __name__ == "__main__":
    unittest.main()
