#!/usr/bin/env python3
"""End-to-end checks for trellis-grok install.

Creates /home/samiya/tmp/trellis-oneclick-<timestamp>/ and never touches the
source checkout or other projects. Exits 0 only when every check passes.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "grok-fixes" / "trellis-grok"
ONECLICK = ROOT / "scripts" / "grok-fixes" / "oneclick.sh"
STAMP = time.strftime("%Y%m%d-%H%M%S")
WORK = Path(f"/home/samiya/tmp/trellis-oneclick-{STAMP}")
GITHUB = "https://github.com/samiya782/trellis-workflow"

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
    ".grok/commands/trellis-start.md",
    ".grok/commands/trellis-continue.md",
    ".grok/commands/trellis-finish-work.md",
    ".grok/commands/trellis-grok-deploy.md",
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


def run(name: str, cmd: list[str], *, cwd: Path | None = None, env: dict | None = None) -> tuple[int, str]:
    log = WORK / "logs" / f"{name}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    print(f"\n$ {' '.join(cmd)}", flush=True)
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log.write_text(proc.stdout or "")
    tail = (proc.stdout or "")[-2500:]
    print(tail, flush=True)
    print(f"(exit {proc.returncode}, log {log})", flush=True)
    return proc.returncode, proc.stdout or ""


def base_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("TRELLIS_GROK_HOME", None)
    env.setdefault("GIT_AUTHOR_NAME", "oneclick")
    env.setdefault("GIT_AUTHOR_EMAIL", "oneclick@example.invalid")
    env.setdefault("GIT_COMMITTER_NAME", "oneclick")
    env.setdefault("GIT_COMMITTER_EMAIL", "oneclick@example.invalid")
    return env


def assert_bootstrap(project: Path, label: str) -> None:
    for filename in ("AGENTS.md", "CLAUDE.md"):
        path = project / filename
        text = path.read_text() if path.is_file() else ""
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
        active.is_file() and "GROK_SESSION_ID" in active.read_text(),
    )
    workflow = project / ".trellis/workflow.md"
    phase = ""
    if (project / ".trellis/scripts/get_context.py").is_file():
        phase = subprocess.check_output(
            [sys.executable, ".trellis/scripts/get_context.py", "--mode", "phase"],
            cwd=project,
            text=True,
        )
    folded = " ".join(phase.split())
    check(
        f"{label} get_context phase mentions an explicit Matt skill",
        "explicitly invokes a Matt skill" in folded,
        folded[:240],
    )


def assert_matt_skills(project: Path, label: str) -> None:
    lock = project / "skills-lock.json"
    text = lock.read_text() if lock.is_file() else ""
    check(f"{label} skills-lock.json records mattpocock/skills", "mattpocock/skills" in text)
    check(f"{label} skills-lock.json records grill-with-docs", "grill-with-docs" in text)
    expected = {
        "claude": project / ".claude/skills/grill-with-docs/SKILL.md",
        "codex": project / ".agents/skills/grill-with-docs/SKILL.md",
        "grok": project / ".grok/skills/grill-with-docs/SKILL.md",
    }
    for agent, path in expected.items():
        check(f"{label} Matt grill-with-docs installed for {agent}", path.is_file(), str(path))


def main() -> int:
    WORK.mkdir(parents=True)
    print(f"workdir: {WORK}", flush=True)
    env = base_env()
    remotes_before = subprocess.check_output(["git", "-C", str(ROOT), "remote", "-v"], text=True)

    local = WORK / "local"
    code, out = run(
        "local-install",
        [str(ONECLICK), str(local), "-u", "oneclick", "--claude", "--codex", "--grok"],
        env=env,
    )
    check("local oneclick install exits 0", code == 0, out[-800:])
    check(
        "local install uses this checkout as the source",
        f"source checkout: {ROOT}" in out,
        out[-800:],
    )
    if local.is_dir():
        assert_overlay(local, "local")
        assert_bootstrap(local, "local")
        assert_matt_skills(local, "local")
        code, out = run("local-apply", [str(CLI), "apply", str(local)], env=env)
        check("apply on a fresh install exits 0", code == 0, out[-800:])
        check("apply reports script patches already applied", "already applied" in out, out[-800:])
        assert_bootstrap(local, "after apply")
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

    clone_dir = WORK / "github-src"
    github = WORK / "github"
    github_env = env.copy()
    github_env["TRELLIS_GROK_CLONE_DIR"] = str(clone_dir)
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
    check("github oneclick install exits 0", code == 0, out[-800:])
    check("github install cloned the requested repository", "github.com/samiya782/trellis-workflow" in out, out[-500:])
    origin = ""
    head = ""
    if (clone_dir / ".git").exists():
        origin = subprocess.check_output(["git", "-C", str(clone_dir), "remote", "get-url", "origin"], text=True).strip()
        head = subprocess.check_output(["git", "-C", str(clone_dir), "rev-parse", "HEAD"], text=True).strip()
    check("clone origin is the GitHub repository", origin.rstrip("/").removesuffix(".git") == GITHUB, origin)
    source_line = ""
    for line in out.splitlines():
        if line.startswith("source checkout: "):
            source_line = line.split(": ", 1)[1].strip()
    check(
        "github install source checkout is the clone, not ~/trellis",
        bool(source_line)
        and os.path.realpath(source_line) == os.path.realpath(clone_dir)
        and os.path.realpath(source_line) != os.path.realpath(ROOT),
        source_line or out[-800:],
    )
    check("clone HEAD is recorded", bool(head), head)
    if github.is_dir() and clone_dir.is_dir():
        assert_overlay(github, "github")
        assert_bootstrap(github, "github")
        assert_matt_skills(github, "github")
        same = (github / ".trellis/workflow.md").read_bytes() == (clone_dir / ".trellis/workflow.md").read_bytes()
        check("github project workflow.md matches the GitHub clone", same)

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
        check("claude-only skips Matt skills", not (claude_only / "skills-lock.json").exists())
        assert_bootstrap(claude_only, "claude-only")

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

    remotes_after = subprocess.check_output(["git", "-C", str(ROOT), "remote", "-v"], text=True)
    check("source checkout remotes are unchanged", remotes_before == remotes_after)

    failed = [name for name, ok, _ in results if not ok]
    print(f"\noneclick: {len(results) - len(failed)}/{len(results)} passed")
    print(f"workdir: {WORK}")
    if head:
        print(f"github clone HEAD: {head}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
