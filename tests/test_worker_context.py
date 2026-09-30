"""Worker identity tests for the actual Codex 0.159.0 hook and role-pull API.

SubagentStart has no prompt. Native starts emit loading instructions; these tests
invoke the same CLI the child uses only after receiving its dispatch.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]


class WorkerContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="trellis-worker-context-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / ".git").mkdir()
        shutil.copytree(
            REPOSITORY / ".trellis/scripts", self.root / ".trellis/scripts",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        for platform in ("codex", "claude"):
            hooks = self.root / f".{platform}/hooks"
            hooks.mkdir(parents=True)
            shutil.copy2(REPOSITORY / f".{platform}/hooks/inject-subagent-context.py", hooks)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("TRELLIS_", "CODEX_", "CLAUDE_"))}
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"
        self.first = self.make_task("first", "FIRST_TASK_ARTIFACT")
        self.second = self.make_task("second", "SECOND_TASK_ARTIFACT")
        sessions = self.root / ".trellis/.runtime/sessions"
        sessions.mkdir(parents=True)
        self.pointer = sessions / "codex_parent-session.json"
        self.pointer.write_text(json.dumps({"current_task": self.second}))

    def make_task(self, slug: str, marker: str) -> str:
        relative = f".trellis/tasks/09-29-{slug}"
        task = self.root / relative
        task.mkdir(parents=True)
        (task / "task.json").write_text(json.dumps({"id": slug, "status": "implementing"}))
        (task / "prd.md").write_text(marker)
        for role in ("implement", "check"):
            guide = self.root / f"{slug}-{role}.md"
            guide.write_text(f"{slug.upper()}_{role.upper()}_GUIDE")
            (task / f"{role}.jsonl").write_text(json.dumps({"file": guide.name}) + "\n")
        return relative

    def invoke(self, *args: str, platform: str = "codex", event: dict | None = None):
        return subprocess.run(
            [sys.executable, f".{platform}/hooks/inject-subagent-context.py", *args],
            cwd=self.root, env=self.env, input=json.dumps(event) if event is not None else None,
            text=True, capture_output=True, timeout=10, check=False,
        )

    def load(self, *identity: str, role: str = "implement"):
        return self.invoke("--load-context", "--agent-type", f"trellis-{role}", *identity)

    def claude(self, prompt: str):
        return self.invoke(platform="claude", event={
            "hook_event_name": "PreToolUse", "tool_name": "Agent", "cwd": str(self.root),
            "tool_input": {"subagent_type": "trellis-implement", "prompt": prompt},
        })

    def assert_claude_denied(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertNotIn("updatedInput", output)
        self.assertNotIn("TASK_ARTIFACT", result.stdout)

    def test_native_event_defers_selection_without_reading_task_or_transcript(self):
        # Exact fields from rust-v0.159.0 subagent-start.command.input.schema.json.
        event = {
            "hook_event_name": "SubagentStart", "session_id": "parent-session",
            "agent_id": "worker-id", "agent_type": "trellis-implement", "turn_id": "turn-id",
            "cwd": str(self.root), "model": "test-model", "permission_mode": "dontAsk",
            "transcript_path": str(self.root / "unavailable.jsonl"),
        }
        for session_id in ("parent-session", "", "other-session"):
            with self.subTest(session_id=session_id):
                result = self.invoke(event={**event, "session_id": session_id})
                self.assertEqual(result.returncode, 0, result.stderr)
                context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
                self.assertIn("trellis-context-loader", context)
                self.assertNotIn("trellis-hook-injected", context)
                self.assertNotIn("TASK_ARTIFACT", context)
                self.assertNotIn(self.second, context)
                self.assertIn(session_id or "unavailable", context)

    def test_distinct_explicit_tasks_override_parent_and_keep_role_context(self):
        for task, marker, other in ((self.first, "FIRST", "SECOND"), (self.second, "SECOND", "FIRST")):
            for role in ("implement", "check"):
                for value in (task, str(self.root / task), f"`{task}`"):
                    with self.subTest(task=value, role=role):
                        result = self.load("--task", value, role=role)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn(f"{marker}_TASK_ARTIFACT", result.stdout)
                        self.assertIn(f"{marker}_{role.upper()}_GUIDE", result.stdout)
                        self.assertNotIn(f"{other}_TASK_ARTIFACT", result.stdout)
                        self.assertIn("trellis-context-loaded", result.stdout)

    def test_repeated_same_identity_is_safe(self):
        result = self.load("--task", self.first, "--task", self.first)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("FIRST_TASK_ARTIFACT", result.stdout)

    def test_external_workflow_store_preserves_explicit_and_parent_loading(self):
        store = tempfile.TemporaryDirectory(prefix="trellis-shared-store-")
        self.addCleanup(store.cleanup)
        workflow = Path(store.name) / "workflow"
        shutil.move(self.root / ".trellis", workflow)
        (self.root / ".trellis").symlink_to(workflow, target_is_directory=True)
        for value in (self.first, str(workflow / "tasks/09-29-first")):
            with self.subTest(value=value):
                result = self.load("--task", value)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("FIRST_TASK_ARTIFACT", result.stdout)
                self.assertIn(f"Active task: {self.first}", result.stdout)
                result = self.claude(f"Active task: {value}")
                self.assertIn("FIRST_TASK_ARTIFACT", result.stdout)
                self.assertNotIn("SECOND_TASK_ARTIFACT", result.stdout)
        result = self.load("--no-explicit-task", "--parent-session-id", "parent-session")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SECOND_TASK_ARTIFACT", result.stdout)
        # Supporting a shared workflow store must not allow its tasks tree to
        # escape that store through a second symlink.
        escaped_tasks = Path(store.name) / "escaped-tasks"
        shutil.move(workflow / "tasks", escaped_tasks)
        (workflow / "tasks").symlink_to(escaped_tasks, target_is_directory=True)
        result = self.load("--task", self.first)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assert_claude_denied(self.claude(f"Active task: {self.first}"))

    def test_invalid_explicit_identity_never_falls_back_on_either_platform(self):
        outside = self.root / "outside-task"
        outside.mkdir()
        (outside / "task.json").write_text("{}")
        escape = self.root / ".trellis/tasks/escape"
        escape.symlink_to(outside, target_is_directory=True)
        loop = self.root / ".trellis/tasks/loop"
        loop.symlink_to(loop)
        external = tempfile.TemporaryDirectory(prefix="trellis-other-project-")
        self.addCleanup(external.cleanup)
        (Path(external.name) / "task.json").write_text("{}")
        external_link = self.root / ".trellis/tasks/external"
        external_link.symlink_to(external.name, target_is_directory=True)
        invalid = ("", "   ", ".trellis/tasks/missing", ".trellis/scripts", str(outside),
                   external.name, ".trellis/tasks/external", ".trellis/tasks/escape",
                   ".trellis/tasks/loop", "../outside", "`" + self.first,
                   self.first + "`", self.first + " trailing", self.first + "\nignored")
        for value in invalid:
            with self.subTest(value=value):
                result = self.load("--task", value)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                # A newline ends a marker in real prompts; CLI path values must
                # still reject it instead of silently accepting only the prefix.
                if "\n" not in value:
                    result = self.claude(f"Active task: {value}\nDo the work.")
                    self.assert_claude_denied(result)
        result = self.load("--task", self.first, "--task", self.second)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        result = self.claude(f"Active task: {self.first}\nActive task: {self.second}")
        self.assert_claude_denied(result)

    def test_fallback_requires_confirmed_absence_and_exact_parent(self):
        result = self.load("--no-explicit-task", "--parent-session-id", "parent-session")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SECOND_TASK_ARTIFACT", result.stdout)
        # Deliberately contaminate the environment; this loader must ignore it.
        self.env["TRELLIS_CONTEXT_ID"] = "codex_parent-session"
        for args in ((), ("--no-explicit-task",),
                     ("--no-explicit-task", "--parent-session-id", "another-session"),
                     ("--task", self.first, "--no-explicit-task")):
            with self.subTest(args=args):
                result = self.load(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
        self.pointer.write_text(json.dumps({"current_task": ".trellis/tasks/stale"}))
        result = self.load("--no-explicit-task", "--parent-session-id", "parent-session")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_claude_retains_no_explicit_single_session_fallback(self):
        result = self.claude("Implement the current task.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SECOND_TASK_ARTIFACT", result.stdout)
        result = self.claude(f"Active task: {self.first}\nImplement the task.")
        self.assertIn("FIRST_TASK_ARTIFACT", result.stdout)
        self.assertNotIn("SECOND_TASK_ARTIFACT", result.stdout)

    def test_research_context_does_not_load_implementation_artifacts(self):
        result = self.load("--task", self.first, role="research")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"Active task: {self.first}", result.stdout)
        self.assertNotIn("TASK_ARTIFACT", result.stdout)
        self.assertNotIn("IMPLEMENT_GUIDE", result.stdout)
        self.assertNotIn("CHECK_GUIDE", result.stdout)

    def test_all_native_roles_require_dispatch_validation_before_loading(self):
        for role in ("implement", "check", "research"):
            with self.subTest(role=role):
                config = tomllib.loads((REPOSITORY / f".codex/agents/trellis-{role}.toml").read_text())
                protocol = config["developer_instructions"]
                self.assertIn("Read your complete current dispatch first", protocol)
                self.assertIn(f"--agent-type trellis-{role}", protocol)
                self.assertIn("Pass every marker's value", protocol)
                self.assertIn("--no-explicit-task --parent-session-id", protocol)
                self.assertIn("Loader failure means no task context was loaded", protocol)


if __name__ == "__main__":
    unittest.main()
