# Remaining runtime integration gaps

## Commit authorization

The user's follow-up `commit these` authorizes committing the completed changes
and their Trellis closeout. It supersedes the earlier uncommitted-review boundary.
No push is authorized. This work was performed directly on main without a PR;
closeout uses the supported non-PR branch-validation exception and no-auto-commit
lifecycle commands. Existing validation is sufficient for unchanged code.

## Current direction (supersedes automation acceptance below)

User now prioritizes stock upstream installation and easy maintenance over full
automation. Required installer: `npx skills@latest add mattpocock/skills --agent
claude-code codex --yes`. Safely restore known patches, remove policy adapters and
their requirements, and let the installer own copies/metadata/links/lockfiles.
Do not change upstream invocation policy or bypass user-only skill boundaries.
Normal Trellis and explicit Matt entry remain; at a required user invocation,
persist progress, present the exact command and pause. Keep independent isolation,
authorization, recovery and closeout fixes. Validate stock install plus one small
fresh Codex session, not another delivery matrix. All repository changes remain
uncommitted; no pushes/global-setting changes/reference writes. Prior evidence
below is historical and does not establish current stock automation.

Current completion: restored eight known policy adaptations, removed both
configure adapters and 17 adapter tests, and executed the exact standard command
in an isolated project and this checkout. Installer owns 37 canonical skills and
37 Claude links; an unrelated non-shadowing legacy skill is preserved. All 23
remaining regressions pass, plus affected checks after final prose compaction.
One fresh Codex resume saved context and paused with the exact `$to-spec` command.
All stock skill files/links/lockfiles and global config hashes stayed unchanged
during execution. Workflow is 6,862 characters; no full delivery matrix or Claude
run. Independent earlier runtime fixes are retained. Current evidence:
`docs/validation/stock-installation.md` and `stock-installation.json`.
Next: user review of uncommitted changes; no required implementation remains.

## Historical runtime-gap scope and results

Route: normal Trellis maintenance. Baseline: `fdb57d2`, clean checkout.

Authorization: user requested minimal local fixes and isolated experiments for
worker context isolation, authorization/closeout sources, and existing-project
installation/loading. Repository changes must remain uncommitted; no pushes,
global settings, hook-trust bypass, or reference-project writes. Fixture-only
commit/archive experiments are authorized. Genuine Matt skill bodies stay intact.

Acceptance:
- Explicit worker task identity wins over the shared pointer; invalid/conflicting
  explicit identity never injects another task. Test actual Codex event inputs and
  existing single-task fallback.
- Remove contradictory start approval and auto-commit guidance at its sources;
  scope authorization survives resume, planning-only/no-commit still hold, and
  direct/interrupted/repeated closeout is covered.
- Install/load in an isolated copy of an existing Trellis project; inspect ancestor
  instructions, actual AGENTS loading, duplicate injection and platform coexistence.
- Reuse existing evidence, run focused regressions before minimal fresh ordinary
  sessions, and distinguish native hooks from explicit reads and static checks.
- Cheap repair-budget/resume boundary check, precise README/evidence updates.

Change boundary: platform context hooks/role fallback instructions, lifecycle
guidance at hooks/commands, focused tests and on-demand docs. No new orchestrator
or mandatory stages. The coordinator alone writes task state. Implementation
workers own separate context and closeout files; reference projects are read-only.

Progress: implementation and verification complete; changes remain uncommitted
for user review. Baseline 26 tests passed in 4.425 seconds; final 40 passed in
7.264 seconds. Both adapters and context manifests validate; independent review's
external-store and Claude rejection findings were fixed and rechecked. Existing
Claude execution evidence and all 24 genuine Matt skill files are unchanged.

Evidence: `docs/validation/runtime-gaps.md` and `runtime-gaps.json`. Three native
worker probes plus invalid/conflicting follow-ups verified explicit task loading
and exact-parent fallback. Five fresh ordinary CLI requests covered existing
project loading, direct/repeated/planning finish and persisted repair-budget stop.
No full delivery matrix was rerun. Workflow and AGENTS are unchanged.

Limits: native Codex start has no readable dispatch identity, so it gives loading
guidance and workers explicitly load validated task context. Copied fixture hooks
were not approved or forced. Literal autonomous three-failure exhaustion remains
untested. Four fixture trust entries appeared during CLI execution; only those
entries were removed afterwards, preserving other config values. No push or
repository commit/archive; all commit/archive experiments were isolated.

Next action: review the uncommitted changes. No additional implementation or
experiment is required for this scope; documented runtime limits remain.
