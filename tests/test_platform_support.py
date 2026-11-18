"""Portable Python, cache-dir, and shortcut resolution. No project installs."""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "scripts" / "grok-fixes"
PLATFORM = FIX / "platform.sh"
SHORTCUT = FIX / "install-shortcut.sh"


def git_bash() -> list[str]:
    if os.name != "nt":
        return ["/bin/bash"]
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Git" / "bin" / "bash.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Git" / "bin" / "bash.exe",
    ]
    for path in candidates:
        if path.is_file():
            resolved = str(path)
            if resolved.lower().endswith(r"\system32\bash.exe"):
                continue
            return [resolved, "--noprofile", "--norc"]
    raise AssertionError("Git for Windows bash.exe was not found")


def run_platform(arg: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*git_bash(), str(PLATFORM), arg],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        env=env,
    )


def shell_path(path: Path) -> str:
    """Path as the installer shell prints it. Git Bash maps the Windows temp dir to /tmp."""
    if os.name != "nt":
        return str(path)
    proc = subprocess.run(
        [*git_bash(), "-c", 'cygpath -u "$1"', "bash", str(path)],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return str(path)
    return proc.stdout.strip()


def base_env(**overrides: str) -> dict[str, str]:
    env = os.environ.copy()
    for key in (
        "TRELLIS_MATT_PLATFORM",
        "TRELLIS_MATT_CLONE_DIR",
        "TRELLIS_MATT_PYTHON",
        "TRELLIS_MATT_HOME",
        "XDG_CACHE_HOME",
        "XDG_BIN_HOME",
    ):
        env.pop(key, None)
    env.update(overrides)
    return env


def write_stub(directory: Path, name: str, body: str) -> None:
    path = directory / name
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


class PlatformSupportTests(unittest.TestCase):
    def test_linux_clone_dir_uses_xdg_or_home_cache(self):
        home = "/tmp/trellis-matt-platform-home"
        env = base_env(HOME=home, TRELLIS_MATT_PLATFORM="unix", PATH=os.environ.get("PATH", ""))
        result = run_platform("clone-dir", env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"{home}/.cache/trellis-matt/workflow")

        env["XDG_CACHE_HOME"] = "/var/tmp/trellis-matt-xdg"
        result = run_platform("clone-dir", env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "/var/tmp/trellis-matt-xdg/trellis-matt/workflow")

    def test_windows_clone_dir_uses_localappdata(self):
        env = base_env(
            TRELLIS_MATT_PLATFORM="windows",
            LOCALAPPDATA=r"C:\Users\Example\AppData\Local",
            HOME="/tmp/unused-home",
            PATH=os.environ.get("PATH", ""),
        )
        result = run_platform("clone-dir", env)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = result.stdout.strip().replace("\\", "/")
        self.assertTrue(text.endswith("/trellis-matt/workflow"), text)
        self.assertIn("AppData/Local", text)
        self.assertNotIn("/home/samiya", text)

    def test_clone_dir_override_wins(self):
        env = base_env(
            TRELLIS_MATT_PLATFORM="unix",
            TRELLIS_MATT_CLONE_DIR="/override/trellis-workflow",
            HOME="/tmp/unused",
            PATH=os.environ.get("PATH", ""),
        )
        result = run_platform("clone-dir", env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "/override/trellis-workflow")

    def test_python_resolution_order(self):
        with tempfile.TemporaryDirectory(prefix="trellis-py-") as raw:
            stub = Path(raw)
            write_stub(stub, "python3", "#!/bin/sh\nexit 0\n")
            write_stub(stub, "python", "#!/bin/sh\necho should-not-run >&2\nexit 0\n")
            env = base_env(PATH=str(stub), TRELLIS_MATT_PLATFORM="unix")
            result = run_platform("python", env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "python3")

            write_stub(stub, "python3", "#!/bin/sh\nexit 1\n")
            result = run_platform("python", env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "python")

            (stub / "python3").unlink()
            (stub / "python").unlink()
            write_stub(
                stub,
                "py",
                "#!/bin/sh\n"
                "if [ \"$1\" = \"-3\" ]; then shift; fi\n"
                "exit 0\n",
            )
            result = run_platform("python", env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "py -3")

            (stub / "py").unlink()
            result = run_platform("python", env)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertIn("python3, python, py -3", result.stderr)

    def test_windows_shortcut_dir_prefers_local_bin_then_user_path(self):
        with tempfile.TemporaryDirectory(prefix="trellis-bin-") as raw:
            home = Path(raw) / "home"
            # Git Bash adds $HOME/bin to PATH. Keep HOME off the profile so that
            # injected directory does not satisfy the $USERPROFILE/bin preference.
            home_shell = Path(raw) / "shell-home"
            local_bin = home / ".local" / "bin"
            tools = home / "tools"
            tools.mkdir(parents=True)
            env = base_env(
                TRELLIS_MATT_PLATFORM="windows",
                HOME=str(home_shell),
                USERPROFILE=str(home),
                PATH=os.pathsep.join([str(local_bin), "/usr/bin"]),
            )
            env.pop("APPDATA", None)
            result = run_platform("shortcut-dir", env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), shell_path(local_bin))

            env["PATH"] = os.pathsep.join([str(tools), "/usr/bin"])
            result = run_platform("shortcut-dir", env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), shell_path(tools))

            mise = home / "mise" / "installs" / "node" / "bin"
            mise.mkdir(parents=True)
            env["PATH"] = os.pathsep.join([str(mise), "/usr/bin"])
            result = run_platform("shortcut-dir", env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), shell_path(home / ".local" / "bin"))

    def test_windows_shortcut_writes_cmd_without_symlink(self):
        with tempfile.TemporaryDirectory(prefix="trellis-shim-") as raw:
            home = Path(raw) / "home"
            bindir = home / ".local" / "bin"
            bindir.mkdir(parents=True)
            env = base_env(
                TRELLIS_MATT_PLATFORM="windows",
                HOME=str(home),
                USERPROFILE=str(home),
                PATH=os.pathsep.join([str(bindir), os.environ.get("PATH", "")]),
            )
            env.pop("APPDATA", None)
            proc = subprocess.run(
                [*git_bash(), str(SHORTCUT), "--home", str(ROOT)],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            cmd = bindir / "trellis-matt.cmd"
            ps1 = bindir / "trellis-matt.ps1"
            self.assertTrue(cmd.is_file(), proc.stdout)
            self.assertTrue(ps1.is_file(), proc.stdout)
            self.assertFalse((bindir / "trellis-matt").exists())
            text = cmd.read_bytes().replace(b"\r\n", b"\n").decode()
            self.assertIn("invoke-git-bash.cmd", text)
            self.assertIn("trellis-matt", text)
            self.assertNotIn("System32", text)
            self.assertNotIn("ln -s", text)

    @unittest.skipIf(os.name == "nt", "Linux shortcut is a symlink; Windows writes trellis-matt.cmd")
    def test_unix_shortcut_remains_a_symlink(self):
        with tempfile.TemporaryDirectory(prefix="trellis-unix-shim-") as raw:
            bindir = Path(raw) / "bin"
            env = base_env(
                TRELLIS_MATT_PLATFORM="unix",
                HOME=str(Path(raw) / "home"),
                XDG_BIN_HOME=str(bindir),
                PATH=os.environ.get("PATH", ""),
            )
            proc = subprocess.run(
                [*git_bash(), str(SHORTCUT), "--home", str(ROOT)],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            link = bindir / "trellis-matt"
            self.assertTrue(link.is_symlink(), proc.stdout)
            self.assertEqual(link.resolve(), (FIX / "trellis-matt").resolve())

    def test_launcher_refuses_system32_bash_and_keeps_default_repo(self):
        launcher = (FIX / "invoke-git-bash.cmd").read_bytes().replace(b"\r\n", b"\n").decode()
        self.assertIn(r"Git\bin\bash.exe", launcher)
        self.assertIn(r"System32\bash.exe", launcher)
        self.assertIn("refusing", launcher)
        self.assertIn("SCRIPT_RUN=%SCRIPT:\\=/%", launcher)
        oneclick = (FIX / "oneclick.sh").read_text(encoding="utf-8")
        cli = (FIX / "trellis-matt").read_text(encoding="utf-8")
        for text in (oneclick, cli):
            self.assertIn("https://github.com/samiya782/trellis-workflow.git", text)
            self.assertIn("LOCALAPPDATA", text)
            self.assertIn("XDG_CACHE_HOME", text)


if __name__ == "__main__":
    unittest.main()
