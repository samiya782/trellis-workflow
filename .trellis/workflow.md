# Development Workflow

## Phase Index

Normal Trellis is the default. Use Matt only when the user explicitly selects
`grill-with-docs` or `wayfinder`, or resumes a recorded Matt task. Read the real
project-local skill; never substitute a summary of its method.

Work within the user's authorized scope until delivery. Ask for unresolved
material decisions, scope changes, or missing permissions, not another command.
Authorization persists across stages and sessions when recorded with its scope.
These project orchestration rules replace generic Trellis skill examples that
require repeated approvals, fixed artifacts, or a mandatory phase sequence.

- Small settled work: edit, run relevant checks, report. No task ceremony.
- Durable work: one task with contract, authorization, progress and evidence.
- Matt work: load `docs/agents/matt-flow.md` on entry or resume; use the real
  skills needed by the work. Publication uses `docs/agents/issue-tracker.md`.
- Read applicable `.trellis/spec/` before coding. Implement and fix in scope;
  verify the combined result before closeout. Keep research and logs on demand.
- Resume from exact task artifacts and current files, not lifecycle status alone.

Details: `python3 .trellis/scripts/get_context.py --mode phase --step <X.Y>`.
Steps below are responsibilities to select as needed, not mandatory ceremonies.

## Phase 1: Plan

#### 1.0 Create task

Use `task.py current --source` to identify existing work. Create a durable task
only when useful; authorization to perform the work includes its local task
bookkeeping. Use `task.py create "title" --slug name --description "scope"
--no-start`. Never change another session's pointer. If identity is ambiguous,
keep the exact path explicit and resolve it before lifecycle changes.

#### 1.1 Discovery and specification

Use `trellis-brainstorm` for unresolved normal-route requirements. On Matt entry,
load the selected real skill and `docs/agents/matt-flow.md`. Resolve material
questions, then record scope, acceptance, decisions and authorization in `prd.md`.
Keep the full Matt specification in one canonical publication; do not split or
rewrite it merely to fill Trellis templates. Add `design.md` only when it adds
information. Never invent a human answer or treat silence as approval.

#### 1.2 Research

Inspect code and primary sources before asking factual questions. Use independent
research agents when worthwhile; save concise evidence under the task or docs.
Load only the sources needed for the current responsibility.

#### 1.3 Tickets and context

Decompose only when separate deliverables help execution. For Matt, use the real
`to-tickets` skill when needed. Record blockers and file ownership. One contract
can be implemented directly; a ticket index references bodies rather than copies
them. Curate only necessary spec/research pointers in implement/check JSONL and
run `task.py validate <task>`. Explicit task paths also reach every worker.
Native task injection already appends the task artifacts; avoid duplicating them
in JSONL. Skip placeholder guidelines. When no additional context is useful,
`start --allow-empty-context` is supported; empty-manifest validation still fails.

#### 1.4 Activate

Check that material decisions are resolved and the user's authorization covers
implementation. Record that authorization once; don't request it again for an
unchanged scope. The coordinator runs `task.py start <task>` for authorized work.
Readiness metadata is not authorization. Workers never change shared lifecycle.

#### 1.5 Ready to execute

The contract, acceptance, authorization and next action must be recoverable.
Artifact count does not establish readiness; missing optional files is valid.

## Phase 2: Implement

#### 2.1 Implement

Normal work uses `trellis-implement` when delegation helps, otherwise load
`trellis-before-dev` and work inline. Matt work uses real `implement` with the
exact contract. In either route, dispatch independent ready tickets concurrently
only with disjoint ownership (or isolated worktrees), explicit blockers and enough
runtime slots. The coordinator alone owns task state and shared Git operations.
Workers load task/spec context themselves if native injection is absent; inherited
chat is not proof of injection. Join and inspect all results before integration.
Describe sequential execution honestly when concurrency is unavailable.

#### 2.2 Verify and repair

Run relevant executable checks and contract/standards review. Matt's actual
`code-review` supplies its two review axes; Trellis checks supply executable and
project checks. Reuse evidence for an unchanged revision; no duplicate full review
or repeated full suite merely to satisfy a stage name. A checker may fix bounded
implementation defects. Recheck affected behavior after changes, then verify the
integrated result. Stop after three unsuccessful repair cycles, or earlier for a
material decision or permission boundary, and persist evidence plus next action.
Never report a skipped, empty-diff or failed check as PASS.

#### 2.3 Recover

Use the exact task path, contract, authorization and latest progress record.
Resolve active/archive references before loading context; archived paths move.
Resume the first unfinished responsibility, retaining verified work. Don't start
blocked work or recreate partial publications. Ask only for genuinely missing
identity, decisions or permissions. Contract changes need renewed authorization.

## Phase 3: Finish

#### 3.2 Retrospective when useful

Use real Matt `retro` if requested or session evidence warrants environment
analysis. Repeated debugging may warrant `trellis-break-loop`. A retrospective
may find nothing actionable; do not manufacture lessons or mandatory artifacts.

#### 3.3 Preserve a lesson when warranted

Use `trellis-update-spec` only for a reusable repository contract or convention.
Retro suggests environment improvements; update-spec stores engineering knowledge.
Neither automatically implies the other. Prefer fixing a faulty rule/check over
adding more prose. No-change is a valid outcome.

#### 3.4 Commit when authorized

Check actual changes and current authorization. Stage only owned paths; never
push or include unrelated work. Matt review's committed-diff ordering is described
in `docs/agents/matt-flow.md`. Without commit authorization, finish permitted work
and record pending committed review/commit; do not invent an empty review PASS.

#### 3.5 Close out

When closeout is authorized and acceptance is verified, archive children before
parent with `task.py archive <task> --no-commit`; record a concise session with
`add_session.py --no-commit`. Use `trellis-finish-work` for its checks, subject to
this explicit no-auto-commit policy. Inspect command help and branch preconditions.
Do not archive unrelated tasks or require a new user command to finish authorized
work. If changes must remain for user review, record that completion boundary.

## Runtime breadcrumbs

[workflow-state:no_task]
Read the Phase Index once. Normal small work can proceed directly. Matt requires explicit entry or recorded route; load the real entry skill and docs/agents/matt-flow.md. Continue authorized work; ask only for material decisions or missing permission.
[/workflow-state:no_task]

[workflow-state:planning]
Read the exact task contract, authorization and next action. Resolve outstanding decisions. Select needed planning responsibilities; don't require duplicate artifacts or command handoffs. Matt: load docs/agents/matt-flow.md and real skills.
[/workflow-state:planning]

[workflow-state:planning-inline]
Read the task contract and authorization. Resolve material decisions, then continue in scope. Matt: docs/agents/matt-flow.md. Use explicit context paths; no command handoffs.
[/workflow-state:planning-inline]

[workflow-state:in_progress]
Recover contract, authorization and progress. Execute ready work, fix and recheck within scope; join workers before integration. Coordinator owns lifecycle/Git. Matt: docs/agents/matt-flow.md. Continue to authorized closeout.
[/workflow-state:in_progress]

[workflow-state:in_progress-inline]
Recover contract, authorization and progress. Load needed specs, implement, fix and recheck in scope. Matt: docs/agents/matt-flow.md. Continue to authorized closeout.
[/workflow-state:in_progress-inline]

[workflow-state:completed]
Verify final evidence and complete any authorized archive/journal work. Preserve pending permissions and unrelated work; don't restart completed stages.
[/workflow-state:completed]
