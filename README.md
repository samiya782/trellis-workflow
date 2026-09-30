# Trellis + Matt Pocock Skills

Normal Trellis is the default. Choose `grill-with-docs` for explicit Matt
requirements discovery or `wayfinder` for planning across sessions. The agent
continues within the agreed scope where the stock skills and harness allow it.
At a user-only skill boundary, it saves context, gives the next command and pauses.

## Install and update

Use an initialized Trellis project with Git, Python 3, Node/npx, and the Claude
Code or Codex runtime you plan to use. From the project root, run:

```bash
npx skills@latest add mattpocock/skills --agent claude-code codex --yes
```

Rerun that same command to install current upstream skills. Let the standard
installer manage skill contents, metadata, links and `skills-lock.json`; this
integration requires no policy patches, wrappers, pinned revision or copy mode.
Review installer changes and refresh the runtime's skill catalog before use.
An upstream update can change available skills or their invocation policy.

This checkout's local routing lives in [.trellis/workflow.md](.trellis/workflow.md),
with [Matt entry and handoff](docs/agents/matt-flow.md) and the
[Trellis publication backend](docs/agents/issue-tracker.md) loaded on demand.
When adopting these files in an existing project, preserve its Trellis setup,
custom hooks and instructions. Inspect applicable ancestor/project instructions
and merge the platform entry points instead of replacing them wholesale.
Trellis updates may report these local workflow/hook edits as user modifications.

## Use

Ordinary requests stay on the normal Trellis route:

> Correct the typo in the help text and run the relevant check. Leave it uncommitted.

For Matt discovery, use the runtime's explicit skill syntax:

```text
# Codex
$grill-with-docs Add CSV import with a preview. Help settle the behavior first.

# Claude Code
/grill-with-docs Add CSV import with a preview. Help settle the behavior first.
```

Record scope, material decisions and permission once. For example:

> Implement the agreed scope. Choose routine engineering details, fix and recheck
> defects, and leave all changes uncommitted. Do not push.

For planning only, use `$wayfinder` in Codex or `/wayfinder` in Claude Code and
state that boundary. A planning decision does not authorize implementation.

When a needed skill requires user invocation, the agent supplies the actual next
command and task path. For example, if `to-spec` is needed:

```text
# Codex
$to-spec .trellis/tasks/09-29-csv-import

# Claude Code
/to-spec .trellis/tasks/09-29-csv-import
```

That handoff preserves the answers and authorization already recorded. It does
not require repeating them. Stages are selected when useful; specification,
ticketing, retro and spec updates are not a mandatory pipeline. Stock `retro`
currently requires user invocation; if an update removes a needed skill, report
it as unavailable instead of reconstructing or patching it.

Resume with the exact task reference, `$trellis-continue` in Codex, or
`/trellis:continue` in Claude Code. Resume recovers task progress and any pending
skill command; it does not itself invoke a user-only Matt skill. Closeout retains
planning/no-commit boundaries, reconciles prior archives and journal entries, and
uses explicit no-auto-commit lifecycle calls.

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

The current `code-review` installation reviews `<fixed-point>...HEAD`, which
excludes uncommitted edits. Review requiring a commit stays pending without commit
permission. Check the installed skill's contract after updates, and never count
an empty diff as acceptance of working-tree changes.

[Current stock-installation evidence](docs/validation/stock-installation.md)
records the exact installer run, installed policies and limited fresh-session
check. Earlier [validation reports](docs/validation/README.md) describe the
historical patched setup and independent runtime fixes; they do not establish
automatic end-to-end delivery with the current stock installation.
