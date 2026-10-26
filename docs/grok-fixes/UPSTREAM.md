# Upstream report draft for mindfold-ai/trellis (NOT submitted)

Patch: [`upstream/0001-grok-session-id-and-archive-jsonl-repoint.patch`](upstream/0001-grok-session-id-and-archive-jsonl-repoint.patch)
(`diff -ruN` against `main`, paths `packages/cli/src/templates/trellis/scripts/common/`).
Submitting it is up to the repository owner.

---

**Title:** Grok Build: `task.py start` writes no session pointer; `task.py archive` leaves stale jsonl paths

**Version:** `@mindfoldhq/trellis` 0.7.0-beta.4 (the same code is still on `main`). Grok Build 1.0.70, Linux (WSL2).

### 1. Grok Build session identity is not recognized

Grok Build exports `GROK_SESSION_ID` (and `GROK_AGENT`) to every tool shell.
`common/active_task.py` `_ENV_SESSION_KEYS` doesn't list it. In a project
initialized with `trellis init --grok`:

```bash
# inside a Grok Build session (tool shell), or simulated:
export GROK_SESSION_ID=demo
python3 .trellis/scripts/task.py create Demo --slug demo -d "demo task" --no-start
python3 .trellis/scripts/task.py start .trellis/tasks/*-demo --allow-empty-context
python3 .trellis/scripts/task.py current --source
```

- **Expected:** `.trellis/.runtime/sessions/grok_demo.json` is written, and the source is `session:grok_demo`.
- **Actual:** `start` prints "Branch recorded: … (degraded)", no pointer is written, and `current` prints "Current task: (none) / Source: none". `/trellis-continue` and the finish-work flow can't find the active task.

**Fix:** add `("grok", ("GROK_SESSION_ID",))` to `_ENV_SESSION_KEYS`.

### 2. `task.py archive` doesn't rewrite context paths into the moved task

Children created by Matt's `/to-tickets` (or by hand with `add-context`) often
reference the parent's `prd.md` in `implement.jsonl`/`check.jsonl`. `cmd_archive`
moves the directory to `archive/YYYY-MM/` but doesn't update those references.
Once the parent is archived, `task.py validate` fails on every child:

```bash
t=.trellis/scripts/task.py   # on a feature branch of a git repo
python3 $t create Parent --slug parent -d "parent spec" --no-start
P=$(ls -d .trellis/tasks/*-parent)
python3 $t create Child --slug child -d "child ticket" --parent $P --no-start
C=$(ls -d .trellis/tasks/*-child)
python3 $t add-context $C implement $P/prd.md "parent spec"
python3 $t archive $(basename $C) --no-commit
python3 $t archive $(basename $P) --no-commit --skip-branch-validation
python3 $t validate .trellis/tasks/archive/*/*-child
```

- **Expected:** validation passes, and the child's entry points at `.trellis/tasks/archive/YYYY-MM/<parent>/prd.md`.
- **Actual:** `implement.jsonl:1: File not found: .trellis/tasks/<MM-DD>-parent/prd.md`, then "✗ Validation failed (1 errors)".

**Fix:** after the move, rewrite `file` values that start with the old task path
to the new path in every task's `implement.jsonl`/`check.jsonl`, active and
archived. Only lines that change are rewritten, and other JSON keys are kept.

Both fixes were verified with regression tests and an interactive Grok Build run:
`/to-tickets` → `/implement-spec` → `/trellis-finish-work`, then archiving the
parent with `--no-commit`. In that run, `task.py validate` passed on the archived
children and no commit was created.
