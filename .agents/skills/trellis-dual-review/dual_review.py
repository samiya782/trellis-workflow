#!/usr/bin/env python3
"""Prepare dual-review prompts. Works on Windows, WSL, and Linux."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
SKILL_REL = Path(".agents") / "skills" / "trellis-dual-review" / "SKILL.md"
HELPER_REL = Path(".agents") / "skills" / "trellis-dual-review" / "dual_review.py"
DEFAULT_OUT = Path(".trellis") / ".runtime" / "dual-review"

SKILL_NEEDLES = (
    "trellis-dual-review",
    "aaaaa495-296c-45b3-82c2-0fa9211be10f",
    "grok-4.7",
    "xhigh",
    "Must",
    "Should",
    "same tip",
)


def die(message: str, code: int = 2) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def resolve_sha(repo: Path | None, ref: str) -> str:
    text = (ref or "").strip()
    if SHA_RE.match(text):
        return text.lower()
    if repo is None or not (repo / ".git").exists() and not (repo / ".git").is_file():
        # Also accept a work tree whose .git is a file (worktrees) or missing.
        if repo is not None:
            git_dir = repo / ".git"
            if not git_dir.exists():
                die(f"not a full 40-character SHA and no git repo at {repo}: {ref}")
        else:
            die(f"not a full 40-character SHA: {ref}")
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "--verify", text + "^{commit}"],
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.STDOUT,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        detail = ""
        if isinstance(exc, subprocess.CalledProcessError):
            detail = (exc.output or "").strip()
        die(f"cannot resolve {ref!r} to a commit" + (f": {detail}" if detail else ""))
    sha = out.strip().splitlines()[-1].strip()
    if not SHA_RE.match(sha):
        die(f"git rev-parse returned a non-SHA for {ref!r}: {sha}")
    return sha.lower()


def render_eggbot(
    *,
    pr: str,
    url: str,
    branch: str,
    tip: str,
    base: str,
    implementer: str,
    background: str,
    claimed_cause: str,
    prev_must: str,
) -> str:
    lines = [
        f"请交叉审查 PR #{pr}（独立 Must/Should，不要合、不要改代码、不要在 GitHub 留言除非发现 Must 需要钉在 PR 上）。",
        "",
        f"- PR: {url}",
        f"- 分支: {branch}",
        f"- tip: {tip}",
        f"- base: main {base}",
        f"- 实现代理: {implementer or '（未提供）'}",
        "",
        f"背景：{background}。实现方称根因是 {claimed_cause}。请你独立核实，并按 Must / Should 回报。",
    ]
    if prev_must.strip():
        lines.append(f"上次 Must 是 {prev_must.strip()}，请核实是否修好、是否引入新问题。")
    return "\n".join(lines) + "\n"


def render_grok(
    *,
    pr: str,
    url: str,
    branch: str,
    tip: str,
    base: str,
    background: str,
    claimed_cause: str,
    banned: str,
    prev_must: str,
) -> str:
    lines = [
        f"READ-ONLY review of PR #{pr} on {url}. Do not modify files, do not commit, do not push, and do not merge or comment on GitHub. If a branch is created, leave it with zero new commits.",
        "",
        f"Review tip {tip} (branch {branch}) against base main {base}.",
        "",
        f"This is a generic fix for {background}. The implementer says {claimed_cause}. Verify independently; you may discard that explanation.",
        "",
        "Output a structured review in Chinese with:",
        "1) exact commit reviewed",
        "2) Must findings (ship-blocking), each with file/path evidence",
        "3) Should findings (non-blocking), same standard",
        "4) what looks solid",
        f"Do not implement fixes. Do not propose changing {banned}.",
    ]
    if prev_must.strip():
        lines.append("")
        lines.append(
            f"Previous Must findings were: {prev_must.strip()}. "
            "Verify whether they are fixed and whether any new issues were introduced."
        )
    return "\n".join(lines) + "\n"


def render_checklist(
    *,
    tip: str,
    base: str,
    eggbot_path: Path,
    grok_path: Path,
) -> str:
    return (
        f"tip: {tip}\n"
        f"base: {base}\n"
        f"eggbot prompt: {eggbot_path}\n"
        f"grok prompt: {grok_path}\n"
        "\n"
        "Gate (all four, or do not merge):\n"
        "1. Both reviewers report no Must findings on this same tip.\n"
        "2. CI is green and mergeable_state is clean, when the project has CI.\n"
        "3. Local retest of the original failure passes; the default path still works.\n"
        "4. Squash-merge only when the user has authorized the merge. Should does not block.\n"
        "\n"
        "If you cannot reach @dr eggbot or a Grok CloudAgent, give the user these\n"
        "prompt files and stop. Do not claim the review ran.\n"
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def cmd_prepare(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve() if args.repo else Path.cwd()
    tip = resolve_sha(repo, args.tip)
    base = resolve_sha(repo, args.base)
    outdir = Path(args.outdir).resolve() if args.outdir else (repo / DEFAULT_OUT)
    outdir.mkdir(parents=True, exist_ok=True)
    egg_path = outdir / "eggbot-prompt.md"
    grok_path = outdir / "grok-review-prompt.md"
    check_path = outdir / "checklist.md"
    banned = args.banned.strip() or (
        "the project's banned items (read them from AGENTS.md / this skill; "
        "do not invent any)"
    )
    write_text(
        egg_path,
        render_eggbot(
            pr=args.pr,
            url=args.url,
            branch=args.branch,
            tip=tip,
            base=base,
            implementer=args.implementer,
            background=args.background,
            claimed_cause=args.claimed_cause,
            prev_must=args.prev_must,
        ),
    )
    write_text(
        grok_path,
        render_grok(
            pr=args.pr,
            url=args.url,
            branch=args.branch,
            tip=tip,
            base=base,
            background=args.background,
            claimed_cause=args.claimed_cause,
            banned=banned,
            prev_must=args.prev_must,
        ),
    )
    write_text(
        check_path,
        render_checklist(tip=tip, base=base, eggbot_path=egg_path, grok_path=grok_path),
    )
    for path in (egg_path, grok_path):
        text = path.read_text(encoding="utf-8")
        if tip not in text:
            die(f"{path} is missing the tip SHA")
        if base not in text:
            die(f"{path} is missing the base SHA")
    print(f"tip: {tip}")
    print(f"base: {base}")
    print(f"wrote: {egg_path}")
    print(f"wrote: {grok_path}")
    print(f"wrote: {check_path}")
    return 0


def cmd_verify_install(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    missing = []
    for rel in (SKILL_REL, HELPER_REL):
        if not (root / rel).is_file():
            missing.append(str(rel))
    if missing:
        print("FAIL: missing " + ", ".join(missing))
        return 1
    skill = (root / SKILL_REL).read_text(encoding="utf-8")
    absent = [needle for needle in SKILL_NEEDLES if needle not in skill]
    if absent:
        print("FAIL: SKILL.md missing " + ", ".join(absent))
        return 1
    print(f"OK: dual-review skill and helper are in {root}")
    return 0


def cmd_selftest(args: argparse.Namespace) -> int:
    tip = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    base = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    outdir = Path(args.outdir).resolve() if args.outdir else Path(tempfile.mkdtemp(prefix="dual-review-selftest-"))
    ns = argparse.Namespace(
        repo=str(outdir),  # no git repo; SHAs are already full
        tip=tip,
        base=base,
        pr="0",
        url="https://example.invalid/pr/0",
        branch="topic",
        implementer="https://cursor.com/agents/bc-example",
        background="example failure: the installer wrote a GBK file on Windows",
        claimed_cause="open() used the locale encoding",
        banned="do not force-push; do not merge unless authorized",
        prev_must="AGENTS.md lost the grill block",
        outdir=str(outdir),
    )
    # Bypass git resolution by passing full SHAs and a repo path without .git.
    # resolve_sha accepts a 40-char SHA without git.
    rc = cmd_prepare(ns)
    if rc != 0:
        return rc
    egg = (outdir / "eggbot-prompt.md").read_text(encoding="utf-8")
    grok = (outdir / "grok-review-prompt.md").read_text(encoding="utf-8")
    check = (outdir / "checklist.md").read_text(encoding="utf-8")
    problems = []
    for label, text in (("eggbot", egg), ("grok", grok)):
        if tip not in text:
            problems.append(f"{label} missing tip")
        if base not in text:
            problems.append(f"{label} missing base")
    if "Must / Should" not in egg:
        problems.append("eggbot missing Must / Should")
    if "上次 Must" not in egg:
        problems.append("eggbot missing re-review line")
    if "Do not implement fixes" not in grok:
        problems.append("grok missing read-only rule")
    if "do not force-push" not in grok:
        problems.append("grok missing banned items")
    if "Previous Must findings" not in grok:
        problems.append("grok missing re-review line")
    if "Both reviewers report no Must findings" not in check:
        problems.append("checklist missing gate")
    if problems:
        print("FAIL: " + "; ".join(problems))
        return 1
    print(f"OK: self-test wrote prompts in {outdir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare or verify trellis-matt dual-review prompts.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    prepare = sub.add_parser("prepare", help="Write the two reviewer prompts and a checklist")
    prepare.add_argument("--repo", default=".", help="Git checkout used to resolve refs (default: cwd)")
    prepare.add_argument("--tip", required=True, help="Tip ref or 40-character SHA")
    prepare.add_argument("--base", default="main", help="Base ref or SHA (default: main)")
    prepare.add_argument("--pr", default="?", help="PR number")
    prepare.add_argument("--url", default="(no PR URL)", help="PR URL")
    prepare.add_argument("--branch", default="HEAD", help="Branch name")
    prepare.add_argument("--implementer", default="", help="Implementer agent URL")
    prepare.add_argument("--background", default="(not provided)", help="Failure or change under review")
    prepare.add_argument("--claimed-cause", default="(not provided)", help="Implementer's claimed root cause")
    prepare.add_argument("--banned", default="", help="Project banned items, pasted into the Grok prompt")
    prepare.add_argument("--prev-must", default="", help="Previous Must findings, for a re-review")
    prepare.add_argument("--outdir", default="", help=f"Output directory (default: {DEFAULT_OUT})")
    prepare.set_defaults(func=cmd_prepare)

    verify = sub.add_parser("verify-install", help="Check that the skill landed in a project")
    verify.add_argument("project", nargs="?", default=".", help="Project directory (default: cwd)")
    verify.set_defaults(func=cmd_verify_install)

    selftest = sub.add_parser("self-test", help="Write dummy prompts and check their contents")
    selftest.add_argument("--outdir", default="", help="Optional output directory")
    selftest.set_defaults(func=cmd_selftest)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
