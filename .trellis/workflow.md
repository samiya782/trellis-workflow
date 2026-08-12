# Development Workflow

---

## Core Principles

1. **Plan before code** - implementation starts only after the task contract is reviewed.
2. **Persist decisions** - requirements, research, approvals, review findings, and validation belong in task artifacts, not only in chat.
3. **Inject specifications** - read the relevant `.trellis/spec/` guidance before implementation and review.
4. **Work incrementally** - implement and verify one unblocked slice at a time.
5. **Protect the contract** - implementation must not silently reinterpret or expand approved requirements.
6. **Review twice when using Matt Skills** - `$code-review` and `trellis-check` are distinct gates.
7. **Capture reusable knowledge** - update `.trellis/spec/` when a task reveals a durable engineering rule.

---

## Trellis System

### Core Paths

- `.trellis/workflow.md` - lifecycle, routing, approvals, and handoffs.
- `.trellis/spec/` - reusable package and layer engineering guidelines.
- `.trellis/tasks/<task>/` - task contract, design, research, execution plan, and review evidence.
- `.trellis/workspace/` - deliberately recorded developer journals.

Initialize developer identity once when needed:

```bash
python3 ./.trellis/scripts/init_developer.py <your-name>
```

### Task Artifacts

Each task directory contains `task.json` and `prd.md`, with these additional artifacts when needed:

- `research/*.md` - source-backed facts and decisions needed downstream.
- `design.md` - technical boundaries, contracts, tradeoffs, compatibility, and rollout shape for complex work.
- `implement.md` - ordered slices, blockers, acceptance criteria, validation, progress, and review findings.
- `implement.jsonl` / `check.jsonl` - spec and research manifests for sub-agent context; they do not replace `implement.md`.

Lightweight tasks may be PRD-only. Complex tasks require `prd.md`, `design.md`, and `implement.md` before implementation starts.

### Core Commands

```bash
python3 ./.trellis/scripts/task.py create "<title>" [--slug <name>] [--parent <dir>]
python3 ./.trellis/scripts/task.py start <task>
python3 ./.trellis/scripts/task.py current --source
python3 ./.trellis/scripts/task.py add-context <task> <implement|check> <file> <reason>
python3 ./.trellis/scripts/task.py validate <task>
python3 ./.trellis/scripts/task.py finish
python3 ./.trellis/scripts/task.py archive <task>
python3 ./.trellis/scripts/get_context.py --mode packages
python3 ./.trellis/scripts/get_context.py --mode phase --step <X.Y>
```

Run `task.py --help` for the authoritative command surface.

### Fresh-Session Recovery

Begin with `task.py current --source`. Accept a fallback only when it identifies one task unambiguously; with no task or multiple possible tasks, ask for the exact task path instead of guessing.

Do not advance a planning task merely to bind a fresh session. Keep its path explicit until planning is approved. Rebinding an already `in_progress` task with `task.py start <task>` must not replace artifact recovery: read `prd.md`, `design.md` when present, and the latest `implement.md` ledger to determine the actual next step. Lifecycle status is coarse; durable artifacts are authoritative.

---

## Phase Index

```text
Phase 1: Plan      -> classify, create with consent, and approve durable planning artifacts
Phase 2: Implement -> implement reviewed work and pass review and executable checks
Phase 3: Finish    -> preserve lessons, commit, archive, and record the session
```

### Request and Route Classification

Classify a new request before selecting a route. Task creation consent is separate from specification approval, implementation approval, and commit approval.

| Request | Route |
|---|---|
| Conversation or read-only answer | No task unless the user requests one. |
| Small deterministic fix | Normal Trellis route; ask whether to create a task. |
| Clear feature with settled requirements | Normal Trellis route, or Matt route beginning at `$to-spec` when selected. |
| Ambiguous feature, product design, or architecture work | Normal Trellis route by default; Matt route begins with `$grill-with-docs` when selected. |
| Effort whose uncertainty spans multiple sessions | Matt route may begin with `$wayfinder`. |
| Existing approved Matt specification or tickets | Resume at `$to-tickets` or `$implement` as appropriate. |

For complex work, ask permission to create a Trellis task and enter planning. If the user declines, clarify or reduce scope; do not silently perform broad implementation outside the lifecycle.

### Route Contract

#### Normal Trellis Route

```text
trellis-brainstorm
  -> Trellis planning artifacts
  -> trellis-before-dev or context-injected implementation agent
  -> trellis-check
  -> Phase 3
```

#### Matt Skills Route

Trellis owns task lifecycle, approvals, durable handoffs, and the final Trellis quality gate. The real Matt Pocock Skills own their methodology. Never reproduce their interviewing, domain modeling, specification, ticketing, implementation, or review behavior in this file.

Installation, discovery, and invocation are separate:

1. The complete project-local skill must exist at `.agents/skills/<name>/`, including its `SKILL.md` and supporting files.
2. The platform must discover and select that project-local source. A same-name global skill is not proof that the project integration ran.
3. A workflow reference is not invocation. The human explicitly invokes upstream human-only stages.

If a required skill is missing, undiscoverable, or resolves ambiguously, stop and report the prerequisite. Do not imitate it or substitute a Trellis skill while calling the result Matt's workflow.

```text
human: $grill-with-docs        # normal discovery on-ramp
   or: $wayfinder              # only for genuinely multi-session uncertainty
          -> human: $to-spec
          -> human: $to-tickets
          -> human: $implement
          -> actual $code-review <fixed-point>
          -> trellis-check
```

`$grill-with-docs`, `$wayfinder`, `$to-spec`, `$to-tickets`, and `$implement` are separate human-owned invocation boundaries. Present the exact next command and stop; never auto-chain them. `$wayfinder` decision tickets are not `$to-tickets` implementation tickets.

At each boundary, Trellis records only the source path, artifact or tracker pointers, approval, and next stage. It does not recreate the skill output:

| Completed skill | Trellis handoff |
|---|---|
| `$grill-with-docs` / `$wayfinder` | Record the selected skill source and durable discovery, domain, ADR, map, and research pointers. |
| `$to-spec` | Import the approved specification faithfully into `prd.md` and, when needed, `design.md`; record its source. |
| `$to-tickets` | Import approved slices, acceptance criteria, and blocker edges into `implement.md` or mapped child tasks. |
| `$implement` | Record the ticket, validation, commit or working-tree state, and unresolved findings. |
| `$code-review <fixed-point>` | Persist its Standards and Spec reports and explicit result; then run `trellis-check` separately. |

Record `Planning route: Trellis` or `Planning route: Matt Skills`, the current methodology stage, and artifact pointers in `prd.md` Notes. Trellis task states remain `planning`, `in_progress`, and `completed`; Matt stages do not create new lifecycle states.

### Parent and Child Tasks

Use a parent task for several independently verifiable deliverables. The parent owns shared requirements, the child map, cross-child criteria, and final integration review. Each child owns its own planning, implementation, check, and archive cycle. Tree position groups work but does not define dependencies; record every blocker explicitly in the affected child artifacts.

[workflow-state:no_task]
No active task. Classify the request and obtain consent before creating a Trellis task.
Normal Trellis route: use `trellis-brainstorm` after task creation for unclear or complex work.
Matt route: require the intended project-local skill, tell the human to invoke `$grill-with-docs` (or `$wayfinder` for genuinely multi-session uncertainty), and STOP. Do not interview or simulate the skill. If the human already invoked a real Matt skill, load that exact skill and obtain task consent before its first repository write.
[/workflow-state:no_task]

### Phase 1: Plan

- 1.0 Create task `[required · once]`
- 1.1 Discovery and specification `[required · repeatable]`
- 1.2 Research `[optional · repeatable]`
- 1.3 Decompose tickets and configure context `[required · once]`
- 1.4 Approve and activate `[required · once]`
- 1.5 Completion criteria

[workflow-state:planning]
Read `prd.md` Notes for the route and last completed stage; remain in planning.
Normal Trellis route: load `trellis-brainstorm` and produce the required Trellis artifacts.
Matt route: require the intended project-local skill, present the next explicit `$grill-with-docs` / `$wayfinder` / `$to-spec` / `$to-tickets` invocation, and STOP. Import real outputs without reimplementing them or auto-chaining human-only skills.
Lightweight work may be PRD-only. Complex work requires reviewed `prd.md`, `design.md`, and `implement.md`. In sub-agent mode, curate and validate `implement.jsonl` and `check.jsonl`.
Persist approval of the specification, testing seam, ticket set, blockers, and complete artifact chain before `task.py start`.
[/workflow-state:planning]

[workflow-state:planning-inline]
Read `prd.md` Notes for the route and last completed stage; remain in planning.
Normal Trellis route: load `trellis-brainstorm` and produce the required Trellis artifacts.
Matt route: require the intended project-local skill, present the next explicit `$grill-with-docs` / `$wayfinder` / `$to-spec` / `$to-tickets` invocation, and STOP. Import real outputs without reimplementing them or auto-chaining human-only skills.
Lightweight work may be PRD-only. Complex work requires reviewed `prd.md`, `design.md`, and `implement.md`. Inline mode skips JSONL curation and loads context through `trellis-before-dev` in Phase 2.
Persist approval of the specification, testing seam, ticket set, blockers, and complete artifact chain before `task.py start`.
[/workflow-state:planning-inline]

### Phase 2: Implement

- 2.1 Implementation `[required · repeatable]`
- 2.2 Quality check `[required · repeatable]`
- 2.3 Rollback `[on demand]`

[workflow-state:in_progress]
Read `prd.md` Notes and the latest `implement.md` ledger before choosing the next action.
Normal Trellis route: next unblocked slice -> `trellis-implement` -> `trellis-check` -> persisted PASS or routed correction.
Matt route: human invokes the real `$implement`; then run the actual `$code-review <fixed-point>` and a separate report-only `trellis-check`. Persist each source, result, and validation record. A failure returns to a new explicit `$implement`, `$to-spec`, or `$to-tickets` as classified; never imitate or auto-chain a human-only skill.
After the final full-scope PASS: `trellis-update-spec` -> commit remaining changes -> `/trellis:finish-work`.
Never reinterpret approved requirements. Contract defects return to Phase 1; implementation defects return to 2.1.
[/workflow-state:in_progress]

[workflow-state:in_progress-inline]
Read `prd.md` Notes and the latest `implement.md` ledger before choosing the next action.
Normal Trellis route: `trellis-before-dev` -> next unblocked slice -> `trellis-check` -> persisted PASS or routed correction.
Matt route: human invokes the real `$implement`; do not implement inline as a substitute. Then run the actual `$code-review <fixed-point>` and a separate report-only `trellis-check`. Failures return through the appropriate real skill.
After the final full-scope PASS: `trellis-update-spec` -> commit remaining changes -> `/trellis:finish-work`.
Never reinterpret approved requirements. Contract defects return to Phase 1; implementation defects return to 2.1.
[/workflow-state:in_progress-inline]

### Phase 3: Finish

- 3.2 Debug retrospective `[on demand]`
- 3.3 Spec update `[required · once]`
- 3.4 Commit and archive `[required · once]`

[workflow-state:completed]
Work is complete. If changes remain uncommitted, return to 3.4; otherwise run `/trellis:finish-work` to archive and record the session.
[/workflow-state:completed]

### Workflow Rules

1. Follow the numbered phases in order; required steps cannot be skipped.
2. A task directory or lifecycle status does not prove approval. Persist each human decision, its scope, date, and approved artifact paths.
3. Missing `design.md` or `implement.md` is valid for lightweight work and incomplete planning for complex work.
4. Artifact presence informs progress, but the latest approvals, checkboxes, and review records determine the next action.
5. A failed or interrupted worker does not complete a phase. Resume from durable artifacts, not its transcript.
6. Rollbacks update the current artifacts and return to the appropriate phase; do not invent lifecycle states.
7. Load step detail when needed:

```bash
python3 ./.trellis/scripts/get_context.py --mode phase --step <step>
```

---

## Phase 1: Plan

Goal: create an approved, durable implementation contract before changing code.

#### 1.0 Create task `[required · once]`

After task-creation consent, create the task:

```bash
python3 ./.trellis/scripts/task.py create "<task title>" --slug <name>
```

Do not include the date prefix in `--slug`. Use `--parent <parent-task>` for a child task. Run only `create`; `task.py start` belongs to step 1.4 because it authorizes implementation. Skip creation when `task.py current --source` already identifies the intended task.

If session identity is unavailable, keep the exact task path explicit. Do not advance a planning task merely to establish a pointer.

#### 1.1 Discovery and specification `[required · repeatable]`

First persist the selected route in `prd.md` Notes.

**Normal Trellis route**

Load the real `trellis-brainstorm` skill. Use its instructions to explore requirements and produce `prd.md`; add `design.md` and `implement.md` for complex work. Do not duplicate the skill's interview algorithm here.

**Matt Skills route**

1. Verify that the intended project-local skill is discoverable and selected. If not, stop and report the installation or discovery prerequisite.
2. For ordinary ambiguous work, tell the human to invoke `$grill-with-docs <task context>` and stop. For uncertainty that genuinely spans sessions, use `$wayfinder <destination or map>` instead and stop.
3. After the real discovery skill finishes, record its selected source and durable output pointers in `prd.md` Notes. Do not run a second interview or invent a parallel decision model.
4. Tell the human to invoke `$to-spec <discovery or map reference>` and stop. Import its approved specification faithfully into `prd.md` and, when needed, `design.md`; record the source.
5. Obtain and persist approval of the imported specification and testing seam.

Return to this step whenever a requirement or architectural contract changes.

#### 1.2 Research `[optional · repeatable]`

Research local code, repository specs, and external primary sources whenever planning depends on facts. Use `trellis-research` when sub-agent dispatch is available; otherwise research in the main session.

Persist each substantial topic under `{TASK_DIR}/research/` with the question, scope, sources, findings, implications, and caveats. Record resolved decisions fully enough for a fresh session; a chat message or external link alone is not a durable handoff.

#### 1.3 Decompose tickets and configure context `[required · once]`

**Normal Trellis route**

For complex work, decompose the approved contract into small vertical slices in `implement.md`. Each slice states:

- what it delivers;
- explicit blockers or `None`;
- acceptance criteria;
- required spec and research context;
- focused and full-scope validation;
- rollback point and progress checkbox.

Use child tasks only for independently verifiable deliverables. Keep dependency edges in artifacts rather than inferring them from child order.

**Matt Skills route**

Tell the human to invoke `$to-tickets <approved spec reference>` and stop. After the real skill publishes an approved ticket set, import its titles, acceptance criteria, blocker edges, order, and source pointers into `implement.md` or mapped child tasks. This is handoff bookkeeping, not a second decomposition pass.

**Sub-agent context**

When implementation or checking will use Trellis sub-agents, curate `implement.jsonl` and `check.jsonl` with repository-relative spec and research paths plus a reason for each entry. Do not add source files merely because they may be edited. Validate before activation:

```bash
python3 ./.trellis/scripts/task.py validate <task>
```

Inline execution skips JSONL curation and loads the same task/spec context through `trellis-before-dev`.

#### 1.4 Approve and activate `[required · once]`

Review the complete handoff with the user:

1. Research and decisions needed downstream are durable.
2. `prd.md` contains requirements, constraints, non-goals, acceptance criteria, and the agreed testing seam.
3. Complex-task `design.md` and `implement.md` agree with the PRD.
4. Slices and blocker edges are explicit and independently verifiable.
5. Required sub-agent context manifests are curated and valid.

Persist the approval, its scope, date, and exact artifact paths in `prd.md` Notes or `implement.md`. Only then activate implementation:

```bash
python3 ./.trellis/scripts/task.py start <task>
```

If lifecycle status advances without a persistent session pointer, follow the command's identity guidance and keep the task path explicit. Later planning changes must be revised and reapproved in the same durable artifacts; do not invent a rollback status.

#### 1.5 Completion criteria

| Condition | Required |
|---|:---:|
| Reviewed `prd.md` and persisted approval | Yes |
| Material research and decisions persisted | When applicable |
| Reviewed `design.md` and `implement.md` | Complex tasks |
| Approved slices, blockers, validation, and rollback | Complex tasks |
| Valid context manifests | Sub-agent mode |
| `task.py start` completed | Yes |

---

## Phase 2: Implement

Goal: implement the reviewed contract one unblocked slice at a time and pass both contract and repository checks.

#### 2.1 Implementation `[required · repeatable]`

Select the first incomplete slice whose explicit blockers are complete.

**Normal Trellis route**

- In sub-agent mode, dispatch `trellis-implement` for the named slice and exact task path.
- In inline mode, load `trellis-before-dev`, then read `prd.md`, optional `design.md`, optional `implement.md`, task research, and relevant `.trellis/spec/` guidance.

Implement only the selected slice. Do not reinterpret interfaces, expand scope, or alter approved requirements. Run its focused tests and the repository's required lint and type checks; persist commands and results with the slice.

**Matt Skills route**

1. Capture a resolvable Git fixed point before the first implementation invocation. If no Git repository exists, do not initialize one or claim the real fixed-point review is available.
2. Identify the approved frontier ticket and obtain explicit consent for the commit behavior owned by upstream `$implement`.
3. Tell the human to invoke `$implement <ticket or spec reference>` and stop. The actual loaded skill is the sole implementation owner; do not dispatch `trellis-implement` or edit inline for the same slice.
4. Record its selected source, validation, commit or working-tree state, and unresolved findings in `implement.md`.

If implementation exposes a missing fact, return to 1.2. If it exposes a contract, architecture, testing-seam, or blocker defect, stop coding and return to the corresponding Phase 1 artifact and approval gate.

#### 2.2 Quality check `[required · repeatable]`

**Normal Trellis route**

Run the real `trellis-check` agent or skill. It may fix bounded implementation or standards defects, but it must not change the approved contract. Recheck after every correction.

**Matt Skills route**

1. Confirm the saved fixed point resolves and the committed diff is non-empty.
2. Invoke the actual `$code-review <fixed-point>`; do not produce a Matt-like review in its place.
3. Persist both review axes, the selected skill source, fixed point, commits, findings, and result.
4. On review PASS, run `trellis-check` separately as a report-only Trellis and executable gate. Any new code finding returns to a fresh explicit `$implement`, followed by `$code-review` again.

For every route, verify separately:

- **Contract** - original request, `prd.md`, material research decisions, optional `design.md`, and current-slice acceptance criteria.
- **Standards** - relevant `.trellis/spec/`, repository conventions, architecture, and established code/test patterns.
- **Executable gates** - the tests, lint, type-check, build, and formatting checks required by the affected packages.

Persist commands, exit states, findings, corrections, and the next route in `implement.md` or `prd.md` Notes. Chat and worker output are not sufficient handoffs.

If the project or affected package is not a Git repository, do not initialize Git or claim a repository-diff review. Use an explicit baseline or changed-file set for the checks that remain possible and record the limitation. The Matt route cannot pass its fixed-point `$code-review` gate without a real Git fixed point.

Outcomes:

- **PASS** - both axes and executable gates pass; mark the slice complete. Repeat 2.1 for remaining slices, then run one final full-scope check.
- **FAIL: implementation** - return to 2.1; on the Matt route, use a new explicit `$implement` and repeat `$code-review`.
- **FAIL: contract or decomposition** - return to Phase 1; on the Matt route, use `$to-spec` or `$to-tickets`, import the corrected result, and reapprove it.
- **DECISION REQUIRED** - persist the human decision before resuming.

#### 2.3 Rollback `[on demand]`

- Missing or stale fact -> 1.2.
- Requirement, design, or testing-seam defect -> 1.1 and renewed approval; Matt route uses `$to-spec`.
- Slice or blocker defect -> 1.3 and renewed approval; Matt route uses `$to-tickets`.
- Implementation defect -> 2.1; Matt route uses `$implement`.
- Standard/contract conflict -> human decision recorded in the relevant artifact.

Keep review and rollback as routing decisions within the current task. Do not invent lifecycle states unless the configured runtime supports them.

---

## Phase 3: Finish

Goal: preserve reusable lessons, commit approved work, archive the task, and record the session.

#### 3.2 Debug retrospective `[on demand]`

If the same issue required repeated fixes, load `trellis-break-loop`. Capture the root-cause class, why earlier fixes failed, and prevention worth preserving.

#### 3.3 Spec update `[required · once]`

Load `trellis-update-spec` and decide whether the task produced a reusable convention, pitfall, or technical decision. Update `.trellis/spec/` only with durable repository guidance, not task-specific requirements. Record the decision even when no spec update is needed.

#### 3.4 Commit and archive `[required · once]`

Before committing, confirm Phase 3.3 and the final full-scope 2.2 check are complete.

If the project or affected package is not a Git repository, do not initialize one. Ask whether to keep the task `in_progress` or explicitly finish without a commit, and record that exception without describing it as a successful commit.

When Git is available:

1. Inspect the dirty state and recent commit style.
2. Separate files changed for this task from unrecognized user or unrelated changes.
3. Propose logically grouped commits with exact file lists; exclude unrecognized files unless the user authorizes them.
4. Obtain one explicit confirmation, then stage only those files and commit in order.
5. Do not amend or push.

Files already committed by the real `$implement` are evidence for this task, not work to recommit. Commit only remaining approved changes.

After the worktree is ready, run `/trellis:finish-work` to archive the task and record the session.
