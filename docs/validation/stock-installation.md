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
