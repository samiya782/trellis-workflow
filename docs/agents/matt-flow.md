# Matt entry and handoff

Load on explicit Matt entry or resume of a recorded Matt task. This is routing
and runtime adaptation; methodology stays in the genuine installed skills.

## Select and authorize

Use the genuine installed skills with their stock invocation policy. Claude Code
uses its skill mechanism; Codex uses its supported skill loading, including
ordinary file reads when permitted. Record the source path. A catalog listing
isn't execution, and task-context loading doesn't authorize skill invocation.
For policy inspection, Codex uses `agents/openai.yaml`, not Claude's frontmatter;
Claude Code uses `disable-model-invocation`. Keep both installer-produced files intact.
Setup and installation evidence are linked from README.

Use `grill-with-docs` for discovery or `wayfinder` for uncertainty spanning
sessions. Wayfinder is planning-only until the user authorizes delivery; a
resolved decision ticket isn't an implementation ticket. Use the configured
Trellis Other tracker, never infer GitHub/GitLab publication from a remote.

Resolve material questions with the real skill. Record the user's answers and
scope, testing seam, delegated engineering decisions, commit/closeout permission,
and any stop condition. Combine overlapping questions and reuse recorded answers.
Existing answers satisfy later skill questions only when they actually cover
them. Never invent approval. Explicit
planning-only requests remain planning-only.

## Continue or hand off

Select only the next needed skill: `to-spec` when a durable spec is useful;
`to-tickets` when decomposition helps; `implement` for ready work; `code-review`
for qualitative review. A small settled contract may go directly to implement.
Avoid duplicate Trellis interviews, specifications and reviews.

Continue while the installed skill and harness permit it. When the next skill
requires user invocation, save the current task context and give the exact next
command: `$<skill> <task-reference>` in Codex or `/<skill> <task-reference>` in
Claude Code, replacing both placeholders with the selected skill and actual task
path. Explain the stock policy boundary and pause. Scope authorization remains
valid, but doesn't replace the required invocation. Do not bypass that boundary
through direct reads, copied or renamed skills, wrappers, or metadata edits.
If a required skill is missing, report the prerequisite without reconstructing it.

Persist route, source paths, authorization, fixed point, ticket/blocker/ownership
map, progress, checks and the next command in existing task Notes/implement.md.
Keep one source for each fact. Resume reads this record and current files, retains
approved decisions and honors any pending invocation boundary. A Trellis resume
command does not invoke a pending user-only Matt skill.

## Delegate and join

Delegate within the invoked skill's permitted scope; dispatch cannot satisfy a
different skill's user-only boundary. Use actual runtime tools. When useful,
spawn independent ready tickets before waiting for either (Claude Code: several
`Agent` calls in one message). Give each worker an exact task path as a line
`Active task: <path>`, real skill path, acceptance, blockers, owned files and
applicable spec pointers. Claude's hook resolves that marker. Codex's native
start event lacks the dispatch prompt: it supplies loading instructions only;
the worker validates and explicitly loads its task after receiving the dispatch.
Invalid or conflicting identity stops loading, never falls back to another task.
Parent-session fallback is only for a dispatch with no explicit task marker.
Tell workers they share a checkout, must preserve others' edits, and must not
mutate task lifecycle, shared indexes or Git. Use
separate worktrees if ownership overlaps. A worker reads its missing context
explicitly; native injection must be observed, not inferred from the agent name.
Claude Code rejects report-file writes from subagents: have research workers
return findings, then persist them as coordinator.

The coordinator owns shared task state, commits and final review. Workers may
execute the real implement skill's code/test responsibilities; its shared review
and commit responsibilities return to the coordinator. This avoids nested review
agents hitting agent depth limits and competing Git index writes. Join all results,
verify accepted blockers, then start dependent integration. Capacity or unavailable
tools can require sequential execution; record that accurately.

## Review, fixing and closeout

Capture a resolvable base before implementation and record the initial dirty
paths. Inspect the installed `code-review` contract when invoked; updates may
change which diff it reviews. If it reviews only `git diff <base>...HEAD`, run
focused checks and create an authorized local checkpoint commit before review
against the saved base and exact spec/ticket paths. Without commit permission,
record that review as pending. If the installed skill supports working-tree
review, follow its actual contract. Report the revision and changes actually
reviewed; an empty diff never establishes acceptance of uncommitted work.

After verified findings, fix in scope, recheck affected behavior and commit the
correction when authorized; rerun affected review axes when invocation is permitted.
Limit unsuccessful repair cycles to three. Use the Trellis checker for remaining
project/executable checks, allowing bounded fixes. Reuse successful checks tied to
an unchanged revision and scope. Final acceptance covers the combined result.

Use real `retro` when installed and requested or warranted, honoring its policy
and dependencies. If unavailable, report that fact; do not restore old copies or
patch the installation to supply it. Retro proposes environment improvements;
use `trellis-update-spec` only for a durable contract learned. Neither requires
the other. Record no-change honestly. Authorized closeout follows workflow 3.5;
archive children before parent, use no-auto-commit flags, and never push by default.
