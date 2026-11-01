# Installing the Grok Build fixes for Trellis

Branch `grok` of this checkout carries two fixes to Trellis-managed scripts and
the Grok layer of the Trellis + Matt integration. They were made and tested
against Trellis **0.7.0-beta.4** with Grok Build **1.0.70**.

| Patch (`scripts/grok-fixes/patches/`) | File | What it fixes |
|---|---|---|
| `0001-active-task-grok-session-id.patch` | `.trellis/scripts/common/active_task.py` | Grok Build exports `GROK_SESSION_ID` to tool shells. Stock Trellis doesn't read it, so `task.py start` under Grok writes no session pointer and `task.py current` falls back to "none". With the patch the pointer is `.trellis/.runtime/sessions/grok_<session>.json`. |
| `0002-task-store-archive-repoint.patch` | `.trellis/scripts/common/task_store.py` | `task.py archive` moved the task but left `implement.jsonl`/`check.jsonl` entries pointing at its old path. A child that references its parent's `prd.md` then fails `task.py validate` once the parent is archived. Archive now rewrites references into the moved directory in every task, active or archived. |
| `0003-grok-commands-aligned.patch` | `.grok/commands/trellis-{start,continue,finish-work}.md` | These are this integration's Grok command texts: they load context with `get_context.py`, start no task on `/trellis-start`, and archive with `--no-commit`. |
| `0004-matt-flow-grok.patch` | `docs/agents/matt-flow.md` | Grok notes for the Matt routing guide. |

`scripts/grok-fixes/apply-grok-fixes.sh` applies them. It:

- checks `.trellis/.version`;
- reports each script as stock, patched, or customized by sha256;
- checks every patch with `git apply --check` before it writes anything;
- backs up every file it touches;
- applies the patches;
- runs `scripts/grok-fixes/smoke_test.py`, which works on a throwaway copy of `.trellis` and leaves the project alone, plus the repo tests when `tests/test_grok_fixes.py` is present.

It commits nothing, and running it twice is safe.

## Quick deploy (`trellis-grok` shortcut)

Install the shell shortcut once (symlink into `~/.local/bin`):

```bash
~/trellis/scripts/grok-fixes/install-shortcut.sh
# uninstall: ~/trellis/scripts/grok-fixes/install-shortcut.sh --uninstall
```

Then, in any Trellis project (or pass `DIR`):

```bash
trellis-grok status              # version + applied/pending/conflict per patch
trellis-grok dry-run [DIR]       # preview
trellis-grok apply [DIR]         # apply + smoke test (idempotent)
trellis-grok revert [DIR]        # undo patches
trellis-grok init [DIR] -u NAME  # new project: trellis init --grok, copy Matt
                                 # docs + workflow + aligned .grok/commands, apply
trellis-grok update [DIR]        # safe: trellis update -n, re-apply, list .new;
                                 # protects .trellis/workflow.md by default
```

Override the source checkout with `TRELLIS_GROK_HOME=/path/to/checkout`.
Grok Build slash command: `.grok/commands/trellis-grok-deploy.md` (`/trellis-grok-deploy`)
runs status → dry-run → wait for confirm → apply.

## Quick start (this checkout or any beta.4 project)

```bash
R=/path/to/this/checkout          # e.g. ~/trellis on branch grok
P=/path/to/project                # a git repo with .trellis/ from trellis init

$R/scripts/grok-fixes/apply-grok-fixes.sh --dry-run --target "$P"   # report only
$R/scripts/grok-fixes/apply-grok-fixes.sh --target "$P"             # apply + smoke test
$R/scripts/grok-fixes/apply-grok-fixes.sh --revert --target "$P"    # undo
```

Options:

- `--only scripts` applies just 0001–0002; `--only grok` applies just 0003–0004.
- `--no-tests` skips the smoke and repo tests.
- `--backup-dir DIR` overrides the default backup location, `~/trellis-backups/grok-fixes/<project>-<timestamp>`.
- `--force-version` skips the version check.

Exit codes:

| Code | Meaning |
|---|---|
| 0 | OK |
| 2 | Usage error |
| 3 | Version mismatch |
| 4 | A patch neither applies nor is already applied (a customized file). Nothing was changed. |
| other | Smoke or repo tests failed |

0003 is skipped when the project has no `.grok/commands` (init without `--grok`).
0004 is skipped when there is no `docs/agents/matt-flow.md`.

## Installing into another project

1. Run `trellis init -u <name> --grok [--claude --codex]` in the project. Then install the
   Matt skills as described in the README.
2. Copy the integration files listed in the README ("Copy them when you want that
   previously tested behavior"). That includes `docs/agents/matt-flow.md`,
   `.trellis/workflow.md` and the `AGENTS.md` paragraph. You can leave out
   `active_task.py`, `task_store.py` and `.grok/commands/*` and let the script patch them.
3. Run `apply-grok-fixes.sh --dry-run --target <project>`, then run it again without
   `--dry-run`.
4. Run `grok --trust` once in the project.

If you copy `docs/agents/matt-flow.md` from this branch, it already contains 0004,
and the script reports it as "applied".

## `trellis update` and re-applying

`trellis update` compares managed files with `.trellis/.template-hashes.json`.
Patched `active_task.py`/`task_store.py`, the customized `.grok/commands/*`, and
`.trellis/workflow.md` (replaced by this integration) all count as user-modified.

1. Preview first:

   ```bash
   trellis update --dry-run
   ```

2. Pick one way to keep the customizations:
   - `trellis update -s` (`--skip-all`) skips every modified file. `workflow.md`, the
     two patched scripts and the Grok commands stay as they are, and unmodified files
     update.
   - `trellis update -n` (`--create-new`) writes the new template next to each
     modified file as `<file>.new`. Compare and merge by hand:

     ```bash
     diff -u .trellis/workflow.md .trellis/workflow.md.new
     ```

     Delete the `.new` files when you're done. You can keep the old `workflow.md`;
     it isn't required by the fixes.
   - `-f` (`--force`) overwrites everything, which drops the fixes. Re-apply afterwards
     (step 3).
3. Re-apply the fixes after any update that replaced the scripts:

   ```bash
   scripts/grok-fixes/apply-grok-fixes.sh --dry-run
   ```

   - **Same version (beta.4):** the files are back to stock, the patches show
     `pending`, and running without `--dry-run` re-applies them.
   - **Newer version:** the script stops with exit 3. Check whether upstream already
     contains the fixes:

     ```bash
     grep -n GROK_SESSION_ID .trellis/scripts/common/active_task.py
     ```

     For `task_store.py`, look for the archive repoint in `cmd_archive`. If upstream
     has a fix, keep upstream and run with `--only grok`. Otherwise run
     `--dry-run --force-version`. If every patch is `pending`, the context still
     matches and applying is fine. A `conflict` means the patch has to be redone
     against the new template.

   Then update `STOCK`/`PATCHED` hashes and `EXPECTED_VERSION` in the script.
4. Run the checks:

   ```bash
   python3 scripts/grok-fixes/smoke_test.py .
   ```

   In this checkout, also run:

   ```bash
   python3 -m unittest discover -s tests
   ```

Do not run `trellis update` without `--dry-run` first in a checkout with
uncommitted customizations.

## Known limits

- If Grok Build runs the project's `.claude/settings.json` hooks, they set
  Claude-style env. The session key may then come out as `claude_<id>` instead of
  `grok_<id>`. The pointer still works for that session.
- In the 2026-10-26 interactive run, Grok skipped workflow step 1.4 (`task.py start`)
  during `/implement-spec` and only ran it when prompted. The fixes make the pointer
  correct when `start` runs. They don't force the model to run it. See
  `docs/validation/2026-10-26-grok/`.
- `smoke_test.py` needs `git` and Python 3.9+.

## Evidence

- `docs/validation/2026-10-26-grok/` contains the transcripts, apply-script test
  output, and before/after test results.
- `tests/test_grok_fixes.py` holds the regression tests: 5 fail on stock beta.4
  and all 30 pass with both fixes.

## Apply syncs the Grok/Matt layer (2026-10-28)

`trellis-grok apply` now **copies** from the source checkout before applying
script patches 0001–0002:

- `.trellis/workflow.md`, `docs/agents/matt-flow.md`, `docs/agents/issue-tracker.md`
- `.grok/commands/trellis-{start,continue,finish-work}.md`
- SessionStart `new`/`load` matchers into `.claude/settings.json`
- Upserts a Matt/grill block (`<!-- TRELLIS-GROK:MATT-START -->`) into **both**
  `AGENTS.md` (Claude Code) and project `CLAUDE.md` (Grok Build loads this via
  `agents_md_files`, not `AGENTS.md`), including `/grill-with-docs` entry
  bootstrap (`get_context` + `task.py create --no-start`). Creates `CLAUDE.md`
  when missing so Grok has somewhere to inject the block.

Patches 0003–0004 remain for reference / older installs, but apply no longer
depends on them for the grok-layer files (those patches go stale when the
source docs evolve, which previously made apply report "already applied"
while bootstrap text was still missing).

## Grok loads CLAUDE.md not AGENTS.md (2026-11-01)

Grok Build session `prompt_context.agents_md_files` only includes project
`CLAUDE.md` (and optional `~/.claude/CLAUDE.md`). The Matt/grill bootstrap that
lives in `AGENTS.md` was invisible to Grok until `trellis-grok apply` also
upserted the same `<!-- TRELLIS-GROK:MATT-START -->` block into `CLAUDE.md`.
Keep both files in sync; do not remove the AGENTS.md copy (Claude Code still
reads it).
