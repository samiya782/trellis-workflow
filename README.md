# Trellis + Matt Pocock Skills

This repository packages a project-level integration between Trellis and the
official [Matt Pocock Skills](https://github.com/mattpocock/skills).

It is an installation and operating guide for an existing Trellis project. It
does not vendor, fork, patch, or imitate Matt's Skills.

The reusable integration payload is:

- [`.trellis/workflow.md`](.trellis/workflow.md) - Trellis lifecycle and route
  orchestration.
- [`docs/agents/issue-tracker.md`](docs/agents/issue-tracker.md) - the
  Trellis `Other` publication backend used by the real Matt Skills.
- [`README.md`](README.md) - this installation and operating guide.

```text
trellis/
|-- .trellis/
|   `-- workflow.md
|-- docs/
|   `-- agents/
|       `-- issue-tracker.md
`-- README.md
```

Other files in this repository belong to Trellis itself or to this checkout's
local runtime. They are not part of the three-file integration payload.

## 1. What this integration does

The integration gives each system one clear responsibility:

- **Trellis** owns task identity, lifecycle state, approvals, durable
  artifacts, context handoffs, recovery, and executable verification.
- **The official Matt Skills** own discovery, interviewing, domain modeling,
  specification, ticket decomposition, implementation methodology, and
  qualitative code review.
- **The developer** selects the route, invokes human-owned Skills, answers
  questions, and approves specifications, tickets, activation, commits, and
  completion.
- **Codex** discovers and executes the installed project-local Skills.

The complete Matt route is:

```text
$grill-with-docs
  -> $to-spec
  -> $to-tickets
  -> $implement
  -> $code-review
  -> $trellis-check
```

This is not one automatic command. The workflow tells the agent which stage is
current, which durable artifacts to load, and which real Skill should run
next. The developer invokes each human-owned Matt stage explicitly.

Trellis does not implement Matt's Skills. It does not simulate
`$grill-with-docs`, copy Matt's question tree into the workflow, or rewrite
Matt's specification and ticket methods. A Skill name appearing in
`.trellis/workflow.md` is routing guidance, not proof that the Skill is
installed, discovered, or invoked.

## 2. Prerequisites

Install these tools before applying the integration:

- **Codex**, with project-local Skill discovery.
- **Trellis**, with the `trellis` command available.
- **Node.js and `npx`**, for the official Skills installer.
- **Git**, when using `$implement` and the fixed-point
  `$code-review` gate.
- **The official Matt Pocock Skills**, installed into the target project.
- **An initialized Trellis project**.

Initialize the target project from its repository root:

```bash
trellis init -u your-name --codex
```

This command creates the Trellis runtime and Codex integration for that
project. Run the remaining installation steps from the same repository root.

The minimum setup after initialization is:

```bash
# 1. Install the official upstream Skills into the target project.
npx skills@latest add mattpocock/skills --agent codex

# 2. Install the project workflow adapter.
cp ~/trellis/.trellis/workflow.md .trellis/workflow.md

# 3. Install the Trellis Other publication backend.
mkdir -p docs/agents
cp ~/trellis/docs/agents/issue-tracker.md docs/agents/issue-tracker.md

# 4. Inspect and commit the shared project configuration.
git status --short
```

Then start a fresh Codex session so it reloads the project's instructions and
Skill catalog. The sections below explain each step and its verification.

Do not initialize Git merely to satisfy the workflow. Without a real Git
repository and committed fixed point, the Matt fixed-point review gate is not
available.

## 3. Install Matt Pocock Skills

Install directly from the official upstream repository:

```bash
npx skills@latest add mattpocock/skills --agent codex
```

Choose project scope when prompted. Installing the complete upstream bundle is
the simplest reproducible option. At minimum, the full chain needs these
upstream Skills and dependencies:

```text
grill-with-docs
grilling
domain-modeling
to-spec
to-tickets
implement
tdd
code-review
```

The installer, not this repository, owns the installed Matt files. The
expected Codex project paths include:

```text
.agents/skills/grill-with-docs/SKILL.md
.agents/skills/grilling/SKILL.md
.agents/skills/domain-modeling/SKILL.md
.agents/skills/to-spec/SKILL.md
.agents/skills/to-tickets/SKILL.md
.agents/skills/implement/SKILL.md
.agents/skills/code-review/SKILL.md
```

Verify the project-scoped installation:

```bash
npx skills@latest list --agent codex --json

test -f .agents/skills/grill-with-docs/SKILL.md
test -f .agents/skills/grilling/SKILL.md
test -f .agents/skills/domain-modeling/SKILL.md
test -f .agents/skills/to-spec/SKILL.md
test -f .agents/skills/to-tickets/SKILL.md
test -f .agents/skills/implement/SKILL.md
test -f .agents/skills/code-review/SKILL.md
```

If `.agents/skills/` already exists, do not delete it. Let the installer add
or update the selected Matt Skills, preserve unrelated project Skills, and
review any reported name collision. Do not manually copy Matt Skills from this
repository: this repository contains Trellis helpers, not a vendored Matt
bundle.

A same-name global Skill is not a substitute for the project-local
installation. In Codex, verify that the loaded source path belongs to the
target repository's `.agents/skills/<name>/SKILL.md`.

The installer normally creates or updates `skills-lock.json`. Commit that
lockfile in the target project so a fresh clone can restore the same upstream
bundle. Do not hand-edit its source or integrity values.

## 4. Install / copy the Trellis workflow

Run this after `trellis init`, because initialization creates a default
workflow:

```bash
cp ~/trellis/.trellis/workflow.md .trellis/workflow.md
```

The copied file is a project-level workflow adapter. It is not Trellis CLI
core code. It preserves the normal Trellis route and adds a small, explicit
Matt route that points to real installed Skills.

This command intentionally replaces the initialized project's workflow.
Before copying into a project with custom workflow rules, review those rules
and merge them deliberately. Do not copy Matt's internal instructions into
the workflow as a conflict-resolution shortcut.

Verify the installed file:

```bash
cmp ~/trellis/.trellis/workflow.md .trellis/workflow.md
rg -n '\$grill-with-docs|\$to-spec|\$to-tickets|\$implement|\$code-review|trellis-check' \
  .trellis/workflow.md
```

A later Trellis initialization or update may offer to replace project files.
Review its diff and preserve this project workflow rather than assuming it
will be regenerated automatically.

## 5. Install the Other publication backend

The full `$to-spec -> $to-tickets` chain needs a publication target. This
integration uses Trellis tasks through Matt's official `Other` tracker
mechanism. It does not use GitHub Issues, GitLab Issues, or the local-markdown
tracker.

Install the validated project-level contract:

```bash
mkdir -p docs/agents
cp ~/trellis/docs/agents/issue-tracker.md docs/agents/issue-tracker.md
```

The file instructs the real Matt Skills how to use supported Trellis
operations:

- A Trellis task is the publication object.
- The exact task basename is the publication identity:
  `trellis-task:MM-DD-slug`.
- `$to-spec` publishes the logical specification to parent `prd.md` and,
  for a complex task, `design.md`.
- `$to-tickets` publishes every approved ticket as a separate Trellis child
  task.
- The parent `implement.md` is an execution index, not a replacement for
  child ticket bodies.
- Each blocker is an explicit `trellis-task:` reference in the child
  `## Blocked by` section.
- `task.json.meta.matt_ready_for_agent` records publication readiness.
- `matt_ready_for_agent=true` never activates implementation.
- Only explicit human approval followed by `task.py start` changes the
  Trellis task to `in_progress`.
- Every publish operation verifies identity, artifacts, metadata,
  parent/child links, blockers, and context before reporting success.

The adapter uses only commands exposed by the target project's Trellis
runtime. It is an operational publication contract, not a second tracker
service and not a replacement Skill.

Do not run `$setup-matt-pocock-skills` just to select a hosted issue system.
This package already supplies the required `Other` configuration. A Git
remote hosted by GitLab or GitHub says nothing about which issue tracker a
project uses.

## 6. Files you need to modify after `trellis init`

| File | Required? | Why |
| --- | --- | --- |
| `.trellis/workflow.md` | Yes | Copy this repository's project workflow so Trellis can route between its normal path and the real Matt path. |
| `docs/agents/issue-tracker.md` | Yes for the complete chain | Copy the Trellis `Other` publication contract used by `$to-spec` and `$to-tickets`. |
| `.agents/skills/` | Yes, installer-managed | Run the upstream `npx skills` installer. Do not copy or edit Matt Skill source manually. |
| `skills-lock.json` | Yes for reproducible clones | Commit the installer-generated upstream source and integrity lock. Do not fabricate it. |
| `AGENTS.md` | No manual integration edit | `trellis init --codex` creates or updates the Trellis-managed instructions. Keep project-specific instructions outside its managed block. |
| `.trellis/scripts/` | No manual integration edit | These are Trellis runtime files. The backend calls their supported commands. |
| Application code and tests | No setup edit | They change only when a real approved implementation task requires it. |
| Matt `SKILL.md` files | Never hand-edit | They remain official upstream content; update them through the Skills installer. |
| Trellis task artifacts | Per real task | They are durable project work, not adapter installation files. |

### Must copy or install

```text
copy:    .trellis/workflow.md
copy:    docs/agents/issue-tracker.md
install: official Matt Skills with npx skills
track:   skills-lock.json generated by that installation
```

### Required only in specific situations

- `design.md` is required for a complex published specification; a genuinely
  lightweight Trellis task may be PRD-only.
- `implement.jsonl` and `check.jsonl` are curated when agent context
  injection is used.
- `CONTEXT.md`, `CONTEXT-MAP.md`, and ADRs are produced only when the real
  Matt Skills determine they are warranted.
- `$wayfinder` is for uncertainty that genuinely spans multiple sessions,
  not the default starting point.

### Do not modify for this integration

- Matt files under `.agents/skills/`.
- Trellis CLI or `.trellis/scripts/`.
- Business code, tests, CI, or package files during installation.
- Git remote or issue-tracker settings.
- `AGENTS.md` merely to repeat this README or Matt prompts.

## 7. First-time setup checklist

- [ ] Run `trellis init -u your-name --codex` in the target repository.
- [ ] Run `npx skills@latest add mattpocock/skills --agent codex`.
- [ ] Confirm the installation is project-local.
- [ ] Confirm the core Matt `SKILL.md` files exist under `.agents/skills/`.
- [ ] Copy `~/trellis/.trellis/workflow.md`.
- [ ] Copy `~/trellis/docs/agents/issue-tracker.md`.
- [ ] Check whether the installer created or updated `skills-lock.json`.
- [ ] Confirm `AGENTS.md` contains the Trellis-managed block; do not duplicate
      the integration instructions there.
- [ ] Run `python3 ./.trellis/scripts/task.py --help`.
- [ ] Verify Codex discovers the project-local `$grill-with-docs`.
- [ ] Verify Codex discovers `$to-spec`, `$to-tickets`, `$implement`, and
      `$code-review`.
- [ ] Verify Codex discovers the Trellis `$trellis-check` Skill.
- [ ] Review the Git diff and commit the shared workflow, backend, and
      `skills-lock.json`; exclude machine-local runtime state.

## 8. How to use

### Route an ambiguous request

Example user request:

> I want to add user preferences to the system, but the exact product
> behavior and data model are not decided yet.

Use this sequence:

1. Trellis classifies the request as ambiguous product/design work.
2. Obtain approval to create a planning task.
3. Create or enter the Trellis task.
4. The developer invokes the real `$grill-with-docs`.
5. The Skill researches the repository and domain.
6. The Skill presents its numbered question frontier.
7. The human answers until discovery is settled.
8. The developer invokes the real `$to-spec`.
9. The human confirms the testing seam and approves the completed spec.
10. The `Other` backend publishes the spec to the parent Trellis task.
11. The developer invokes the real `$to-tickets`.
12. The human approves ticket granularity and explicit blockers.
13. The backend publishes one Trellis child task per ticket.
14. The human selects one ready, unblocked child and explicitly activates it.
15. The developer invokes the real `$implement`.
16. After the implementation commit, the developer invokes
    `$code-review <fixed-point>` with the complete spec paths.
17. The developer invokes `$trellis-check` independently.
18. After both gates pass and completion is approved, archive the child.
19. Repeat for the next frontier ticket, then complete the parent.

The workflow may present the exact next invocation, but it must stop at every
human-owned boundary. It must not answer the discovery questions, generate a
Matt-like spec, or decompose tickets in place of the real Skills.

### Stage inputs, outputs, and approvals

| Stage | Input | Durable output or handoff | Human boundary |
| --- | --- | --- | --- |
| `$grill-with-docs` | Ambiguous request, repository, parent task reference | Settled decisions and pointers to research, domain context, or ADR artifacts | Answer numbered questions and confirm shared understanding |
| `$to-spec` | Settled discovery context and task reference | Parent `prd.md`, complex-task `design.md`, publication identity and readiness metadata | Confirm testing seam and approve final spec |
| `$to-tickets` | Approved published spec | One child task per ticket, parent index, context manifests, blocker references | Approve granularity, ordering, and blocker edges |
| `task.py start` | One ready and unblocked child | Child lifecycle changes from `planning` to `in_progress` | Explicit implementation approval |
| `$implement` | Exact child, parent spec/design, acceptance criteria, context | Code, tests, validation evidence, and commit | Approve implementation and commit behavior |
| `$code-review` | Fixed point, committed diff, child and parent spec paths | Parallel Standards and Spec findings plus conclusion | Resolve findings; return contract changes to planning |
| `$trellis-check` | Diff, artifacts, repository specifications and checks | Independent executable and Trellis quality result | Approve completion only after PASS |
| Finish | Passed gates and completed children | Archived task and durable history | Explicit completion approval |

### Create the parent planning task

Run from the target repository root:

```bash
PARENT_TASK="$(python3 ./.trellis/scripts/task.py create \
  "User preferences" \
  --slug user-preferences \
  --description "Define and implement user preferences")"

PARENT_BASENAME="${PARENT_TASK##*/}"
PARENT_REF="trellis-task:${PARENT_BASENAME}"

printf '%s\n' "${PARENT_TASK}" "${PARENT_REF}"
```

Do not include a date prefix in `--slug`; Trellis creates it. Task creation is
not implementation approval. The task remains in `planning` until a human
approves the complete implementation handoff and activates a child.

## 9. Manual Skill invocation

Enter these commands in the Codex conversation. They are Skill invocations,
not shell commands.

### Discovery

```text
$grill-with-docs

Trellis task: trellis-task:<MM-DD-parent-slug>
Request: Add user preferences, but product behavior and the data model are not
settled. Research the repository before opening the question frontier.
```

The real Skill may research for some time before it asks its first numbered
question. Do not mistake that research phase for a missing installation. Do
not answer on the user's behalf.

Use `$wayfinder` instead only when the uncertainty itself needs a
multi-session map:

```text
$wayfinder <destination and trellis-task reference>
```

### Specification

After discovery is settled:

```text
$to-spec

Publish the settled specification to trellis-task:<MM-DD-parent-slug> using
the configured Other backend.
Discovery artifacts:
- <durable research/domain/ADR paths>
```

The Skill owns the testing-seam discussion and specification format. The
backend only persists and verifies the approved result.

### Tickets

After the spec is approved and published:

```text
$to-tickets trellis-task:<MM-DD-parent-slug>
```

The Skill owns vertical-slice decomposition and the granularity quiz. The
backend publishes the approved set as child tasks.

### Implementation

After a human activates one unblocked child:

```text
$implement trellis-task:<MM-DD-child-slug>

Child path: .trellis/tasks/<MM-DD-child-slug>
Parent spec: .trellis/tasks/<MM-DD-parent-slug>/prd.md
Parent design: .trellis/tasks/<MM-DD-parent-slug>/design.md
```

The real `$implement` owns the implementation method and may commit changes.
Obtain permission for that commit behavior before invocation.

### Code review

After implementation is committed:

```text
$code-review <FIXED_POINT_SHA>

Spec sources:
- .trellis/tasks/<MM-DD-child-slug>/prd.md
- .trellis/tasks/<MM-DD-parent-slug>/prd.md
- .trellis/tasks/<MM-DD-parent-slug>/design.md
```

The real Skill must run both review axes against the committed diff. Do not
replace it with an inline parent-agent summary.

### Final Trellis check

After `$code-review` passes:

```text
$trellis-check

Check trellis-task:<MM-DD-child-slug> against its parent specification and
the committed implementation diff.
```

This is a separate Trellis gate, not another name for `$code-review`.

## 10. When not to use the full Matt chain

Do not force every request through discovery, spec publication, and ticket
decomposition.

Use the full Matt route when one or more of these are true:

- Product behavior is unsettled.
- The data model, API contract, or architecture has meaningful alternatives.
- The change crosses several layers or needs multiple independently
  verifiable slices.
- Human decisions must be captured before implementation.
- The work is large enough that context must survive multiple sessions.

Use the normal Trellis route for a deterministic small fix, a mechanical
rename, a localized test correction, or another change whose requirement and
implementation boundary are already clear:

```text
trellis-brainstorm when clarification is needed
  -> Trellis artifacts
  -> trellis-before-dev or Trellis implementation agent
  -> trellis-check
  -> finish
```

A small task may still need a Trellis task and approval, but it does not need
a performative `$grill-with-docs -> $to-spec -> $to-tickets` chain.

## 11. Architecture and operation

### Ownership

```text
User
  |
  +-- $grill-with-docs
  +-- $to-spec
  +-- $to-tickets
  +-- $implement
  +-- $code-review
          |
          v
       Trellis
   task / artifacts / state
          |
          v
    $trellis-check
```

Matt owns:

- interviewing and the numbered question frontier;
- repository and domain exploration;
- product decisions and domain modeling;
- specification methodology;
- tracer-bullet ticket methodology;
- implementation methodology;
- qualitative Standards and Spec review.

Trellis owns:

- task identity and parent/child grouping;
- `planning -> in_progress -> completed` lifecycle;
- human approval boundaries;
- durable `prd.md`, `design.md`, `implement.md`, and research artifacts;
- publication metadata and context manifests;
- cross-session handoff and recovery;
- executable validation and final archival.

The publication backend joins these systems without merging their
responsibilities.

### Publication identity and readiness

A publication reference is the complete task basename:

```text
path:      .trellis/tasks/08-12-user-preferences
reference: trellis-task:08-12-user-preferences
```

The date prefix is part of the identity. A bare slug is not sufficient.

A published parent spec has metadata equivalent to:

```text
matt_publication_kind=spec
matt_publication_ref=trellis-task:08-12-user-preferences
matt_spec_artifacts=prd.md,design.md
matt_ready_for_agent=true
```

A published ticket also records:

```text
matt_publication_kind=ticket
matt_publication_ref=trellis-task:<complete-child-basename>
matt_parent_ref=trellis-task:<complete-parent-basename>
matt_ready_for_agent=true
```

Readiness means that the publication is complete enough for another agent to
fetch. It does not mean approved, scheduled, or active. Publication must never
call `task.py start`.

### Multiple tickets, blockers, and the next frontier

Parent/child links group work but do not schedule dependencies. A child ticket
stores blockers in its authoritative `prd.md`:

```markdown
## Blocked by

- trellis-task:08-12-preference-storage
```

An unblocked ticket uses:

```markdown
## Blocked by

- None - can start immediately
```

To select the next ticket:

1. Read the parent `task.json.children` list.
2. Read every child `task.json` and `prd.md`.
3. Exclude children that are not ready, completed, or already in progress.
4. Resolve every `trellis-task:` reference under `## Blocked by`.
5. A `planning` child is available only when every blocker is
   completed/archived.
6. Preserve the approved parent index order when several children are ready.
7. Let a human select one child, then activate only that child:

```bash
python3 ./.trellis/scripts/task.py start \
  .trellis/tasks/<MM-DD-selected-child>
```

Do not infer dependencies from child order or the `parent` field. Do not
start blocked work or activate all children as a batch.

### Fixed point and two independent review gates

Save a resolvable fixed point before implementation changes:

```bash
git rev-parse HEAD
```

After the implementation commit, verify the review range:

```bash
git rev-parse <FIXED_POINT_SHA>
git log <FIXED_POINT_SHA>..HEAD --oneline
git diff --stat <FIXED_POINT_SHA>...HEAD
```

Pass the fixed point and explicit child/parent spec paths to
`$code-review`. The custom `trellis-task:` token is not a hosted issue
number, so explicit paths ensure that the Spec reviewer receives the complete
logical contract.

The two gates serve different purposes:

- `$code-review` performs qualitative, parallel **Standards** and **Spec**
  review against the committed diff.
- `$trellis-check` independently runs the repository's executable checks and
  Trellis compliance checks: tests, lint, type checks, build checks, relevant
  `.trellis/spec/`, context, data flow, reuse, and consistency.

A slice is not complete until both gates pass. Persist findings in the child
task. Implementation defects return to a new `$implement`; specification
defects return to `$to-spec`; decomposition or blocker defects return to
`$to-tickets`.

### Complete command sequence

Shell, from the target repository root:

```bash
PARENT_TASK="$(python3 ./.trellis/scripts/task.py create \
  "User preferences" \
  --slug user-preferences \
  --description "Define and implement user preferences")"
PARENT_REF="trellis-task:${PARENT_TASK##*/}"
```

Codex conversation, one human-owned invocation at a time:

```text
$grill-with-docs
Trellis task: <PARENT_REF>
Request: User preferences are desired, but behavior and data model are open.
```

After all numbered questions are answered and discovery is settled:

```text
$to-spec
Publish to <PARENT_REF> using the configured Other backend.
```

After the testing seam and final spec are approved:

```text
$to-tickets <PARENT_REF>
```

After ticket granularity and blockers are approved, choose one frontier child.

Shell:

```bash
CHILD_TASK=.trellis/tasks/<MM-DD-frontier-child>
python3 ./.trellis/scripts/task.py start "${CHILD_TASK}"
FIXED_POINT="$(git rev-parse HEAD)"
printf '%s\n' "${FIXED_POINT}"
```

Codex conversation:

```text
$implement trellis-task:<MM-DD-frontier-child>
Child: .trellis/tasks/<MM-DD-frontier-child>
Parent: .trellis/tasks/<MM-DD-parent-slug>
```

After the real Skill commits the implementation:

```text
$code-review <FIXED_POINT_SHA>
Spec sources:
- .trellis/tasks/<MM-DD-frontier-child>/prd.md
- .trellis/tasks/<MM-DD-parent-slug>/prd.md
- .trellis/tasks/<MM-DD-parent-slug>/design.md
```

After both review axes pass:

```text
$trellis-check
Check the active child against its parent spec and committed diff.
```

After both gates pass and a human approves completion:

```bash
python3 ./.trellis/scripts/task.py archive "${CHILD_TASK}" --no-commit
```

Repeat for each newly unblocked child. Archive the parent only after all
children and the final integration check are complete. Prefer
`/trellis:finish-work` when the platform exposes it.

### Fresh-session recovery

Do not depend on the old conversation. Start with a canonical task reference
or exact task path.

```bash
python3 ./.trellis/scripts/task.py current --source
python3 ./.trellis/scripts/task.py list --json
```

Given `trellis-task:MM-DD-slug`:

1. Resolve `.trellis/tasks/MM-DD-slug/`.
2. If it is not active, find exactly one matching archived directory under
   `.trellis/tasks/archive/`.
3. Verify `task.json.meta.matt_publication_ref`.
4. Read `task.json`, `prd.md`, the files listed by
   `matt_spec_artifacts`, `implement.md`, and referenced research.
5. For a child, follow `matt_parent_ref` and read the parent spec/design.
6. Load and validate curated context:

```bash
python3 ./.trellis/scripts/task.py list-context <TASK_DIR>
python3 ./.trellis/scripts/task.py validate <TASK_DIR>
```

7. Read approval notes, review records, completion markers, and blockers to
   identify the next stage.
8. Present the exact next real Skill invocation and stop at its human boundary.

Do not call `task.py start` merely to recover a planning task. Lifecycle
status is coarse; the durable artifacts and approval ledger determine actual
progress.

### Git and distribution policy

Commit these shared integration inputs in the target project:

- `.trellis/workflow.md`;
- `docs/agents/issue-tracker.md`;
- installer-generated `skills-lock.json`;
- the target project's normal shared Trellis configuration/specification
  files according to its Trellis policy.

For this distribution repository, commit:

- `.trellis/workflow.md`;
- `docs/agents/issue-tracker.md`;
- `README.md`.

Under the recommended lockfile-based installation model, do not vendor the
official Matt Skill source into this distribution. Restore it in each target
project using the official installer. If a team intentionally vendors
project-local Skills instead, keep the upstream files byte-for-byte and define
one update policy; never maintain a hidden local fork.

Do not commit machine-local or transient state:

- `.trellis/.developer`;
- `.trellis/.runtime/`;
- session pointers, Codex session logs, caches, backups, and temporary files;
- credentials, local IDE state, build output, or disposable runtime artifacts.

Do not copy this repository's `AGENTS.md` into a target. The target's
`trellis init --codex` owns its managed Trellis block. Do not copy this
repository's `.agents/skills/`; install Matt Skills from upstream in the
target.

If a target `.gitignore` ignores all of `.trellis/` or
`.agents/skills/`, do not force-add an entire runtime tree. Track the shared
workflow and lockfile deliberately, keep runtime state ignored, and review the
repository's Git policy separately. This integration does not silently edit
`.gitignore`.

### Restore a configured project after a fresh clone

When the configured project commits the workflow, backend, and lockfile:

```bash
git clone <repository-url>
cd <repository-directory>

trellis init -u your-name --codex --skip-existing
npx skills@latest experimental_install

test -f .trellis/workflow.md
test -f docs/agents/issue-tracker.md
test -f .agents/skills/grill-with-docs/SKILL.md
test -f .agents/skills/to-spec/SKILL.md
test -f .agents/skills/to-tickets/SKILL.md
test -f .agents/skills/implement/SKILL.md
test -f .agents/skills/code-review/SKILL.md
python3 ./.trellis/scripts/task.py --help
```

If no committed `skills-lock.json` exists, use the explicit upstream install
command instead:

```bash
npx skills@latest add mattpocock/skills --agent codex
```

Do not rerun `$setup-matt-pocock-skills` and choose a hosted tracker over the
committed Trellis `Other` backend. Change the publication backend only as a
separately reviewed architecture decision.

## 12. Troubleshooting

### `$grill-with-docs` does not ask questions immediately

The real Skill researches the repository and domain before opening its
numbered question frontier. An initial research period is expected.

Verify the actual sources:

```bash
test -f .agents/skills/grill-with-docs/SKILL.md
test -f .agents/skills/grilling/SKILL.md
test -f .agents/skills/domain-modeling/SKILL.md
```

In the Codex transcript, confirm that the project-local files were loaded.
Wait for a real numbered frontier and answer it yourself. Do not add fallback
questions to `.trellis/workflow.md`.

### `$code-review` reports an issue-tracker problem

Verify that the project has the configured `Other` backend:

```bash
test -f docs/agents/issue-tracker.md
sed -n '1,40p' docs/agents/issue-tracker.md
```

The semantic review inputs are the fixed point, committed diff, and explicit
spec paths. This integration does not need an external issue service. Pass the
child `prd.md` plus the parent `prd.md` and `design.md` explicitly.

If the configured file exists but the Skill still stops before diff/spec
review, verify which project-local `code-review/SKILL.md` Codex loaded. Do
not select GitLab or Local markdown merely to bypass the error.

### `$to-spec` or `$to-tickets` cannot publish

Check all three layers:

```bash
test -f docs/agents/issue-tracker.md
test -f .trellis/scripts/task.py
python3 ./.trellis/scripts/task.py --help
python3 ./.trellis/scripts/task.py list --json
```

Then verify:

- the exact parent task exists;
- `matt_publication_ref` uses the complete basename;
- required `prd.md` and `design.md` files exist;
- every ticket has its own child task;
- parent/child metadata agrees;
- blockers resolve to exact sibling references;
- `task.py validate` passes before readiness becomes true.

A partially published batch stays identifiable and not-ready. Do not delete it
and report success.

### Skills do not exist or resolve to the wrong source

Reinstall from upstream:

```bash
npx skills@latest add mattpocock/skills --agent codex
```

Then inspect:

```bash
npx skills@latest list --agent codex --json
```

If both global and project-local copies exist, make the loaded project path
explicit. Duplicate names are not merged.

### The workflow does not take effect

Check that the target file matches this distribution:

```bash
cmp ~/trellis/.trellis/workflow.md .trellis/workflow.md
```

Confirm that Trellis/Codex was initialized in the repository root and start a
fresh Codex session so project instructions and the Skill catalog are
reloaded. A workflow can route to a Skill, but it cannot make a missing Skill
appear or automatically cross a human-only invocation boundary.

### `$code-review` cannot launch both review agents

This is a Codex host/tool-dispatch problem, not a Trellis publication problem.
The real Skill requires two parallel child reviews, Standards and Spec. Both
must be spawned before the host waits, and the host must use its collaboration
agent wait mechanism. Do not weaken the Skill, run the axes sequentially, or
replace them with a parent-agent summary.

### A fresh session cannot identify the next action

Supply the exact `trellis-task:MM-DD-slug` reference. Verify its metadata,
read the parent and child artifacts, parse blockers, and validate context.
Conversation memory is not an accepted publication or recovery mechanism.

### Known limitations and ownership

- Matt human-owned stages do not auto-chain. Explicit invocation is expected.
- Trellis parent/child links are grouping, not a native dependency graph.
- The backend has no external labels, comments, assignment API, or atomic
  multi-task transaction.
- `trellis-task:` is a custom publication identity; pass explicit filesystem
  spec paths to `$code-review`.
- `$code-review` requires a real committed diff and resolvable Git fixed
  point.
- Parallel code review depends on Codex host support for real child agents.
- Upstream Matt updates may change Skill contracts. Update through the
  installer, review `skills-lock.json`, and rerun acceptance checks before
  adopting a changed contract.
- Trellis updates may propose a new workflow. Review rather than blindly
  replacing the project adapter.
- The integration deliberately provides no fallback imitation when a Skill is
  missing or a human boundary has not been crossed.

The operating rule is simple: **Trellis owns lifecycle and durable state; the
real upstream Matt Skills own the methodology; people explicitly cross the
approval and invocation boundaries.**
