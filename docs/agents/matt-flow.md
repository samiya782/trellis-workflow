# Matt execution adapter

Load on explicit Matt entry or resume of a recorded Matt task. This is routing
and runtime adaptation; methodology stays in the genuine installed skills.

## Select and authorize

Read the selected `.agents/skills/<name>/SKILL.md` and its referenced resources
(Codex); Claude uses `.claude/skills/`. Record the source path. If missing or
blocked by invocation policy, report the exact prerequisite; never simulate it.
Codex setup and policy checks are in README. A catalog listing isn't execution.

Use `grill-with-docs` for discovery or `wayfinder` for uncertainty spanning
sessions. Wayfinder is planning-only until the user authorizes delivery; a
resolved decision ticket isn't an implementation ticket. Use the configured
Trellis Other tracker, never infer GitHub/GitLab publication from a remote.

Resolve material questions with the real skill. Record the user's answers and
scope, testing seam, delegated engineering decisions, commit/closeout permission,
and any stop condition. Combine overlapping questions; don't require separate
consent for bookkeeping or a skill name. Existing answers satisfy later skill
questions only when they actually cover them. Never invent approval. Explicit
planning-only requests remain planning-only.

## Continue within that scope

The coordinator selects and loads the next needed real skill without a command
handoff: `to-spec` when a durable spec is useful; `to-tickets` when decomposition
helps; `implement` for ready work; `code-review` for qualitative review. A small
settled contract may go directly to implement. No duplicate Trellis interview,
specification, decomposition or Standards/Spec review is needed.

Codex downstream metadata permits implicit invocation only after this project's
explicit Matt route selection. Entry skills remain explicit. Claude's upstream
`disable-model-invocation` boundaries remain in force: show required commands if
the harness disallows continuation. Do not bypass a runtime invocation control.

Persist route, source paths, authorization, fixed point, ticket/blocker/ownership
map, progress, checks and next action in existing task Notes/implement.md. Keep
one source for each fact. Resume reads this record and current files; it doesn't
repeat approved interviews or stop merely because a skill finished.

## Delegate and join

Use actual runtime tools, not names presumed from another platform. When useful,
spawn independent ready tickets before waiting for either. Give each worker an
exact task path, real skill path, acceptance, blockers, owned files and applicable
spec pointers. Tell workers they share a checkout, must preserve others' edits,
and must not mutate task lifecycle, shared indexes or Git. Use separate worktrees
if ownership overlaps. A worker reads its missing context explicitly; native
injection must be observed, not inferred from the agent name.

The coordinator owns shared task state, commits and final review. Workers may
execute the real implement skill's code/test responsibilities; its shared review
and commit responsibilities return to the coordinator. This avoids nested review
agents hitting Codex depth limits and competing Git index writes. Join all results,
verify accepted blockers, then start dependent integration. Capacity or unavailable
tools can require sequential execution; record that accurately.

## Review, fixing and closeout

Capture a resolvable base before implementation and record the initial dirty
paths. The installed `code-review` uses `git diff <base>...HEAD`; it cannot review
uncommitted edits. The installed `implement` asks for review before committing.
Resolve that ordering explicitly: run focused executable checks, create an
**authorized local checkpoint commit**, then run real `code-review` against the
saved base with exact full spec/ticket paths. Uncommitted changes never count as
reviewed. With no commit permission, report the pending committed review; do not
claim PASS or silently change the real review skill's diff.

After verified findings, fix in scope, recheck affected behavior and commit the
correction when authorized; rerun affected review axes on the new revision.
Limit unsuccessful repair cycles to three. Use the Trellis checker for remaining
project/executable checks, allowing bounded fixes. Reuse successful checks tied to
an unchanged revision and scope. Final acceptance covers the combined result.

Use real `retro` when requested or evidence warrants it, including its
`writing-for-agents` dependency. Retro proposes environment improvements; it need
not change `.trellis/spec/`. Use `trellis-update-spec` only when a durable contract
was learned. Record no-change honestly. Authorized closeout follows workflow 3.5;
archive children before parent, use no-auto-commit flags, and never push by default.
