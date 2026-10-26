#!/usr/bin/env python3
"""Standalone smoke test for the two Grok fixes in a Trellis project.

Copies <target>/.trellis into a throwaway git repo (the target is never
modified), then checks:
  1. GROK_SESSION_ID: `task.py start` writes a grok_<session> pointer and
     `task.py current --source` reports it.
  2. Archive jsonl repointing: child then parent archived with --no-commit;
     the archived child's implement/check entries follow the parent into
     archive/ and `task.py validate` passes; no commit is created.
Exit 0 only if every check passes.
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
if not (target / ".trellis" / "scripts" / "task.py").is_file():
    sys.exit(f"smoke: {target} has no .trellis/scripts/task.py")

tmp = Path(tempfile.mkdtemp(prefix="trellis-grok-smoke-"))
keep = os.environ.get("SMOKE_KEEP") == "1"
env = {k: v for k, v in os.environ.items()
       if not k.startswith(("TRELLIS_", "CODEX_", "CLAUDE_", "DSH_", "GROK_", "GIT_"))}
env.update(GROK_SESSION_ID="smoke-sess", GROK_AGENT="1",
           GIT_AUTHOR_NAME="smoke", GIT_AUTHOR_EMAIL="smoke@example.invalid",
           GIT_COMMITTER_NAME="smoke", GIT_COMMITTER_EMAIL="smoke@example.invalid")
results = []

def run(*cmd, ok=True):
    p = subprocess.run(cmd, cwd=tmp, env=env, text=True, capture_output=True)
    if ok and p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} -> {p.returncode}\n{p.stdout}\n{p.stderr}")
    return p

def task(*a, ok=True):
    return run(sys.executable, ".trellis/scripts/task.py", *a, ok=ok)

def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"\n       {detail}" if detail and not cond else ""))

try:
    shutil.copytree(target / ".trellis", tmp / ".trellis", symlinks=True,
                    ignore=shutil.ignore_patterns(".runtime", "__pycache__", "workspace"))
    tasks = tmp / ".trellis" / "tasks"
    shutil.rmtree(tasks, ignore_errors=True)
    tasks.mkdir()
    (tasks / ".gitkeep").write_text("")
    run("git", "init", "-q", "-b", "main")
    run("git", "add", "-A"); run("git", "commit", "-qm", "smoke base")
    run("git", "checkout", "-qb", "smoke-feature")
    if (tmp / ".trellis/scripts/init_developer.py").is_file():
        run(sys.executable, ".trellis/scripts/init_developer.py", "smoke", ok=False)

    def create(slug, parent=None):
        a = ["create", f"Smoke {slug}", "--slug", slug, "-d", f"smoke {slug}", "--no-start"]
        if parent:
            a += ["--parent", parent]
        task(*a)
        d = next(p for p in tasks.iterdir() if p.is_dir() and p.name.endswith(slug))
        if not (d / "prd.md").exists():
            (d / "prd.md").write_text(f"# {slug}\n")
        return d

    parent = create("smoke-parent")
    child = create("smoke-child", parent=f".trellis/tasks/{parent.name}")
    rel = lambda p: str(p.relative_to(tmp))
    for kind in ("implement", "check"):
        task("add-context", rel(child), kind, rel(parent / "prd.md"), "parent spec")
        task("add-context", rel(child), kind, rel(child / "prd.md"), "own spec")
    run("git", "add", "-A"); run("git", "commit", "-qm", "smoke tasks")

    # 1. Grok session pointer
    task("start", rel(child), "--allow-empty-context", ok=False)
    ptr = tmp / ".trellis/.runtime/sessions/grok_smoke-sess.json"
    cur = ""
    if ptr.is_file():
        cur = json.loads(ptr.read_text()).get("current_task", "")
    check("GROK_SESSION_ID -> .runtime/sessions/grok_smoke-sess.json", child.name in cur,
          f"pointer file present={ptr.is_file()} current_task={cur!r}")
    src = task("current", "--source", ok=False).stdout
    check("task.py current --source names session:grok_smoke-sess", "grok_smoke-sess" in src, src.strip())

    # 2. archive child then parent, --no-commit
    before = run("git", "rev-list", "--count", "HEAD").stdout.strip()
    task("archive", child.name, "--no-commit", "--skip-branch-validation")
    task("archive", parent.name, "--no-commit", "--skip-branch-validation")
    after = run("git", "rev-list", "--count", "HEAD").stdout.strip()
    check("--no-commit archive created no commit", before == after, f"{before} -> {after}")
    arch_child = next(tasks.glob(f"archive/*/{child.name}"), None)
    arch_parent = next(tasks.glob(f"archive/*/{parent.name}"), None)
    check("child and parent moved under archive/", arch_child and arch_parent)
    if arch_child and arch_parent:
        txt = (arch_child / "implement.jsonl").read_text()
        check("archived child implement.jsonl points at archived parent",
              rel(arch_parent) + "/prd.md" in txt, txt.strip())
        v = task("validate", rel(arch_child), ok=False)
        check("task.py validate passes on the archived child", v.returncode == 0,
              (v.stdout + v.stderr).strip()[-600:])
    ptr_after = ptr.is_file() and child.name in ptr.read_text()
    check("archive cleared the grok pointer", not ptr_after)
except Exception as exc:  # noqa: BLE001
    check(f"smoke harness ran ({exc.__class__.__name__})", False, str(exc)[-1500:])
finally:
    if keep:
        print(f"smoke: kept {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)

failed = [n for n, ok in results if not ok]
print(f"smoke: {len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
