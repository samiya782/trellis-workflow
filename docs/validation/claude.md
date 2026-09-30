# Fresh Claude Code validation — 2026-09-29

Evidence, not startup instructions. Separate from the Codex runs in this directory;
Codex results were treated as hypotheses and re-tested here.

## Runtime and method

- Claude Code **2.1.284**, model `claude-opus-5-5[1m]` (the user's configured default).
- Base: `efd8006` plus this change's working-tree edits. Every fixture is a disposable
  copy of that tree under `/tmp/cm/`, with local Git, no remote and a fixture developer.
- Each session: `claude -p <ordinary request> --output-format stream-json --verbose
  --permission-mode acceptEdits --allowedTools <list>`. The explicit mode overrides the
  user's global `bypassPermissions` default for the run. The allowlist grants `python3`,
  `git`, read-only shell tools, `Skill` and `Agent`; web/MCP tools, `cd` compounds and
  shell loops were not granted. No `--dangerously-skip-permissions`, no global edits.
- Follow-up human answers used `--resume <session>` with the plain text shown below.
  No per-stage commands, workflow reminders or this optimization brief were sent.
- Native transcripts: `~/.claude/projects/-tmp-cm-<fixture>/<session>.jsonl`; worker
  transcripts under `<session>/subagents/`. Costs are the CLI's `total_cost_usd` for
  that invocation, not a controlled benchmark.

Evidence classes used below:

- **Skill execution**: a `Skill` tool call whose result is the harness skill expansion
  (`Base directory for this skill: …/.claude/skills/<name>`), or a user `/name` expansion.
- **Native injection**: a worker transcript whose first prompt carries the hook marker
  `<!-- trellis-hook-injected -->` and the injected task artifacts.
- **Explicit-loading fallback**: the agent reads a `SKILL.md` or task file itself.

## Invocation policy (capability probes)

| Session | Setup | Result |
| --- | --- | --- |
| `5f65da90` | Upstream frontmatter | `Skill to-spec cannot be used with Skill tool due to disable-model-invocation … Do not replicate this skill's workflow by other means` |
| `9ab09399` | Same + `--settings '{"skillOverrides":{"to-spec":"on"}}'` | Identical block: settings cannot re-enable a frontmatter-disabled skill |
| `89e17439` | After `configure_claude_matt.py` | `retro` executed (skill expansion); `wayfinder` still blocked |

So without the adapter, a Claude coordinator must hand `/to-spec`, `/to-tickets`,
`/implement` back to the user, and a file-read workaround contradicts the runtime's
own instruction. The adapter flips only `disable-model-invocation` on `to-spec`,
`to-tickets`, `implement` and `retro`; entry skills stay user-only.

## Normal route stays normal

| Session | Ordinary request | Observed |
| --- | --- | --- |
| `d910e7bf` | Codex's README typo request | Direct edit, no task, no Skill call, no question, $0.20 |
| `381c81db` | Durable textstats module, "track it as a Trellis task", uncommitted | Task created without asking; 24 tests pass; no Skill call; `validate` failure on empty manifests reported, not called PASS; $0.39 |
| `081e44bc` | "Implement the following small spec…" (slugify) | Direct edit, 32 tests; Matt `implement` **not** selected despite now being model-invocable; $0.21 |

SessionStart (3,485-char context) and UserPromptSubmit hooks fired in every run.

## Authorized Matt delivery with parallel workers — fixture `fx-t2`

Request: Codex's rectangle-toolkit prompt with `/grill-with-docs` instead of
`$grill-with-docs` (entry, scope, local commits and archival authorized).

- Turn 1 (`5938b86e`): user `/grill-with-docs` expansion; **skill execution** of
  `grilling` and `domain-modeling`; one numbered round (file placement, validation
  location, test seam, edge cases, glossary, split). This is the real grilling
  method's material-decision pause, not a stage handoff.
- Turn 2, user text `Agree with all.`: **skill execution** of `to-spec` (reused the
  answered seam question), `to-tickets` (reused the answered split), `implement`,
  `code-review`. Parent spec + three children published with the backend's metadata.
- Two `trellis-implement` workers dispatched in one message:
  01:34:51.8–01:35:57.2 and 01:34:58.6–01:35:44.2 (**45.6 s overlap**). The
  coordinator joined, verified 20 tests, committed per ticket, then did the dependent
  summary test-first.
- Real Standards/Spec review agents overlapped **29.8 s**; one Spec finding was
  fixed, committed, and the Spec axis plus `trellis-check` rechecked the new revision.
- Closeout: children then parent archived with `--no-commit`, moved context pointers
  repaired, journal recorded once with `--no-commit`, one closeout commit.
  6 commits on `feature/geometry`; `main` unchanged; `unrelated-note.txt` byte-identical
  and never committed. $0.33 + $3.93.

**Defect found:** both workers were native-injected, but the area worker's context
carried the *perimeter* ticket's `prd.md`. The Claude PreToolUse hook took the task
from the single session pointer, which `task.py start` had moved to the last started
ticket. The coordinator noticed and reported it. Fixed in
`.claude/hooks/inject-subagent-context.py`: a dispatch line `Active task: <path>`
(existing task under `.trellis/tasks/`, exactly one) takes precedence. Regression:
`test_parallel_claude_workers_receive_their_named_task` fails on the old hook with the
same wrong-ticket injection and passes on the fix.

## Interrupted delivery and fresh resume — fixture `fx-t3` (with the fix)

- Turn 1 `3a8bfffb`, turn 2 `All recommended.`: workers dispatched with the marker
  unprompted; each transcript shows native injection of **its own** ticket only.
  Overlap 01:55:03.0–01:56:35.3 and 01:55:08.3–01:56:06.7 (**58.4 s**). The summary
  ticket executed real `tdd`.
- The session was killed (SIGTERM) after the helpers' commit while the summary was
  uncommitted. The test then changed `areas.py` (`height < 0` → `height < -1`) and
  added an untracked `unrelated-note.txt`.
- Fresh session `41da4f15`, request: *Resume the rectangle toolkit task at
  .trellis/tasks/09-29-rectangle-toolkit. I changed areas.py and its negative-input
  tests are failing; repair that regression, then finish the previously authorized
  delivery. Keep unrelated-note.txt untouched and uncommitted.*
- Recovered route/scope/commit authority from task files with no question. Noted the
  claim was inaccurate (existing tests only probed −2.5), added a failing boundary
  test, restored `< 0`. `implement` was loaded by **explicit file read** (permitted
  after the adapter; not a skill execution); `code-review` was a **skill execution**.
- Review: three low findings fixed, both axes re-reviewed; checker passed; children
  then parent archived; one journal entry; closeout commit. It reworded its own
  unpushed commit message once (history rewrite within local-commit authority).
  51 tests; note untouched; `main` unchanged. $1.97.

## Boundaries

- **Planning-only Wayfinder** (`f418ed33`, Codex's prompt with `/wayfinder`, answers
  `Agree with all.` twice): two grilling rounds, then one `wayfinder-map` and eight
  typed decision tickets, all `planning`, nothing started, committed or implemented.
  Three research subagents ran concurrently (**128.1 s** common overlap), each with a
  **skill execution** of `research` inside the subagent. Web access was not granted and
  Claude Code rejected subagent report-file writes; the coordinator saved partial
  findings, left tickets open and asked for network permission. $0.55 + $0.70 + $6.25.
- **No commit** (`661fde58`, `/grill-with-docs` temperature helper, "do not commit…
  do not archive"): `implement` and `tdd` executed, 36 tests, no commit, no archive.
  Committed `code-review` reported **not run** with the reason and base; no PASS claim.
  A later fresh `/trellis:continue` (`t7`, rewritten command) re-ran the 36 tests,
  kept the boundary and pending review, and left the working tree unchanged.
- **Repair bound** (`fafbfc53`, fresh "Continue the task at …" on a recorded in-progress
  task whose platform-owned latency test needs 25 ns per call): two benchmark rounds,
  concluded the budget is unreachable without breaking the contract, changed no code or
  threshold, recorded measurements and a blocked next action in `prd.md`, asked for a
  decision. This exercised the *material decision* stop, not three failed cycles. $0.38.
- **Non-duplicating closeout** (`541026fb`, `/trellis:finish-work` on the delivered
  `fx-t2`): recognized archive and journal were done; HEAD and journal bytes unchanged.

## Setup and cost

A clean `/tmp` project ran `npx @mindfoldhq/trellis@0.7.0-beta.4 init -u fixture
--claude --yes`, then the pinned `skills@1.7.0 add … --agent claude-code --copy`
twelve-skill install (real copies, no `.agents`). Generated hooks and continue
command equal this repository's baseline; the adapter applied and checked. The twelve
installed bodies equal this repository's `.claude/skills` byte for byte after the
adapter.

The adapter adds **547 characters** of skill descriptions to every Claude turn.
SessionStart context is 3,485 characters. `matt-flow.md` grew 190 characters (on
demand); `/trellis:continue` shrank 2,382 → 986 (on demand). Skill bodies, task files
and reviews dominate a Matt session; no total-token saving is claimed.

## Not established

- Interactive TUI sessions, `AskUserQuestion` prompts, and permission prompts were
  not exercised; headless runs deny unlisted tools instead of asking.
- Literal three-consecutive-failure termination was not reproduced.
- Claude Code blocks some allowlisted Bash forms (`cd` + git, `$VAR` expansion,
  loops); agents retried with simpler commands. Other permission configurations vary.
- The generic `/trellis:finish-work` text still describes auto-committing archives;
  workflow 3.5's `--no-commit` rule governed in the observed runs.
