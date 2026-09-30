# Trellis + Matt Pocock Skills

Keep normal Trellis for everyday work. Explicitly enter Matt with
`grill-with-docs` (or `wayfinder` for multi-session uncertainty), settle the
material questions, and authorize a scope. The agent then selects the needed
**real Matt skills**, implements ready work (in parallel where tickets are
independent), fixes and rechecks within bounds, and completes authorized closeout
without asking for another stage command. The same experience works in Claude
Code and Codex; each was set up and tested separately.

This is project configuration, not a replacement skill methodology or a new
orchestration service. Automatic continuation lasts while the session can run;
durable task records support recovery after an interruption.

## Tested baseline and evidence

Trellis **0.7.0-beta.4**, Skills installer **1.7.0**, Matt skills at
[`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60).
Installed Claude and Codex Matt bodies are byte-identical to that revision apart
from the invocation-policy adaptations below.

- **Claude Code 2.1.284**: fresh headless sessions with ordinary requests covered
  normal work, authorized delivery with parallel workers, an interrupted delivery
  resumed in a new session, planning-only Wayfinder, a no-commit boundary, a repair
  stop and a repeated closeout. See [claude.md](docs/validation/claude.md).
- **Codex CLI 0.159.0**: delivery, parallel implementation/review, resume,
  planning-only Wayfinder and retro. See [validation](docs/validation/README.md).

26 local regression tests exercise the adapters and the installed Trellis runtime
in disposable repositories. Measured reductions (Phase Index, small-task reads) are
specific loads, not a total token saving: a Matt session is dominated by skill
bodies, task files and reviews, and the downstream skills add listing text.

## Install in a project

The target needs Git, Python 3, Node/npx and an initialized Trellis project.
Initialize Trellis only if the project doesn't have it yet:

```bash
npx --yes @mindfoldhq/trellis@0.7.0-beta.4 init -u your-name --claude --codex --yes
```

(Each flag was tested on its own; drop the one you don't need.) Then install the
genuine skills per platform, as below. From this checkout, copy or merge:

| File | Purpose |
| --- | --- |
| `.trellis/workflow.md` | Compact default routing and runtime-required steps/breadcrumbs |
| `docs/agents/matt-flow.md` | Matt continuation, authorization, delegation and review ordering |
| `docs/agents/issue-tracker.md` | Trellis `Other` publication backend |
| `scripts/configure_codex_matt.py` | Codex invocation adapter; also shared helpers for the Claude adapter |
| `scripts/configure_claude_matt.py` | Claude Code invocation adapter |
| `.claude/hooks/inject-subagent-context.py` | Claude: honors `Active task:` for parallel workers |
| `.claude/commands/trellis/continue.md` | Claude: artifact-based resume without repeated approvals |
| `.agents/skills/trellis-start/SKILL.md`, `trellis-continue/SKILL.md` | Codex: compact start and resume |

Preserve existing project customizations when merging. Keep Trellis's managed
`AGENTS.md` block and add the short navigation paragraph outside it from this
checkout's [AGENTS.md](AGENTS.md). Claude Code 2.1.284 and Codex both load
`AGENTS.md` natively; no `CLAUDE.md` is needed. Do not inject this README or
validation reports into every session. No application changes or global settings.

### Claude Code

```bash
npx --yes skills@1.7.0 add \
  https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60 \
  --agent claude-code --copy --yes \
  --skill grill-with-docs wayfinder grilling domain-modeling to-spec to-tickets \
          implement tdd code-review retro writing-for-agents research
python3 scripts/configure_claude_matt.py
python3 scripts/configure_claude_matt.py --check
```

Upstream marks every stage `disable-model-invocation: true`. Claude Code then
refuses Skill-tool calls to `to-spec`, `to-tickets`, `implement` and `retro` and
tells the agent not to reproduce them another way; a `skillOverrides` setting
cannot re-enable them. The adapter changes only that frontmatter value for those
four and keeps `grill-with-docs` and `wayfinder` user-only. Bodies are untouched.
`--copy` matters: the adapter refuses symlinked skill files so it can never edit
another agent's canonical copy. Start a fresh session (or run `/skills`) to check.

### Codex

```bash
npx --yes skills@1.7.0 add \
  https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60 \
  --agent codex --yes \
  --skill grill-with-docs wayfinder grilling domain-modeling to-spec to-tickets \
          implement tdd code-review retro writing-for-agents research
python3 scripts/configure_codex_matt.py
python3 scripts/configure_codex_matt.py --check
npx --yes skills@1.7.0 list --agent codex --json
```

Codex ignores Claude's frontmatter and uses `agents/openai.yaml`. The adapter
changes only `allow_implicit_invocation` for the same four stages; entries stay
explicit. Use independent installed directories: a `SKILL.md` symlink to a Claude
copy makes Codex resolve metadata beside that target, defeating the override (see
[upstream investigation](docs/validation/upstream.md)). This checkout ignores the
generated Codex Matt directories and restores them with the pinned command.

The workflow keeps newly invocable stages from silently selecting Matt for normal
work. Fresh Claude runs confirmed this, including a request phrased "Implement the
following spec…".

## Entry examples

Ordinary small work needs no Matt ceremony:

> Correct the typo in the help text and run the relevant check. Leave it uncommitted.

Explicit Matt entry (Claude Code types `/`, Codex types `$`):

> /grill-with-docs Add CSV import with a preview. Help settle the behavior first;
> once we agree on scope, carry it through implementation and verification locally.

The agent asks one round of numbered questions with recommendations. A useful
answer can cover several boundaries at once — "Agree with all." is enough when
the recommendations already say it:

> Use the agreed API test seam. The proposed three tickets and blockers are right.
> Implement that scope, choose routine engineering details, fix and recheck defects,
> and make local commits and archive the completed tasks. Do not push.

No need to repeat `to-spec`, `to-tickets`, `implement`, `code-review` or
`trellis-check` after that authorization. Existing answers satisfy later skill
questions (test seam, ticket breakdown) only when they cover the choice.

For planning across sessions:

> /wayfinder Plan a replacement for our import system. Keep this planning-only.

Wayfinder preserves its decision/session boundaries. Planning-only authority
never becomes delivery authority automatically.

## Automation, decisions and parallelism

The agent asks about unresolved behavior, testing seams, scope or permissions.
It does not ask the user to approve the same scope under a new stage name.
Specification, ticketing, review, retro and spec updates are selected when useful;
there is no mandatory artifact count or second Trellis copy of Matt's output.

The coordinator reads blocker edges and dispatches ready independent tickets
together (Claude Code: several `Agent` calls in one message; Codex: `spawn_agent`).
Each worker receives `Active task: <path>`, the skill path, acceptance, context
pointers and exclusive file ownership. Overlapping changes need isolated worktrees
or sequential execution. The coordinator alone mutates task state and Git, joins
results, verifies blockers, and then starts dependent integration. Tool
availability and observed overlap determine whether a run was parallel.

Checkers can fix bounded defects without another command. After a change, rerun
affected checks and review, then verify the integrated result. Stop after three
unsuccessful repair cycles, or immediately for a material decision or missing
permission. Successful evidence can be reused for an unchanged revision and scope.
This bound is workflow guidance, not a hook-enforced autonomous daemon.

Matt's installed `code-review` inspects `<base>...HEAD`, excluding uncommitted
work. Authorized delivery therefore runs executable checks, a local checkpoint
commit, then the real two-axis review. Corrections are checked and committed
before reviewing the changed revision. Without commit permission the agent
reports the committed review as pending; it never calls an empty diff PASS.

Real `retro` examines session evidence and proposes environment improvements.
`trellis-update-spec` is conditional on a reusable engineering lesson. Neither
requires the other, an artificial lesson, or a new document after every ticket.

## Permissions

Workflow authorization and runtime permission are separate. Recording "local
commits authorized" never grants a tool the runtime denies, and a runtime grant
never widens the recorded scope. Use a permission mode your environment allows;
never bypass approvals or change global settings to reproduce these tests.

- **Claude Code**: interactive sessions prompt for unlisted tools. Headless runs
  (`claude -p`) deny them instead; pass a narrow `--allowedTools` list (e.g.
  `Bash(python3:*) Bash(git:*) Skill Agent`) with `--permission-mode acceptEdits`.
  Claude Code still blocks some allowlisted Bash shapes (`cd` + git, variable
  expansion, loops); agents retried with simpler commands. Subagents may not
  write report files; research workers return findings for the coordinator.
- **Codex**: `codex exec --sandbox workspace-write` with approvals disabled could
  edit code but not write `.git/index.lock`, so an authorized checkpoint stayed
  pending. `codex exec --approve-for-me` completed the commits through the
  runtime's automatic approval reviewer — a supported guarded mode.

A denied tool is a boundary: the agent persists evidence and the next action and
asks, rather than reporting a blocked or sequential run as complete or parallel.

## Recovery and closeout

> Resume the task at `.trellis/tasks/<MM-DD-task-name>` within its recorded authorization.

Recovery reads the exact task's contract, scope, progress, current files and
verification evidence, even in a new session. It resumes unfinished work without
repeating approved interviews. A partial publication stays identifiable and is
repaired instead of recreated. Ambiguous task identity or changed scope requires
clarification. Claude also offers `/trellis:continue`; Codex `$trellis-continue`.

References resolve in the active tree or archive. Trellis moves directories on
archive without rewriting JSONL paths: resolve moved sources before redispatch.
Archive children before their parent. Closeout uses supported `--no-commit` flags
and stages only owned files when a commit is authorized; running closeout again
changes nothing. Trellis branch validation still applies. No push, external issue
publication or unrelated-task cleanup is implied.

## Rollback

```bash
python3 scripts/configure_claude_matt.py --restore   # exact original frontmatter
python3 scripts/configure_codex_matt.py --restore    # exact original openai.yaml
```

Both keep byte-exact backups under `.trellis/.runtime/` and refuse to restore over
later edits; reconcile reported drift instead of overwriting it. Before updating
skills, restore, reinstall, then apply and `--check` again: `skills-lock.json`
records source provenance, not the policy change. Revert the copied workflow,
docs, hook and command files with your VCS. The hook change is a local edit to a
Trellis-managed file; `trellis update` treats it as user-modified — merge rather
than overwrite, or re-apply it afterwards.

## Platform limits

- Skill discovery, invocation policy and runtime permissions are separate. A
  workflow reference or file read does not prove skill invocation.
- Claude Code: SessionStart, UserPromptSubmit and subagent hooks fired in fresh
  headless sessions. Native worker injection used the single session pointer until
  the `Active task:` fix; observe injection in worker transcripts rather than
  inferring it from an agent name. Interactive TUI prompts and `AskUserQuestion`
  were not exercised.
- Codex 0.159.0: fresh fixture runs observed native delegation, but copied hooks
  were untrusted, so those runs exercised explicit child context loading. Project
  trust and hook approval are separate. Hooks and multi-agent flags were already
  enabled; older generated config comments describe older defaults.
- The generic Trellis `finish-work` text still describes auto-commit archiving; the
  workflow's closeout rule governs. Literal three-failure termination and
  unattended persistence after session exit are untested on both platforms.

Local regression checks:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/configure_claude_matt.py --check
python3 scripts/configure_codex_matt.py --check
```

See [validation evidence](docs/validation/README.md) for prompts, actual
skill/agent events, measurements and remaining limitations.
