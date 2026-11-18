"""Install wiring for codefree-o and CodeFree Space.

These tests run real `trellis init` in temporary directories. They do not
touch live projects. pytest is not required.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "grok-fixes" / ("trellis-grok.cmd" if os.name == "nt" else "trellis-grok")
SKILL_NAMES = ("trellis-start", "trellis-continue", "trellis-finish-work")
NEEDLES = ("get_context.py", "grill-with-docs", "task.py create", "--no-start")
ABSENT = (".claude", ".codex", ".grok", ".opencode", ".cursor")


def command(args):
    if os.name == "nt" and args and str(args[0]).lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/d", "/s", "/c", subprocess.list2cmdline([str(a) for a in args])]
    return [str(a) for a in args]


def run_install(project: Path, args: list[str], env: dict | None = None, timeout: int = 240):
    return subprocess.run(
        command([CLI, "install", str(project), "-u", "codefree-test", *args]),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
        env=env,
        cwd=str(ROOT),
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def assert_bootstrap(test: unittest.TestCase, project: Path) -> None:
    for name in ("AGENTS.md", "CLAUDE.md"):
        text = (project / name).read_text(encoding="utf-8")
        for needle in NEEDLES:
            test.assertIn(needle, text, f"{name} missing {needle}")


def assert_aligned_skills(test: unittest.TestCase, project: Path) -> None:
    for name in SKILL_NAMES:
        installed = project / ".agents" / "skills" / name / "SKILL.md"
        source = ROOT / ".agents" / "skills" / name / "SKILL.md"
        test.assertTrue(installed.is_file(), installed)
        test.assertEqual(installed.read_text(encoding="utf-8"), source.read_text(encoding="utf-8"))


def assert_no_codex_hashes(test: unittest.TestCase, project: Path) -> None:
    manifest = project / ".trellis" / ".template-hashes.json"
    test.assertTrue(manifest.is_file(), manifest)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    bad = [
        key
        for key in data.get("hashes", {})
        if key.replace("\\", "/").startswith(".codex/")
    ]
    test.assertEqual(bad, [])


def absent_platform_dirs(project: Path) -> list[str]:
    return [name for name in ABSENT if (project / name).exists()]


class CodefreeOnlyInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="trellis-codefree-both-")
        cls.project = Path(cls.tmp.name) / "both"
        cls.project.mkdir()
        write(cls.project / "AGENTS.md", "PROJECT-NOTE-KEEP\n")
        write(cls.project / ".agents" / "skills" / "grill-me" / "SKILL.md", "KEEP-MATT-SKILL\n")
        write(cls.project / "KEEP.txt", "untouched\n")
        cls.first = run_install(
            cls.project,
            ["--codefree-o", "--codefree-space", "--no-skills"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_install_exits_zero(self):
        self.assertEqual(
            self.first.returncode,
            0,
            self.first.stdout[-2000:] + "\n" + self.first.stderr[-2000:],
        )
        self.assertIn("platforms: (none)", self.first.stdout)
        self.assertIn("codefree-o", self.first.stdout)
        self.assertIn("codefree-space", self.first.stdout)
        self.assertIn("skip Matt skills", self.first.stdout)

    def test_shared_files_and_codefree_o_commands(self):
        self.assertEqual(self.first.returncode, 0, "install failed")
        assert_bootstrap(self, self.project)
        self.assertIn("PROJECT-NOTE-KEEP", (self.project / "AGENTS.md").read_text(encoding="utf-8"))
        assert_aligned_skills(self, self.project)
        assert_no_codex_hashes(self, self.project)
        self.assertEqual(absent_platform_dirs(self.project), [])
        self.assertFalse((self.project / "skills-lock.json").exists())
        self.assertEqual((self.project / "KEEP.txt").read_text(encoding="utf-8"), "untouched\n")
        self.assertIn(
            "KEEP-MATT-SKILL",
            (self.project / ".agents" / "skills" / "grill-me" / "SKILL.md").read_text(encoding="utf-8"),
        )
        self.assertTrue((self.project / ".trellis" / "workflow.md").is_file())
        self.assertTrue((self.project / "docs" / "agents" / "matt-flow.md").is_file())
        self.assertTrue((self.project / ".gitattributes").is_file())
        self.assertFalse((self.project / ".codefree-o" / "command" / "trellis-grok-deploy.md").exists())
        for name in SKILL_NAMES:
            command = self.project / ".codefree-o" / "command" / f"{name}.md"
            text = command.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), command)
            self.assertIn("description:", text)
            self.assertIn("$ARGUMENTS", text)
            self.assertIn("get_context.py", text)

    def test_second_install_skips_init_and_keeps_existing_skill(self):
        if self.first.returncode != 0:
            self.fail("first install failed")
        second = run_install(
            self.project,
            ["--codefree-o", "--codefree-space", "--no-skills"],
        )
        self.assertEqual(second.returncode, 0, second.stdout[-1500:] + second.stderr[-1500:])
        self.assertIn("skipping trellis init", second.stdout)
        self.assertIn(
            "KEEP-MATT-SKILL",
            (self.project / ".agents" / "skills" / "grill-me" / "SKILL.md").read_text(encoding="utf-8"),
        )
        assert_bootstrap(self, self.project)

    def test_codefree_o_lists_project_skill_and_commands(self):
        if self.first.returncode != 0:
            self.fail("first install failed")
        binary = shutil.which("codefree-o")
        if not binary:
            self.skipTest("codefree-o is not on PATH")
        env = os.environ.copy()
        env.pop("FORCE_COLOR", None)
        env["NO_COLOR"] = "1"
        # A pipe stops this command near 64KiB with exit 0, before project
        # skills. Write stdout to a file so the full list is captured.
        skill_out = Path(self.tmp.name) / "debug-skill.txt"
        with skill_out.open("w", encoding="utf-8") as stdout:
            skill = subprocess.run(
                [binary, "debug", "skill", "--pure", "--log-level", "ERROR"],
                cwd=self.project,
                stdout=stdout,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                env=env,
            )
        skill_text = skill_out.read_text(encoding="utf-8", errors="replace")
        self.assertEqual(skill.returncode, 0, (skill.stderr or "")[-1500:])
        project_skill = str(self.project / ".agents" / "skills" / "trellis-start" / "SKILL.md")
        self.assertIn(project_skill, skill_text)
        self.assertIn('"name": "trellis-start"', skill_text)
        config_out = Path(self.tmp.name) / "debug-config.txt"
        with config_out.open("w", encoding="utf-8") as stdout:
            config = subprocess.run(
                [binary, "debug", "config", "--pure", "--log-level", "ERROR"],
                cwd=self.project,
                stdout=stdout,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                env=env,
            )
        self.assertEqual(config.returncode, 0, (config.stderr or "")[-1500:])
        raw = config_out.read_text(encoding="utf-8", errors="replace")
        raw = raw[raw.find("{") :]
        parsed = json.loads(raw)
        commands = parsed.get("command") or {}
        for name in SKILL_NAMES:
            self.assertIn(name, commands)
            blob = json.dumps(commands[name])
            self.assertIn("$ARGUMENTS", blob)
            self.assertIn("get_context.py", blob)


class ClaudeOnlyDoesNotWireCodefreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="trellis-codefree-claude-")
        cls.project = Path(cls.tmp.name) / "claude"
        cls.project.mkdir()
        cls.result = run_install(cls.project, ["--claude", "--no-skills"])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_claude_hook_without_codefree_or_codex_trees(self):
        self.assertEqual(
            self.result.returncode,
            0,
            self.result.stdout[-2000:] + "\n" + self.result.stderr[-2000:],
        )
        self.assertTrue((self.project / ".claude" / "hooks" / "session-start.py").is_file())
        self.assertFalse((self.project / ".codefree-o").exists())
        self.assertFalse((self.project / ".codex").exists())
        self.assertFalse((self.project / ".grok").exists())
        self.assertFalse((self.project / ".opencode").exists())
        self.assertFalse((self.project / "skills-lock.json").exists())
        assert_bootstrap(self, self.project)


class ClaudePlusCodefreeOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="trellis-codefree-mix-")
        cls.project = Path(cls.tmp.name) / "mix"
        cls.project.mkdir()
        write(cls.project / ".agents" / "skills" / "grill-me" / "SKILL.md", "KEEP-MATT-SKILL\n")
        cls.result = run_install(cls.project, ["--claude", "--codefree-o", "--no-skills"])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_claude_init_plus_shared_skill_seed_without_codex_tree(self):
        self.assertEqual(
            self.result.returncode,
            0,
            self.result.stdout[-2000:] + "\n" + self.result.stderr[-2000:],
        )
        self.assertTrue((self.project / ".claude" / "hooks" / "session-start.py").is_file())
        self.assertTrue(
            (self.project / ".agents" / "skills" / "trellis-before-dev" / "SKILL.md").is_file()
        )
        assert_aligned_skills(self, self.project)
        assert_no_codex_hashes(self, self.project)
        self.assertFalse((self.project / ".codex").exists())
        self.assertFalse((self.project / ".grok").exists())
        self.assertFalse((self.project / ".opencode").exists())
        self.assertIn(
            "KEEP-MATT-SKILL",
            (self.project / ".agents" / "skills" / "grill-me" / "SKILL.md").read_text(encoding="utf-8"),
        )
        command = (self.project / ".codefree-o" / "command" / "trellis-start.md").read_text(encoding="utf-8")
        self.assertIn("$ARGUMENTS", command)
        assert_bootstrap(self, self.project)


class CodefreeSpaceSkillsAgentTests(unittest.TestCase):
    def test_space_install_asks_skills_cli_for_codex_not_claude(self):
        with tempfile.TemporaryDirectory(prefix="trellis-codefree-npx-") as tmp:
            root = Path(tmp)
            project = root / "space"
            project.mkdir()
            bin_dir = root / "bin"
            bin_dir.mkdir()
            log = root / "npx.log"
            fake = bin_dir / ("npx.cmd" if os.name == "nt" else "npx")
            if os.name == "nt":
                fake.write_text(
                    "@echo off\r\necho %*>>%NPX_LOG%\r\nexit /b 0\r\n",
                    encoding="utf-8",
                )
            else:
                fake.write_text(
                    "#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$NPX_LOG\"\nexit 0\n",
                    encoding="utf-8",
                )
                fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
            env = os.environ.copy()
            env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
            env["NPX_LOG"] = str(log)
            result = run_install(project, ["--codefree-space"], env=env)
            self.assertEqual(result.returncode, 0, result.stdout[-2000:] + "\n" + result.stderr[-2000:])
            recorded = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
            self.assertIn("--agent", recorded)
            self.assertIn("codex", recorded)
            self.assertNotIn("claude-code", recorded)
            self.assertNotIn(" grok", recorded)
            self.assertIn("platforms: (none)", result.stdout)
            self.assertIn("codefree-space", result.stdout)
            self.assertIn(".agents/skills is what codefree-o and CodeFree Space scan", result.stdout)
            self.assertFalse((project / ".codefree-o").exists())
            self.assertFalse((project / ".codex").exists())
            self.assertTrue((project / ".agents" / "skills" / "trellis-start" / "SKILL.md").is_file())
            assert_bootstrap(self, project)
            assert_no_codex_hashes(self, project)


if __name__ == "__main__":
    unittest.main()
