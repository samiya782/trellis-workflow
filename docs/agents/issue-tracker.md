# Issue tracker: Trellis Tasks

This repository uses Trellis tasks as the `Other` publication backend for the
Matt Pocock engineering skills. It does not use GitHub Issues, GitLab Issues,
or the local-markdown tracker. A Trellis task directory is the published
object; its files are the object body and its `task.json` is the identity and
lifecycle record.

This document is an operational contract for an agent running one of the Matt
skills. Follow it when a skill says to publish, fetch, label, claim, block, or
close an issue. Do not report publication until the verification checklist for
the operation has passed.

## Commands and boundaries

Run commands from the repository root:

```bash
python3 .trellis/scripts/task.py <command> ...
```

The supported Trellis operations used by this backend are:

```text
task.py create <title> [--slug <slug>] [--description <text>] [--parent <dir>] [--meta key=value] [--no-start]
task.py set-meta <dir> <key> <value>
task.py add-context <dir> <implement|check> <path> [reason]
task.py list --json
task.py current --json
task.py list-context <dir>
task.py validate <dir>
task.py start <dir>
task.py finish
task.py archive <dir> --no-commit
```

`task.py create --parent` is the supported parent/child operation. It writes
the child `parent` field and the parent's `children` list. Parent/child is
grouping, not a dependency scheduler. `task.py set-meta` stores string values
under `task.json.meta`; it does not change lifecycle status. `task.py start`
changes `planning` to `in_progress` and is an implementation activation, so it
must never be used merely to publish or mark a specification ready.

Use `task.py archive <dir> --no-commit` only after implementation, review, and
the Trellis quality gate have passed and the human has approved completion.
The `--no-commit` flag leaves the Phase 3 commit decision to the normal
workflow. `task.py finish` only clears the current-session pointer; it does not
complete a task.

There is no native Trellis dependency graph, issue label API, comment API, or
task fetch command used by this backend. Dependencies and notes are therefore
stored in task artifacts, while `task.json` and the task directory provide the
recoverable identity. Do not invent another command or lifecycle state.

## Publication identity and lookup

### Canonical reference

The publication identity is the exact Trellis task directory basename emitted
by `task.py create`:

```text
MM-DD-<slug>
```

Use the opaque reference form below in skill handoffs, task artifacts, and
human-facing reports:

```text
trellis-task:MM-DD-<slug>
```

The date prefix is part of the identity. `task.json.id` is only the slug and
is not a sufficient reference because it is not globally unique by itself.
Never use a bare slug as a publication identity.

For an active publication, the canonical path is:

```text
.trellis/tasks/MM-DD-<slug>/
```

After archival, the directory moves to:

```text
.trellis/tasks/archive/YYYY-MM/MM-DD-<slug>/
```

The `trellis-task:` reference does not change. Resolve an active path first;
if it is absent, search the archive for exactly one directory with the exact
basename. If zero or multiple matches are found, stop and ask for the full
path. Do not guess from a title, a suffix, the active-task list, or chat
history.

### Fetch procedure

Given `trellis-task:MM-DD-<slug>`:

1. Remove only the `trellis-task:` prefix and retain the complete basename.
2. Resolve `.trellis/tasks/<basename>/`; otherwise resolve the one exact
   archive match under `.trellis/tasks/archive/`.
3. Read `task.json`, then read the artifact named by the publication metadata.
4. Verify the `task.json` `meta.matt_publication_ref` equals the reference and
   verify the expected `parent`/`children` relationship before using content.
5. Read the task's `implement.jsonl` and `check.jsonl` with
   `task.py list-context` when implementation or checking context is needed.

A fresh session can reconstruct a publication using this procedure without a
conversation transcript. `task.py current --json` / `--source` may identify a
session-bound task, but the explicit `trellis-task:` reference remains the
source of truth when no unambiguous pointer exists.

### Lifecycle and readiness

Trellis lifecycle and Matt readiness are separate dimensions:

| Meaning | Trellis record | Matt backend record |
| --- | --- | --- |
| Published but not activated | `task.json.status=planning` | `meta.matt_ready_for_agent=true` |
| Human-approved implementation is active | `status=in_progress` after `task.py start` | readiness metadata remains descriptive |
| Completed and archived | `status=completed` in the archive copy | readiness metadata remains historical |

The value `ready-for-agent` means "the published body is complete enough for
the next agent to inspect." It is a metadata marker, not permission to start,
not a scheduler state, and not a replacement for human approval. Use the
literal string `true`/`false` in metadata:

```bash
python3 .trellis/scripts/task.py set-meta <TASK_DIR> matt_ready_for_agent true
```

Every publication also sets one of these values:

```text
matt_publication_kind=spec | ticket | wayfinder-map | wayfinder-ticket
matt_publication_ref=trellis-task:<same complete basename>
```

Ticket tasks additionally set:

```text
matt_parent_ref=trellis-task:<parent complete basename>
```

Metadata values are strings. Do not store JSON, comma-separated state
machines, or a synthetic `ready-for-agent` lifecycle status in `task.json`.

## Specification publication (`$to-spec`)

`$to-spec` owns synthesis, the user seam check, and the Matt specification
format. This backend only defines how its completed output is persisted and
identified. Do not interview again, rewrite requirements, or silently omit a
section while publishing.

### Preconditions

- A human has approved the task creation and the settled conversation is
  available to `$to-spec`.
- Use the existing top-level planning task when one was created by Trellis.
- If no task exists, obtain task-creation consent before running the verified
  `task.py create ... --no-start` command. Do not create a publication as a
  side effect of merely reading a spec.
- Do not overwrite an existing non-placeholder publication. If the reference
  is wrong or the task belongs to another request, stop.

### Canonical artifacts

The complete Matt specification is preserved across the task's two Trellis
artifacts without dropping or rewriting a section. Use this section mapping:

- `prd.md` contains `Problem Statement`, `Solution`, `User Stories`,
  `Testing Decisions`, `Out of Scope`, and `Further Notes`. Keep the
  requirements and user-facing acceptance contract here. Add a Trellis
  `## Acceptance Criteria` projection when the approved Matt output does not
  already have one; every item must be traceable to that output and is not a
  new requirement.
- `design.md` contains `Implementation Decisions` and any technical detail
  needed to make those decisions executable. Keep the approved wording and
  all decision alternatives that Matt recorded; do not add a new decision.

The logical specification is reconstructed by reading both files and ordering
the mapped sections according to the original Matt output. It must contain the
complete upstream section set:

```text
Problem Statement
Solution
User Stories
Implementation Decisions
Testing Decisions
Out of Scope
Further Notes
```

`prd.md` is the canonical requirements publication; it is not a summary or a
ticket index. `design.md` is its required technical companion for a complex
task. Preserve all requirements, decisions, acceptance implications, and
non-goals from the approved Matt output. Do not split one Matt section between
the two files or silently discard its original heading/content.

For a complex task (the normal case for this chain), also write the Trellis
`design.md` companion. It records only the technical boundaries, data flow,
compatibility, tradeoffs, and rollback shape already authorized by `prd.md`.
It may point back to the corresponding sections, but it must not introduce a
new requirement or replace any part of the Matt body. A lightweight task may
omit `design.md` only when the Trellis workflow explicitly classifies it as
PRD-only.

Do not create `implement.md` during `$to-spec`; ticket decomposition belongs to
`$to-tickets`.

### Publication operation

If a task must be created, use the actual task command and capture the exact
path it prints:

```bash
python3 .trellis/scripts/task.py create "<spec title>" \
  --slug <slug> \
  --description "<problem summary>" \
  --no-start
```

For an existing task, use its exact `.trellis/tasks/MM-DD-<slug>` path. Write
the completed Matt body to `prd.md`; for a complex task write the corresponding
technical companion to `design.md`. Set the identity metadata and an initial
false readiness marker without changing the lifecycle:

```bash
python3 .trellis/scripts/task.py set-meta <TASK_DIR> matt_publication_kind spec
python3 .trellis/scripts/task.py set-meta <TASK_DIR> matt_publication_ref trellis-task:<TASK_BASENAME>
python3 .trellis/scripts/task.py set-meta <TASK_DIR> matt_spec_artifacts "prd.md,design.md"
python3 .trellis/scripts/task.py set-meta <TASK_DIR> matt_ready_for_agent false
```

Use `matt_spec_artifacts=prd.md` for a PRD-only task. The value is a fetch
manifest, not a new Trellis schema field.

### Verification and result

Publication succeeds only when all applicable checks pass:

1. The exact task directory and `task.json` exist.
2. `prd.md` is non-empty and contains every mapped requirements section and
   the Trellis `Acceptance Criteria` projection; no `TBD` placeholder remains
   in a required decision or acceptance section.
3. `design.md` exists and is non-empty when the task is complex, contains the
   complete mapped `Implementation Decisions` section, and does not contradict
   `prd.md`.
4. `task.py list --json` (or an exact direct `task.json` read for an archived
   task) confirms the task identity; a top-level spec has `parent: null`.
5. `task.py list-context <TASK_DIR>` and `task.py validate <TASK_DIR>` are run
   when manifests were seeded or curated; any validation error is a failure.
6. Only after checks 1-5 pass, set `matt_ready_for_agent=true`, then directly
   reread `task.json` and confirm every metadata value, including the complete
   `matt_publication_ref` and final readiness marker.

Report the reference, canonical path, artifact list, and current Trellis
status. Never call the Matt publication complete if any check fails. Do not
run `task.py start` as part of this operation. On any failure, leave
`matt_ready_for_agent=false`. A human must approve the specification and later
activation separately.

### Fetching a published specification

For `trellis-task:<basename>`, resolve the task, verify
`matt_publication_kind=spec`, then read all files named by
`matt_spec_artifacts` in order (`prd.md`, then `design.md` when listed). The
logical spec is the complete `prd.md` plus its non-conflicting Trellis design
companion. If either required artifact or the identity metadata is missing,
stop and report an unpublished/incomplete spec instead of reconstructing it
from conversation history.

## Ticket publication (`$to-tickets`)

`$to-tickets` owns vertical-slice design, the granularity quiz, user approval,
and blocker decisions. This backend owns only the durable Trellis objects and
their references. Do not re-decompose an approved set while publishing it.

### Preconditions

- Fetch the approved parent spec using the procedure above.
- Obtain explicit user approval of ticket granularity and every blocking edge.
- Publish blockers before tickets that reference them, so every reference can
  be verified immediately.
- Do not change the parent `prd.md`, its readiness metadata, or its lifecycle
  status. Establishing child links and adding a Trellis execution index are
  the only parent-side bookkeeping allowed here.

### One ticket, one child task

Each approved Matt ticket is one independently identifiable child task. Never
put the entire ticket set in one `implement.md` and call publication done.
For each ticket, create a child with the verified parent operation:

```bash
python3 .trellis/scripts/task.py create "<ticket title>" \
  --slug <ticket-slug> \
  --description "<ticket outcome>" \
  --parent <PARENT_TASK_DIR> \
  --meta matt_publication_kind=ticket \
  --meta matt_ready_for_agent=false \
  --no-start
```

Capture the command's returned basename. The resulting `task.json.parent`
must equal the parent's basename and the parent `task.json.children` list
must contain it. Set the identity metadata only after the basename is known;
leave readiness false while writing and validating the batch:

```bash
python3 .trellis/scripts/task.py set-meta <CHILD_TASK_DIR> matt_publication_ref trellis-task:<CHILD_BASENAME>
python3 .trellis/scripts/task.py set-meta <CHILD_TASK_DIR> matt_parent_ref trellis-task:<PARENT_BASENAME>
```

Write the complete approved ticket body to the child's `prd.md`; preserve its
title, `What to build`, acceptance criteria, and `Blocked by` edges. Add these
Trellis handoff fields without replacing the Matt content:

```markdown
## Parent

trellis-task:<PARENT_BASENAME>

## Context

Read the parent task's `prd.md` and `design.md` (when present), then this
ticket's complete body. The ticket is the slice contract; the parent is the
source requirement contract.
```

The canonical blocker syntax is a `## Blocked by` section with one
`trellis-task:<CHILD_BASENAME>` list item per dependency. Use
`- None - can start immediately` when there are no blockers. Do not represent
a blocker with a Trellis `parent` field: parentage is grouping only.

Create or update the parent's `implement.md` as a Trellis execution index. It
must list every child reference in dependency order, the child title, the
acceptance summary, and the exact blocker references. The child `prd.md` is
the authoritative ticket body; the index must not contain a second divergent
copy of it.

### Context handoff

For every child that will be implemented or checked, add the parent contract
and relevant research/spec files to both manifests using the supported command:

```bash
python3 .trellis/scripts/task.py add-context <CHILD_TASK_DIR> implement <PARENT_TASK_DIR>/prd.md "Approved parent specification"
python3 .trellis/scripts/task.py add-context <CHILD_TASK_DIR> check <PARENT_TASK_DIR>/prd.md "Approved parent specification"
python3 .trellis/scripts/task.py add-context <CHILD_TASK_DIR> implement <PARENT_TASK_DIR>/design.md "Approved technical design"
python3 .trellis/scripts/task.py add-context <CHILD_TASK_DIR> check <PARENT_TASK_DIR>/design.md "Approved technical design"
```

Use repository-relative paths and omit the `design.md` entries only when the
parent publication is PRD-only. Add applicable `research/` or `.trellis/spec/`
files the same way. `add-context` records pointers; it does not copy files.
Run `task.py list-context` and `task.py validate` for each child after
curation. The child task's own `prd.md` remains directly discoverable and need
not be duplicated into its manifests.

### Ticket verification and result

Do not report `$to-tickets` publication success until every approved ticket
passes all checks:

1. One child directory exists for the ticket and its `task.json` has a unique
   complete basename, `status=planning`, exact `parent`, and
   `matt_publication_kind=ticket`.
2. The child `prd.md` is non-empty and contains the complete ticket body,
   acceptance criteria, the parent reference, and canonical blocker
   references.
3. Every blocker reference resolves to an existing sibling task (active or
   archived) and is not the child itself. A missing or cyclic edge fails the
   publication; Trellis does not validate dependencies for us.
4. The parent `task.json.children` contains every published child exactly once
   (while preserving any pre-existing children), and the parent `implement.md`
   index matches the new batch without changing the parent spec body or
   lifecycle.
5. Both context manifests are listed and `task.py validate <CHILD_TASK_DIR>`
   passes for every child that has them.
6. Only after checks 1-5 pass for the entire batch, set
   `matt_ready_for_agent=true` on every child. Reread each `task.json` and
   verify `matt_publication_ref`, `matt_parent_ref`, and the final readiness
   marker before reporting success.

If any child fails, leave the partial objects identifiable, set every child in
the incomplete batch back to `matt_ready_for_agent=false`, report every
created reference, and do not claim a completed ticket publication. Do not
delete or silently recreate partial tasks.

### Fetching tickets and selecting the frontier

To fetch one ticket, resolve its `trellis-task:` reference, verify
`matt_publication_kind=ticket`, read its complete `prd.md`, then follow
`matt_parent_ref` to the parent `prd.md` and `design.md`. Read
`implement.jsonl`/`check.jsonl` through `task.py list-context` when context
injection is relevant. Treat a ticket as published only when
`matt_ready_for_agent=true`; false means a partial or failed publication. The
ticket's `task.json.status` is the lifecycle status: `planning` is
published/unstarted, `in_progress` is active after an approved `task.py start`,
and an archived copy with `status=completed` is done.

The next available ticket is determined textually, not by a hidden scheduler:

1. Read the parent `children` list and each child's status and readiness
   metadata.
2. Ignore children that are not ready, completed, or already `in_progress`.
3. Parse every reference under `## Blocked by` in the child body.
4. A planning child is on the frontier only when every referenced blocker is
   archived/completed. Preserve the approved parent-list order when several
   children are available.

Before implementation, the human chooses a frontier child and explicitly runs
`task.py start <CHILD_TASK_DIR>`. Never start all children, start a blocked
child, or treat `matt_ready_for_agent=true` as activation.

## Implementation and review handoff

The real `$implement` skill is invoked with one exact child reference/path. It
must read the child ticket, parent spec/design, and curated context before
coding. The adapter does not implement, reinterpret, or close a ticket. Record
the skill's validation and commit evidence in the child `implement.md` or
review record, and keep the child reference available for the reviewer.

Invoke the real review skill with a fixed Git point and the exact published
spec/ticket path. The path is mandatory for this backend because the upstream
review skill's automatic lookup understands external issue syntax, not the
custom `trellis-task:` token. For a parent specification split across Trellis
artifacts, pass both paths so the Spec axis receives the complete logical spec:

```text
$code-review <fixed-point> .trellis/tasks/<PARENT_BASENAME>/prd.md .trellis/tasks/<PARENT_BASENAME>/design.md
```

If the review is for a child, pass the child `prd.md` plus the parent `prd.md`
and `design.md` resolved through `matt_parent_ref`. A `trellis-task:<basename>`
token is a valid reference for this backend, but it is not a GitLab/GitHub
issue number; resolve it with this document before reviewing. Review findings
are persisted under the task (for example, a `## Review` section in
`implement.md`) before routing a failure to a new explicit `$implement`
invocation. `$code-review` and `trellis-check` remain separate: the former is
qualitative Standards/Spec review, while the latter runs the repository's
executable and Trellis quality checks.

### Closing and archival

After the implementation slice, review, and `trellis-check` pass, obtain human
completion approval, then archive the child with:

```bash
python3 .trellis/scripts/task.py archive <CHILD_TASK_DIR> --no-commit
```

Archive all children before archiving their parent. This preserves the
parent/child history because archiving a parent clears `parent` fields on
still-active children. Archive the parent only after the final integration
check and approval. The stable `trellis-task:` references continue to resolve
through the archive path.

## Notes and unsupported operations

Append discussion, publication evidence, and review findings to the relevant
task artifact under a dated `## Notes` or `## Review` heading. Do not invent a
separate comments API or issue number. When an upstream skill asks to apply a
triage label, use `meta.matt_ready_for_agent` as the only configured state
marker; do not add a synthetic lifecycle status or mutate `task.json.status`.

This adapter intentionally does not claim native tracker features that Trellis
does not expose: external URLs, labels, comments, assignment mutation,
dependency edges, or atomic multi-task transactions. Parent/child links,
metadata, task artifacts, JSONL context, and the verified commands above are
the complete backend surface. Any operation outside that surface is blocked
until a human supplies an approved project-level extension; do not silently
fall back to GitLab or local markdown.

## Wayfinding operations

The optional `$wayfinder` route uses the same Trellis task surface; it must not
fall back to local markdown. A map is a top-level planning task with
`meta.matt_publication_kind=wayfinder-map` (the configured representation of
the upstream `wayfinder:map` label); its `prd.md` contains the exact
`Destination`, `Notes`, `Decisions so far`, `Not yet specified`, and `Out of
scope` sections from the real skill. A decision ticket is a child task with
`meta.matt_publication_kind=wayfinder-ticket`,
`meta.matt_wayfinder_type=research|prototype|grilling|task` (the configured
representation of the upstream `wayfinder:<type>` label), and a `prd.md`
beginning with `## Question`.

Use `task.py create --parent ... --no-start` for map children. Because Trellis
has no assignment mutation command, claiming an existing decision ticket is
recorded with `task.py set-meta <TICKET_DIR> matt_claimed_by <developer>`;
this marker is the claim, and it must be written before research or discussion.
Blocking edges use the same exact `## Blocked by` section and
`trellis-task:<basename>` list convention as implementation tickets. The frontier is the first child in
the map's `children` list whose blockers are archived/completed and whose
`matt_claimed_by` is absent. Resolve a decision by appending `## Resolution`
and a durable context pointer to the map's `Decisions so far`, then archive
the child with `task.py archive <TICKET_DIR> --no-commit`; do not call
`task.py start` for a planning decision. Each map update and child resolution
must be verified by rereading the exact task files and metadata. These
operations preserve wayfinder's planning-only boundary; they never activate
implementation.
