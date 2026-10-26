#!/usr/bin/env python3
"""Insert the explicit Trellis activation rule for the Matt delivery route.
Usage: apply_fix.py <repo-root>. Idempotent; fails loudly if an anchor is missing."""
import sys, pathlib
root = pathlib.Path(sys.argv[1])

AGENTS_ANCHOR = "`$implement <scope>`) and pause.\n"
AGENTS_ADD = (
    "When that command (or any authorized delivery) targets a Trellis task still in\n"
    "`planning`, its first action is workflow 1.4: run\n"
    "`python3 .trellis/scripts/task.py start <task>` and confirm\n"
    "`task.py current --source` names the task, before any product edit or worker.\n"
)
MATT_ANCHOR = ("Keep one source for each fact. Resume reads this record and current files, retains\n"
               "approved decisions and honors any pending invocation boundary. A Trellis resume\n"
               "command does not invoke a pending user-only Matt skill.\n")
MATT_ADD = (
    "When the user invokes the skill for a Trellis task still in `planning`, activate\n"
    "first (workflow 1.4, `task.py start <task>`); the skill's own steps follow.\n"
)

def patch(rel, anchor, add):
    p = root / rel
    s = p.read_text()
    if add in s:
        print(f"{rel}: already patched"); return
    if s.count(anchor) != 1:
        sys.exit(f"{rel}: anchor found {s.count(anchor)} times")
    p.write_text(s.replace(anchor, anchor + add))
    print(f"{rel}: patched")

patch("AGENTS.md", AGENTS_ANCHOR, AGENTS_ADD)
patch("docs/agents/matt-flow.md", MATT_ANCHOR, MATT_ADD)
