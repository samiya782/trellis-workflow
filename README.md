# Trellis + Matt Pocock Skills

Keep normal Trellis for everyday work. Explicitly enter Matt with
`$grill-with-docs` (or `$wayfinder` for multi-session uncertainty), settle the
material questions, and authorize a scope. Codex then selects the needed **real
Matt skills**, implements ready work, fixes and rechecks within bounds, and
completes authorized closeout without asking for another stage command.

This is project configuration, not a replacement skill methodology or a new
orchestration service. Automatic continuation lasts while the Codex session can
run; durable task records support recovery after an interruption.

## Tested baseline and evidence

Baseline: `ca67648`, including the existing Claude integration. Tested tools:
Trellis **0.7.0-beta.4** (CLI and core), Codex CLI **0.159.0**, Skills installer
**1.7.0**, and Matt skills at
[`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60).
The source bodies of the main installed Matt stages match that upstream revision.

Validation includes 17 regression tests, a fresh 18-test delivery/repair run,
actual parallel implementation and review, planning-only Wayfinder, and retro.
The controlled small-edit test reduced shell-output characters by 95.3%; this
is a measured load reduction for that test, not a universal token estimate.
Detailed runs, sanitized history, source research and measurements
live in [docs/validation](docs/validation/README.md). They distinguish observed execution,
static checks and untested behavior. Claude skill files are preserved; **this
change does not claim a fresh Claude Code harness test**. OMC autopilot/team were
studied for bounded continuation and ownership; OMC is not a dependency.

## Install in a project

The target needs Git, Python 3, Node/npx, Codex and an initialized Trellis project.
The following pinned Matt installation was executed in this checkout:

```bash
# Only for a project that has not already initialized Trellis:
npx --yes @mindfoldhq/trellis@0.7.0-beta.4 init -u your-name --codex --yes

# Project scope; complete upstream skills and supporting resources:
npx --yes skills@1.7.0 add \
  https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60 \
  --agent codex --yes \
  --skill grill-with-docs wayfinder grilling domain-modeling to-spec to-tickets \
          implement tdd code-review retro writing-for-agents research
```

From this integration checkout, copy or merge these files into the target:

| File | Purpose |
| --- | --- |
| `.trellis/workflow.md` | Compact default routing and runtime-required steps/breadcrumbs |
| `docs/agents/matt-flow.md` | Matt continuation, authorization, delegation and review ordering |
| `docs/agents/issue-tracker.md` | Trellis `Other` publication backend |
| `scripts/configure_codex_matt.py` | Reversible Codex invocation metadata adapter |
| `.agents/skills/trellis-start/SKILL.md` | Compact startup using the current workflow |
| `.agents/skills/trellis-continue/SKILL.md` | Artifact-based resume without repeated approvals |

Preserve existing project customizations when merging. Keep Trellis's managed
`AGENTS.md` block and add the short navigation paragraph outside it from this
checkout's [AGENTS.md](AGENTS.md). That paragraph loads the compact Phase Index
and points to the two on-demand adapters. Do not inject this README or validation
reports into every session. No application changes or global settings are needed.

Then run in the target project:

```bash
python3 scripts/configure_codex_matt.py
python3 scripts/configure_codex_matt.py --check
npx --yes skills@1.7.0 list --agent codex --json
```

Start a fresh Codex session. The adapter changes **only** OpenAI invocation
metadata: `to-spec`, `to-tickets`, `implement`, and `retro` may be selected after
Matt route authorization; `grill-with-docs` and `wayfinder` stay explicit-only.
Bodies and resources remain genuine upstream files. `.claude/skills` is untouched.
The project workflow prevents these newly discoverable skills from silently
selecting Matt for normal work.

Commit the installer-generated lock and integration changes according to your
project policy. This checkout ignores generated Codex Matt directories and uses
the pinned command to restore them. The existing Claude installation stays
tracked. A lock records source provenance, not the subsequent metadata override.
Before updating skills, restore the metadata, install the new source, then apply
and check again. To undo the metadata changes, run
`python3 scripts/configure_codex_matt.py --restore`. If upstream metadata already
changed, reconcile the reported drift instead of overwriting it blindly.

Use independent installed directories for adapted Codex skills. A `SKILL.md`
symlink to a Claude copy also makes Codex resolve metadata beside that canonical
target, defeating a separate OpenAI policy override. See the
[upstream investigation](docs/validation/upstream.md).

## Entry examples

Ordinary small work needs no Matt ceremony:

> Correct the typo in the help text and run the relevant check. Leave it uncommitted.

Explicit Matt entry:

> $grill-with-docs Add CSV import with a preview. Help settle the behavior first;
> once we agree on scope, carry it through implementation and verification locally.

A useful scope answer can cover several boundaries at once:

> Use the agreed API test seam. The proposed three tickets and blockers are right.
> Implement that scope, choose routine engineering details, fix and recheck defects,
> and make local commits and archive the completed tasks. Do not push.

No need to repeat `$to-spec`, `$to-tickets`, `$implement`, `$code-review` or
`$trellis-check` after that authorization. Their actual use is recorded. Small
settled contracts may need fewer skills; a multi-ticket task uses the real ticket
skill. Existing answers satisfy later questions only when they cover the choice.

For planning across sessions:

> $wayfinder Plan a replacement for our import system. Keep this planning-only.

Wayfinder preserves its decision/session boundaries. Planning-only authority
never becomes delivery authority automatically.

## Automation, decisions and parallelism

The agent asks about unresolved behavior, testing seams, scope or permissions.
It does not ask the user to approve the same scope under a new stage name.
Specification, ticketing, review, retro and spec updates are selected when useful;
there is no mandatory artifact count or second Trellis copy of Matt's output.

The coordinator reads blocker edges and dispatches ready independent tickets when
concurrency helps. Each worker receives an exact task/skill path, acceptance,
context pointers and exclusive file ownership. Overlapping changes need isolated
worktrees or sequential execution. The coordinator alone mutates shared task state
and Git, joins results, and starts dependent integration after verified blockers.
Tool availability and observed overlap determine whether a run was parallel.

Checkers can fix bounded defects without another command. After a change, rerun
affected checks and review, then verify the integrated result. Stop after three
unsuccessful repair cycles, or immediately for a material decision or missing
permission. Successful evidence can be reused for an unchanged revision and scope.
This bound is workflow guidance, not a hook-enforced autonomous daemon.

Matt's installed `code-review` inspects `<base>...HEAD`, excluding uncommitted
work. Therefore authorized delivery uses executable checks, a local checkpoint
commit, then the real two-axis review. Corrections are checked and committed
before reviewing the changed revision. Without commit permission, report the
pending committed review; never call an empty diff PASS. Normal small uncommitted
work can still receive its appropriate checks.

Real `retro` examines session evidence and proposes environment improvements.
`trellis-update-spec` is conditional on a reusable engineering lesson. Neither
requires the other, an artificial lesson, or a new document after every ticket.

## Recovery and closeout

> Continue `trellis-task:<complete-MM-DD-task-name>` within its recorded authorization.

Recovery reads the exact task's contract, scope, progress, current files and
verification evidence. It resumes unfinished work without repeating approved
interviews. A partial publication stays identifiable and is repaired instead of
recreated. Ambiguous task identity or changed scope requires clarification.

References resolve in the active tree or archive. Trellis moves directories on
archive without rewriting JSONL paths: resolve moved sources before redispatch.
Archive children before their parent. Closeout uses supported `--no-commit` flags
and stages only owned files when a commit is authorized. Trellis branch validation
still applies; initialization on `main` does not authorize bypassing it. No push,
external issue publication or unrelated-task cleanup is implied.

## Platform limits

- Codex skill discovery, invocation policy and runtime permissions are separate.
  A workflow reference or filesystem read does not prove skill invocation.
- Codex 0.159.0 source ignores Claude's `disable-model-invocation` frontmatter;
  Codex uses `agents/openai.yaml`. Other hosts/versions need verification.
- Fresh fixture runs observed native delegation. Copied hooks were not trusted,
  so those runs exercised explicit child context loading. This checkout's live
  session received a workflow breadcrumb. Neither observation proves all hooks
  fire in a fresh installation. Project trust and hook approval are separate.
- On 0.159.0 the hooks and multi-agent feature flags were already enabled; older
  generated config comments describe older defaults. Do not change global flags
  or bypass approvals to reproduce these tests. Use available tools and fallbacks.
- Claude retains its upstream human-only invocation policy. Where its harness
  requires another invocation, report that limitation; Codex metadata does not
  alter Claude's policy. Existing Claude source/history evidence is retained.
- Runtime permission denials, unavailable tools, budget limits or session exits
  can interrupt delivery. Persist the next action; do not describe a blocked or
  sequential run as complete or parallel.

In the tested CLI, `codex exec --sandbox workspace-write` with approvals disabled
could edit code but could not write `.git/index.lock`. An authorized checkpoint
therefore remained pending. A fresh `codex exec --approve-for-me` run completed
the fixture commits through the runtime's automatic approval reviewer. This is
a supported guarded mode, not permission inferred from the workflow. Use a mode
your environment permits; do not bypass approvals or change global settings.

Local regression checks:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/configure_codex_matt.py --check
```

See [validation evidence](docs/validation/README.md) for ordinary fresh-session prompts,
actual skill/agent events, measurements and remaining limitations.
