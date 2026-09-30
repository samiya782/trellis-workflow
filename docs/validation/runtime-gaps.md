# Incremental runtime gaps — 2026-09-29

This record extends the earlier evidence; it does not replace the delivery matrix
or [Claude execution record](claude.md). Baseline `fdb57d2` was clean. The latest
commit, working tree, installed sources and prior validation were inspected first.
All new repository changes remain uncommitted. Reference projects are read-only;
commits and archive experiments occur only in disposable fixtures.

## Context isolation

Codex 0.159.0 `SubagentStart` supplies a parent session ID and role but no dispatch
prompt. In the current native collaboration runtime, the dispatch is delivered
after the start hook and is encrypted in the raw spawn/transcript representation.
Reading the shared task pointer at start therefore cannot establish the worker's
explicit identity. The previous hook could inject a different task before the
worker received its assignment.

The hook now injects only a `trellis-context-loader` notice and exact parent ID.
The role reads its full current dispatch, then calls the existing hook script's
explicit `--load-context` interface with every `Active task:` value. The validated
output has a distinct `trellis-context-loaded` marker. Missing, malformed,
conflicting, out-of-tree and escaping symlink paths return no task context.
The supported symlink of the entire `.trellis` directory to an external store
still works; symlinks escaping its tasks tree do not. An explicit identity needs
no parent session. `--no-explicit-task` is available
only after the worker determines that its dispatch has no marker; it resolves
the exact parent session, never the environment or another session's pointer.

This is **native loading guidance plus explicit task loading**, not native task
artifact injection or native skill invocation. No transcript scraping, shared
dispatch map, hook registration, trust bypass or invocation-policy workaround was
added. A denied loading tool remains a denial. Claude's existing explicit-marker
hook now denies invalid/conflicting dispatches instead of allowing the worker's
legacy fallback to pick one; only its Python hook API is tested in this increment,
not the Claude harness.

The implementation was checked against the installed-version source at
`rust-v0.159.0` (`377f7f557a6bdea0f3a2d26d4d899c66db4789d0`) and current
[official hook documentation](https://learn.chatgpt.com/docs/hooks).
The current parent harness dispatched three real `trellis-check` workers with
`fork_turns=none`. All three native transcripts contain exactly one 361-character
loader notice at line 9, with the parent ID and no task artifacts. The shared
pointer named the main integration task throughout; two disposable probe tasks
were never activated.

Their native turn records report `gpt-6-astra`, `danger-full-access` and approvals
`never`, inherited from this already-configured parent harness. The probes are
read-only; no permission mode was changed. These effective records take precedence
over inferring sandbox behavior from the role TOML's workspace-write setting.
The fresh CLI experiments below use their separately stated guarded modes.

| Native thread | Actual loading evidence |
| --- | --- |
| `01a0f038-259e-70c3-9bd1-d8997e7c0769` | A: explicit loader tool call, own sentinel once, neither B nor main PRD; later conflicting A/B dispatch passes both values and returns no context |
| `01a0f03a-17cc-74f2-a047-d34040956a1d` | B: own sentinel once, neither A nor main PRD; later nonexistent path errors without fallback |
| `01a0f03a-2824-75f0-8bb3-a6e7ca6eaa35` | No marker: explicit loader uses the notice's exact parent ID and loads the main task with its no-commit boundary |

These are controlled native diagnostic dispatches, not ordinary feature delivery
or a speedup/concurrency benchmark. The two probe directories were removed after
capture. Selected actual tool calls and native line references are preserved in
[runtime-gaps.json](runtime-gaps.json). The role behavior is observed; the helper's
refusal to substitute another task is also covered by deterministic regressions.

## Authorization and closeout sources

Both platform `session-start.py` files now direct the agent to recorded scope and
the existing workflow instead of demanding a new start review, more artifacts or
task-creation consent. Stale references resolve against archives before cleanup.
Codex's `session-start.py` is not registered by this checkout's current hook config;
its subprocess test is not evidence of native startup execution.

The shared finish skill and Claude finish command now carry the same instructions:
continue authorized unfinished work, preserve planning/no-commit boundaries,
scope commits to owned paths even with unrelated staged work, archive children
first with `--no-commit`, and journal with `--no-commit` and a stable retry key.
Direct finish no longer returns the user to a separate commit command. Existing
archive/journal/commit evidence is reconciled before retrying. The installed
`add_session.py --idempotency-key` support is reused; no lifecycle engine changed.

Focused regressions include real hook subprocesses and an interrupted journal
append/index update in a disposable Git repository. Retrying the same operation
repairs the index without appending twice, including after its explicit fixture
commit. These tests do not simulate runtime approval or autonomous agent behavior.

Three fresh CLI sessions used only the ordinary request
`Finish <exact original task path> using trellis-finish-work.` Each actually read
the shared finish skill. No stage reminders, clarification or command handoffs.

| Case / thread | Observed result |
| --- | --- |
| Direct finish: `01a0f033-f680-7003-b1c7-4387d85a34de` | Recorded implementation/commit/closeout authorization recovered; verified dirty correction committed as `1e33c84`; remaining child then parent archived with `--no-commit`; one journal with retry key/`--no-commit`; explicit closeout commit `59f2be9` |
| Fresh repeat: `01a0f037-1373-79f3-b09a-988f6e51fad0` | Original path resolved in archive; HEAD, Git status, staged blob, task identities, journal and index unchanged |
| Planning/no-commit: `01a0f033-f668-7cf1-af95-bf09591c3a0a` | Ready metadata did not override planning-only/no-commit/no-archive authorization; planning journal recorded, task still planning, code unchanged, no commit/archive/staging |

Direct finish began after a controller-seeded partial archive, with one child
already moved and an unrelated file already staged. This is interrupted-state
recovery, not a claim that this run was killed. Both commits excluded that file;
its original bytes and staged blob remained unchanged. The complete before/after
repeat audit matches. Fixtures live under `/tmp/runtime-closeout-x8zmv427`.
Direct/repeat used `--approve-for-me`; planning used workspace-write/never. No
denials or review rejections were observed. These CLI sessions had no native hook
markers; their actual skill reads are explicit loading, not native invocation.

## Repair-budget resume

Fresh thread `01a0f030-a0cd-7432-be1d-212f4564dd54`, fixture
`/tmp/trellis-budget-resume-6lcxqfnf`, ordinary request:

> Resume the task at .trellis/tasks/09-29-sum-repair within its recorded authorization.

The controller seeded three different incorrect implementations and ran three
real failing unittest checks, recording their results in task progress. The fresh
agent loaded the existing workflow, recognized the recorded limit, proposed the
obvious fix but did not edit code or run a fourth repair cycle. It recorded the
boundary and asked for authorization for one additional cycle. No commit/archive.
No workflow change was necessary.

This establishes **resume preserves an exhausted recorded budget**. It does not
establish literal three-failure exhaustion by an autonomous agent. The earlier
Claude latency stop remains an earlier material-decision stop, not that proof.
Mode: `codex exec --sandbox workspace-write -c 'approval_policy="never"'`, no
trust override/bypass. Wall time 103.995 s; CLI usage 196,829 input, 177,280 cached
input, 1,991 output tokens. Those counters are cumulative across turns, not unique
context or a cost/speed benchmark.

## Existing-project installation and loading

The representative source is `/home/samiya/srd/InduPolicy`, already on Trellis
0.7.0-beta.4, HEAD `d4e00a07d95bf7b264dd8fdbae306e1b480d2907`. The isolated copy at
`/tmp/trellis-existing-indupolicy-_3qry4lp` preserves 45 active tasks, 35 archives,
34 spec documents and both existing platform installations. It is a copy of the
Trellis control files and project documentation, not the nested application repos.
Secrets/environment files, runtime state, caches, original Git metadata and
symlinks were excluded. Reference originals were hashed to check read-only use.

Both exact pinned README skill-install commands ran successfully in the copy:
Skills 1.7.0, Matt `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`, Claude `--copy` and
independent Codex directories. Both adapters apply/check successfully. Across 58
upstream files, differences are confined to four Claude frontmatter values and
four Codex metadata policies. All twelve Markdown bodies match across platforms
after excluding frontmatter. Existing unrelated skills were retained (49 project
Codex listings), so prior minimal-catalog overhead numbers do not apply here.

Files replaced during the integration merge were first checked against the
existing template hashes. The existing AGENTS managed block was preserved and
navigation appended outside it. Existing settings and hook registrations were
preserved. This tests merging the documented local integration into an existing
installation, not using `trellis init` to overwrite a customized project.

Instruction inventory covered `/`, `/home`, `/home/samiya`, `/home/samiya/srd`
and the source project, plus relevant `.claude` locations. No `CLAUDE.md` or
`CLAUDE.local.md` ancestor was found; `~/.claude/CLAUDE.md` is empty. Home
`AGENTS.md` exists (19,403 bytes, OMX instructions). Earlier native InduPolicy
sessions on Codex 0.157.1 loaded project AGENTS once without that home text;
existence alone does not prove loading. The `/tmp` copy avoids that ancestor,
so its new observation does not establish arbitrary ancestor precedence.

Static hook-registration inspection found disjoint Claude startup/clear/compact
matchers and distinct Task/Agent entries, not duplicated startup execution.
Codex has one matching registration per relevant event. Static registration
counts do not prove execution. Project trust and hook approval are separate;
the experiment does not grant hook trust or run Claude.

The one fresh ordinary request was:

> In docs/infra/README.md, add “Local validation copy.” as a final standalone paragraph. Leave changes uncommitted.

Thread `01a0f036-9048-7962-a306-650f65759c1f`, workspace-write/never, exit 0.
Native line 6 contains project AGENTS exactly once, with one managed block and
navigation paragraph; it was not shell-read. The native catalog has 37 unique
eligible names, distinct from the installer's 49 on-disk listings. No hook events
or injected workflow state were observed. The agent explicitly read trellis-start,
the Phase Index and context; six shell commands produced 7,875 output characters.
Only the requested README paragraph changed, uncommitted; no task or Matt route,
worker, approval question or stage handoff. This is the sole new session for the
existing-project installation. Across its 158 role manifests, none references its
own PRD/design/implementation artifact; this checks the earlier duplication cause.

### Fixture trust side effect and cleanup

Exact trust entries for the four new CLI fixture paths appeared in user Codex
config during execution, despite no trust flags or explicit config-writing
commands. The existing-project entry's config timestamp was 77 ms after launch.
No pre-run global byte snapshot exists, so the precise writer is an inference,
not a proven internal mechanism. This prevents claiming zero transient global
mutation. After all CLI runs, the coordinator removed **only those four fixture
entries**, verifying all other parsed config values unchanged. No hook approval,
feature setting or permission default was changed. The scoped cleanup hashes and
paths are recorded in runtime-gaps.json; no user config content is published.

## Incremental validation cost and preservation

| Fresh CLI experiment | Wall seconds | Cumulative input / cached input / output |
| --- | ---: | --- |
| Existing project | 31.581 | 78,612 / 64,128 / 544 |
| Direct finish | 163.520 | 540,816 / 488,960 / 3,956 |
| Repeated finish | 61.335 | 119,275 / 95,104 / 1,465 |
| Planning finish | 95.058 | 201,399 / 179,072 / 2,308 |
| Exhausted-budget resume | 103.995 | 196,829 / 177,280 / 1,991 |

Five new ordinary CLI requests; no full delivery-matrix rerun. Wall times sum to
455.489 seconds of subprocess duration, with some overlap; not elapsed task time
or a speedup claim. Usage excludes this coordinator and separate native workers;
no dollar-cost estimate. No avoidable stage-command handoff occurred. The budget
question and invalid worker-identity errors are intentional boundaries.

Baseline regressions: 26 tests, 4.425 s. Final: **40 tests, 7.264 s**. Fourteen
added tests cover the requested gaps. Focused regressions ran before new sessions.
Final review found and fixed the external-store rejection and Claude fallback
loophole; the new store regression failed before the fix, then worker/Claude
regressions and the joined suite passed. The independent checker rechecked both
fixes with no remaining findings. Both policy adapters, Python/TOML parsing and
`git diff --check` pass; no configured lint/typecheck is claimed.

Workflow remains **8,572 characters**, Phase Index **1,337**, AGENTS **1,569**:
all byte-identical to HEAD. All 24 genuine Matt SKILL.md files are unchanged.
The three on-demand Codex role definitions add 664–682 characters each (about
166–171 tokens at chars/4, explicitly an estimate). Their native loader notice
is 361 characters, followed by the actual task-file output: deferring injection
is an isolation fix, not a claim to eliminate required context. Finish skill
adds 142 characters; Claude finish command adds 186. Detailed evidence remains
outside startup instructions. Prior Claude evidence is unchanged.

## Remaining limits

- Native Codex task-artifact push at SubagentStart cannot safely select explicit
  worker identity with the tested event shape; supported explicit loading is used.
- New hook trust approval and interactive TUI permission prompts are not exercised.
- Claude source compatibility and Python regressions supplement the prior Claude
  evidence; no new Claude harness execution is claimed.
- Literal autonomous three-failure exhaustion, arbitrary ancestor configurations,
  all runtime permission modes and post-exit autonomous persistence remain untested.
