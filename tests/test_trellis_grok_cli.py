"""Contract checks for trellis-grok install. No network and no trellis init."""

import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "scripts" / "grok-fixes"
CLI = FIX / ("trellis-grok.cmd" if os.name == "nt" else "trellis-grok")


def command(args):
    """Run a .cmd through cmd.exe. Windows CreateProcess does not do that itself."""
    if os.name == "nt" and args and str(args[0]).lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/d", "/s", "/c", subprocess.list2cmdline([str(a) for a in args])]
    return [str(a) for a in args]


def run(*args):
    return subprocess.run(
        command([CLI, *args]),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        cwd=None if os.name == "nt" else ROOT,
    )


class TrellisGrokCliTests(unittest.TestCase):
    def test_help_documents_one_click_platforms_and_github(self):
        result = run("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = result.stdout
        self.assertIn("trellis-grok install", text)
        self.assertIn("--claude", text)
        self.assertIn("--codex", text)
        self.assertIn("--grok", text)
        self.assertIn("--codefree-o", text)
        self.assertIn("--codefree-space", text)
        self.assertIn("opt-in", text)
        self.assertIn("Official trellis init has no flag", text)
        self.assertIn("--from-github", text)
        self.assertIn("--no-skills", text)
        self.assertIn("Windows", text)
        self.assertIn("py -3", text)
        for command in ("status", "dry-run", "apply", "revert", "init", "update"):
            self.assertIn(command, text)

    def test_install_help_exits_zero(self):
        result = run("install", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--from-github", result.stdout)

    def test_unknown_command_still_fails(self):
        result = run("not-a-command")
        self.assertEqual(result.returncode, 2)

    def test_install_refuses_the_source_checkout(self):
        result = run("install", str(ROOT), "--no-skills", "-u", "refuse-test")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("refusing to install", result.stderr)

    def test_windows_launcher_forwards_new_flags_without_a_param_block(self):
        ps1 = (FIX / "oneclick.ps1").read_text(encoding="utf-8")
        for line in ps1.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            self.assertNotIn("param(", stripped.lower())
        self.assertIn("@args", ps1)
        self.assertIn("invoke-git-bash.cmd", ps1)
        self.assertIn("System32\\bash.exe", ps1)
        sh = (FIX / "oneclick.sh").read_text(encoding="utf-8")
        self.assertIn('"$@"', sh)
        self.assertIn("--codefree-o", sh)
        self.assertIn("--codefree-space", sh)
        cmd = (FIX / "oneclick.cmd").read_text(encoding="utf-8")
        self.assertIn("%*", cmd)
        self.assertIn("invoke-git-bash.cmd", cmd)


if __name__ == "__main__":
    unittest.main()
