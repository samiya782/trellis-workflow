"""Closeout instruction regressions and real CLI retry boundaries.

Hook subprocesses and lifecycle fixtures are not autonomous session evidence.
"""

import json
from pathlib import Path
import re
import shlex
import shutil
import sys
import unittest

import test_integration


REPOSITORY = Path(__file__).resolve().parents[1]


class CloseoutTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_integration.InstalledRuntimeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        for platform in ("codex", "claude"):
            shutil.copy2(
                REPOSITORY / f".{platform}/hooks/session-start.py",
                self.root / f".{platform}/hooks/session-start.py",
            )

    def status(self, platform):
        result = self.fixture.run_command(
            sys.executable, f".{platform}/hooks/session-start.py",
            input_text=json.dumps({"cwd": str(self.root), "source": "startup"}),
        )
        body = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        return body.split("<task-status>\n", 1)[1].split("\n</task-status>", 1)[0]

    def test_start_uses_recorded_authorization_with_optional_artifacts(self):
        task = self.fixture.create_task("authorized-plan")
        self.fixture.task("start", str(task), "--allow-empty-context")
        data = self.fixture.record(task)
        data["status"] = "planning"
        (task / "task.json").write_text(json.dumps(data))
        for optional in (False, True):
            if optional:
                (task / "design.md").write_text("# Design\n")
                (task / "implement.md").write_text("Authorization: implement; no commit.\n")
            for platform in ("codex", "claude"):
                with self.subTest(platform=platform, optional=optional):
                    status = self.status(platform)
                    self.assertIn("--step 1.4", status)
                    self.assertIn("authorization", status)
                    self.assertIn("planning-only", status)
                    self.assertNotIn("review before", status)
                    self.assertNotIn("user confirms start", status)
                    self.assertNotIn("complex task must", status)

    def test_completed_and_no_task_status_follow_workflow_scope(self):
        for platform in ("codex", "claude"):
            with self.subTest(platform=platform, state="no_task"):
                status = self.status(platform)
                self.assertIn("--mode phase", status)
                self.assertNotIn("ask for", status.lower())
        task = self.fixture.create_task("completed")
        self.fixture.task("start", str(task), "--allow-empty-context")
        data = self.fixture.record(task)
        data["status"] = "completed"
        (task / "task.json").write_text(json.dumps(data))
        for platform in ("codex", "claude"):
            with self.subTest(platform=platform, state="completed"):
                status = self.status(platform)
                self.assertIn("--step 3.5", status)
                self.assertIn("authorization", status)
                self.assertNotIn("task.py archive", status)
                self.assertNotIn("return to Phase 3.4", status)

    def test_finish_entrypoints_disable_auto_commit_in_every_lifecycle_example(self):
        skill = (REPOSITORY / ".agents/skills/trellis-finish-work/SKILL.md").read_text()
        command = (REPOSITORY / ".claude/commands/trellis/finish-work.md").read_text()
        self.assertEqual(skill.split("---", 2)[2].strip(), command.strip())
        for document in (skill, command):
            commands = re.findall(r"```bash\n(.*?)\n```", document, re.S)
            lifecycle = []
            for block in commands:
                for line in block.replace("\\\n", " ").splitlines():
                    argv = shlex.split(line)
                    if "archive" in argv or any(arg.endswith("add_session.py") for arg in argv):
                        lifecycle.append(argv)
                        self.assertIn("--no-commit", argv)
            self.assertEqual(len(lifecycle), 2)
            journal = next(argv for argv in lifecycle if "archive" not in argv)
            self.assertIn("--idempotency-key", journal)

    def test_stale_pointer_reconciles_archive_before_clearing_context(self):
        task = self.fixture.create_task("interrupted-archive")
        self.fixture.task("start", str(task), "--allow-empty-context")
        archive = self.root / ".trellis/tasks/archive/2026-09" / task.name
        archive.parent.mkdir(parents=True)
        task.rename(archive)
        for platform in ("codex", "claude"):
            with self.subTest(platform=platform):
                status = self.status(platform)
                self.assertIn("STALE POINTER", status)
                self.assertIn("active/archive", status)
                self.assertIn("journal/Git", status)
                self.assertNotIn("task.py finish", status)

    def initialize_journal(self):
        (self.root / ".trellis/.developer").unlink()
        self.fixture.run_command(
            sys.executable, ".trellis/scripts/init_developer.py", "integration-test",
        )
        return self.root / ".trellis/workspace/integration-test"

    def test_journal_retry_repairs_interrupted_index_and_stays_idempotent_after_commit(self):
        workspace = self.initialize_journal()
        index = workspace / "index.md"
        original_index = index.read_bytes()
        index.write_text("Interrupted fixture: index markers unavailable.\n")
        before = self.fixture.run_command("git", "rev-parse", "HEAD").stdout
        args = (
            sys.executable, ".trellis/scripts/add_session.py", "--no-commit",
            "--title", "Closeout fixture", "--commit", "-", "--summary", "Verified fixture.",
            "--idempotency-key", "closeout-fixture-v1",
        )
        interrupted = self.fixture.run_command(*args, success=False)
        self.assertIn("Checkpoint", interrupted.stderr)
        journal = workspace / "journal-1.md"
        journal_after_append = journal.read_bytes()
        index.write_bytes(original_index)
        resumed = self.fixture.run_command(*args)
        self.assertIn("[RESUME]", resumed.stderr)
        self.assertEqual(journal.read_bytes(), journal_after_append)
        after = {path: path.read_bytes() for path in workspace.iterdir() if path.is_file()}
        self.fixture.run_command(*args)
        self.assertEqual(after, {path: path.read_bytes() for path in after})
        self.assertEqual(self.fixture.run_command("git", "rev-parse", "HEAD").stdout, before)
        self.assertEqual(self.fixture.run_command("git", "diff", "--cached", "--name-only").stdout, "")
        # Only this disposable fixture is authorized to commit. A repeated finish
        # after that boundary must still resolve the same journal operation.
        self.fixture.run_command("git", "add", "--", str(workspace.relative_to(self.root)))
        self.fixture.run_command("git", "commit", "--quiet", "-m", "fixture closeout")
        self.fixture.run_command(*args)
        self.assertEqual(after, {path: path.read_bytes() for path in after})


if __name__ == "__main__":
    unittest.main()
