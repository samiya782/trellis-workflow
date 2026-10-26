"""Regressions for the two Grok-validation script fixes.

1. Grok Build tool shells export GROK_SESSION_ID; `task.py start` must write a
   `grok_<session>` pointer instead of running degraded.
2. `task.py archive` must repoint implement/check jsonl entries that named files
   under the moved task, so archived children still pass `task.py validate`.
"""

import json
import os
import sys
import unittest

import test_integration


class GrokFixTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_integration.InstalledRuntimeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root

    def grok_env(self, session):
        for key in list(self.fixture.env):
            if key.startswith("GROK_") or key == "TRELLIS_CONTEXT_ID":
                del self.fixture.env[key]
        self.fixture.env["GROK_SESSION_ID"] = session
        self.fixture.env["GROK_AGENT"] = "1"

    def test_grok_session_id_writes_and_clears_grok_pointer(self):
        task = self.fixture.create_task("grok-pointer")
        self.grok_env("sess-1234")
        self.fixture.task("start", str(task), "--allow-empty-context")
        pointer = self.root / ".trellis/.runtime/sessions/grok_sess-1234.json"
        self.assertTrue(pointer.is_file(), "start must write a grok_<session> pointer")
        self.assertEqual(json.loads(pointer.read_text())["current_task"],
                         str(task.relative_to(self.root)))
        current = self.fixture.task("current", "--source").stdout
        self.assertIn(str(task.relative_to(self.root)), current)
        self.assertIn("session:grok_sess-1234", current)
        # A different Grok session must not see this pointer.
        self.fixture.env["GROK_SESSION_ID"] = "other-session"
        self.assertIn("(none)", self.fixture.task("current", "--source", success=False).stdout)
        self.fixture.env["GROK_SESSION_ID"] = "sess-1234"
        self.fixture.archive(task, "--skip-branch-validation")
        self.assertFalse(pointer.exists(), "archive must clear the session pointer")
        self.assertIn("(none)", self.fixture.task("current", "--source", success=False).stdout)

    def add_context(self, task, target, kind="implement"):
        self.fixture.task("add-context", str(task), kind,
                          str(target.relative_to(self.root)), "fixture context")

    def commits(self):
        return self.fixture.run_command("git", "rev-list", "--count", "HEAD").stdout.strip()

    def test_child_then_parent_archive_keeps_archived_child_valid(self):
        parent = self.fixture.create_task("rank-parent")
        child = self.fixture.create_task("rank-child", parent=parent)
        for kind in ("implement", "check"):
            self.add_context(child, parent / "prd.md", kind)
            self.add_context(child, child / "prd.md", kind)
        before = self.commits()
        archived_child = self.fixture.archive(child)
        archived_parent = self.fixture.archive(parent)
        self.assertEqual(self.commits(), before, "--no-commit must not commit")
        text = (archived_child / "implement.jsonl").read_text()
        self.assertIn(str(archived_parent.relative_to(self.root)) + "/prd.md", text)
        self.assertIn(str(archived_child.relative_to(self.root)) + "/prd.md", text)
        self.fixture.task("validate", str(archived_child.relative_to(self.root)))

    def test_parent_archived_first_repoints_active_child(self):
        parent = self.fixture.create_task("solo-parent")
        child = self.fixture.create_task("solo-child", parent=parent)
        self.add_context(child, parent / "prd.md")
        self.add_context(child, parent / "prd.md", "check")
        archived_parent = self.fixture.archive(parent)
        text = (child / "implement.jsonl").read_text()
        self.assertIn(str(archived_parent.relative_to(self.root)) + "/prd.md", text)
        self.fixture.task("validate", str(child.relative_to(self.root)))

    def test_lone_task_archive_repoints_own_entries_and_spares_siblings(self):
        task = self.fixture.create_task("lone")
        sibling = self.fixture.create_task("lone-extra")
        for kind in ("implement", "check"):
            self.add_context(task, task / "prd.md", kind)
            self.add_context(sibling, sibling / "prd.md", kind)
        archived = self.fixture.archive(task)
        self.fixture.task("validate", str(archived.relative_to(self.root)))
        self.assertIn(str(sibling.relative_to(self.root)) + "/prd.md",
                      (sibling / "implement.jsonl").read_text())
        self.fixture.task("validate", str(sibling.relative_to(self.root)))

    def test_committed_archive_stages_repointed_child(self):
        parent = self.fixture.create_task("commit-parent")
        child = self.fixture.create_task("commit-child", parent=parent)
        self.add_context(child, parent / "prd.md")
        self.add_context(child, parent / "prd.md", "check")
        self.fixture.run_command("git", "add", ".trellis/tasks")
        self.fixture.run_command("git", "commit", "--quiet", "-m", "tasks")
        self.fixture.task("archive", str(parent))
        dirty = self.fixture.run_command(
            "git", "status", "--porcelain", "--", str(child.relative_to(self.root))
        ).stdout
        self.assertEqual(dirty, "", "repointed child jsonl must be in the archive commit")
        self.fixture.task("validate", str(child.relative_to(self.root)))


if __name__ == "__main__":
    unittest.main()
