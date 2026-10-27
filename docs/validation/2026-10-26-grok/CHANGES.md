# Changes made during the 2026-10-26 Grok validation

Repo `~/trellis`, local branch **`grok`** (parent `835396a`, not pushed). See the diffs with
`git diff 835396a..grok -- <file>` or `git show <commit>`. Backups were taken with `cp`
before each non-trivial edit.

## Committed on `grok`

| Commit | File | Change | Backup of pre-edit file |
|---|---|---|---|
| `393c488` fix(trellis): Grok session identity and archive jsonl repointing | `.trellis/scripts/common/active_task.py` | +3: `("grok", ("GROK_SESSION_ID",))` in `_ENV_SESSION_KEYS` | `~/trellis-backups/20261026/.trellis/scripts/common/active_task.py` |
| `393c488` | `.trellis/scripts/common/task_store.py` | +48: `cmd_archive` rewrites `implement.jsonl`/`check.jsonl` `file` paths into the moved task, in all tasks including archived ones | `~/trellis-backups/20261026/task_store.py.orig` |
| `393c488` | `tests/test_grok_fixes.py` (new) | Regression tests for both fixes (5) | — |
| `393c488` | `tests/test_integration.py` | Expectations updated for the Grok session key and repointed archive | `~/trellis-backups/20261026/test_integration.py.orig` |
| `a4d429f` docs(grok): aligned Grok commands, matt-flow Grok notes, grill-me authority rule | `.grok/commands/trellis-start.md`, `trellis-continue.md`, `trellis-finish-work.md` (new to git; init had generated stock copies) | Aligned bodies: `get_context.py` context loading, no task on start, `--platform grok`, `--no-commit` archive and journal | `~/trellis-backups/20261026/.grok/commands/*.md` (stock `trellis init --grok` output) |
| `a4d429f` | `docs/agents/matt-flow.md` | Grok skill loading, `/<skill> <reference>` syntax, grill-me "confirmation is not edit authority" | `~/trellis-backups/20261026/docs/agents/matt-flow.md` (== 835396a) |
| `a4d429f` | `AGENTS.md` | +3: user-invoked Matt skill is not edit authority; end with `/implement <scope>` | `~/trellis-backups/20261026/AGENTS.md` |
| `a4d429f` | `README.md` | Grok row and copy list (adds `.grok/commands`, `active_task.py`, `task_store.py`), apply-script pointer, 2026-10-26 headless and TUI validation; "known upstream gap" replaced with a note that it is fixed on `grok` | `~/trellis-backups/20261026/README.md` (original), `README.md.pre-grokfix` (before the last edit) |
| `78d2f30` feat(grok-fixes) | `scripts/grok-fixes/apply-grok-fixes.sh`, `smoke_test.py`, `patches/0001–0004*.patch`, `patches/format-patch/0001-*.patch` (all new) | Idempotent installer and patches | — |
| `78d2f30` | `docs/grok-fixes/INSTALL.md`, `UPSTREAM.md`, `upstream/0001-grok-session-id-and-archive-jsonl-repoint.patch` (new) | Install / `trellis update` guide, upstream issue draft and patch (not submitted) | — |
| (this commit) | `docs/validation/2026-10-26-grok/**` (new) | This audit | — |

## Not committed / outside the repo

| Path | Change | Backup |
|---|---|---|
| `~/.grok/trusted_folders.toml` | Added fixture entries (see DECISIONS.md #1) | `~/trellis-backups/20261026/trusted_folders.toml.bak2` (taken before `recheck-tui` was added) |
| `~/tmp/trellis-grok-val-20261026/*` | Disposable fixtures created by the assistant, kept for inspection | — |
| `~/tmp/trellis-before-20261026` | Disposable copy used for the before/after test matrix | — |
| `~/trellis-backups/grok-fixes/install-fresh-20261026-074152/` | Backup written by an apply-script test on the `install-fresh` fixture | — |

These files in `~/trellis` were already uncommitted before this work. They were left as they were, not reverted and not committed: `.agents/skills/*` (16 files), `.agents/skills/wizard/template.sh`, `.trellis/.template-hashes.json`, `skills-lock.json`. Untracked `.grok/skills/` and `.grok/agents/` come from `trellis init --grok` and were not committed.

## 2026-10-27 — trellis-grok shortcut

| Commit | File | Change |
|---|---|---|
| (this) | `scripts/grok-fixes/trellis-grok` | CLI: status / dry-run / apply / revert / init / update |
| (this) | `scripts/grok-fixes/install-shortcut.sh` | Install/uninstall `~/.local/bin/trellis-grok` symlink |
| (this) | `.grok/commands/trellis-grok-deploy.md` | Slash command: status → dry-run → confirm → apply |
| (this) | `docs/grok-fixes/INSTALL.md`, `README.md` | Quick deploy sections |

