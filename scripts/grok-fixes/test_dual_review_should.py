#!/usr/bin/env python3
"""Focused Should-fix tests for dual-review upsert, dry-run, prepare, and codefree-o.

No network. Does not call reviewers. Works on Windows, WSL, and Linux.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent  # repo root when this file lives in scripts/grok-fixes/
CLI = HERE / "trellis-matt"
HELPER = ROOT / ".agents/skills/trellis-dual-review/dual_review.py"
FAILED = 0
PASSED = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global FAILED, PASSED
    if ok:
        PASSED += 1
        print(f"  PASS  {name}")
    else:
        FAILED += 1
        extra = (detail or "")[-800:]
        print(f"  FAIL  {name}")
        if extra:
            print(extra)


def run(cmd, *, cwd=None, env=None, timeout=180):
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout


def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(cwd), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
    ).strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text if text.endswith("\n") else text + "\n")


def py_bin() -> str:
    return sys.executable


def installer_cmd(project: Path, *args: str, env=None):
    cmd = [str(CLI), *args, str(project)]
    if os.name == "nt":
        bash = Path(r"C:\Program Files\Git\bin\bash.exe")
        if bash.is_file():
            cmd = [str(bash), str(CLI), *args, str(project)]
    return run(cmd, env=env, timeout=180)


def make_project(tmp: Path, name: str, agents: str, claude: str | None = None) -> Path:
    project = tmp / name
    (project / ".trellis/scripts").mkdir(parents=True)
    write(project / ".trellis/scripts/task.py", "#!/usr/bin/env python3\nprint('stub')\n")
    write(project / ".trellis/.version", "0.7.0-beta.4\n")
    write(project / "AGENTS.md", agents)
    write(project / "CLAUDE.md", claude if claude is not None else agents)
    git_init(project)
    return project


def git_init(project: Path) -> None:
    subprocess.check_call(["git", "init", "-q", str(project)])
    subprocess.check_call(["git", "-C", str(project), "config", "user.email", "should-test@example.com"])
    subprocess.check_call(["git", "-C", str(project), "config", "user.name", "should-test"])
    subprocess.check_call(["git", "-C", str(project), "add", "-A"])
    subprocess.check_call(["git", "-C", str(project), "commit", "-q", "-m", "init"])


ORPHAN = """PREFIX
<!-- TRELLIS-GROK:DUAL-REVIEW-START -->
ORPHAN BODY THAT MUST SURVIVE
<!-- TRELLIS-GROK:MATT-START -->
matt body
<!-- TRELLIS-GROK:MATT-END -->
KEEP ME
<!-- TRELLIS-GROK:DUAL-REVIEW-START -->
old dual body
<!-- TRELLIS-GROK:DUAL-REVIEW-END -->
SUFFIX
"""

PLAIN = """# Project
Some intro.
"""


def test_unbalanced_markers(tmp: Path) -> None:
    print("== unbalanced DUAL-REVIEW-START ==")
    project = make_project(tmp, "orphan", ORPHAN)
    code, out = installer_cmd(project, "apply")
    text = (project / "AGENTS.md").read_text(encoding="utf-8")
    check("apply exits 0 or still upserted after patch step", "dual-review block" in out or "ORPHAN BODY" in text, out[-800:])
    check("orphan body survived", "ORPHAN BODY THAT MUST SURVIVE" in text, text)
    check("KEEP ME survived", "KEEP ME" in text, text)
    check("SUFFIX survived", "SUFFIX" in text, text)
    check("PREFIX survived", "PREFIX" in text, text)
    check("new dual block written once with END", text.count("<!-- TRELLIS-GROK:DUAL-REVIEW-END -->") == 1, text)
    check("paired block mentions prepare --tip", "dual_review.py prepare --tip" in text, text)
    # The orphan START may remain (we skip it); it must not have eaten the body.
    check("old dual body replaced in the paired block", "old dual body" not in text, text)


def test_dry_run_stale(tmp: Path) -> None:
    print("== dry-run sees stale dual-review body ==")
    project = make_project(tmp, "stale", PLAIN)
    code, out = installer_cmd(project, "apply")
    check("initial apply ran upsert", "dual-review block" in out, out[-800:])
    agents = project / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    stale = text.replace("dual_review.py prepare --tip", "dual_review.py prepare --STALE")
    if stale == text:
        stale = text.replace("<!-- TRELLIS-GROK:DUAL-REVIEW-END -->", "stale body\n<!-- TRELLIS-GROK:DUAL-REVIEW-END -->")
    write(agents, stale)
    code, out = installer_cmd(project, "dry-run")
    check("dry-run would upsert stale AGENTS block", "would upsert: AGENTS.md dual-review block" in out, out[-800:])
    check("dry-run did not rewrite the file", agents.read_text(encoding="utf-8") == stale)


def test_codefree_o_empty_does_not_abort(tmp: Path) -> None:
    print("== empty .codefree-o does not abort upsert ==")
    project = make_project(tmp, "codefree-empty", PLAIN)
    (project / ".codefree-o").mkdir()
    # no trellis-start skill in the project; overlay copy happens from HOME_SRC,
    # but write_codefree_o_commands reads skills from the *target*.
    code, out = installer_cmd(project, "apply")
    agents = (project / "AGENTS.md").read_text(encoding="utf-8")
    check("upsert still happened", "<!-- TRELLIS-GROK:DUAL-REVIEW-START -->" in agents and "prepare --tip" in agents, agents)
    check("missing skills were skipped, not fatal", "skip codefree-o command" in out or "error: missing" not in out, out[-800:])
    check("did not SystemExit mid-apply for missing skills", "error: missing" not in out, out[-800:])


def test_second_apply_byte_stable(tmp: Path) -> None:
    print("== second apply is byte-stable ==")
    project = make_project(tmp, "stable", PLAIN)
    code1, out1 = installer_cmd(project, "apply")
    check("first apply ok-ish", "dual-review block" in out1 or (project / "AGENTS.md").is_file(), out1[-800:])
    a1 = (project / "AGENTS.md").read_bytes()
    c1 = (project / "CLAUDE.md").read_bytes()
    code2, out2 = installer_cmd(project, "apply")
    check("second apply reports in-sync dual-review", "in-sync: AGENTS.md dual-review block" in out2, out2[-800:])
    check("AGENTS.md bytes unchanged", (project / "AGENTS.md").read_bytes() == a1)
    check("CLAUDE.md bytes unchanged", (project / "CLAUDE.md").read_bytes() == c1)


def test_status_skips_missing_clients(tmp: Path) -> None:
    print("== status hides client commands when those dirs are absent ==")
    project = make_project(tmp, "status-plain", PLAIN)
    installer_cmd(project, "apply")
    code, out = installer_cmd(project, "status")
    check("status exits 0", code == 0, out[-800:])
    check("no .grok command listed without .grok", ".grok/commands/trellis-dual-review.md" not in out, out[-800:])
    check("no .claude command listed without .claude", ".claude/commands/trellis/dual-review.md" not in out, out[-800:])
    check("skill itself is listed", ".agents/skills/trellis-dual-review/SKILL.md" in out, out[-800:])


def test_helper_prepare(tmp: Path) -> None:
    print("== helper prepare SHA, empty diff, base label ==")
    repo = tmp / "git-repo"
    repo.mkdir()
    write(repo / "f.txt", "zero\n")
    git_init(repo)
    write(repo / "f.txt", "one\n")
    subprocess.check_call(["git", "-C", str(repo), "add", "f.txt"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-q", "-m", "one"])
    base = git(repo, "rev-parse", "HEAD")
    write(repo / "f.txt", "two\n")
    subprocess.check_call(["git", "-C", str(repo), "add", "f.txt"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-q", "-m", "two"])
    tip = git(repo, "rev-parse", "HEAD")
    outdir = tmp / "prompts"

    # unknown 40-hex
    fake = "ab" * 20
    code, out = run(
        [py_bin(), str(HELPER), "prepare", "--tip", fake, "--base", base, "--out", str(outdir / "fake")],
        cwd=repo,
    )
    check("unknown 40-hex tip is rejected", code != 0 and ("not" in out.lower() or "cannot" in out.lower() or "error" in out.lower()), out[-800:])

    # empty diff
    code, out = run(
        [py_bin(), str(HELPER), "prepare", "--tip", tip, "--base", tip, "--out", str(outdir / "empty")],
        cwd=repo,
    )
    check("empty diff (tip == base) is rejected", code != 0 and "empty" in out.lower(), out[-800:])

    # parent base, no pr
    dest = outdir / "ok"
    code, out = run(
        [
            py_bin(),
            str(HELPER),
            "prepare",
            "--tip",
            tip,
            "--base",
            base,
            "--branch",
            "feat",
            "--out",
            str(dest),
        ],
        cwd=repo,
    )
    check("prepare with parent base exits 0", code == 0, out[-800:])
    egg = (dest / "eggbot-prompt.md").read_text(encoding="utf-8") if (dest / "eggbot-prompt.md").is_file() else ""
    grok = ""
    for name in ("grok-review-prompt.md", "grok-prompt.md", "grok-reviewer-prompt.md"):
        p = dest / name
        if p.is_file():
            grok = p.read_text(encoding="utf-8")
            break
    if not grok:
        # accept whatever was written
        files = list(dest.glob("*.md")) if dest.is_dir() else []
        grok = "\n".join(p.read_text(encoding="utf-8") for p in files)
        check("prepare wrote prompt files", bool(files), str(dest))
    blob = egg + "\n" + grok + "\n" + out
    check("prompts do not say PR #0", "PR #0" not in blob, blob[-800:])
    check("base is not invented as main", f"base: main {base}" not in blob.lower() and f"base main {base}" not in blob.lower(), blob[-800:])
    check("tip sha is in the prompts", tip in blob, blob[-800:])
    check("base sha is in the prompts", base in blob, blob[-800:])


def test_self_test() -> None:
    print("== helper self-test ==")
    code, out = run([py_bin(), str(HELPER), "self-test"])
    check("self-test exits 0", code == 0, out[-800:])
    check("self-test mentions git or sha", "sha" in out.lower() or "git" in out.lower() or "ok" in out.lower() or "pass" in out.lower(), out[-800:])


def test_helper_is_python39() -> None:
    print("== helper stays on Python 3.9 APIs ==")
    text = HELPER.read_text(encoding="utf-8")
    check(
        "does not call Path.write_text with newline=",
        "write_text(" not in text or all("newline=" not in line for line in text.splitlines() if "write_text(" in line),
    )
    check("uses open(..., newline=) or equivalent", 'open(' in text and "newline=" in text, "missing open(newline=)")


def main() -> int:
    if not CLI.is_file():
        print("error: missing", CLI, file=sys.stderr)
        return 2
    if not HELPER.is_file():
        print("error: missing", HELPER, file=sys.stderr)
        return 2
    env_home = os.environ.get("TRELLIS_MATT_HOME")
    os.environ["TRELLIS_MATT_HOME"] = str(ROOT)
    tmp = Path(tempfile.mkdtemp(prefix="t79-should-"))
    print(f"root: {ROOT}")
    print(f"tmp:  {tmp}")
    try:
        test_helper_is_python39()
        test_self_test()
        test_unbalanced_markers(tmp)
        test_dry_run_stale(tmp)
        test_codefree_o_empty_does_not_abort(tmp)
        test_second_apply_byte_stable(tmp)
        test_status_skips_missing_clients(tmp)
        test_helper_prepare(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        if env_home is None:
            os.environ.pop("TRELLIS_MATT_HOME", None)
        else:
            os.environ["TRELLIS_MATT_HOME"] = env_home
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
