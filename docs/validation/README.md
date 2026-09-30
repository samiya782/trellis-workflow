# Validation record — 2026-09-29

This directory is evidence, not startup instructions. Raw native histories stay
in their existing stores; the checked-in reports contain selected sanitized
observations and fixture-only command evidence. Reference projects were read-only.

## Versions and baseline

- Current checkout started clean at `ca6764825667bcc0ee6cc6b2b70a84dea9a32cb1`.
  Public `samiya782/trellis-workflow` HEAD independently resolved to that SHA.
- Installed Trellis CLI and core: **0.7.0-beta.4**. Upstream tag independently
  resolved to `be9e19b269c25cb2787489eb81062bf96619442c`.
- Codex CLI **0.159.0**, default configured model **gpt-6-astra** in fresh runs.
- Skills installer **1.7.0**; genuine Matt source
  `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.
- OMC researched at `9fd35ece5d6de65b511bf43b55e42c499e4fc194`;
  no OMC execution or dependency.

Pinned initialization was executed separately in
`/tmp/trellis-matt-install-1qlmdya7` using
`npx --yes @mindfoldhq/trellis@0.7.0-beta.4 init -u fixture --codex --yes`:
exit 0, correct .version, AGENTS.md and Codex config generated. The exact pinned
12-skill installation in README ran in this checkout, then the adapter changed
four metadata files; `--check` passed. Upstream skill bodies/resources remain
installer-owned and generated Codex directories are ignored by Git.

## Evidence map

| Evidence | What it establishes |
| --- | --- |
| [execution.md](execution.md), [execution.json](execution.json) | Ordinary fresh prompts, baseline failures, exact downstream reads, native worker events, review/commit experiment, permission boundary, resume and delivery |
| [delivery-audit.json](delivery-audit.json) | Independent final fixture checks: all four tasks completed, references valid, reviewed code unchanged, unrelated file preserved |
| [normal-retro.md](normal-retro.md) | Controlled small-task comparison; actual retro and its dependency, conditional spec relationship |
| [wayfinder.md](wayfinder.md) | Real planning-only entry and preserved delivery boundary |
| [history.md](history.md) | Multiple reference projects, native transcript locations/turn evidence, material versus artificial interruptions |
| [upstream.md](upstream.md) | Current official documentation and pinned installed source research; Codex/Claude policy differences and OMC lessons |
| [context.json](context.json) | Static payload character counts; chars/4 token estimates explicitly labeled |
| [source-audit.json](source-audit.json) | All 29 installed Matt files compared with pinned upstream; only four metadata differences, 103 Claude files unchanged, root HEAD unchanged |

Native `spawn_agent` evidence is stronger than CLI event summaries: the latter
omit some dispatch details. No literal Claude Skill tool exists in this tested
Codex runtime. Explicit entry is observed as a user skill expansion. Downstream
execution is established by exact project skill body/resource reads plus their
actual publication, TDD and two-axis review behavior—not a skill name in prose.

## Outcomes and interruption attribution

- **Discovery:** baseline lacked project Codex Matt skills; explicit entry stopped.
- **Workflow:** with genuine skills installed, old workflow twice ended with a new
  required stage command even after decisions were settled. Historical native
  records show additional implementation handoffs. We do not count static rules
  as executed interruptions.
- **Skill policy:** upstream OpenAI metadata hid downstream skills from implicit
  discovery. Supported project metadata changes expose four stages; entries stay
  explicit. Claude frontmatter has different semantics and is unchanged.
- **Decisions:** the old actual to-spec run separately asked for a testing-seam
  confirmation. That is distinct from a command-only handoff. New execution used
  fully specified behavior and delegated routine engineering choices.
- **Permissions:** workspace-write/never blocked `.git/index.lock`, regardless of
  workflow authorization. Code/checks finished, committed review/closeout stayed
  pending. A fresh supported `--approve-for-me` run used automatic approval review
  to finish authorized local commits. No sandbox bypass or global edits.
- **Codex:** an area worker hit model capacity. Coordinator used `followup_task`
  and preserved its work; the worker finished without user intervention.

Updated delivery and fresh resume had **zero avoidable stage-command handoffs**.
The natural permission pause remains a real boundary, not hidden success. Root
session user messages and testing-controller prompts are not counted as fixture
workflow interruptions.

Two implementation workers overlapped **151.849 seconds**, owned separate files,
and finished before dependent summary implementation. Real Standards/Spec agents
overlapped **28.699 seconds**. These are agent-lifetime measurements, not speedup
claims. Shared task-state writes and commits belonged to the coordinator.

Fresh resume reproduced and fixed the seeded negative-input regression, passed
**18 tests**, committed checkpoint `03c1199`, obtained **0 findings on each real
review axis**, archived all four tasks children-first, repaired moved context
references and recorded the journal in closeout commit `a65c8c8`. The unrelated
file stayed unchanged and untracked; main stayed at the fixture base. No push.

## Context and simplification

Measured extracted Phase Index fell **5,923 → 1,337 characters** in the first
integrated execution, **77.4%**. The final Phase Index remains 1,337 characters; always-loaded
AGENTS guidance and on-demand detail are measured separately in context.json. Per-turn bodies also shrink there. These are real character
counts; chars/4 figures are estimates, not tokenizer measurements.

The initial integrated run retained the old README and loaded a 35,874-character
README/index output. That proved workflow-only compression insufficient. After
README/start/continue simplification, the identical small-task request read
**65,569 → 13,877 shell-output characters** (**78.8% less**) over 7 → 5 commands,
with zero interruptions. The phase-only targeted-read attempt still loaded README before consuming the
rule (13,742 characters). Moving that small rule into always-loaded AGENTS
produced an actual `rg`/`tail` run: **3,055 characters**, **95.3% less than baseline**
and 77.8% below the first simplified run. See normal-retro.md for all four runs;
none of these counts is a tokenizer or universal performance claim.

The necessary Matt catalog has a cost: pure skill blocks measured **7,706 chars /
18 entries** without Matt, **9,866 / 28** for the selected adapted installation,
and **11,628 / 34** for the old whole-collection link experiment. The selected
installation adds 2,160 characters over no-Matt and saves 1,762 against the larger
installation. Skill bodies and task evidence are additional on-demand loads.

CLI cumulative input-token counters include repeated turns/cache reuse and exclude
some child usage. They are preserved as usage evidence, **not unique context or
controlled token-savings estimates**. Different feature scenarios are not a
performance benchmark.

## Runtime checks and limits

`python3 -m unittest discover -s tests -v`: **17 passing tests**. Tests exercise
actual installed parser/hook/task APIs in temporary repositories, metadata
apply/check/restore, invocation-policy drift and cross-platform preservation.
`git diff --check`, Python syntax checks and adapter `--check` pass. No linter or
typechecker is configured; syntax checks are not labeled typechecking.

Actual parent-spawned custom Trellis checker
`01a0ee21-5157-7043-b345-3da5d354580d` received a **5,316-character SubagentStart
payload**, including the PRD twice (native transcript line 21). The own-artifact
manifest duplication was removed. Empty manifests are rejected by validate and
ordinary start; installed `start --allow-empty-context` is a supported explicit
exception, tested in a disposable fixture. The workflow now explains this instead
of adding placeholder context merely to make validation green.

Copied fresh-fixture hooks were unapproved, so their successful workers demonstrate
child-side context loading, not hook injection. Native injection was separately
observed here. Project trust is not hook approval. Existing config comments about
feature defaults are older than the tested runtime; no global flags were changed.

All **103 tracked .claude files are byte-identical** to baseline. Existing Claude
history evidence is retained; no fresh Claude Code harness was run. No automated
three-failure exhaustion test was run: one repair cycle is observed and the limit
is guidance, not an enforcement service. Unattended background persistence after
session exit, arbitrary platforms, and every permission configuration are untested.

Retro's CI suggestion was not automatically adopted: this task adds focused local
regressions and does not introduce a hosted CI execution dependency. Its measured
full-file-read finding led to a narrow routing improvement and a fresh regression.
No artificial engineering lesson or duplicate .trellis/spec document was created.
