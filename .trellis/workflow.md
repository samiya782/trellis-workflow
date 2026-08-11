# Development Workflow

---

## Core Principles

1. **Plan before code** — discovery, specification, and execution slices are reviewed before implementation starts
2. **Decisions become artifacts** — preserve resolved requirements and constraints in task files; do not rely on chat history
3. **Specs injected, not remembered** — repository guidelines are injected via hook/skill, not recalled from memory
4. **Persist everything** — research, decisions, validation, and lessons go to files; conversations get compacted, files don't
5. **Incremental development** — implement one independently verifiable slice at a time
6. **Review on two axes** — verify both task-contract fidelity and repository-standard compliance
7. **Capture learnings** — after each task, review and write reusable engineering knowledge back to spec

---

## Trellis System

### Developer Identity

On first use, initialize your identity:

```bash
python3 ./.trellis/scripts/init_developer.py <your-name>
```

Creates `.trellis/.developer` (gitignored) + `.trellis/workspace/<your-name>/`.

### Spec System

`.trellis/spec/` holds coding guidelines organized by package and layer.

- `.trellis/spec/<package>/<layer>/index.md` — entry point with **Pre-Development Checklist** + **Quality Check**. Actual guidelines live in the `.md` files it points to.
- `.trellis/spec/guides/index.md` — cross-package thinking guides.

```bash
python3 ./.trellis/scripts/get_context.py --mode packages   # list packages / layers
```

**When to update spec**: new pattern/convention found · bug-fix prevention to codify · new technical decision.

### Task System

Every task has its own directory under `.trellis/tasks/{MM-DD-name}/` holding `task.json`, `prd.md`, optional `design.md`, optional `implement.md`, optional `research/`, and context manifests (`implement.jsonl`, `check.jsonl`) for sub-agent-capable platforms.

```bash
# Task lifecycle
python3 ./.trellis/scripts/task.py create "<title>" [--slug <name>] [--parent <dir>]
python3 ./.trellis/scripts/task.py start <name>          # set active task (session-scoped when available)
python3 ./.trellis/scripts/task.py current --source      # show active task and source
python3 ./.trellis/scripts/task.py finish                # clear active task (triggers after_finish hooks)
python3 ./.trellis/scripts/task.py archive <name>        # move to archive/{year-month}/
python3 ./.trellis/scripts/task.py list [--mine] [--status <s>]
python3 ./.trellis/scripts/task.py list-archive

# Code-spec context (injected into implement/check agents via JSONL).
# `implement.jsonl` / `check.jsonl` are seeded on `task create` for sub-agent-capable
# platforms; the AI curates real spec + research entries during planning when needed.
python3 ./.trellis/scripts/task.py add-context <name> <implement|check> <file> <reason>
python3 ./.trellis/scripts/task.py list-context <name>
python3 ./.trellis/scripts/task.py validate <name>

# Task metadata
python3 ./.trellis/scripts/task.py set-branch <name> <branch>
python3 ./.trellis/scripts/task.py set-base-branch <name> <branch>    # PR target
python3 ./.trellis/scripts/task.py set-scope <name> <scope>

# Hierarchy (parent/child)
python3 ./.trellis/scripts/task.py add-subtask <parent> <child>
python3 ./.trellis/scripts/task.py remove-subtask <parent> <child>

```

> Run `python3 ./.trellis/scripts/task.py --help` to see the authoritative, up-to-date list.

**Current-task mechanism**: `task.py create` creates the task directory and (when session identity is available) auto-sets the per-session active-task pointer so the planning breadcrumb fires immediately. `task.py start` writes the same pointer (idempotent if already set) and flips `task.json.status` from `planning` to `in_progress`. State is stored under `.trellis/.runtime/sessions/`. If no context key is available from hook input, `TRELLIS_CONTEXT_ID`, or a platform-native session environment variable, lifecycle status may still change without a persistent active-task pointer. Follow the command's identity hint, keep the task path explicit, and do not rely on later hook injection until session identity is available. `task.py finish` deletes the current session file (status unchanged). `task.py archive <task>` writes `status=completed`, moves the directory to `archive/`, and deletes any runtime session files that still point at the archived task.

**Fresh-session recovery**: begin with `task.py current --source`. Accept a session fallback only when it resolves unambiguously to exactly one session pointer. With zero or multiple pointers, do not guess from the active-task list; ask for the exact task path and keep it explicit. For an already `in_progress` task, `task.py start <task>` is an idempotent way to bind the new session. Do not advance a `planning` task merely to rebind a fresh session, because `start` authorizes implementation; keep the task path explicit until planning is approved. After recovery, treat `planning` / `in_progress` as coarse lifecycle states: inspect `prd.md`, `design.md`, and especially the latest `implement.md` checkboxes and review records to reconstruct the exact step. An `in_progress` breadcrumb that says “next slice” does not override an artifact ledger showing all slices and the final review have passed.

### Workspace System

Records every AI session for cross-session tracking under `.trellis/workspace/<developer>/`.

- `journal-N.md` — session log. **Max 2000 lines per file**; a new `journal-(N+1).md` is auto-created when exceeded.
- `index.md` — personal index (total sessions, last active).

```bash
python3 ./.trellis/scripts/add_session.py --title "Title" --commit "hash" --summary "Summary"
```

### Context Script

```bash
python3 ./.trellis/scripts/get_context.py                            # full session runtime
python3 ./.trellis/scripts/get_context.py --mode packages            # available packages + spec layers
python3 ./.trellis/scripts/get_context.py --mode phase --step <X.Y>  # detailed guide for a workflow step
```

---

<!--
  WORKFLOW-STATE BREADCRUMB CONTRACT (read this before editing the tag blocks below)

  The [workflow-state:STATUS] blocks embedded in the ## Phase Index section
  below are the SINGLE source of truth for the per-turn `<workflow-state>`
  breadcrumb that every supported AI platform's UserPromptSubmit hook
  reads. inject-workflow-state.py (Python platforms) and
  inject-workflow-state.js (OpenCode plugin) only parse them — there is no
  fallback dictionary baked into the scripts.

  STATUS charset: [A-Za-z0-9_-]+. When the hook can't find a tag, it
  degrades to a generic "Refer to workflow.md for current step." line —
  intentionally visible so users notice and fix a broken workflow.md.

  INVARIANT (test/regression.test.ts):
    Every workflow-walkthrough step marked `[required · once]` must have a
    matching enforcement line in its phase's [workflow-state:*] block. The
    breadcrumb is the only per-turn channel; if a mandatory step isn't
    mentioned there, the AI silently skips it (Phase 1 planning gate
    skip and Phase 3.4 commit skip both manifested via this gap).

  TAG ↔ PHASE scoping:
    [workflow-state:no_task]      → no active task; before Phase 1
    [workflow-state:planning]     → all of Phase 1 (status='planning')
    [workflow-state:planning-inline] → Codex inline variant of Phase 1
    [workflow-state:in_progress]  → Phase 2 + Phase 3.2-3.4
                                    (status stays 'in_progress' from
                                    task.py start until task.py archive)
    [workflow-state:in_progress-inline] → Codex inline variant of Phase 2/3
    [workflow-state:completed]    → currently DEAD: cmd_archive flips
                                    status and moves the dir in the same
                                    call, so the resolver loses the
                                    pointer (block kept for a future
                                    explicit in_progress→completed
                                    transition)

  Editing checklist:
    - When you change a [workflow-state:STATUS] block, also check the
      matching phase's `[required · once]` walkthrough steps for sync
    - Run `trellis update` after editing to push the new bodies to
      downstream user projects (block-level managed replacement)
    - Runtime parser is generated per configured platform; this project's
      Codex copy is .codex/hooks/inject-workflow-state.py
-->

## Phase Index

```
Phase 1: Plan    → classify, get task-creation consent, then write planning artifacts
Phase 2: Execute → implement only after task status is in_progress
Phase 3: Finish  → verify, update spec, commit, and wrap up
```

### Request Triage

Classify every new request before selecting a lifecycle route. This table routes to real skills; it does not reproduce their instructions.

| Request type | Route before implementation |
|---|---|
| Ambiguous feature, product design, or architecture change that fits one working session | Create a Trellis task with consent, then ask the human to explicitly invoke the installed `$grill-with-docs`. Stop until that real skill finishes. |
| Huge, foggy effort whose decisions span multiple sessions | Create a Trellis task with consent, then ask the human to explicitly invoke the installed `$wayfinder`. This replaces `$grill-with-docs` as the discovery on-ramp; it is not an implementation plan. |
| Clear feature with a settled conversation but no published specification | Skip discovery and ask the human to invoke the installed `$to-spec`. |
| Approved specification with no implementation tickets | Ask the human to invoke the installed `$to-tickets`. |
| Approved ticket or specification ready to build | Activate the Trellis task, then ask the human to invoke the installed `$implement` for the named frontier ticket/slice. |
| Small bug fix or exact mechanical change | Use the normal Trellis route unless the human explicitly selects a Matt skill. Do not force a discovery interview onto deterministic work. |
| Conversation or research-only answer with no requested proposal, plan, spec, tickets, or implementation | No task is required. |

When no task is active, obtain task-creation consent before creating one. If the user has already explicitly invoked a Matt skill, load that real skill; obtain Trellis task consent before its first repository write, then continue the loaded skill rather than substituting `trellis-brainstorm`. Approval to create a task is not approval of the specification, ticket set, implementation, or commit.

### Planning Artifacts

- `research/*.md` — source-backed facts, code findings, resolved decision detail, and caveats that later stages must not lose.
- `prd.md` — the task specification: problem, requirements, constraints, non-goals, acceptance criteria, and agreed testing seams. Do not put technical design or execution checklists here.
- `design.md` — technical design for complex tasks: boundaries, contracts, data flow, architectural decisions, tradeoffs, compatibility, and rollout / rollback shape.
- `implement.md` — ticket decomposition and execution plan for complex tasks: small vertical slices, explicit blockers and order, per-slice acceptance criteria, required context, validation commands, review gates, progress checklist, and rollback points.
- `implement.jsonl` / `check.jsonl` — spec and research manifests for sub-agent context. They do not replace `implement.md`.
- Lightweight tasks may be PRD-only. Complex tasks must have `prd.md`, `design.md`, and `implement.md` before `task.py start`.

The task specification in `prd.md` / `design.md` is not the same as `.trellis/spec/`. Task artifacts say what this change must do; `.trellis/spec/` says how this repository is engineered across tasks.

### Actual Matt Skills Integration

Trellis owns lifecycle, durable task state, context injection, and its final quality gate. The installed Matt Pocock skills own discovery, domain modeling, specification, ticketing, implementation, and qualitative review. Do not implement a second version of those skills in this file.

For Codex, keep these three mechanisms separate:

1. **Installation** — the complete upstream skill directory exists at `.agents/skills/<name>/`, including `SKILL.md`, `agents/openai.yaml`, and any references/assets. `.codex/skills/` is not the project skill root for this integration.
2. **Discovery** — Codex exposes the skill's name, description, and source path in its skill catalog. If duplicate names exist, confirm the selected source is this repository's `.agents/skills/` copy; Codex does not merge duplicates.
3. **Invocation** — the human types `$skill-name` (or selects it through `/skills`) and Codex loads that exact `SKILL.md`. A name in workflow prose is neither installation nor invocation.

The upstream Codex policy marks `$grill-with-docs`, `$wayfinder`, `$to-spec`, `$to-tickets`, and `$implement` as human-invoked (`allow_implicit_invocation: false`). The workflow and agent must not auto-chain them. At each boundary, present the exact next invocation and stop. `$grilling`, `$domain-modeling`, `$tdd`, and `$code-review` are model-reachable dependencies; follow them only through their real loaded instructions.

If the required project-local skill is absent or undiscoverable, stop and report the prerequisite instead of imitating it. The supported upstream project installer is `npx skills@latest add mattpocock/skills`; installation and the one-time `$setup-matt-pocock-skills` repository setup require separate user approval because they create files outside `.trellis/workflow.md`.

```text
human: $grill-with-docs       (or $wayfinder for multi-session fog)
          -> human: $to-spec
          -> human: $to-tickets
          -> human: $implement
          -> actual $code-review <fixed-point>
```

| Real skill | Skill-owned work | Trellis-owned handoff |
|---|---|---|
| `$grill-with-docs` | Loads the actual `grilling` and `domain-modeling` skills; conducts the interview and writes glossary/ADR material when warranted. | Record the invoked skill source and pointers to resulting decisions, `CONTEXT.md`, ADRs, research, or conversation handoff in the task. Do not run a second interview. |
| `$wayfinder` | Optional multi-session decision map for work too foggy to hold in one session. | Record the map and resolved-ticket pointers. Decision tickets are not implementation tickets; continue only when the map says the route is clear. |
| `$to-spec` | Synthesizes the settled discussion and publishes the specification to the configured tracker. | Copy/import the approved specification without reinterpretation into `prd.md` and, when needed, `design.md`; record the source URL/path. |
| `$to-tickets` | Creates and obtains approval for tracer-bullet tickets and their blocking edges. | Copy/import the approved ticket set, acceptance criteria, and blockers into `implement.md` or mapped child tasks. Do not decompose it again. |
| `$implement` | Implements the referenced spec/ticket, uses the real TDD/check dependencies, and commits. | Make it the sole implementation owner for that slice; record its validation/commit evidence and never dispatch `trellis-implement` for the same work. Obtain explicit commit consent before invocation; Phase 3.4 skips already-committed files. |
| `$code-review <fixed-point>` | Runs the actual two-axis Standards/Spec review against a resolvable Git fixed point. | Persist findings and route failures back to a new explicit `$implement`; run `trellis-check` separately for executable and Trellis-specific gates. |

### Artifact Handoff

```text
Request + codebase + existing specs
  -> actual $grill-with-docs or $wayfinder artifacts + task pointers
  -> actual $to-spec output -> prd.md + optional design.md (approved task contract)
  -> actual $to-tickets output -> implement.md / child tasks (slices + explicit blockers)
  -> implement.jsonl + check.jsonl (stable spec/research context)
  -> task.py start
  -> actual $implement output + recorded validation/commit
  -> actual $code-review report + executable trellis-check
       PASS -> Phase 3
       FAIL -> explicit $implement, or explicit $to-spec/$to-tickets when the contract/decomposition is wrong
```

Human approval is required for task creation, the specification and ticket decomposition before `task.py start`, any review finding that changes requirements or architecture, and the Phase 3.4 commit plan.

Task lifecycle status is not an approval record. Persist each approval before advancing: record the human's decision, its scope (specification/testing seam, decomposition/artifact chain, or revised contract), date, and the exact approved artifact paths in `prd.md` Notes or `implement.md`. `status=in_progress` proves only that `task.py start` ran; it is not evidence of what the human approved.

### Parent / Child Task Trees

Use a parent task when one user request contains several independently verifiable deliverables. The parent task owns the source requirement set, the task map, cross-child acceptance criteria, and final integration review; it normally should not be the implementation target unless it also has direct work.

Use child tasks for deliverables that can be planned, implemented, checked, and archived independently. Parent/child structure is not a dependency system: if one child must wait for another, write that ordering in the child `prd.md` / `implement.md` and keep each child's acceptance criteria testable.

Create new children with `task.py create "<title>" --slug <name> --parent <parent-dir>`. Link existing tasks with `task.py add-subtask <parent> <child>`, and unlink mistakes with `task.py remove-subtask <parent> <child>`.

<!-- Per-turn breadcrumb: shown when there is no active task (before Phase 1) -->

[workflow-state:no_task]
No active task. Classify the request with Request Triage and obtain consent before creating a Trellis task.
For an ambiguous/exploratory feature on the Matt route, create the task after consent, then tell the human to invoke the real project-local `$grill-with-docs` (or `$wayfinder` for multi-session fog) and STOP. Do not interview on its behalf. If the skill is missing or a duplicate source is ambiguous, report the installation/discovery problem instead of simulating it.
If the human already explicitly invoked an installed Matt skill, load that exact skill; obtain task consent before its first repository write. Small deterministic work may use the normal Trellis route, and read-only conversation/research needs no task.
[/workflow-state:no_task]

### Phase 1: Plan
- 1.0 Create task `[required · once]` (only after task-creation consent)
- 1.1 Discovery and specification `[required · repeatable]` (`prd.md`; complex tasks also need `design.md`)
- 1.2 Research `[optional · repeatable]`
- 1.3 Decompose tickets and configure context `[required · once]` — complex tasks need `implement.md`; sub-agent-dispatch platforms also curate JSONL
- 1.4 Approve and activate task `[required · once]` (artifact-chain review gate, then `task.py start`; status -> in_progress)
- 1.5 Completion criteria

<!-- Per-turn breadcrumb: shown throughout Phase 1 (status='planning') -->

[workflow-state:planning]
Read `prd.md` Notes to determine the planning route.
Matt route: do not load `trellis-brainstorm` or reproduce any Matt skill. Require the real project-local skill and record its selected path. If discovery is incomplete, tell the human to invoke `$grill-with-docs` (or `$wayfinder`) and STOP. After it finishes, bridge its artifact pointers into the task, then request the next human invocation `$to-spec`; after that real output is approved/imported, request `$to-tickets`. Never auto-chain human-invoked skills.
Normal Trellis route: load `trellis-brainstorm` and follow it normally; never describe that route as Matt's workflow.
Lightweight: an approved `prd.md` can be enough. Complex: finish `prd.md`, `design.md`, and a vertical-slice `implement.md` with explicit blockers, acceptance criteria, validation, and rollback.
Multi-deliverable scope: consider a parent task plus independently verifiable child tasks; dependencies must be written in child artifacts, not implied by tree position.
Sub-agent mode: curate `implement.jsonl` and `check.jsonl` as spec/research manifests before start.
Ask the user to approve the imported specification, ticket set, and complete artifact chain; persist approval and the last completed real skill, then run `task.py start`.
[/workflow-state:planning]

<!-- Per-turn breadcrumb: shown throughout Phase 1 when codex.dispatch_mode=inline.
     Codex-only opt-in alternate to [workflow-state:planning]. The main agent
     edits code directly in Phase 2, so jsonl curation is skipped —
     the inline workflow loads `trellis-before-dev` instead of injecting JSONL
     into a sub-agent. -->

[workflow-state:planning-inline]
Read `prd.md` Notes to determine the planning route.
Matt route: do not load `trellis-brainstorm` or reproduce any Matt skill. Require the real project-local skill and record its selected path. If discovery is incomplete, tell the human to invoke `$grill-with-docs` (or `$wayfinder`) and STOP. After it finishes, bridge its artifact pointers into the task, then request the next human invocation `$to-spec`; after that real output is approved/imported, request `$to-tickets`. Never auto-chain human-invoked skills.
Normal Trellis route: load `trellis-brainstorm` and follow it normally; never describe that route as Matt's workflow.
Lightweight: an approved `prd.md` can be enough. Complex: finish `prd.md`, `design.md`, and a vertical-slice `implement.md` with explicit blockers, acceptance criteria, validation, and rollback.
Multi-deliverable scope: consider a parent task plus independently verifiable child tasks; dependencies must be written in child artifacts, not implied by tree position.
Inline mode: skip jsonl curation; Phase 2 reads artifacts/specs via `trellis-before-dev`.
Ask the user to approve the imported specification, ticket set, and complete artifact chain; persist approval and the last completed real skill, then run `task.py start`.
[/workflow-state:planning-inline]

### Phase 2: Execute
- 2.1 Implement `[required · repeatable]`
- 2.2 Code review and quality check `[required · repeatable]`
- 2.3 Rollback `[on demand]`

<!-- Per-turn breadcrumb: shown while status='in_progress'.
     Scope: all of Phase 2 + Phase 3.2-3.4 (status stays 'in_progress' from
     task.py start until task.py archive; only archive flips it). The body
     therefore must cover every required step from implementation through
     commit, including Phase 3.3 spec update and Phase 3.4 commit. -->

Sub-agent dispatch protocol applies to all platforms and all sub-agents, including native Codex `SubagentStart` context injection with child-side pull fallback, class-2 Gemini/Qoder/Copilot/Reasonix/Trae/Grok/Kimi Code, hook-backed ZCode/Snow, and `trellis-research`: every dispatch prompt starts with `Active task: <task path from task.py current>` before role-specific instructions. On Grok Build, use `spawn_subagent` with `subagent_type` set to the Trellis agent name (e.g. `trellis-implement`). On Kimi Code, dispatch the built-in `coder` / `explore` sub-agent with the matching `.kimi-code/skills/trellis-<role>/SKILL.md` instructions.

This automatic platform injection does not apply to `trellis channel`; channel coordinators must wait for `spawned` and pass the task artifacts with explicit `--file` / `--jsonl` context.

[workflow-state:in_progress]
Tools: `trellis-implement` / `trellis-research` are sub-agent types only (Task/Agent tool, NOT Skill; there is no skill by these names). `trellis-update-spec` is a skill. `trellis-check` exists as both; prefer the Agent form when verifying after code changes.
Resume guard: status is coarse. Read `prd.md` Notes for the route and the latest `implement.md` ledger before acting.
Matt route: the human explicitly invokes the real `$implement` for the next unblocked ticket; never dispatch `trellis-implement` for the same slice. After implementation, require an actual `$code-review <fixed-point>` with a non-empty committed diff, then run `trellis-check` as the separate executable/Trellis gate. Persist each real skill source, output, and review result. FAIL returns to a new explicit `$implement`; never imitate or auto-chain a human-invoked skill.
Normal Trellis route: next unblocked implementation slice -> two-axis `trellis-check` -> PASS or routed correction.
All routes: PASS -> `trellis-update-spec` -> commit if still dirty (Phase 3.4) -> `/trellis:finish-work`.
Contract axis: verify `prd.md`, `design.md`, `implement.md` slice acceptance criteria, and no scope creep. Standards axis: verify relevant `.trellis/spec/`, repository conventions, architecture, and executable checks.
Do not silently change requirements. A contract/decomposition defect returns to Phase 1 artifacts and human approval; a code defect returns to Phase 2.1.
Normal Trellis route default: dispatch implement/check sub-agents. Sub-agent self-exemption: if already running as `trellis-implement`, do NOT spawn another `trellis-implement` or `trellis-check`; if already running as `trellis-check`, do NOT spawn another `trellis-check` or `trellis-implement`. Dispatch is main session only.
Dispatch prompt starts with `Active task: <task path from task.py current>`. Read context: jsonl entries -> `prd.md` -> `design.md if present` -> `implement.md if present`.
[/workflow-state:in_progress]

<!-- Per-turn breadcrumb: shown while status='in_progress' when
     codex.dispatch_mode=inline. Codex-only opt-in alternate to
     [workflow-state:in_progress]. The main session edits code directly
     instead of dispatching sub-agents. -->

[workflow-state:in_progress-inline]
Read `prd.md` Notes for the route and reconcile the latest `implement.md` ledger before acting.
Matt route: the human explicitly invokes the real `$implement`; do not implement inline as a substitute. Require an actual `$code-review <fixed-point>` after a non-empty committed diff, then run `trellis-check` separately. FAIL returns to a new explicit `$implement`; never imitate or auto-chain a human-invoked skill.
Normal Trellis route: `trellis-before-dev` -> next unblocked slice -> two-axis `trellis-check` -> PASS or routed correction.
All routes: PASS -> `trellis-update-spec` -> commit if still dirty (Phase 3.4) -> `/trellis:finish-work`.
Do not dispatch implement/check sub-agents in inline mode; the Matt skill is a main-session skill, not a Trellis sub-agent.
Contract axis: verify `prd.md`, `design.md`, `implement.md` slice acceptance criteria, and no scope creep. Standards axis: verify relevant `.trellis/spec/`, repository conventions, architecture, and executable checks.
Do not silently change requirements. A contract/decomposition defect returns to Phase 1 artifacts and human approval; a code defect returns to Phase 2.1.
Read context: `prd.md` -> `design.md if present` -> `implement.md if present`, plus relevant spec/research loaded by skills.
[/workflow-state:in_progress-inline]

### Phase 3: Finish
- 3.2 Debug retrospective `[on demand]`
- 3.3 Spec update `[required · once]`
- 3.4 Commit changes `[required · once]`
- 3.5 Wrap-up reminder

> Note: step 3.1 was folded into 2.2 (last-iteration full-scope check) and 3.4 (commit preamble). Numbering kept stable to avoid breaking external references.

<!-- Per-turn breadcrumb: shown while status='completed'.
     Currently DEAD in normal flow: cmd_archive writes status='completed' in
     the same call that moves the task dir to archive/, so the active-task
     resolver loses the pointer and the hook never fires on archived tasks.
     Block preserved for a future status-transition redesign (e.g. an
     explicit in_progress→completed command). Edit through the same spec
     channel as the live blocks. -->

[workflow-state:completed]
Code committed. Run `/trellis:finish-work`; if dirty, return to Phase 3.4 first.
[/workflow-state:completed]

### Rules

1. Identify which Phase you're in, then continue from the next step there
2. Run steps in order inside each Phase; `[required]` steps can't be skipped
3. Phases can roll back (e.g., Execute reveals a prd defect → return to Plan to fix, then re-enter Execute)
4. Steps tagged `[once]` are skipped if the output already exists; don't re-run
5. Artifact presence informs the next step; missing `design.md` / `implement.md` is valid for lightweight tasks and incomplete planning for complex tasks.
6. A rollback does not invent a new task status. Update the current task artifacts, obtain the required approval, and resume through the existing `planning` / `in_progress` lifecycle.
7. Keep decision tickets, implementation slices, and parent/child grouping distinct; only explicit blocker text defines execution order.
8. A worker timeout, crash, or interrupted turn is not phase completion. Inspect its owned artifacts, keep the task at the last verified step, and retry with a fresh worker given the exact task path and durable inputs. Do not depend on the failed worker's transcript; partial output must pass the same review gate as a normal handoff.

### Active Task Routing

When a user request matches one of these intents inside an active task, route first, then load the detailed phase step if needed.

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

- Matt planning route -> wait for the human's explicit invocation of the installed `$grill-with-docs`, `$wayfinder`, `$to-spec`, or `$to-tickets` appropriate to the current handoff; never substitute `trellis-brainstorm` or auto-chain the next skill.
- Normal Trellis planning route -> `trellis-brainstorm`.
- Matt `in_progress` route -> actual `$implement` / `$code-review`, with `trellis-check` only as the separate Trellis quality gate; never dispatch `trellis-implement` for the same slice.
- Normal Trellis `in_progress` route -> dispatch `trellis-implement` / `trellis-check`.
- Repeated debugging -> `trellis-break-loop`; spec updates -> `trellis-update-spec`.

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

[codex-inline, Kilo, Antigravity, Devin]

- Matt planning route -> wait for the human's explicit invocation of the installed `$grill-with-docs`, `$wayfinder`, `$to-spec`, or `$to-tickets` appropriate to the current handoff; never substitute `trellis-brainstorm` or auto-chain the next skill.
- Normal Trellis planning route -> `trellis-brainstorm`.
- Matt `in_progress` route -> actual `$implement` / `$code-review`, then `trellis-check`; never edit inline as a substitute for `$implement`.
- Normal Trellis route -> before editing `trellis-before-dev`; after editing `trellis-check`.
- Repeated debugging -> `trellis-break-loop`; spec updates -> `trellis-update-spec`.

[/codex-inline, Kilo, Antigravity, Devin]

### Guardrails

- Task creation approval is not implementation approval; implementation waits for `task.py start` after artifact review.
- On the Matt route, never generate interview questions, a specification, tickets, implementation, or a review as a fallback for an unavailable Matt skill. Stop and report the missing installation/discovery/invocation prerequisite.
- Mentioning a skill in workflow prose neither installs nor invokes it. Record actual use only when the platform loaded the intended project-local `SKILL.md`; a same-name global copy is not proof that the repository integration ran.
- Upstream human-invoked skills are separate approval boundaries. The agent may present `$grill-with-docs`, `$wayfinder`, `$to-spec`, `$to-tickets`, or `$implement` as the next command, but must stop until the human explicitly invokes it.
- PRD-only is valid for lightweight tasks; complex tasks need `design.md` + `implement.md`.
- Planning must be persisted to task artifacts; a glossary, ADR, issue-map gist, or conversation is not a substitute for the task contract.
- `prd.md` / `design.md` are the change specification; `.trellis/spec/` remains the repository's reusable engineering contract.
- Actual `$wayfinder` decision tickets answer questions; imported `$to-tickets` output and mapped child Trellis tasks deliver code. Do not implement product work while the real decision map is still open.
- Parent/child task links group work but do not schedule it. Record every blocker explicitly in `implement.md` and, for child tasks, their own `prd.md` / `implement.md`.
- Implement agents may not reinterpret or silently expand approved requirements. Route ambiguity back to planning and human approval.
- Actual `$code-review` owns its Standards/Spec review; `trellis-check` remains a separate executable and Trellis-spec gate. Neither may be relabeled as the other, and both must reach an explicit PASS before Phase 3 on the Matt route.

### Loading Step Detail

At each step, run this to fetch detailed guidance:

```bash
python3 ./.trellis/scripts/get_context.py --mode phase --step <step>
# e.g. python3 ./.trellis/scripts/get_context.py --mode phase --step 1.1
```

---

## Phase 1: Plan

Goal: classify the request, get task-creation consent when a task is needed, and produce the planning artifacts required before implementation.

#### 1.0 Create task `[required · once]`

Create the task directory only after task-creation consent. The command sets status to `planning`, writes `task.json`, creates a default `prd.md`, and auto-targets the new task when session identity is available:

```bash
python3 ./.trellis/scripts/task.py create "<task title>" --slug <name>
```

`--slug` is the human-readable name only. Do **not** include the `MM-DD-` date prefix; `task.py create` adds that prefix automatically.

For task trees, create the parent task first and then create each child with `--parent <parent-dir>`. Do not start the parent just because children exist; start the child that owns the next independently verifiable deliverable.

When session identity is available, the per-turn breadcrumb auto-switches to `[workflow-state:planning]`, telling the AI to stay in planning. Without session identity, task creation still succeeds but no pointer is persisted; keep the task path explicit until identity is available.

Run only `create` here — do not also run `start`. `start` flips status to `in_progress`, which switches the breadcrumb to the implementation phase before planning artifacts are reviewed. Save `start` for step 1.4.

Skip when `python3 ./.trellis/scripts/task.py current --source` already points to a task.

#### 1.1 Discovery and specification `[required · repeatable]`

Choose and persist `Planning route: Matt Skills` or `Planning route: Trellis` in `prd.md` Notes. Also persist the current stage because the lifecycle value `planning` represents the whole planning phase, not its individual workflow steps.

**Matt Skills route**:

1. Verify the required skill is discoverable and that its selected `SKILL.md` is the intended project-local `.agents/skills/` copy. Record the skill name and source path. If it is missing or ambiguous, stop with the installation/discovery prerequisite; do not load `trellis-brainstorm` as a substitute.
2. For ordinary ambiguous feature/design work, tell the human to invoke `$grill-with-docs <task context>` and stop. For a genuinely multi-session foggy effort, tell the human to invoke `$wayfinder <destination or map reference>` and stop. Follow only the loaded skill's own instructions.
3. When the real discovery skill finishes, add a bridge record to `prd.md` Notes: the completed skill, its source path, and pointers to its `CONTEXT.md`, ADRs, map/tickets, research, or other durable outputs. Preserve any implementation-relevant resolved decision that otherwise exists only in chat, but do not conduct another interview or invent a parallel decision model.
4. Tell the human to invoke `$to-spec <discovery/map reference>` and stop. `$to-spec` owns specification synthesis and publication. After it finishes, copy/import its approved body without reinterpretation into `prd.md` and, for complex technical detail, `design.md`; record the tracker URL/path and selected skill source.
5. Ask the human to approve the imported specification and testing seam. Append a dated approval record to `prd.md` Notes. Do not advance with a missing, contradictory, or low-resolution source specification.

`$wayfinder` is an alternative discovery on-ramp, not a mandatory stage before `$grill-with-docs`, and its decision tickets do not authorize implementation. A human must explicitly invoke `$to-spec` when the map is clear; the agent must not call it automatically.

**Normal Trellis route**:

Load `trellis-brainstorm` and follow that actual skill normally. Persist the resulting `prd.md` and, for complex work, `design.md`; ask for specification/testing-seam approval. Never describe this route as `grill-with-docs` or claim a Matt skill ran.

When considering a parent/child split:
- Use a parent task when one request contains several independently verifiable deliverables.
- Parent tasks own source requirements, child-task mapping, cross-child acceptance criteria, and final integration review.
- Child tasks own actual deliverables that can be planned, implemented, checked, and archived independently.
- Parent/child structure is not a dependency system. If child B depends on child A, write that ordering in child B's `prd.md` / `implement.md`.
- Start the child task that owns the next deliverable. Do not start the parent unless the parent itself has direct implementation work.

Return to this step whenever requirements change and revise the relevant artifact.

#### 1.2 Research `[optional · repeatable]`

Research can happen at any time during requirement exploration. It isn't limited to local code — you can use any available tool (MCP servers, skills, web search, etc.) to look up external information, including third-party library docs, industry practices, API references, etc.

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

Spawn the research sub-agent:

- **Agent type**: `trellis-research`
- **Task description**: Research <specific question>
- **Key requirement**: Research output MUST be persisted to `{TASK_DIR}/research/`

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

[codex-inline, Kilo, Antigravity, Devin]

Do the research in the main session directly and write findings into `{TASK_DIR}/research/`. `codex-inline` is the explicit mode that keeps work in the main session.

[/codex-inline, Kilo, Antigravity, Devin]

**Research artifact conventions**:
- One file per research topic (e.g. `research/auth-library-comparison.md`)
- Record the question, scope, date/version, source links, code references, findings, implications for the task, and caveats / not-found results
- Prefer primary sources and distinguish verified behavior from inference
- When research resolves a decision dependency, record the full outcome and relevant rejected alternatives, not only a summary or external pointer
- Record third-party library usage examples, API references, version constraints, and relevant spec file paths for later context curation

Brainstorm and research can interleave freely — pause to research a technical question, then return to talk with the user.

**Key principle**: Research output must be written to files, not left only in the chat. Conversations get compacted; files don't.

**Channel-runtime boundary**: `trellis channel` workers do not receive the active task's planning artifacts or platform sub-agent hook injection automatically. Wait for the worker's `spawned` event before sending work, then supply the exact task path plus explicit `--file` / `--jsonl` context. The bundled channel role cards cover `implement` and `check`; keep research on the main/platform `trellis-research` path unless a compatible research role is explicitly configured. Do not ask a generic channel worker to invoke another research sub-agent recursively; the channel runtime rejects recursive worker dispatch.

#### 1.3 Decompose tickets and configure context `[required · once]`

On the Matt Skills route, do not translate the specification yourself. Tell the human to invoke `$to-tickets <approved spec reference>` and stop. After the actual skill has obtained approval and published its tickets, copy/import their titles, acceptance criteria, explicit blocking edges, source URLs/paths, and order into `implement.md` or mapped child tasks. Record the loaded `$to-tickets` source path. The import is Trellis context bookkeeping, not a second decomposition pass.

On the normal Trellis route, translate the approved specification into implementation-sized tracer bullets using the rules below. In either route, implementation tickets are distinct from `$wayfinder` decision tickets.

For a complex task, write `implement.md` as an ordered checklist. Each slice must include:
- **What it delivers** — a narrow but complete, independently demonstrable or verifiable behavior
- **Blocked by** — explicit slice or child-task names; `None` when it can start immediately
- **Acceptance criteria** — the task-contract behavior that proves this slice is complete
- **Required context** — relevant research/spec artifacts, without pre-registering source files to edit
- **Validation** — focused tests/checks during the slice and any full-scope check it contributes to
- **Rollback point** — how to back out the slice without disturbing unrelated or user-owned work

Prefer vertical slices across affected layers over horizontal layer batches. Size each slice for one fresh implementation context. For a wide mechanical refactor that cannot remain green as a vertical slice, use an explicit expand -> migrate in independently verifiable batches -> contract sequence.

Use child Trellis tasks when slices can be planned, implemented, checked, and archived independently. The parent/child relationship is grouping only: copy blockers into the relevant child `prd.md` / `implement.md`. Keep a progress checkbox for every slice, but mark it complete only after its step 2.2 review passes.

Lightweight PRD-only work may omit `implement.md` when it is genuinely one independently verifiable slice. The user reviews decomposition and blockers at step 1.4.

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

Curate `implement.jsonl` and `check.jsonl` so the Phase 2 sub-agents get the right spec/research context. These files were seeded on `task create` with a single self-describing `_example` line; your job here is to fill in real entries.

**Location**: `{TASK_DIR}/implement.jsonl` and `{TASK_DIR}/check.jsonl` (already exist).

**Format**: one JSON object per line — `{"file": "<path>", "reason": "<why>"}`. Paths are repo-root relative.

**What to put in**:
- **Spec files** — `.trellis/spec/<package>/<layer>/index.md` and any specific guideline files (`error-handling.md`, `conventions.md`, etc.) relevant to this task
- **Research files** — `{TASK_DIR}/research/*.md` that the sub-agent will need to consult

**What NOT to put in**:
- Code files (`src/**`, `packages/**/*.ts`, etc.) — those are read by the sub-agent during implementation, not pre-registered here
- Files you're about to modify — same reason

**Split between the two files**:
- `implement.jsonl` → specs + research the implement sub-agent needs to write code correctly
- `check.jsonl` → specs for the check sub-agent (quality guidelines, check conventions, same research if needed)

These manifests do not replace `implement.md`. `implement.md` is the human-readable execution plan for a complex task; jsonl files only list context files to inject or load.

**How to discover relevant specs**:

```bash
python3 ./.trellis/scripts/get_context.py --mode packages
```

Lists every package + its spec layers with paths. Pick the entries that match this task's domain.

**How to append entries**:

Either edit the jsonl file directly in your editor, or use:

```bash
python3 ./.trellis/scripts/task.py add-context "$TASK_DIR" implement "<path>" "<reason>"
python3 ./.trellis/scripts/task.py add-context "$TASK_DIR" check "<path>" "<reason>"
```

Delete the seed `_example` line once real entries exist (optional — it's skipped automatically by consumers).

Ready gate: both `implement.jsonl` and `check.jsonl` must contain at least one real `{"file": "...", "reason": "..."}` entry before `task.py start`. The seed `_example` row alone is not ready.

Skip this step only when both files already have real curated entries.

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

[codex-inline, Kilo, Antigravity, Devin]

The ticket decomposition above still applies. Skip only JSONL curation; context is loaded directly by the `trellis-before-dev` skill in Phase 2.

[/codex-inline, Kilo, Antigravity, Devin]

#### 1.4 Approve and activate task `[required · once]`

Review the complete handoff with the user before changing task status:

1. Research and decision evidence needed downstream is persisted, not chat-only.
2. `prd.md` faithfully captures the original request, constraints, non-goals, acceptance criteria, and agreed testing seams.
3. Complex-task `design.md` and `implement.md` are consistent with the PRD; slices are vertical, independently verifiable, and have explicit blockers.
4. Required `.trellis/spec/` and task research are represented in the correct context manifests for sub-agent mode.
5. Validation and rollback expectations are concrete.

If the user changes or rejects any part, return to 1.1, 1.2, or 1.3 and review again. Approval of the artifact chain is approval to enter implementation; task-creation consent alone is not.

Before activation, append a dated artifact-chain approval record to `implement.md` (or `prd.md` Notes for a PRD-only task). Include the human decision, approved artifact paths, testing seam, slice granularity, blocker edges, validation expectations, and whether the context manifests were included. Do not run `task.py start` while this record is absent.

On sub-agent-dispatch platforms, validate the manifests before activation:

```bash
python3 ./.trellis/scripts/task.py validate <task-dir>
```

After artifact review, flip the task status to `in_progress`:

```bash
python3 ./.trellis/scripts/task.py start <task-dir>
```

For lightweight tasks, `prd.md` can be enough. For complex tasks, `prd.md`, `design.md`, and `implement.md` must exist and be reviewed before start. On sub-agent-dispatch platforms, `implement.jsonl` and `check.jsonl` must both have real curated entries before start. Runtime consumers tolerate missing or seed-only manifests for compatibility, but that tolerance is not a planning-ready state.

When session identity is available, this command persists the session pointer, flips `planning` to `in_progress`, and the breadcrumb switches to `[workflow-state:in_progress]`. If session identity is unavailable, the command may still advance lifecycle status without persisting an active-task pointer. Follow its identity hint before relying on later hook injection, and keep the task path explicit in the current conversation meanwhile.

If a later review requires planning changes while status is already `in_progress`, revise and reapprove the same task artifacts. Do not invent a rollback status or rerun `task.py start` merely to represent the loop.
Persist the revised-contract approval beside the changed artifact before implementation resumes.

#### 1.5 Completion criteria

| Condition | Required |
|------|:---:|
| `prd.md` contains a reviewed, implementation-ready task contract | ✅ |
| Material research / decision dependencies are persisted with sources | when applicable |
| User approves specification, testing seams, ticket granularity, and blockers | ✅ |
| Specification approval and artifact-chain activation approval are durably recorded | ✅ |
| `task.py start` has been run (status = in_progress) | ✅ |
| `design.md` exists (complex tasks) | ✅ |
| `implement.md` has vertical slices, explicit blockers, acceptance criteria, validation, and rollback (complex tasks) | ✅ |

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

| `implement.jsonl` and `check.jsonl` each contain at least one real curated entry (seed row does not count) | ✅ |

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

---

## Phase 2: Execute

Goal: turn reviewed planning artifacts into code that passes quality checks.

#### 2.1 Implement `[required · repeatable]`

Select the first incomplete slice whose explicit blockers are complete.

**Matt Skills route**:

1. Before the first implementation invocation, capture a resolvable Git fixed point (normally the current `HEAD`) for the later real `$code-review`. If no Git fixed point exists, state that the upstream review skill is unavailable; do not fake it or initialize Git.
2. Tell the human exactly which approved spec/ticket is on the frontier and that upstream `$implement` commits. Obtain and persist explicit commit consent. This committed change is required so the real post-implementation `$code-review` can compare `HEAD` with the saved fixed point; Phase 3.4 later skips files already committed by the skill.
3. Tell the human to invoke `$implement <spec/ticket reference>` and stop. Verify Codex loaded the intended project-local skill. The loaded skill is the sole implementation owner: do not dispatch `trellis-implement`, edit inline as a substitute, or paraphrase its TDD/validation instructions.
4. After the real skill returns, record its source path, ticket/slice, focused/full validation evidence, resulting commit or working-tree state, and any unresolved finding in `implement.md`. Then continue to 2.2.

**Normal Trellis route**:

State the selected slice in the dispatch prompt or inline work plan; do not ask an implement agent to consume an entire multi-slice backlog implicitly. The platform-specific dispatch instructions below apply only to this route.

For each slice:
1. Read its acceptance criteria and the approved task artifacts in the platform-specific order below.
2. Implement only that slice. Do not silently redesign interfaces, expand scope, or reinterpret a requirement.
3. Run the slice's focused tests and relevant lint / type-check commands during implementation; record commands and outcomes with the slice in `implement.md`. Reserve the full affected suite for the final full-scope review unless the plan requires it sooner.
4. Hand the diff and validation result to step 2.2. The main session marks the `implement.md` checkbox complete only after review passes.

If implementation exposes a missing fact, return to 1.2. If it exposes an ambiguous or defective requirement, design, testing seam, or blocker, stop coding and return to the corresponding Phase 1 artifact plus human approval.

[Claude Code, Cursor, OpenCode, codex-sub-agent, CodeBuddy, Droid, Pi, ZCode, Snow, Oh My Pi]

Spawn the implement sub-agent:

- **Agent type**: `trellis-implement`
- **Task description**: Implement the named next unblocked slice from the reviewed task artifacts, consulting `{TASK_DIR}/research/`; run that slice's specified validation
- **Dispatch prompt guard**: The prompt MUST start with `Active task: <task path>`, then tell the spawned agent it is already the `trellis-implement` sub-agent and must implement directly, not spawn another `trellis-implement` / `trellis-check`.

The platform hook/plugin auto-handles:
- Reads `implement.jsonl` and injects referenced spec/research files into the agent prompt
- Injects `prd.md`, `design.md` if present, and `implement.md` if present
- For Codex, `SubagentStart` supplies native context injection; the agent profile keeps child-side loading as the fallback

[/Claude Code, Cursor, OpenCode, codex-sub-agent, CodeBuddy, Droid, Pi, ZCode, Snow, Oh My Pi]

[Gemini, Qoder, Copilot, Reasonix, Trae, Grok, Kimi Code]

Spawn the implement sub-agent:

- **Agent type**: `trellis-implement`
- **Task description**: Implement the named next unblocked slice from the reviewed task artifacts, consulting `{TASK_DIR}/research/`; run that slice's specified validation
- **Dispatch prompt guard**: The prompt MUST start with `Active task: <task path>`, then explicitly say the spawned agent is already `trellis-implement` and must implement directly without spawning another `trellis-implement` / `trellis-check`.

The pull-based sub-agent definition auto-handles the context load requirement:
- Resolves the active task with `task.py current --source`, then reads `prd.md`, `design.md` if present, and `implement.md` if present
- Reads `implement.jsonl` and requires the agent to load each referenced spec/research file before coding

[/Gemini, Qoder, Copilot, Reasonix, Trae, Grok, Kimi Code]

[Kiro]

Spawn the implement sub-agent:

- **Agent type**: `trellis-implement`
- **Task description**: Implement the named next unblocked slice from the reviewed task artifacts, consulting `{TASK_DIR}/research/`; run that slice's specified validation
- **Dispatch prompt guard**: Tell the spawned agent it is already the `trellis-implement` sub-agent and must implement directly, not spawn another `trellis-implement` / `trellis-check`.

The platform prelude auto-handles the context load requirement:
- Reads `implement.jsonl` and injects referenced spec/research files into the agent prompt
- Injects `prd.md`, `design.md` if present, and `implement.md` if present

[/Kiro]

[codex-inline, Kilo, Antigravity, Devin]

1. Load the `trellis-before-dev` skill to read project guidelines
2. Read `{TASK_DIR}/prd.md`, then `design.md` if present, then `implement.md` if present
3. Consult materials under `{TASK_DIR}/research/`
4. Implement only the named next unblocked slice per reviewed artifacts
5. Run the slice's specified focused validation and relevant lint / type-check

[/codex-inline, Kilo, Antigravity, Devin]

#### 2.2 Code review and quality check `[required · repeatable]`

**Matt Skills route**:

1. Confirm the saved fixed point resolves and `git diff <fixed-point>...HEAD` is non-empty. The current upstream `$code-review` compares committed `HEAD` history; an internal review attempted by `$implement` before its commit does not prove that the implementation diff was reviewed.
2. Tell the human to invoke `$code-review <fixed-point>` and stop. Verify the intended project-local `SKILL.md` loaded; do not produce a Matt-like review in its place.
3. Persist the actual Standards and Spec reports, source path, fixed point, commit list, and explicit result in `implement.md`.
4. On FAIL, keep the finding durable, tell the human to invoke `$implement <ticket plus review findings>`, and after correction require the real `$code-review <same fixed-point>` again. Do not restart discovery unless the finding identifies a specification/decomposition defect, and do not run an unbounded automatic loop.
5. On PASS, run `trellis-check` as a separate, report-only gate for `.trellis/spec/` compliance and executable validation. On this route it must not self-fix: any code finding returns to a new explicit `$implement`, commit, and real `$code-review`. Matt's qualitative review does not replace tests, lint, type-check, or build checks, and Trellis's check must never be reported as the Matt skill.

For the normal Trellis route, review the working-tree diff before the Phase 3 commit. For the additive Trellis gate on the Matt route, review the same fixed-point scope and recorded task artifacts. Keep two axes separate so one cannot mask the other:

1. **Contract axis** — compare behavior with the original request as preserved in `prd.md`, material research decisions, `design.md` if present, and the current `implement.md` slice's acceptance criteria. Report missing/partial behavior, incorrect behavior, and scope creep.
2. **Standards axis** — compare the diff with relevant `.trellis/spec/`, repository conventions, architectural constraints, and established code/test patterns. Report hard violations separately from judgment calls.

Then run the executable gate appropriate to every affected package: focused and full tests required by the plan, lint, type-check, and build/format checks the repository defines. Do not claim the qualitative review replaces these commands.

Persist the outcome and validation evidence with the task: update the current slice in `implement.md`, or for a PRD-only task mark its acceptance checklist and add a concise validation note under `prd.md` Notes. Unresolved findings stay recorded until the routed correction passes review.

The main coordinator owns this persistence even when the check agent reports only to chat/channel: before routing a failure or marking a PASS, ensure the task artifact records both axis results, commands and exit states, concrete unresolved findings, the next route, and any later correction. A channel message or original conversation is not a durable feedback handoff.

If the project root is not a Git repository, do not initialize Git and do not claim a repository-diff review. Use only an explicit baseline or changed-file set plus executable artifact checks, state that scope limitation in the review record, and keep Contract/Standards conclusions limited to the files actually inspected. Absence of Git evidence never turns a partial scope review into a full working-tree review.

Review outcomes:
- **PASS** — both axes have no unresolved hard findings, every current-slice acceptance criterion is met, and required commands pass. Mark the slice complete; continue at 2.1 if slices remain, otherwise run the final full-scope 2.2 pass.
- **FIXED** — normal Trellis route only: the check agent may directly fix bounded code/standards defects, rerun affected commands, and report PASS when clean. On the Matt route, route every code change through explicit `$implement` and `$code-review`; do not let the additive check create an unreviewed diff.
- **FAIL: implementation** — on the Matt route, request a new explicit `$implement` with the concrete findings; on the normal Trellis route, return to 2.1. Rerun 2.2 after correction.
- **FAIL: contract/decomposition** — on the Matt route, return to a new explicit `$to-spec` or `$to-tickets` as appropriate, then import and reapprove the corrected artifacts; on the normal Trellis route, return to 1.1 or 1.3. Resume 2.1 only after approval.
- **DECISION REQUIRED** — when a standard conflicts with the approved contract or a judgment call would change architecture/requirements, ask the user; persist the decision before resuming.

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

Spawn the check sub-agent:

- **Agent type**: `trellis-check`
- **Task description**: Review the current slice on separate Contract and Standards axes; self-fix bounded code issues; run the slice's required executable checks and return an explicit outcome
- **Dispatch prompt guard**: The prompt MUST start with `Active task: <task path>`, then tell the spawned agent it is already the `trellis-check` sub-agent and must review/fix directly, not spawn another `trellis-check` / `trellis-implement`.

The check agent's job:
- Review code changes against `prd.md`, material research decisions, `design.md` if present, and the current `implement.md` slice
- Review code changes against relevant `.trellis/spec/`, repository conventions, architecture, and established patterns
- Keep Contract and Standards findings separate
- Normal Trellis route: auto-fix bounded implementation/standards issues, but never silently change the approved contract. Matt route: report findings without edits so corrections stay inside real `$implement` -> `$code-review`.
- Run the required tests, lint, type-check, build, or other repository checks and return PASS / FIXED / FAIL / DECISION REQUIRED

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi, ZCode, Snow, Reasonix, Trae, Grok, Kimi Code]

[codex-inline, Kilo, Antigravity, Devin]

Load the `trellis-check` skill and verify the code per its guidance:
- Contract compliance against task artifacts and current-slice acceptance criteria
- Standards compliance against `.trellis/spec/` and repository conventions
- lint / type-check / tests / build checks required by the repository and plan
- Cross-layer consistency (when changes span layers)

Apply the same explicit outcome routing above; do not run an unbounded fix/review loop.

[/codex-inline, Kilo, Antigravity, Devin]

**Final pass (before Phase 3.4 commit)**: the last 2.2 of a task must run full-scope, not just on the latest implement chunk. List all affected packages with `python3 ./.trellis/scripts/get_context.py --mode packages`, then load each package's spec index Quality Check section. This catches cross-layer / multi-package issues a mid-iteration local 2.2 cannot.

#### 2.3 Rollback `[on demand]`

- Missing or stale fact -> 1.2, persist research, update affected artifacts, reapprove when the contract changes
- PRD/design/testing-seam defect -> on the Matt route, request a new explicit `$to-spec`; otherwise return to 1.1. Import/revise the specification, obtain human approval, then redo 2.1.
- Slice granularity, order, blocker, or validation defect -> on the Matt route, request a new explicit `$to-tickets`; otherwise return to 1.3. Import/revise `implement.md` / child artifacts, obtain human approval, then redo 2.1.
- Implementation defect -> on the Matt route, request a new explicit `$implement`; otherwise return to 2.1. Change only the failed slice while preserving unrelated and user-owned work, then rerun 2.2.
- Standards/contract conflict or architectural judgment -> user decision, persist it in the appropriate task artifact, then resume at the routed step

The task normally remains `in_progress` during these feedback loops. Keep review and rollback as workflow routing decisions; do not invent lifecycle states unless the configured runtime supports them.

---

## Phase 3: Finish

Goal: ensure code quality, capture lessons, record the work.

#### 3.2 Debug retrospective `[on demand]`

If this task involved repeated debugging (the same issue was fixed multiple times), load the `trellis-break-loop` skill to:
- Classify the root cause
- Explain why earlier fixes failed
- Propose prevention

The goal is to capture debugging lessons so the same class of issue doesn't recur.

#### 3.3 Spec update `[required · once]`

Load the `trellis-update-spec` skill and review whether this task produced new knowledge worth recording:
- Newly discovered patterns or conventions
- Pitfalls you hit
- New technical decisions

Update the docs under `.trellis/spec/` accordingly. Do not copy task-only requirements into repository specs; only reusable engineering contracts belong there. Even if the conclusion is "nothing to update", walk through the judgment.

#### 3.4 Commit changes `[required · once]`

**Spec-sync preamble**: before drafting commits, ask: did this task fix a bug or surface non-obvious knowledge that should land in `.trellis/spec/` so future-you (or future-AI) doesn't repeat the mistake? If yes, return to Phase 3.3 first — spec writes belong in the same task's commit batch, not as a forgotten follow-up.

The AI drives a batched commit of this task's code changes so `/finish-work` can run cleanly afterwards. Goal: produce work commits FIRST, then bookkeeping (archive + journal) commits land after — never interleaved.

If neither the project root nor the affected package root is a Git repository, do not initialize Git. Report that this required commit step is unavailable and ask the user whether to keep the task `in_progress` or finish without a commit. Only after explicit no-commit approval may the task be archived with `task.py archive <task> --no-commit`; record that exception in the task artifact and do not describe it as a successful commit.

**Step-by-step**:

1. **Inspect dirty state**:
   ```bash
   git status --porcelain
   ```
   Snapshot every dirty path. If the working tree is clean, skip to 3.5.

2. **Learn commit style** from recent history (so drafted messages blend in):
   ```bash
   git log --oneline -5
   ```
   Note the prefix convention (`feat:` / `fix:` / `chore:` / `docs:` ...), language (中文/English), and length style.

3. **Classify dirty files into two groups**:
   - **AI-edited this session** — files you wrote/edited via Edit/Write/Bash tool calls in this session. You know what changed and why.
   - **Unrecognized** — dirty files you did NOT touch this session (could be the user's manual edits, leftover WIP from a previous session, or unrelated work). Do NOT silently include these.

4. **Draft a commit plan**. Group AI-edited files into logical commits (1 commit per coherent change unit, not 1 commit per file). Each entry: `<commit message>` + file list. List unrecognized files separately at the bottom.

5. **Present the plan once, ask for one-shot confirmation**. Format:
   ```
   Proposed commits (in order):
     1. <message>
        - <file>
        - <file>
     2. <message>
        - <file>

   Unrecognized dirty files (NOT in any commit — confirm include/exclude):
     - <file>
     - <file>

   Reply 'ok' / '行' to execute. Reply with edits, or '我自己来' / 'manual' to abort.
   ```

6. **On confirmation**: run `git add <files>` + `git commit -m "<msg>"` for each batch in order. Do not amend. Do not push.

7. **On rejection** (user replies "不行" / "我自己来" / "manual" / any pushback on the plan): stop. Do not attempt a second plan. The user will commit by hand; you skip ahead to 3.5 once they confirm.

**Rules**:
- No `git commit --amend` anywhere — three-stage three-commit flow (work commits → archive commit → journal commit).
- Never push to remote in this step.
- If the user wants different message wording but accepts the file grouping, edit the message and re-confirm once — but if they reject the grouping, exit to manual mode.
- The batched plan is one prompt; do not prompt per commit.

#### 3.5 Wrap-up reminder

After the above, remind the user they can run `/finish-work` to wrap up (archive the task, record the session).

---

## Customizing Trellis (for forks)

This section is for developers who want to modify the Trellis workflow itself. All customization is done by editing this file; the scripts are parsers only.

### Changing what a step means

Edit the corresponding step's walkthrough body in the Phase 1 / 2 / 3 sections above. Critical invariants:
- No active task must triage first and ask for task-creation consent before creating a Trellis task.
- Planning must distinguish lightweight PRD-only tasks from complex tasks that require `prd.md`, `design.md`, and `implement.md` before start.
- Every required execution path must keep the Phase 3.4 commit reminder reachable before `/trellis:finish-work`.

All tag blocks live in the `## Phase Index` section above, immediately after each phase summary:

| Scope | Corresponding tag |
|---|---|
| No active task (before Phase 1) | `[workflow-state:no_task]` (after the Phase Index ASCII art) |
| All of Phase 1 (task created → ready for implementation) | `[workflow-state:planning]` (after Phase 1 summary) |
| Codex inline Phase 1 | `[workflow-state:planning-inline]` |
| Phase 2 + Phase 3.2–3.4 (implementation + check + wrap-up) | `[workflow-state:in_progress]` (after Phase 2 summary) |
| Codex inline Phase 2 + Phase 3.2–3.4 | `[workflow-state:in_progress-inline]` |
| After Phase 3.5 (archived) | `[workflow-state:completed]` (after Phase 3 summary; **currently DEAD**) |

### Changing the per-turn prompt text

Directly edit the body of the corresponding `[workflow-state:STATUS]` block. After editing, run `trellis update` (if you're a template maintainer) or restart your AI session (if you're customizing your own project) — no script changes required.

### Adding a custom status

Add a new block:

```
[workflow-state:my-status]
your per-turn prompt text
[/workflow-state:my-status]
```

Constraints:
- STATUS charset: `[A-Za-z0-9_-]+` (underscores and hyphens allowed, e.g. `in-review`, `blocked-by-team`)
- A lifecycle hook must write `task.json.status` to your custom value, otherwise the tag is never read
- Lifecycle hooks live in `task.json.hooks.after_*` and bind to one of `after_create / after_start / after_finish / after_archive`

### Adding a lifecycle hook

Add a `hooks` field to your `task.json`:

```json
{
  "hooks": {
    "after_finish": [
      "your-script-or-command-here"
    ]
  }
}
```

Supported events: `after_create / after_start / after_finish / after_archive`. Note that `after_finish` ≠ a status change (it only clears the active-task pointer); use `after_archive` for "task is done" notifications.

### Full contract

For the workflow state machine implementation in this configured Codex project, see:

- `.codex/hooks/inject-workflow-state.py` — workflow-state parser, active-task lookup, and selected-workflow resolution
- `.trellis/scripts/common/workflow_phase.py` — phase-index and step extraction used by `get_context.py --mode phase`
- `.trellis/scripts/common/active_task.py` — session pointer and pseudo-status source resolution
- `.trellis/scripts/task.py` and `.trellis/scripts/common/task_store.py` — lifecycle commands and status writers
