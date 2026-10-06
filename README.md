# Trellis + Matt Pocock Skills

Normal Trellis is the default. Explicitly invoking a Matt skill selects the Matt
route for that work item. Small work stays light: ordinary edits, bug reports,
`/grill-me` discussions and direct `/implement` runs create no Trellis task. At a
user-only skill boundary, the agent is meant to save context, give the next
command and pause. See the evidence note below for what has actually been run.

## Files that make up this setup

Matt's skills are installed unmodified by the standard installer. Trellis files
come from `trellis init`. This integration is a small layer of local files:

| File | Purpose |
| --- | --- |
| [.trellis/workflow.md](.trellis/workflow.md) | Phase Index, routes and hook breadcrumbs. Replaces the stock workflow, including its per-turn task-consent prompt |
| [docs/agents/matt-flow.md](docs/agents/matt-flow.md) | Matt entry, record size per entry skill, handoff/resume, delegation, review |
| [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md) | Matt publication backend on Trellis tasks; this is the file `/setup-matt-pocock-skills` would otherwise write |
| `AGENTS.md` (paragraph after the Trellis block) | Points agents at the workflow and `docs/agents/` |
| `.claude/hooks/{session-start,inject-subagent-context}.py`, `.claude/commands/trellis/{continue,finish-work}.md` | Claude Code context loading, worker task binding, resume and closeout |
| `.codex/config.toml`, `.codex/hooks/{session-start,inject-subagent-context}.py`, `.codex/agents/trellis-{check,implement,research}.toml` | The same for Codex |
| `.agents/skills/trellis-{start,continue,finish-work}/SKILL.md` | Trellis start/resume/closeout skills aligned with this workflow |

`docs/validation/`, `tests/` and this README document and test this checkout.
New projects don't need them.

## Set up a new project

Requirements: Git, Python 3, Node/npx, the `trellis` CLI, and Claude Code and/or
Codex. The files above were made against Trellis **0.7.0-beta.4**. Under another
Trellis version, merge their changes into that version's generated files instead
of copying over them. From the new project's root, with this checkout at
`~/trellis`:

```bash
git init                                   # skip if already a repository
trellis init -u your-name --claude --codex # choose your platforms
npx skills@latest add mattpocock/skills --agent claude-code codex --yes

R=~/trellis
for f in .trellis/workflow.md docs/agents/matt-flow.md docs/agents/issue-tracker.md \
  .claude/hooks/session-start.py .claude/hooks/inject-subagent-context.py \
  .claude/commands/trellis/continue.md .claude/commands/trellis/finish-work.md \
  .codex/config.toml .codex/hooks/session-start.py .codex/hooks/inject-subagent-context.py \
  .codex/agents/trellis-check.toml .codex/agents/trellis-implement.toml \
  .codex/agents/trellis-research.toml .agents/skills/trellis-start/SKILL.md \
  .agents/skills/trellis-continue/SKILL.md .agents/skills/trellis-finish-work/SKILL.md
do mkdir -p "$(dirname "$f")" && cp "$R/$f" "$f"; done
```

Skip the `.claude` or `.codex` files for a platform you didn't initialize. Then
add this paragraph to `AGENTS.md` after the Trellis-managed block. Edits outside
that block survive `trellis update`:

```markdown
For work in this project, load the compact workflow with
`python3 .trellis/scripts/get_context.py --mode phase` before choosing a route.
It governs local orchestration even when bundled skill examples prescribe extra
stages. Matt entry/resume details: `docs/agents/matt-flow.md`; publication:
`docs/agents/issue-tracker.md`.
```

Check that `python3 .trellis/scripts/get_context.py --mode phase` mentions
"explicitly invokes a Matt skill". Then review and commit the result, and start a
fresh agent session. Codex hooks also need `features.hooks = true` in
`~/.codex/config.toml` and a one-time `/hooks` approval, as `trellis init` reports.

Don't run `/setup-matt-pocock-skills` for this layout: `docs/agents/issue-tracker.md`
already configures Trellis tasks as the tracker. Rerun it only to switch to a
hosted tracker. When adopting these files into an existing project, keep its
custom hooks and instructions and merge entry points rather than replacing them.
`trellis update` reports the files above as user modifications. Review its
changes and keep the local edits.

## Update the Matt skills

Rerun the same `npx skills@latest add mattpocock/skills …` command for current
upstream skills. The standard installer manages skill contents, metadata, links
and `skills-lock.json`. This integration needs no policy patches, wrappers,
pinned revision or copy mode. Review installer changes and refresh the runtime's
skill catalog. An upstream update can add or remove skills or change their
invocation policy.

## Use

Pick the entry by the situation. Codex uses `$skill` where Claude Code uses `/skill`.

| Situation | You type | What happens |
| --- | --- | --- |
| Small, clear change | A plain request, e.g. "Correct the typo in the help text and run the check. Leave it uncommitted." | Normal Trellis: edit, check, report. No task |
| Bug report: you describe the symptom, not the fix | A plain request, e.g. "`textstats` prints 4 words for `hello   world`; fix it." | Stock `diagnosing-bugs`: reproduce, then fix, then a regression test. No task |
| Small idea to settle before building | `/grill-me <idea>` | Stateless interview: no task, glossary or ADR. Ends with an `/implement <scope>` command for you to run |
| Small settled build | `/implement <scope>` | Builds directly with `tdd` and `code-review`. No spec, tickets or task |
| Feature that deserves a durable record | `/grill-with-docs <idea>` | Interview with `GLOSSARY.md`/ADRs. A minimal Trellis task carries the handoff |
| Published spec with tickets | `/implement-spec <task>` | Works the tickets as a task graph on an integration branch. Without a spec it stops and offers `/implement` |
| Uncertainty spanning sessions | `/wayfinder <goal>` | Planning only, until you authorize delivery |

Stock `/implement` commits to the current branch. Agents have treated invoking
it as commit permission. Say "leave it uncommitted" in the request to prevent
that. The installed `code-review` reviews `<fixed-point>...HEAD`, so without a
commit, review stays pending. Recorded authorization for larger work reads like:

> Implement the agreed scope. Choose routine engineering details, fix and recheck
> defects, and leave all changes uncommitted. Do not push.

When a needed skill requires user invocation, the agent gives the actual next
command and pauses. Stateful entries (`grill-with-docs`, `wayfinder`) reference a
task path:

```text
/implement .trellis/tasks/09-29-csv-import      # Codex: $implement …
```

Same-session small work references the agreed scope instead. Handoffs keep the
answers and authorization already given. Specification, ticketing, retro and
spec updates are selected when useful, not a mandatory pipeline. Stock `retro`
requires user invocation. If an update removes a needed skill, the agent reports
it instead of reconstructing it.

Resume with the exact task reference, `$trellis-continue` in Codex, or
`/trellis:continue` in Claude Code. Resume recovers task progress and any pending
skill command; it does not itself invoke a user-only Matt skill. `/grill-me` and
other task-free work have nothing to resume after the session ends. Closeout
retains planning/no-commit boundaries, reconciles prior archives and journal
entries, and uses explicit no-auto-commit lifecycle calls.

## Runtime limits and evidence

Skill discovery, invocation controls and tool permissions are separate. A file
read is an ordinary loading mechanism where the harness permits it; it cannot
bypass a user-only invocation boundary. Claude Code uses the upstream
`disable-model-invocation` frontmatter; Codex uses upstream `agents/openai.yaml`
policy, including `allow_implicit_invocation`. Do not infer Codex controls from
Claude frontmatter. Project trust and hook approval are also
separate. Keep existing hook registrations, avoid duplicates, and verify actual
instruction/context loading in the runtime being used.

Independent ready tickets can run in parallel when tools and file ownership
permit. The coordinator joins results, owns task lifecycle and shared Git
operations, and fixes verified defects within the recorded repair budget.
Codex workers explicitly validate and load their dispatched task context when
native events lack the dispatch prompt. That loads task data; it does not grant
permission to invoke a skill.

In Claude Code, `implement-spec` workers that must call `tdd` run as general-purpose
agents, because `trellis-implement` has no Skill tool. Their worktrees don't contain
uncommitted planning files, so the dispatch gives absolute paths to the spec and
ticket in the main checkout. Workers leave edits uncommitted; the coordinator
reviews, commits and merges. The coordinator resolves merge conflicts itself,
without asking, and reports how. Code that git merges without a conflict can still
be wrong. In the recorded run, git flagged the option definitions as conflicting.
It merged the output dispatch without a conflict, and that merged code dropped the
`--min-length` filter from `--json`. Review the merged code, not only the conflict
hunks.

The current `code-review` installation reviews `<fixed-point>...HEAD`, which
excludes uncommitted edits. Review requiring a commit stays pending without commit
permission. Check the installed skill's contract after updates, and never count
an empty diff as acceptance of working-tree changes.

[Current stock-installation evidence](docs/validation/stock-installation.md)
records the installer run, installed policies, a seeded Codex handoff check and
Claude Code checks:
- **`grill-with-docs` handoff:** the first run implemented inline. After a
  routing fix, one retest recorded a task, returned `/implement <task>` and paused,
  and one fresh session recovered it.
- **Small-task routes (2026-10-05):** the first bug-report run fixed the bug
  without `diagnosing-bugs`. After a wording fix, the plain small-change and
  bug-report routes each passed 4 of 4 headless Claude Code runs. `/grill-me` →
  `/implement` and `/implement-spec` without a spec passed once each.
- **Durable routes (2026-10-05, Claude Code, once each):** passed.
  - `/grill-with-docs` recorded a task and paused with `/to-spec <task>`.
  - A fresh session recovered that command.
  - `/to-spec` and `/to-tickets` published a spec and three tickets.
  - `/wayfinder` published a map and resolved a research ticket, without code.
- **`/implement-spec` on that spec (once):** passed. It built three tickets in
  parallel worktrees with `tdd` and integrated them on a branch. It reviewed with
  `code-review`, fixed two findings and archived the tickets. At the user's
  request, a second review found no spec issues and four minor style issues;
  those were fixed. The branch was then merged and the task closed out with
  `/trellis:finish-work`.
- **New-project setup:** the procedure above was run once in a scratch project.
- **Not run:** Codex with the current routing text (preliminary runs are
  recorded in the evidence).

Earlier [validation reports](docs/validation/README.md) describe the historical
patched setup and independent runtime fixes; they do not establish automatic
end-to-end delivery with the current stock installation.
