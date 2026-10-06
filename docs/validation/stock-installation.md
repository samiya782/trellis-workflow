# Stock installation — 2026-09-29

This is the current supported setup. Earlier [Codex/Claude automation results](README.md)
used policy adaptations and remain historical evidence, not requirements or proof
of stock end-to-end automation. HEAD was `fdb57d2`; the uncommitted runtime-gap
fixes already present were preserved. No repository commit or push was made.

## Installation and migration

The exact command ran successfully in an isolated Git project and this checkout:

```bash
npx skills@latest add mattpocock/skills --agent claude-code codex --yes
```

Observed installer **1.7.0**, upstream HEAD
`d81f3a183412e71a5b1e84ca21bc1a35eea03a60`. These identify this test, not mandatory
installation pins. The isolated project is `/tmp/trellis-stock-install-9269692g`.
The installer produced **37 canonical skill directories / 101 files** under
`.agents/skills`, **37 Claude symlinks**, and its normal `skills-lock.json`.
The checkout's corresponding files match the isolated installation byte for byte.

Before migration, each of four Claude frontmatter files and four Codex metadata
files exactly matched its saved adaptation. Both existing adapters restored the
saved originals without drift, then their scripts and 17 adapter-only tests were
removed. No manual upstream body, frontmatter or metadata edit followed restoration.
The installer replaced the old copies that occupied its standard destinations
with its normal shared-directory/link layout. Git consequently shows old Claude
copy deletions together with new canonical files and links; this is installer
output, not renamed/forked skills. The independent old `resolving-merge-conflicts`
copy shadows no installed name and was preserved, as was its installer lock entry.

Removed the old selective `.gitignore` rules tied to the pinned twelve-skill setup.
No replacement metadata override, wrapper, custom installer, fork or pin was added.
Rerunning the same standard command is the documented update path; inspect upstream
changes and refresh runtime discovery normally.

Setup correction: the first installer call used `/tmp` rather than the intended
fixture cwd. Only its newly generated 37 Matt directories/links and lockfile were
moved intact into `/tmp/trellis-stock-initial-output-z6lgbuwc`, outside fixture
ancestry, before the correct isolated run. No reference-project files were touched.
That first output is not counted as the isolated-project validation.

## Stock policies and retained integration

Observed stock `grill-with-docs`, `wayfinder`, `to-spec`, `to-tickets`, `implement`
and `retro` have Claude `disable-model-invocation: true` and Codex
`allow_implicit_invocation: false`. Those fields remain upstream-owned. Codex's
policy comes from `agents/openai.yaml`; Claude frontmatter alone does not establish
Codex's controls. `retro` is installed but user-only; optional retrospective work
does not justify restoring a patched installation.

The workflow defaults to normal Trellis. Explicit Matt entry or a recorded Matt
route selects its genuine skills. Each next responsibility is conditional; where
stock invocation requires the user, context and the exact command are saved before
pausing. General scope authorization does not substitute for skill invocation.
Ordinary permitted file loading remains valid; it is not a way around denial or
user-only controls. Retro and update-spec remain independent and conditional.

Preserved the independent worker-identity validator, exact-parent fallback,
recorded authorization, no-auto-commit closeout and idempotent recovery fixes.
Fourteen runtime/source-test/historical-evidence files were verified byte-identical
to the pre-migration working tree. Continue/finish guidance changed only to honor
the next stock skill boundary. The task-context helper loads task data and does
not alter or impersonate a Matt skill.

## Focused checks and one fresh session

After removing the 17 tests specific to deleted adapters, all **23 remaining
regressions passed in 6.870 seconds**. They cover workflow parsing/breadcrumbs,
worker isolation, authorization and closeout. No expensive delivery matrix ran.
Final prose compaction then passed the three affected parser/index/breadcrumb
tests. Workflow is **6,862 characters**, down from HEAD's 8,572, retaining all
13 step headers and six breadcrumbs. README is about 5,000 characters, down from
HEAD's 13,124. These are character counts, not token/performance measurements.

Fresh Codex **0.159.0**, model **gpt-6-astra**, thread
`01a0f05c-f978-73d3-9ef1-b02322045165`, ordinary request:

> Continue the task at .trellis/tasks/09-29-stock-resume within its recorded scope.

The fixture seeds a completed Matt discovery record with settled requirements
and local implementation authorization. This is **not** a claim that a new stock
grill interview executed. The prompt contains no optimization brief or per-stage
reminder. Native project AGENTS loaded once (line 6); copied hooks were not approved
or forced, and no native hook context was observed.

Observed behavior:

- Read Trellis start/continue, exact task records and on-demand routing/backend.
- Inspected the installed to-spec file; did not invoke its specification workflow.
- Wrote only `implement.md`, retaining the approved scope and pending work.
- Returned the exact next command and paused:

  ```text
  $to-spec .trellis/tasks/09-29-stock-resume
  ```

- No spec publication, implementation, task activation, commit, archive or worker.
  This is a policy-aware handoff, not an observed runtime tool rejection or native
  skill invocation. The original task/readiness state was preserved.

The session's final explanation cites Claude's frontmatter rather than Codex's
actual metadata field. The outcome agrees with the independently inspected stock
Codex policy. Guidance now explicitly distinguishes the two fields; the erroneous
explanation is not treated as proof of Codex frontmatter semantics.
The single fresh session used the stock routing before the final prose compaction;
that compaction preserved its invocation rule and was checked by the focused tests.

Exit 0; **77.470 seconds**. CLI cumulative usage: **156,471 input**, **128,256
cached input**, **1,741 output** tokens. These are repeated/cache-reused turn totals,
not unique context, dollar cost or a performance benchmark.

## File integrity and execution permissions

Before regression/runtime execution, hashed all installed Matt files, symlink
targets and lockfiles in both checkout and fixture. After execution, snapshots
match exactly: **141 checkout entries**, **139 fixture entries** (the checkout
retains the unrelated legacy skill). All **101 stock files** remained unchanged;
neither integration execution nor the fresh runtime mutated installer output.

The fresh CLI used workspace-write and approvals `never`, with an invocation-only
project-trust setting:

```text
-c 'projects={"/tmp/trellis-stock-install-9269692g"={trust_level="trusted"}}'
```

This is not hook trust or a permission bypass. Matching-version source explains
the earlier transient trust writes: thread startup persists project trust when
cwd is writable and effective project trust is unset
(`app-server/src/request_processors/thread_processor.rs:1350–1378`). The inline
TOML value sets the exact project key only in the session override layer, so that
branch is skipped. A dotted override with quoted path segments is parsed
differently in 0.159.0 and should not be presumed equivalent. Source inspected at
`rust-v0.159.0`, commit `377f7f557a6bdea0f3a2d26d4d899c66db4789d0`.

Before/after hashes of user Codex config/hooks and Claude settings match. **No
global-setting change or cleanup was needed in this stock test.** No reference
project was written, and no Claude harness ran. The stock command itself uses no
custom flags beyond those requested by the user.

Exact commands, native references, installed file hashes, integrity checks and
usage are in [stock-installation.json](stock-installation.json). Raw logs stay in
`/tmp/trellis-stock-run.*` and the native session store. Remaining limits: no stock
full delivery matrix, fresh stock entry interview, Claude execution or hook-trust
approval test; automatic end-to-end delivery is not an acceptance requirement.

## Claude Code compatibility check — 2026-09-29

Verification only; no integration change. Claude Code **2.1.284**, model
`claude-opus-5-5[1m]`, checkout `db83481` with a clean working tree. Fixtures are
`git archive HEAD` copies under `/tmp/cs/` plus a two-function `textstats.py`
sample app, local Git, a fixture developer and no remote. Before the interactive
run, every tracked file and symlink in the Matt fixture matched the checkout.
Only ignored per-developer/runtime state and an unrelated `ask` override differed.

| Check | Execution mode | Result |
| --- | --- | --- |
| 1. Normal route | Fresh headless `claude -p`, `--permission-mode acceptEdits`, tool allowlist; `317236af` | **Pass.** "Correct the typo in the textstats help text and run the relevant check. Leave it uncommitted." Direct edit, tests run, uncommitted; no task, question or Skill call. $0.27 |
| 2. Explicit Matt entry and boundary | Interactive TUI, `--permission-mode acceptEdits`; the user typed every prompt; `5cab24dd` | **Entry passes; boundary fails.** See below |
| 3. Fresh-session recovery | Not run | **Blocked:** session 2 recorded no task path or handoff to recover |

Static only: session init listed the six stock Matt skills and their dependencies.
Observed in `5cab24dd` (native transcript
`~/.claude/projects/-tmp-cs-fx-matt-4R7h/5cab24dd-e93a-4594-a15b-ae553d61a34f.jsonl`):

- SessionStart and UserPromptSubmit hook context loaded; AGENTS.md loaded natively.
- User input `/grill-with-docs Add a --top N option to textstats that prints the N
  most frequent words. Help settle the behavior first.` produced the harness skill
  expansion. Its stock body led to `Skill` executions of `grilling` and
  `domain-modeling`. The agent read the phase index and `matt-flow.md`.
- One numbered round of five questions with recommendations. It stated it would
  write the contract into a Trellis task before any code.
- The user replied `accept all`. Claude wrote `GLOSSARY.md`, then implemented `--top`
  in `textstats.py` and its tests (10 app and 23 repo tests passed), uncommitted. No
  task, `to-spec`/`implement` Skill call or SKILL.md read, next command or pause. It
  cited the Phase Index small-settled-work rule.

The user-only control was not circumvented through a skill read or call. The Matt
route was nevertheless abandoned: implementation replaced the next stock skill
without a recorded task or handoff. This contradicts `matt-flow.md`, whether or
not the original "Add …" request authorized implementation. Workflow, hooks and
configuration were not changed to make it pass, and the check was not retried.

Integrity: 239 entries per tree matched before and after for the checkout and both
fixtures. The entries are: every `.agents/skills` file (mode and SHA-256), 37 Claude
symlink targets, the legacy skill, `skills-lock.json`, workflow, routing doc,
AGENTS.md, Claude settings and hooks. `~/.claude/settings.json` was unchanged. No
commit, push or reference-project write. Delivery, parallelism, retro and
repair-exhaustion matrices were not rerun.

### Routing fix and handoff/resume retest

Authorized minimal fix for the failure above; the failed fixture and transcript are
preserved. Transcript text was treated as evidence of likely contributors, not of a
single cause, because the model's reasoning is redacted:

- the unscoped Phase Index small-work bullet, which the agent cited;
- the `no_task` breadcrumb ("Normal small work proceeds directly"), injected
  before `accept all`;
- `matt-flow.md` naming only an "existing task" for state and an unformatted
  "go directly to implement".

Changes: the Phase Index and `no_task` breadcrumb now state that an explicit Matt
selection governs its work item. Settled requirements, small size or general
authorization don't switch it; only the user can. Unrelated work defaults to normal
Trellis, and the small-work bullet is limited to the normal route. `matt-flow.md`
states the same rule. At a user-only boundary it now creates or reuses a minimal
`--no-start` task and records only what happened. Inline substitution for the
needed skill is listed as a bypass. Stage selection stays conditional. One text
test (`test_explicit_matt_route_is_not_replaced_by_small_work_shortcut`) fails on
the old text; all **24** tests pass. Workflow is 7,126 characters, with 13 step
headers and 6 breadcrumbs.

Fresh fixture `/tmp/cs/fx-retest-Ayjc`: current working-tree files, pre-feature
app, every tracked file and link identical to the checkout.

| Check | Execution mode | Result |
| --- | --- | --- |
| 2. Entry and boundary | Interactive TUI, started `acceptEdits`; the user switched to Claude Code's `auto` permission mode after round 1; the user typed every prompt; `0ff11216` | **Pass** |
| 3. Fresh recovery | Fresh headless `claude -p "Continue the task at .trellis/tasks/09-29-textstats-top."`, `acceptEdits`, allowlist; `d088de09` | **Pass**, $0.23 |

Observed in `0ff11216`:

- The same `/grill-with-docs` request produced the harness expansion and `Skill`
  executions of `grilling` and `domain-modeling`.
- Two numbered rounds (Q1–Q6, then Q7–Q10), each answered `accept all` by the
  user. Q10 asked whether local commits and pushes were allowed, and proposed going
  directly to `/implement`.
- The agent inspected `implement`/`to-spec` frontmatter for policy and wrote
  `GLOSSARY.md` (domain-modeling output).
- It created `.trellis/tasks/09-29-textstats-top` with `--no-start` (status
  `planning`, no session pointer). Its `prd.md` holds the ten decisions, marked as
  assistant-proposed and user-accepted. It also records route, source skills, the
  testing seam, commit yes/push no, base `419849c`, dirty paths and the next command.
- It returned `/implement .trellis/tasks/09-29-textstats-top` and paused. No code,
  commit, `implement` call or `SKILL.md` body load.

Observed in `d088de09`:

- It read the task, glossary, `matt-flow.md` and the first lines of the installed
  `implement` file (policy check, not execution).
- It restated the settled contract and permissions without asking a question.
- It returned the same `/implement` command and stopped. No Skill call, no denial,
  no file or Git change: status and hashes identical before and after.

Not established: the `/implement` run itself (not requested), Codex behavior with
the new text, and repeatability beyond one run.

Integrity: all 230 installed Matt entries (`.agents/skills` files, Claude links,
legacy skill, `skills-lock.json`) match the first baseline, in the checkout and
the retest fixture. `~/.claude/settings.json` is unchanged. No commit, push or
reference-project write; the delivery matrix was not rerun.

## Small-task routes — 2026-10-05

Routing-text change plus one runtime check per scenario. Claude Code **2.1.289**,
model `claude-opus-5-5[1m]`. No installer, skill, hook-code or config change.

**Sources.** Installed stock skills and upstream `README.md`/`ask-matt` (fetched
2026-10-05):
- `implement` builds "a piece of work based on a spec or set of tickets". `ask-matt`
  routes builds that are not multi-session to "`/implement` right here".
- `implement-spec` "Implement[s] the result of /to-spec and /to-tickets": a ticket
  task graph, integration branch, worktrees and merger subagents. It is the
  multi-session option, so it is not the small-task route requested. Small
  builds use `implement`; `implement-spec` without a spec stops and offers it.
- `grill-me` is the stateless interview: no `GLOSSARY.md` or ADRs.
- `diagnosing-bugs` is model-invoked, for reported broken, throwing, failing or
  slow behavior.

**Changes.**
- `workflow.md`: any explicit Matt skill invocation selects the route.
  A reported bug symptom without a stated fix invokes `diagnosing-bugs` before code
  is read for a theory; a stated fix or typo stays small work. The no_task
  breadcrumb says the same.
- `matt-flow.md`: the entry skill sets the record size:
  - `grill-with-docs` and `wayfinder` keep the task record;
  - `grill-me` keeps none;
  - `implement` needs no spec, tickets or task;
  - `implement-spec` requires a published spec with tickets, never fabricated.

  Same-session small handoffs reference the agreed scope instead of a task.
- One focused test in `tests/test_integration.py`. 25 tests pass, and the new test
  fails against the previous routing text.

Fixtures: working-tree copies (`git stash create` + `git archive`) under
`/tmp/cs/` with the `textstats.py` sample app. The bug fixtures change
`word_count` to `text.split(" ")`; the existing app test still passes there.

| Scenario | Mode; session | Result |
| --- | --- | --- |
| Small change | Headless `claude -p`, `acceptEdits`, allowlist; `11108fd4`, rerun on final text `2d2101be` | **Pass** both: direct edit and app tests, uncommitted; no Skill call, task or question. $0.25 / $0.21 |
| Bug report, first wording | Headless; `c4be4f06` | **Fail (routing):** correct fix and regression test, no task, but no `diagnosing-bugs`. It read the code and edited before reproducing. $0.30 |
| Bug report, final wording | Headless, fresh fixture; `c591495c` | **Pass:** `Skill diagnosing-bugs` first. It reproduced the bug (red) and minimised it. Its regression test failed `4 != 2`, then the fix went in and the repro was rerun. No task, uncommitted. $0.34 |
| `/grill-me` → `/implement` | Interactive TUI, user typed both commands; ran in `bypassPermissions` (user's default); `49be3b33` | **Pass,** see below |
| `/implement-spec` without spec → `/implement` | Interactive TUI, user typed both commands; `bypassPermissions`; `15801f40` | **Pass,** see below |
| New-project setup + bug report | Scratch `trellis init` + current upstream installer + README steps; headless `c7fd53ce` | **Pass,** see below. $0.31 |

`49be3b33` (`~/.claude/projects/-tmp-cs-fx-grillme2-qyyd/`):
- The `/grill-me` expansion led to `Skill grilling`. The agent said up front that
  nothing goes to a task, glossary or ADR.
- Rounds: Q1–Q8, answered `accept all`, then Q9–Q10 with a summary.
- It ended with `/implement textstats --top N per the behavior agreed in this
  conversation`. It noted that only the user can start `implement`, suggested
  `/grill-with-docs` for a recoverable record, and paused.
- The user ran that command without answering Q9–Q10. The agent used its
  recommendations and said so in the final report.
- `implement` ran `Skill tdd` (six red-green slices), the full suite (34 tests) and
  `Skill code-review` with two parallel reviewers.
- It committed `2eb3fec` on `main` without asking. Its stated basis was the stock
  `implement` commit step and `code-review`'s `<base>...HEAD` contract.
- No task, spec, tickets or `GLOSSARY.md`.

`15801f40` (`~/.claude/projects/-tmp-cs-fx-ispec2-2q4Y/`):
- `/implement-spec Make textstats accept -l as a short alias for --lines.`
  searched tasks for a spec and tickets and found none. Citing `matt-flow.md`, it
  wrote no code and returned `/implement Make textstats accept -l as a short alias
  for --lines.`
- After the user's `/implement`, it ran `tdd` (red: argparse exit 2; green) and
  asked about the seam and the branch. The user chose "Commit on main".
- It ran `code-review` on both axes and applied one low-severity test suggestion.
  Commits: `c19a0fe` and `f01fbec`.
- No task, spec or tickets.

New-project setup (`/tmp/cs/newproj`, isolated `HOME` for `trellis` and `npx`):
- `trellis init -u tester --claude --codex -y` (0.7.0-beta.4) left 17 files
  different from this checkout. They are the 14 copied integration files,
  `AGENTS.md`, `.template-hashes.json`, and `.claude/settings.json` (the optional
  statusline only). Only `docs/agents/*`, `statusline.py`, `.gitignore` and the
  lockfile existed only in the checkout.
- The current upstream installer added `chief-of-staff` and changed `ask-matt` to
  suggest `/retro` after a bug fix. `resolving-merge-conflicts` is absent.
  Policies of `grill-me`, `implement`, `implement-spec` and `diagnosing-bugs` are
  unchanged.
- After the README copy steps, `get_context.py --mode phase`, both
  UserPromptSubmit hooks and Claude SessionStart carried the new routing. The
  stock breadcrumb asked for task-creation consent on every turn.
- The headless bug report invoked `diagnosing-bugs` and reproduced the bug before
  reading code. Its regression test went red, then the fix went in. No task,
  uncommitted.

Not run: `/grill-with-docs` and `/wayfinder` with the new text, `implement-spec`
with a real spec, Codex behavior, and repeatability. Each scenario ran once.

Integrity: all 230 installed Matt entries match before and after in the checkout
and all eight fixtures. The only checkout change after its baseline was the
intended `workflow.md` wording. `~/.claude/settings.json` is unchanged. No push
or reference-project write. Fixture commits stay local to the disposable fixtures.

## Remaining Claude Code routes — 2026-10-05 (after `c962f9b`)

Validation only; no routing change. Fixtures were rebuilt from `c962f9b` under
`/var/tmp/cs/` (the `/tmp` fixtures were lost to a reboot; native transcripts of
every cited session remain under `~/.claude/projects/`). Claude Code 2.1.289,
`claude-opus-5-5[1m]`.

| Scenario | Mode; session | Result |
| --- | --- | --- |
| Repeat: small change ×2 | Headless, `acceptEdits`, allowlist; `1bebc697`, `6998ffd0` | **Pass** both. Totals on final text: 4/4 |
| Repeat: bug report ×2 | Headless; `5a932171`, `e0a1c860` | **Pass** both: `diagnosing-bugs` first, repro and minimisation before reading code, red regression test before the fix, no task. Totals on final wording: 4/4 |
| `/grill-with-docs` → `/to-spec` → `/to-tickets` | Interactive TUI, user typed all three; `bypassPermissions`; `938548bb` | **Pass**, see below |
| Fresh recovery from that handoff | Headless on a copy taken at the first pause; `1909c45d` | **Pass**, $0.26 |
| `/wayfinder` planning only | Interactive TUI, user typed; `bypassPermissions`; `87785278` | **Pass**, see below |

`938548bb`:
- Ran `Skill grilling` and `Skill domain-modeling`; wrote `GLOSSARY.md` (Token,
  Word, Report) and no ADRs ("nothing met the bar").
- Three rounds, Q1–Q14, each answered `accept all`. Q13 set planning only
  (spec, tickets, stop) and Q14 set no commits and no push.
- It created `10-05-textstats-report-mode` (`--no-start`), recorded route,
  scope, decisions and the next command in `implement.md`, returned
  `/to-spec .trellis/tasks/10-05-textstats-report-mode` and paused.
- `/to-spec` treated the Q11 seam answer as the skill's seam check, and
  published the full template into `prd.md` (30 user stories, kind `spec`,
  ready true).
- `/to-tickets` treated Q12 as approval and published three child tickets with
  exact `trellis-task:` blockers, all `task.py validate` clean. The parent's
  empty manifests fail validation, as workflow 1.3 states.
- It stopped at the recorded planning boundary and offered
  `/implement-spec .trellis/tasks/10-05-textstats-report-mode`. Nothing was
  committed and no code changed.

`1909c45d` ("Continue the task at .trellis/tasks/10-05-textstats-report-mode.",
on the copy): it read the task record and loaded `matt-flow.md` because the task
is on the Matt route. It checked `to-spec`'s policy, restated the scope and
decisions without asking anything, refused to write the spec inline, and
returned the same `/to-spec …` command. Git status and file hashes were
unchanged.

`87785278`:
- Ran `grilling` and `domain-modeling` to set the destination, a published
  spec, over two rounds answered `accept all`.
- Published a `wayfinder-map` task with seven typed `wayfinder-ticket`
  children (research, grilling, prototype). The graph was validated before
  readiness was set.
- A research subagent resolved the packaging-facts ticket. The coordinator
  wrote `research.md` and appended `## Resolution`, plus a "Decisions so far"
  line on the map. It archived the ticket with `--no-commit` and added the
  research to the dependent ticket's context.
- No code; everything uncommitted. It ended with
  `/wayfinder .trellis/tasks/10-05-textstats-library-map` for the next ticket.

Still not run: `implement-spec` executing a real spec. Session `938548bb`
published one, but the user's planning-only choice ended there.

Codex (recorded, not pursued in this round):
- Two headless `codex exec` runs (`gpt-6-luna`, workspace-write, per-run
  `--dangerously-bypass-hook-trust`). The configured `gpt-6-astra` is rejected
  for this account.
- The small change passed.
- Three bug reports each loaded `diagnosing-bugs`, reproduced the bug and
  probed it before reading code. None wrote a regression test or reran the
  check after the fix.
- One run grepped the planted bug's description out of this file.
- Those runs added three fixture `trust_level` entries to `~/.codex/config.toml`.
  They were removed, and the file's hash matches the pre-run baseline.

Integrity: all 230 installed Matt entries match before and after, in the
checkout and all 13 fixtures. `~/.claude/settings.json` is unchanged.

### `implement-spec` on the published spec — 2026-10-05

Same interactive session `938548bb` (`bypassPermissions`). The user typed
`/implement-spec @.trellis/tasks/10-05-textstats-report-mode/`, which supplied the
delivery authorization that Q13 had deferred. **Pass**, with the notes below.

- **Branch and tickets.** It created integration branch `textstats-report-mode`
  from `f32ce58`, opened no PR (the Trellis tracker closes work by archive) and
  started ticket 1.
- **Workers.**
  - The coordinator dispatched one worktree implementer for the unblocked
    ticket. After it merged, it dispatched the two parallel tickets
    concurrently, each in its own worktree.
  - Each worker prompt began with `Active task: <ticket>`. All four
    implementers (three tickets, one review-fix) called `Skill tdd` and made no
    commits.
  - The coordinator reviewed each diff and reran the tests. It committed and
    merged as `1df071d`, `4e727d4`, `0a46932`, `12c5f36` and `afde5b0`.
- **Merge.** It resolved additive conflicts with the local legacy
  `resolving-merge-conflicts` skill. It also found that the clean auto-merge had
  dropped `--min-length` from the JSON path, fixed it, and had the worker add
  the combined test.
- **Review.**
  - It ran `code-review` against `f32ce58` with parallel Standards and Spec
    reviewers.
  - There were no hard violations or spec gaps, but two defects: ASCII symbols
    weren't stripped, and `int()` accepted `1_0`.
  - One review-fix worker fixed both test-first, plus the cleanups (`b293cfb`).
  - The review axes were not rerun after the fixes. The coordinator verified
    each fix directly and said so. `matt-flow.md` asks for affected axes to be
    rerun when invocation is permitted, so this is a minor gap.
- **Closeout.**
  - The children were archived `completed` with `--no-commit`, and the worker
    worktrees and branches were removed.
  - The parent stayed `planning` for the user's merge and closeout decision.
    Its `implement.md` holds the integration log, review findings, fix
    decisions and acceptance.
  - `main`, `GLOSSARY.md` and the task files were untouched; the task files
    stay uncommitted per Q14.
- **Disclosed decisions** made without asking: the punctuation reading, keeping
  `ensure_ascii`, and the skipped review rerun.
- **Independent check:** 57 app tests and 25 repo tests pass on `b293cfb`, and
  the combined `--json --top --min-length` CLI output applies the filter.
- **Adaptation:** stock `implement-spec` has implementers commit and a merger
  subagent merge. Here the coordinator did both, as `matt-flow.md` assigns
  shared Git to the coordinator.

Integrity: the fixture's and checkout's 230 installed Matt entries are unchanged,
and `~/.claude/settings.json` and `~/.codex/config.toml` match their baselines.

### Follow-up closeout and skills update — 2026-10-05

Same session `938548bb`, after the user reviewed the report above and authorized
closeout. The user accepted the disclosed decisions as long as each is reported
and recorded.

- **Review rerun.** `code-review` was rerun at `b293cfb` against `f32ce58`.
  - Spec: nothing missing, nothing beyond the spec and nothing wrong. Both
    earlier defects were confirmed fixed.
  - Standards: no hard violations, and every first-round item was resolved.
    One claim was checked and rejected: that `GLOSSARY.md` spells it
    "normalized". It doesn't.
  - One worker fixed four minor style issues (`4514aa9`), with 57 tests passing.
    That behavior-neutral commit was not reviewed a third time.
- **Merge and closeout.**
  - `textstats-report-mode` was merged into fixture `main` with `--no-ff`
    (`b995fbd`).
  - `GLOSSARY.md`, the task records and the fixture README were committed by
    explicit path (`9f892d9`). The user's untracked transcript export was left
    out.
  - `/trellis:finish-work` archived the parent as `completed` and appended one
    journal entry with idempotency key `textstats-report-mode-closeout-1`
    (`76aad34`).
  - The user then deleted the merged integration branch. No push from the
    fixture.
- **Skills update in this checkout.** The user ran
  `npx skills@latest add mattpocock/skills --agent claude-code` to drop legacy
  and removed skills. With one agent, the installer replaced the Claude links
  with copies and left `.agents/skills` stale.
  - The README's two-agent command (`--agent claude-code codex --yes`) was
    rerun. It restored the shared directory and link layout, updated `ask-matt`
    and added `chief-of-staff` for both runtimes.
  - `npx skills remove resolving-merge-conflicts --yes` removed the legacy copy
    and its lock entry. Merge conflicts are now resolved by the coordinator
    directly.
  - Lock: 38 skills before and after.
