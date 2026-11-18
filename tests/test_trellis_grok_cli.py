"""Contract checks for trellis-grok install. No network and no trellis init."""

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "grok-fixes" / "trellis-grok"


def run(*args):
    return subprocess.run(
        [str(CLI), *args],
        text=True,
        capture_output=True,
        cwd=ROOT,
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
        self.assertIn("--from-github", text)
        self.assertIn("--no-skills", text)
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


if __name__ == "__main__":
    unittest.main()
