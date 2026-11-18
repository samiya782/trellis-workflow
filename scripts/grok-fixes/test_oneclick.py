#!/usr/bin/env python3
"""End-to-end checks for trellis-matt install.

Work directory: TRELLIS_ONECLICK_WORKDIR, else
$TRELLIS_ONECLICK_TMP/<stamp> or the OS temp dir. Never touches the source
checkout or other projects. Exits 0 only when every check passes.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "scripts" / "grok-fixes"
if os.name == "nt":
    CLI = FIX / "trellis-matt.cmd"
    ONECLICK = FIX / "oneclick.cmd"
    SHORTCUT = FIX / "install-shortcut.cmd"
else:
    CLI = FIX / "trellis-matt"
    ONECLICK = FIX / "oneclick.sh"
    SHORTCUT = FIX / "install-shortcut.sh"
STAMP = time.strftime("%Y%m%d-%H%M%S")
GITHUB = "https://github.com/samiya782/trellis-workflow"


def default_work() -> Path:
    override = os.environ.get("TRELLIS_ONECLICK_WORKDIR")
    if override:
        return Path(override)
    base = os.environ.get("TRELLIS_ONECLICK_TMP")
    if not base:
        base = os.environ.get("TEMP") or os.environ.get("TMP") or os.environ.get("TMPDIR") or "/tmp"
    return Path(base) / f"trellis-winlinux-{STAMP}"


WORK = default_work()

BOOTSTRAP_NEEDLES = (
    "get_context.py",
    "grill-with-docs",
    "task.py create",
    "--no-start",
)

ALL_OVERLAY = (
    ".claude/hooks/session-start.py",
    ".claude/hooks/inject-subagent-context.py",
    ".claude/commands/trellis/continue.md",
    ".claude/commands/trellis/finish-work.md",
    ".codex/config.toml",
    ".codex/hooks/session-start.py",
    ".codex/hooks/inject-subagent-context.py",
    ".codex/agents/trellis-check.toml",
    ".codex/agents/trellis-implement.toml",
    ".codex/agents/trellis-research.toml",
    ".agents/skills/trellis-start/SKILL.md",
    ".agents/skills/trellis-continue/SKILL.md",
    ".agents/skills/trellis-finish-work/SKILL.md",
    ".agents/skills/trellis-dual-review/SKILL.md",
    ".agents/skills/trellis-dual-review/dual_review.py",
    ".claude/commands/trellis/dual-review.md",
    ".grok/commands/trellis-start.md",
    ".grok/commands/trellis-continue.md",
    ".grok/commands/trellis-finish-work.md",
    ".grok/commands/trellis-dual-review.md",
    ".grok/commands/trellis-matt-deploy.md",
    ".trellis/workflow.md",
    "docs/agents/matt-flow.md",
    "docs/agents/issue-tracker.md",
    ".trellis/scripts/common/active_task.py",
    ".trellis/scripts/common/task_store.py",
)

results: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    results.append((name, bool(cond), detail))
    line = f"[{'PASS' if cond else 'FAIL'}] {name}"
    if detail and not cond:
        line += f"\n       {detail}"
    print(line, flush=True)


def command(cmd: list[str]) -> list[str]:
    """Run a .cmd through cmd.exe. Windows CreateProcess does not do that itself."""
    if os.name == "nt" and cmd and str(cmd[0]).lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/d", "/s", "/c", subprocess.list2cmdline([str(part) for part in cmd])]
    return [str(part) for part in cmd]


def same_path(printed: str, expected: Path | str) -> bool:
    left = printed.strip().strip('"')
    candidates = [left, left.replace("/", "\\"), left.replace("\\", "/")]
    if left.startswith("//"):
        candidates.append("\\\\" + left[2:].replace("/", "\\"))
    if len(left) >= 3 and left[0] == "/" and left[1].isalpha() and left[2] == "/":
        rest = left[3:].replace("/", "\\")
        candidates.append(f"{left[1].upper()}:\\{rest}")
        candidates.append(f"{left[1].upper()}:/{left[3:]}")

    def norm(value: str) -> str:
        try:
            return os.path.normcase(os.path.realpath(value))
        except OSError:
            return os.path.normcase(os.path.abspath(value))

    target = norm(str(expected))
    return any(norm(item) == target for item in candidates)


def line_value(out: str, prefix: str) -> str:
    for line in out.splitlines():
        if line.startswith(prefix):
            return line.split(": ", 1)[1].strip()
    return ""


def run(name: str, cmd: list[str], *, cwd: Path | None = None, env: dict | None = None) -> tuple[int, str]:
    log = WORK / "logs" / f"{name}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    argv = command(cmd)
    print(f"\n$ {' '.join(argv)}", flush=True)
    proc = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log.write_text(proc.stdout or "", encoding="utf-8")
    tail = (proc.stdout or "")[-2500:]
    print(tail, flush=True)
    print(f"(exit {proc.returncode}, log {log})", flush=True)
    return proc.returncode, proc.stdout or ""


def allow_dubious_git(env: dict[str, str]) -> None:
    """Process-local safe.directory so Windows git can read a WSL checkout.

    Does not write the user's git config. Linux git already owns the checkout.
    """
    if os.name != "nt":
        return
    try:
        count = int(env.get("GIT_CONFIG_COUNT", "0") or "0")
    except ValueError:
        count = 0
    for index in range(count):
        if env.get(f"GIT_CONFIG_KEY_{index}") == "safe.directory" and env.get(f"GIT_CONFIG_VALUE_{index}") == "*":
            return
    env["GIT_CONFIG_COUNT"] = str(count + 1)
    env[f"GIT_CONFIG_KEY_{count}"] = "safe.directory"
    env[f"GIT_CONFIG_VALUE_{count}"] = "*"


def base_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in (
        "TRELLIS_MATT_HOME",
        "TRELLIS_MATT_CLONE_DIR",
        "TRELLIS_MATT_REPO",
        "TRELLIS_MATT_BRANCH",
        "TRELLIS_MATT_PLATFORM",
        "TRELLIS_MATT_PYTHON",
    ):
        env.pop(key, None)
    allow_dubious_git(env)
    env.setdefault("GIT_AUTHOR_NAME", "oneclick")
    env.setdefault("GIT_AUTHOR_EMAIL", "oneclick@example.invalid")
    env.setdefault("GIT_COMMITTER_NAME", "oneclick")
    env.setdefault("GIT_COMMITTER_EMAIL", "oneclick@example.invalid")
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    env.setdefault("CI", "1")
    env.setdefault("NPM_CONFIG_UPDATE_NOTIFIER", "false")
    return env


def assert_bootstrap(project: Path, label: str) -> None:
    for filename in ("AGENTS.md", "CLAUDE.md"):
        path = project / filename
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        missing = [needle for needle in BOOTSTRAP_NEEDLES if needle not in text]
        check(
            f"{label} {filename} has grill/get_context/--no-start bootstrap",
            path.is_file() and not missing,
            f"missing file" if not path.is_file() else f"missing {missing}",
        )


def assert_overlay(project: Path, label: str) -> None:
    missing = [rel for rel in ALL_OVERLAY if not (project / rel).is_file()]
    check(f"{label} Claude, Codex, and Grok overlay files exist", not missing, ", ".join(missing))
    active = project / ".trellis/scripts/common/active_task.py"
    check(
        f"{label} active_task.py reads GROK_SESSION_ID",
        active.is_file() and "GROK_SESSION_ID" in active.read_text(encoding="utf-8"),
    )
    workflow = project / ".trellis/workflow.md"
    phase = ""
    if (project / ".trellis/scripts/get_context.py").is_file():
        phase = subprocess.check_output(
            [sys.executable, ".trellis/scripts/get_context.py", "--mode", "phase"],
            cwd=project,
            text=True, encoding="utf-8", errors="replace",
        )
    folded = " ".join(phase.split())
    check(
        f"{label} get_context phase mentions an explicit Matt skill",
        "explicitly invokes a Matt skill" in folded,
        folded[:240],
    )



def assert_dual_review(project: Path, label: str, *, claude: bool = False, grok: bool = False, codefree_o: bool = False) -> None:
    skill = project / ".agents/skills/trellis-dual-review/SKILL.md"
    helper = project / ".agents/skills/trellis-dual-review/dual_review.py"
    check(f"{label} dual-review skill exists", skill.is_file(), str(skill))
    check(f"{label} dual-review helper exists", helper.is_file(), str(helper))
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        check(f"{label} dual-review skill names both reviewers", "aaaaa495-296c-45b3-82c2-0fa9211be10f" in text and "grok-4.7" in text)
    for filename in ("AGENTS.md", "CLAUDE.md"):
        path = project / filename
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        check(
            f"{label} {filename} has the dual-review block",
            "<!-- TRELLIS-GROK:DUAL-REVIEW-START -->" in text and "dual_review.py prepare" in text,
            "missing block" if path.is_file() else "missing file",
        )
    if claude:
        check(
            f"{label} Claude dual-review command exists",
            (project / ".claude/commands/trellis/dual-review.md").is_file(),
        )
    if grok:
        check(
            f"{label} Grok dual-review command exists",
            (project / ".grok/commands/trellis-dual-review.md").is_file(),
        )
    if codefree_o:
        check(
            f"{label} codefree-o dual-review command exists",
            (project / ".codefree-o/command/trellis-dual-review.md").is_file(),
        )
    if helper.is_file():
        code, out = run(
            f"{label}-dual-review-self-test",
            [sys.executable, str(helper), "self-test"],
            cwd=project,
        )
        check(f"{label} dual-review self-test exits 0", code == 0, out[-400:])
        code, out = run(
            f"{label}-dual-review-verify",
            [sys.executable, str(helper), "verify-install", str(project)],
            cwd=project,
        )
        check(f"{label} dual-review verify-install exits 0", code == 0, out[-400:])


def assert_matt_skills(project: Path, label: str) -> None:
    lock = project / "skills-lock.json"
    text = lock.read_text(encoding="utf-8") if lock.is_file() else ""
    check(f"{label} skills-lock.json records mattpocock/skills", "mattpocock/skills" in text)
    check(f"{label} skills-lock.json records grill-with-docs", "grill-with-docs" in text)
    expected = {
        "claude": project / ".claude/skills/grill-with-docs/SKILL.md",
        "codex": project / ".agents/skills/grill-with-docs/SKILL.md",
        "grok": project / ".grok/skills/grill-with-docs/SKILL.md",
    }
    for agent, path in expected.items():
        check(f"{label} Matt grill-with-docs installed for {agent}", path.is_file(), str(path))


def snapshot_repo(dest: Path, env: dict[str, str]) -> None:
    """Commit the current worktree, including uncommitted installer files, on a temp branch."""
    if dest.exists():
        shutil.rmtree(dest)
    subprocess.check_call(
        ["git", "clone", "--branch", "grok", str(ROOT), str(dest)],
        stdout=subprocess.DEVNULL,
    )
    status = subprocess.check_output(
        ["git", "-C", str(ROOT), "status", "--porcelain", "-uall"],
        text=True, encoding="utf-8", errors="replace",
    )
    for line in status.splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        src = ROOT / path
        target = dest / path
        if not src.exists() and not src.is_symlink():
            if target.exists() or target.is_symlink():
                if target.is_dir() and not target.is_symlink():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or target.exists():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        if src.is_symlink():
            target.symlink_to(os.readlink(src))
        elif src.is_dir():
            shutil.copytree(src, target, symlinks=True)
        else:
            shutil.copy2(src, target)
    subprocess.check_call(["git", "add", "-A"], cwd=dest, env=env)
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=dest, text=True, encoding="utf-8", errors="replace", env=env)
    if dirty.strip():
        subprocess.check_call(
            ["git", "-c", "commit.gpgsign=false", "commit", "-m", "snapshot for from-github test"],
            cwd=dest,
            env=env,
        )


def main() -> int:
    allow_dubious_git(os.environ)
    WORK.mkdir(parents=True, exist_ok=True)
    print(f"workdir: {WORK}", flush=True)
    env = base_env()
    bindir = WORK / "bin"
    shortcut_env = env.copy()
    shortcut_env["XDG_BIN_HOME"] = str(bindir)
    shortcut_env["PATH"] = str(bindir) + os.pathsep + shortcut_env.get("PATH", "")
    code, out = run("shortcut", [str(SHORTCUT), "--home", str(ROOT)], env=shortcut_env)
    if os.name == "nt":
        check("shortcut install exits 0", code == 0, out[-800:])
        check("shortcut writes trellis-matt.cmd", (bindir / "trellis-matt.cmd").is_file())
        check("shortcut writes trellis-matt.ps1", (bindir / "trellis-matt.ps1").is_file())
        shim = bindir / "trellis-matt.cmd"
    else:
        check("shortcut install exits 0", code == 0, out[-800:])
        check("shortcut symlinks trellis-matt", (bindir / "trellis-matt").is_symlink())
        shim = bindir / "trellis-matt"
    code, out = run("shortcut-help", [str(shim), "--help"], env=shortcut_env)
    check("shortcut command runs --help", code == 0 and "trellis-matt install" in out, out[-800:])

    remotes_before = subprocess.check_output(["git", "-C", str(ROOT), "remote", "-v"], text=True, encoding="utf-8", errors="replace")

    local = WORK / "local"
    code, out = run(
        "local-install",
        [str(ONECLICK), str(local), "-u", "oneclick", "--claude", "--codex", "--grok"],
        env=env,
    )
    check("local oneclick install exits 0", code == 0, out[-800:])
    check(
        "local install uses this checkout as the source",
        same_path(line_value(out, "source checkout: "), ROOT),
        line_value(out, "source checkout: ") or out[-800:],
    )
    if local.is_dir():
        assert_overlay(local, "local")
        assert_bootstrap(local, "local")
        assert_matt_skills(local, "local")
        assert_dual_review(local, "local", claude=True, grok=True)
        code, out = run("local-apply", [str(CLI), "apply", str(local)], env=env)
        check("apply on a fresh install exits 0", code == 0, out[-800:])
        check("apply reports script patches already applied", "already applied" in out, out[-800:])
        assert_bootstrap(local, "after apply")
        assert_dual_review(local, "after apply", claude=True, grok=True)
        code, _ = run("local-status", [str(CLI), "status", str(local)], env=env)
        check("status exits 0", code == 0)
        code, _ = run("local-dry-run", [str(CLI), "dry-run", str(local)], env=env)
        check("dry-run exits 0", code == 0)
        code, out = run(
            "local-reinstall",
            [str(CLI), "install", str(local), "-u", "oneclick", "--claude", "--codex", "--grok", "--no-skills"],
            env=env,
        )
        check("second install skips trellis init and exits 0", code == 0 and "skipping trellis init" in out, out[-800:])
        assert_bootstrap(local, "reinstall")
        assert_dual_review(local, "reinstall", claude=True, grok=True)

    snapshot = WORK / "snapshot-repo"
    snapshot_repo(snapshot, env)
    clone_dir = WORK / "github-src"
    github = WORK / "github"
    github_env = env.copy()
    github_env["TRELLIS_MATT_CLONE_DIR"] = str(clone_dir)
    github_env["TRELLIS_MATT_REPO"] = str(snapshot)
    code, out = run(
        "github-install",
        [
            str(ONECLICK),
            str(github),
            "-u",
            "oneclick",
            "--from-github",
            "--claude",
            "--codex",
            "--grok",
        ],
        env=github_env,
    )
    check("local-repo --from-github install exits 0", code == 0, out[-800:])
    origin = ""
    head = ""
    if (clone_dir / ".git").exists():
        origin = subprocess.check_output(["git", "-C", str(clone_dir), "remote", "get-url", "origin"], text=True, encoding="utf-8", errors="replace").strip()
        head = subprocess.check_output(["git", "-C", str(clone_dir), "rev-parse", "HEAD"], text=True, encoding="utf-8", errors="replace").strip()
    check("clone origin is the local snapshot", same_path(origin, snapshot), origin)
    source_line = line_value(out, "source checkout: ")
    check(
        "from-github install source checkout is the clone, not the source tree",
        bool(source_line) and same_path(source_line, clone_dir) and not same_path(source_line, ROOT),
        source_line or out[-800:],
    )
    check("clone HEAD is recorded", bool(head), head)
    if github.is_dir() and clone_dir.is_dir():
        assert_overlay(github, "github")
        assert_bootstrap(github, "github")
        assert_matt_skills(github, "github")
        assert_dual_review(github, "github", claude=True, grok=True)
        same = (github / ".trellis/workflow.md").read_bytes() == (clone_dir / ".trellis/workflow.md").read_bytes()
        check("github project workflow.md matches the snapshot clone", same)

    published = WORK / "published-grok"
    pub_code, pub_out = run(
        "published-clone",
        ["git", "clone", "--depth", "1", "--branch", "grok", GITHUB + ".git", str(published)],
        env=env,
    )
    pub_head = ""
    pub_origin = ""
    if pub_code == 0 and (published / ".git").exists():
        pub_head = subprocess.check_output(["git", "-C", str(published), "rev-parse", "HEAD"], text=True, encoding="utf-8", errors="replace").strip()
        pub_origin = subprocess.check_output(
            ["git", "-C", str(published), "remote", "get-url", "origin"],
            text=True, encoding="utf-8", errors="replace",
        ).strip()
    windows_on_origin = (published / "scripts" / "grok-fixes" / "invoke-git-bash.cmd").is_file()
    check(
        "published origin/grok clones and HEAD is recorded (not a Windows-file pass)",
        pub_code == 0 and pub_origin.rstrip("/").removesuffix(".git") == GITHUB and bool(pub_head),
        f"origin={pub_origin} HEAD={pub_head} windows_launcher_on_origin={windows_on_origin}\n{pub_out[-500:]}",
    )
    print(
        f"published grok HEAD: {pub_head or 'clone failed'}; "
        f"windows launcher on origin: {windows_on_origin}",
        flush=True,
    )

    claude_only = WORK / "claude-only"
    code, out = run(
        "claude-only",
        [str(CLI), "install", str(claude_only), "-u", "oneclick", "--claude", "--no-skills"],
        env=env,
    )
    check("claude-only install exits 0", code == 0, out[-800:])
    if claude_only.is_dir():
        check("claude-only has the Claude hook", (claude_only / ".claude/hooks/session-start.py").is_file())
        check("claude-only does not create .grok", not (claude_only / ".grok").exists())
        check("claude-only does not create .codex", not (claude_only / ".codex").exists())
        check("claude-only does not create .codefree-o", not (claude_only / ".codefree-o").exists())
        check("claude-only does not create .opencode", not (claude_only / ".opencode").exists())
        check("claude-only skips Matt skills", not (claude_only / "skills-lock.json").exists())
        assert_bootstrap(claude_only, "claude-only")
        assert_dual_review(claude_only, "claude-only", claude=True)
        check(
            "claude-only has no Grok dual-review command",
            not (claude_only / ".grok/commands/trellis-dual-review.md").exists(),
        )
        check(
            "claude-only has no codefree-o dual-review command",
            not (claude_only / ".codefree-o/command/trellis-dual-review.md").exists(),
        )

    legacy = WORK / "legacy-init"
    code, out = run(
        "legacy-init",
        [str(CLI), "init", str(legacy), "-u", "oneclick"],
        env=env,
    )
    check("legacy init exits 0", code == 0, out[-800:])
    if legacy.is_dir():
        check("legacy init still passes --grok", "--grok" in out)
        check("legacy init copies the Grok start command", (legacy / ".grok/commands/trellis-start.md").is_file())
        check("legacy init does not copy the Codex overlay", not (legacy / ".codex/config.toml").exists())
        check(
            "legacy init does not install Matt skills",
            not (legacy / "skills-lock.json").exists() and "--- npx skills" not in out,
        )
        assert_bootstrap(legacy, "legacy init")

    remotes_after = subprocess.check_output(["git", "-C", str(ROOT), "remote", "-v"], text=True, encoding="utf-8", errors="replace")
    check("source checkout remotes are unchanged", remotes_before == remotes_after)

    failed = [name for name, ok, _ in results if not ok]
    print(f"\noneclick: {len(results) - len(failed)}/{len(results)} passed")
    print(f"workdir: {WORK}")
    if head:
        print(f"github clone HEAD: {head}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
