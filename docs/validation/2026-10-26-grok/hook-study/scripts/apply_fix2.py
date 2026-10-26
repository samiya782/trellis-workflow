#!/usr/bin/env python3
"""Insert the explicit Trellis activation rule for the Matt delivery route (v2).
v2 ties activation to the user-typed command only, so an authorization message is
not read as delivery permission. Usage: apply_fix2.py <repo-root>. Idempotent."""
import sys, pathlib
root = pathlib.Path(sys.argv[1])

AGENTS_ANCHOR = "`$implement <scope>`) and pause.\n"
AGENTS_ADD = (
    "When the user types that command for a Trellis task still in `planning`, its\n"
    "first action is workflow 1.4: run `python3 .trellis/scripts/task.py start <task>`\n"
    "and confirm `task.py current --source` names the task, before any product edit\n"
    "or worker. An approval or authorization message does not replace the command.\n"
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
