# Stock installation — 2026-09-29

This is the current supported setup. Earlier [Codex/Claude automation results](README.md)
used policy adaptations and remain historical evidence, not requirements or proof
of stock end-to-end automation. HEAD was `fdb57d2`; the uncommitted runtime-gap
fixes already present were preserved. No repository commit or push was made.

## Installation and migration

The exact command ran successfully in an isolated Git project and this checkout:

```bash
npx skills@latest add mattpocock/skills --agent claude-code codex --yes
```

Observed installer **1.7.0**, upstream HEAD
`d81f3a183412e71a5b1e84ca21bc1a35eea03a60`. These identify this test, not mandatory
installation pins. The isolated project is `/tmp/trellis-stock-install-9269692g`.
The installer produced **37 canonical skill directories / 101 files** under
`.agents/skills`, **37 Claude symlinks**, and its normal `skills-lock.json`.
The checkout's corresponding files match the isolated installation byte for byte.

Before migration, each of four Claude frontmatter files and four Codex metadata
files exactly matched its saved adaptation. Both existing adapters restored the
saved originals without drift, then their scripts and 17 adapter-only tests were
removed. No manual upstream body, frontmatter or metadata edit followed restoration.
The installer replaced the old copies that occupied its standard destinations
with its normal shared-directory/link layout. Git consequently shows old Claude
copy deletions together with new canonical files and links; this is installer
output, not renamed/forked skills. The independent old `resolving-merge-conflicts`
copy shadows no installed name and was preserved, as was its installer lock entry.

Removed the old selective `.gitignore` rules tied to the pinned twelve-skill setup.
No replacement metadata override, wrapper, custom installer, fork or pin was added.
Rerunning the same standard command is the documented update path; inspect upstream
changes and refresh runtime discovery normally.

Setup correction: the first installer call used `/tmp` rather than the intended
fixture cwd. Only its newly generated 37 Matt directories/links and lockfile were
moved intact into `/tmp/trellis-stock-initial-output-z6lgbuwc`, outside fixture
ancestry, before the correct isolated run. No reference-project files were touched.
That first output is not counted as the isolated-project validation.

## Stock policies and retained integration

Observed stock `grill-with-docs`, `wayfinder`, `to-spec`, `to-tickets`, `implement`
and `retro` have Claude `disable-model-invocation: true` and Codex
`allow_implicit_invocation: false`. Those fields remain upstream-owned. Codex's
policy comes from `agents/openai.yaml`; Claude frontmatter alone does not establish
Codex's controls. `retro` is installed but user-only; optional retrospective work
does not justify restoring a patched installation.

The workflow defaults to normal Trellis. Explicit Matt entry or a recorded Matt
route selects its genuine skills. Each next responsibility is conditional; where
stock invocation requires the user, context and the exact command are saved before
pausing. General scope authorization does not substitute for skill invocation.
Ordinary permitted file loading remains valid; it is not a way around denial or
user-only controls. Retro and update-spec remain independent and conditional.

Preserved the independent worker-identity validator, exact-parent fallback,
recorded authorization, no-auto-commit closeout and idempotent recovery fixes.
Fourteen runtime/source-test/historical-evidence files were verified byte-identical
to the pre-migration working tree. Continue/finish guidance changed only to honor
the next stock skill boundary. The task-context helper loads task data and does
not alter or impersonate a Matt skill.

## Focused checks and one fresh session

After removing the 17 tests specific to deleted adapters, all **23 remaining
regressions passed in 6.870 seconds**. They cover workflow parsing/breadcrumbs,
worker isolation, authorization and closeout. No expensive delivery matrix ran.
Final prose compaction then passed the three affected parser/index/breadcrumb
tests. Workflow is **6,862 characters**, down from HEAD's 8,572, retaining all
13 step headers and six breadcrumbs. README is about 5,000 characters, down from
HEAD's 13,124. These are character counts, not token/performance measurements.

Fresh Codex **0.159.0**, model **gpt-6-astra**, thread
`01a0f05c-f978-73d3-9ef1-b02322045165`, ordinary request:

> Continue the task at .trellis/tasks/09-29-stock-resume within its recorded scope.

The fixture seeds a completed Matt discovery record with settled requirements
and local implementation authorization. This is **not** a claim that a new stock
grill interview executed. The prompt contains no optimization brief or per-stage
reminder. Native project AGENTS loaded once (line 6); copied hooks were not approved
or forced, and no native hook context was observed.

Observed behavior:

- Read Trellis start/continue, exact task records and on-demand routing/backend.
- Inspected the installed to-spec file; did not invoke its specification workflow.
- Wrote only `implement.md`, retaining the approved scope and pending work.
- Returned the exact next command and paused:

  ```text
  $to-spec .trellis/tasks/09-29-stock-resume
  ```

- No spec publication, implementation, task activation, commit, archive or worker.
  This is a policy-aware handoff, not an observed runtime tool rejection or native
  skill invocation. The original task/readiness state was preserved.

The session's final explanation cites Claude's frontmatter rather than Codex's
actual metadata field. The outcome agrees with the independently inspected stock
Codex policy. Guidance now explicitly distinguishes the two fields; the erroneous
explanation is not treated as proof of Codex frontmatter semantics.
The single fresh session used the stock routing before the final prose compaction;
that compaction preserved its invocation rule and was checked by the focused tests.

Exit 0; **77.470 seconds**. CLI cumulative usage: **156,471 input**, **128,256
cached input**, **1,741 output** tokens. These are repeated/cache-reused turn totals,
not unique context, dollar cost or a performance benchmark.

## File integrity and execution permissions

Before regression/runtime execution, hashed all installed Matt files, symlink
targets and lockfiles in both checkout and fixture. After execution, snapshots
match exactly: **141 checkout entries**, **139 fixture entries** (the checkout
retains the unrelated legacy skill). All **101 stock files** remained unchanged;
neither integration execution nor the fresh runtime mutated installer output.

The fresh CLI used workspace-write and approvals `never`, with an invocation-only
project-trust setting:

```text
-c 'projects={"/tmp/trellis-stock-install-9269692g"={trust_level="trusted"}}'
```

This is not hook trust or a permission bypass. Matching-version source explains
the earlier transient trust writes: thread startup persists project trust when
cwd is writable and effective project trust is unset
(`app-server/src/request_processors/thread_processor.rs:1350–1378`). The inline
TOML value sets the exact project key only in the session override layer, so that
branch is skipped. A dotted override with quoted path segments is parsed
differently in 0.159.0 and should not be presumed equivalent. Source inspected at
`rust-v0.159.0`, commit `377f7f557a6bdea0f3a2d26d4d899c66db4789d0`.

Before/after hashes of user Codex config/hooks and Claude settings match. **No
global-setting change or cleanup was needed in this stock test.** No reference
project was written, and no Claude harness ran. The stock command itself uses no
custom flags beyond those requested by the user.

Exact commands, native references, installed file hashes, integrity checks and
usage are in [stock-installation.json](stock-installation.json). Raw logs stay in
`/tmp/trellis-stock-run.*` and the native session store. Remaining limits: no stock
full delivery matrix, fresh stock entry interview, Claude execution or hook-trust
approval test; automatic end-to-end delivery is not an acceptance requirement.
