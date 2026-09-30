"""Exercise the installed Trellis runtime in disposable Git repositories.

These tests validate parser, hook and task APIs, not autonomous agent behavior.
Run with: python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
STEPS = (
    "1.0", "1.1", "1.2", "1.3", "1.4", "1.5",
    "2.1", "2.2", "2.3", "3.2", "3.3", "3.4", "3.5",
)


class InstalledRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="trellis-integration-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.env = {
            key: value for key, value in os.environ.items()
            if not key.startswith(("TRELLIS_", "CODEX_", "CLAUDE_", "DSH_", "GIT_"))
        }
        self.env.update({
            "TRELLIS_CONTEXT_ID": "integration-test",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Integration Test",
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Integration Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        shutil.copytree(
            REPOSITORY / ".trellis/scripts", self.root / ".trellis/scripts",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        shutil.copy2(REPOSITORY / ".trellis/workflow.md", self.root / ".trellis/workflow.md")
        (self.root / ".trellis/.developer").write_text("name=integration-test\n")
        (self.root / ".trellis/config.yaml").write_text("codex:\n  dispatch_mode: auto\n")
        for platform in ("codex", "claude"):
            hook_dir = self.root / f".{platform}/hooks"
            hook_dir.mkdir(parents=True)
            # Shared hook platform branches are tested; no Claude harness is run.
            shutil.copy2(
                REPOSITORY / ".codex/hooks/inject-workflow-state.py",
                hook_dir / "inject-workflow-state.py",
            )
        self.run_command("git", "init", "--quiet", "--initial-branch=main")
        self.run_command("git", "add", ".")
        self.run_command("git", "commit", "--quiet", "-m", "fixture baseline")

    def run_command(
        self, *args: str, input_text: str | None = None, success: bool = True,
        context: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = dict(self.env)
        if context:
            env["TRELLIS_CONTEXT_ID"] = context
        result = subprocess.run(
            args, cwd=self.root, env=env, text=True, input=input_text,
            capture_output=True, timeout=20, check=False,
        )
        if success:
            self.assertEqual(result.returncode, 0, f"{args}\n{result.stdout}\n{result.stderr}")
        else:
            self.assertNotEqual(result.returncode, 0, f"Unexpected success: {args}")
        return result

    def task(self, *args: str, **kwargs) -> subprocess.CompletedProcess[str]:
        return self.run_command(sys.executable, ".trellis/scripts/task.py", *args, **kwargs)

    def create_task(self, slug: str, parent: Path | None = None) -> Path:
        args = [
            "create", f"Fixture {slug}", "--slug", slug,
            "--description", f"Verify {slug} in an isolated fixture",
            "--base-branch", "main", "--no-start",
        ]
        if parent:
            args.extend(["--parent", str(parent.relative_to(self.root))])
        self.task(*args)
        matches = list((self.root / ".trellis/tasks").glob(f"??-??-{slug}"))
        self.assertEqual(len(matches), 1)
        path = matches[0]
        (path / "prd.md").write_text(
            f"# {slug}\n\n## Acceptance Criteria\n\n- [ ] Fixture behavior is verified.\n"
        )
        return path

    def record(self, task: Path) -> dict:
        return json.loads((task / "task.json").read_text())

    def archive(self, task: Path, *args: str) -> Path:
        self.task("archive", str(task), "--no-commit", *args)
        self.assertFalse(task.exists())
        matches = list((self.root / ".trellis/tasks/archive").glob(f"*/{task.name}"))
        self.assertEqual(len(matches), 1, "Stable identity must resolve to exactly one archive")
        return matches[0]

    def hook(self, platform: str = "codex", prompt: str = "Continue the task.") -> str:
        result = self.run_command(
            sys.executable, f".{platform}/hooks/inject-workflow-state.py",
            input_text=json.dumps({"cwd": str(self.root), "prompt": prompt}),
        )
        payload = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(payload["hookEventName"], "UserPromptSubmit")
        return payload["additionalContext"]

    def test_effective_index_is_compact_and_detail_stays_on_demand(self) -> None:
        result = self.run_command(
            sys.executable, ".trellis/scripts/get_context.py", "--mode", "phase",
        )
        index = result.stdout
        self.assertTrue(index.startswith("## Phase Index"))
        self.assertLess(len(index), 5000)
        self.assertNotIn("#### 1.0", index)
        self.assertNotIn("workflow-state:", index)
        self.assertNotIn("## Runtime breadcrumbs", index)
        self.assertIn("get_context.py --mode phase --step", index)

    def test_every_runtime_step_renders_for_codex_and_claude(self) -> None:
        for platform in ("codex", "claude"):
            for step in STEPS:
                with self.subTest(platform=platform, step=step):
                    body = self.run_command(
                        sys.executable, ".trellis/scripts/get_context.py", "--mode", "phase",
                        "--step", step, "--platform", platform,
                    ).stdout
                    self.assertTrue(body.startswith(f"#### {step} "), body)
                    self.assertGreater(len(body.split("\n", 1)[1].strip()), 60)
                    self.assertEqual(len(re.findall(r"^#### \d+\.\d+", body, re.M)), 1)
                    self.assertNotIn("workflow-state:", body)

    def test_all_breadcrumb_states_reach_the_actual_hook(self) -> None:
        for platform in ("codex", "claude"):
            with self.subTest(platform=platform, state="no_task"):
                self.assertIn("Status: no_task", self.hook(platform))
        task = self.create_task("breadcrumb")
        self.task("start", str(task), "--allow-empty-context")
        for mode in ("auto", "inline"):
            (self.root / ".trellis/config.yaml").write_text(f"codex:\n  dispatch_mode: {mode}\n")
            for status in ("planning", "in_progress", "completed"):
                data = self.record(task)
                data["status"] = status
                (task / "task.json").write_text(json.dumps(data))
                for platform in ("codex", "claude"):
                    with self.subTest(mode=mode, status=status, platform=platform):
                        body = self.hook(platform)
                        self.assertIn(f"Task: breadcrumb ({status})", body)
                        self.assertNotIn("Refer to workflow.md for current step.", body)
                        self.assertLess(len(body), 1600)
                        if status != "completed":
                            self.assertIn("docs/agents/matt-flow.md", body)
                        if platform == "codex":
                            self.assertIn("<codex-mode>", body)

    def test_publication_readiness_does_not_activate_or_steal_a_session(self) -> None:
        self.run_command("git", "checkout", "--quiet", "-b", "feature/fixture")
        parent = self.create_task("spec")
        self.task("set-meta", str(parent), "matt_publication_kind", "spec")
        self.task("set-meta", str(parent), "matt_publication_ref", f"trellis-task:{parent.name}")
        self.task("set-meta", str(parent), "matt_spec_artifacts", "prd.md")
        self.task("set-meta", str(parent), "matt_ready_for_agent", "true")
        child = self.create_task("ticket", parent)
        self.task("set-meta", str(child), "matt_publication_kind", "ticket")
        self.task("set-meta", str(child), "matt_publication_ref", f"trellis-task:{child.name}")
        self.task("set-meta", str(child), "matt_parent_ref", f"trellis-task:{parent.name}")
        self.task("set-meta", str(child), "matt_ready_for_agent", "true")
        for phase in ("implement", "check"):
            self.task("add-context", str(child), phase, str((parent / "prd.md").relative_to(self.root)))
        self.task("validate", str(child))
        self.assertEqual(self.record(parent)["status"], "planning")
        self.assertEqual(self.record(child)["status"], "planning")
        self.assertEqual(self.record(child)["meta"]["matt_ready_for_agent"], "true")
        self.assertIn(child.name, self.record(parent)["children"])
        self.assertEqual(self.record(child)["parent"], parent.name)
        self.assertIn("Status: no_task", self.hook())
        self.task("start", str(child))
        self.assertEqual(self.record(child)["status"], "in_progress")
        self.assertEqual(self.record(parent)["status"], "planning")
        self.assertIn("Task: ticket (in_progress)", self.hook())
        other = self.task("current", "--json", context="independent-worker", success=False)
        self.assertIsNone(json.loads(other.stdout)["current_task"])

    def test_child_before_parent_archive_preserves_identity_without_committing(self) -> None:
        parent = self.create_task("archive-parent")
        child = self.create_task("archive-child", parent)
        self.task("set-meta", str(child), "matt_parent_ref", f"trellis-task:{parent.name}")
        before = self.run_command("git", "rev-parse", "HEAD").stdout
        archived_child = self.archive(child)
        self.assertEqual(self.record(archived_child)["parent"], parent.name)
        archived_parent = self.archive(parent)
        self.assertIn(child.name, self.record(archived_parent)["children"])
        self.assertEqual(self.record(archived_child)["parent"], archived_parent.name)
        self.assertEqual(self.record(archived_child)["meta"]["matt_parent_ref"], f"trellis-task:{parent.name}")
        self.assertEqual(self.record(archived_parent)["status"], "completed")
        self.assertEqual(self.run_command("git", "rev-parse", "HEAD").stdout, before)
        self.assertEqual(self.run_command("git", "diff", "--cached", "--name-only").stdout, "")

    def test_parent_first_archive_demonstrates_why_order_matters(self) -> None:
        parent = self.create_task("early-parent")
        child = self.create_task("remaining-child", parent)
        self.archive(parent)
        self.assertIsNone(self.record(child)["parent"])
        self.assertEqual(self.record(child)["status"], "planning")

    def test_archive_refuses_self_targeting_branch_before_mutation(self) -> None:
        task = self.create_task("branch-safety")
        self.task("set-branch", str(task), "main")
        before = (task / "task.json").read_bytes()
        result = self.task("archive", str(task), "--no-commit", success=False)
        self.assertIn("branch and base_branch", result.stderr)
        self.assertEqual((task / "task.json").read_bytes(), before)
        # The fixture is local-only and never PR-backed; exercise the supported
        # explicit exception instead of falsifying its branch metadata.
        archived = self.archive(task, "--skip-branch-validation")
        self.assertEqual(self.record(archived)["status"], "completed")

    def test_archival_does_not_rewrite_context_file_references(self) -> None:
        parent = self.create_task("context-parent")
        child = self.create_task("context-child", parent)
        old_path = str((parent / "prd.md").relative_to(self.root))
        for phase in ("implement", "check"):
            self.task("add-context", str(child), phase, old_path)
        self.task("validate", str(child))
        archived_child = self.archive(child)
        archived_parent = self.archive(parent)
        self.assertTrue((archived_parent / "prd.md").is_file())
        self.assertFalse((self.root / old_path).exists())
        # Stable publication IDs survive, but JSONL filesystem paths need
        # resolution/curation on resume; the runtime must not silently PASS.
        result = self.task("validate", str(archived_child), success=False)
        self.assertIn(old_path, result.stdout)


if __name__ == "__main__":
    unittest.main()
