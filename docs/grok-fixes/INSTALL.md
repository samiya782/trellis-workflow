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

## Quick deploy (`trellis-matt` shortcut)

Prerequisites on Linux and Windows: Git, Python 3, Node/npx, and the Trellis CLI
at exactly **0.7.0-beta.4**. Install the CLI with the same command on both:

```bash
npm install -g @mindfoldhq/trellis@0.7.0-beta.4
```

Do not upgrade Trellis past `0.7.0-beta.4` for this branch. The installer looks
up Python as `python3`, then `python`, then `py -3`.

On Linux, install the shell shortcut once (symlink into `~/.local/bin`):

```bash
~/trellis/scripts/grok-fixes/install-shortcut.sh
# uninstall: ~/trellis/scripts/grok-fixes/install-shortcut.sh --uninstall
```

On Windows, from cmd or PowerShell (no Administrator, and no need to open Git Bash):

```bat
scripts\grok-fixes\install-shortcut.cmd
```

That writes `trellis-matt.cmd` and `trellis-matt.ps1` into a user-writable
directory already on PATH, or `%USERPROFILE%\.local\bin`. If the directory is
not on PATH, the command says so. The `.cmd` file finds
`C:\Program Files\Git\bin\bash.exe` (or Git's `bash.exe` next to `git.exe`).
It does not call `C:\Windows\System32\bash.exe`.

Then, in any Trellis project (or pass `DIR`):

```bash
trellis-matt status              # version + applied/pending/conflict per patch
trellis-matt dry-run [DIR]       # preview
trellis-matt apply [DIR]         # apply + smoke test (idempotent)
trellis-matt revert [DIR]        # undo patches
trellis-matt init [DIR] -u NAME  # new project: trellis init --grok, copy Matt
                                 # docs + workflow + aligned .grok/commands, apply
trellis-matt update [DIR]        # safe: trellis update -n, re-apply, list .new;
                                 # protects .trellis/workflow.md by default
```

Override the source checkout with `TRELLIS_MATT_HOME=/path/to/checkout`.
Grok Build slash command: `.grok/commands/trellis-matt-deploy.md` (`/trellis-matt-deploy`)
runs status → dry-run → wait for confirm → apply.

## One-click install (Claude Code, Codex, and Grok Build)

You do not need a `trellis-matt` command already installed.

`trellis-matt install` is the full new-project path. It keeps
`status`, `dry-run`, `apply`, `revert`, `init`, and `update` as they are.
`init` still means "Grok project, no Matt skills installer". `apply` stays
idempotent and still upserts the Matt/grill block into both `AGENTS.md` and
`CLAUDE.md`.

Prerequisites: Git, Python 3, Node/npx, and `@mindfoldhq/trellis@0.7.0-beta.4`.
On Windows, install Git for Windows; the launcher uses
`C:\Program Files\Git\bin\bash.exe` and does not call
`C:\Windows\System32\bash.exe`.

Linux or WSL, from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/samiya782/trellis-workflow/main/scripts/grok-fixes/oneclick.sh \
  | bash -s -- ~/my-project -u your-name --claude --codex --grok
```

Windows, from PowerShell, from GitHub:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/samiya782/trellis-workflow/main/scripts/grok-fixes/oneclick.ps1))) "$env:USERPROFILE\my-project" -u your-name --claude --codex --grok
```

A standalone download of `oneclick.sh` or `oneclick.ps1` clones branch `main`,
then runs that clone's installer. The cache is `TRELLIS_MATT_CLONE_DIR`, or
`$XDG_CACHE_HOME/trellis-matt/workflow` (default `~/.cache/trellis-matt/workflow`)
on Linux, or `%LOCALAPPDATA%\trellis-matt\workflow` on Windows. A dirty cache
is left alone and the command stops.

Platforms (any combination). Omit every platform flag to install Claude Code,
Codex, and Grok Build. `--codefree-o` and `--codefree-space` are opt-in and
are not included in that default. Official `trellis init` has no flag for
codefree-o or CodeFree Space, so those names are not passed through to it.

| Flag | `trellis init` | What the overlay writes | Matt skills agent |
|---|---|---|---|
| `--claude` | `--claude` | `.claude/hooks/session-start.py`, `.claude/hooks/inject-subagent-context.py`, `.claude/commands/trellis/{continue,finish-work}.md`, plus the SessionStart `new`/`load` merge into `.claude/settings.json` | `claude-code` |
| `--codex` | `--codex` | `.codex/config.toml`, `.codex/hooks/{session-start,inject-subagent-context}.py`, `.codex/agents/trellis-{check,implement,research}.toml`, `.agents/skills/trellis-{start,continue,finish-work}/SKILL.md` | `codex` |
| `--grok` | `--grok` | `.grok/commands/trellis-*.md` (start, continue, finish-work, and `trellis-matt-deploy`) | `grok` |
| `--codefree-o` | not passed | `.agents/skills/trellis-{start,continue,finish-work}/SKILL.md` and `.codefree-o/command/trellis-{start,continue,finish-work}.md`. The grill block is upserted into `AGENTS.md` and `CLAUDE.md` on every install | `codex` (the skills CLI writes `.agents/skills` for that name; this is not a Codex install) |
| `--codefree-space` | not passed | the same `.agents/skills/trellis-*` files, plus the grill block in `AGENTS.md` and `CLAUDE.md`. CodeFree Space has no project command directory | `codex` (same directory; one `--agent codex` if either new client or `--codex` is requested) |

An install that names only `--codefree-o` and/or `--codefree-space` still
needs a `.trellis/` tree. The installer runs `trellis init --codex` in a
throwaway directory, copies `.trellis/`, `AGENTS.md` (only if the target has
none), `.gitattributes` (only if the target has none), and `.agents/` files
that are not already present, then deletes `.codex/` keys from
`.trellis/.template-hashes.json`. It does not copy `.codex/`. Existing files
under `.agents/` are left in place, then the three aligned Trellis skills are
overwritten from this checkout. `--opencode` is not used.

codefree-o reads the first existing file among `AGENTS.md`, `CLAUDE.md`, and
`CONTEXT.md`. The grill / `get_context.py` / `task.py create … --no-start`
block is written into `AGENTS.md`, so that is the file codefree-o loads.
CodeFree Space reads `AGENTS.md` and `CLAUDE.md`. Neither client has a
SessionStart hook in this overlay. Do not add a project `codefree.json`.

From this checkout, with no `trellis-matt` command on PATH:

```bash
scripts/grok-fixes/oneclick.sh ~/my-project -u your-name --codefree-o --codefree-space
```

```powershell
.\scripts\grok-fixes\oneclick.ps1 "$env:USERPROFILE\my-project" -u your-name --codefree-o --codefree-space
```

The GitHub `curl` and `irm` examples above publish whatever is on branch
`grok`. They still show `--claude --codex --grok`. Run the CodeFree flags
from this checkout until that branch is pushed. Windows launchers forward
the new flags in `$args` / `%*`. `oneclick.ps1` has no `param()` block, and
it still calls Git for Windows `bash.exe`, not `C:\Windows\System32\bash.exe`.

Every install also copies `.trellis/workflow.md`, `docs/agents/matt-flow.md`,
`docs/agents/issue-tracker.md`, and the patched
`.trellis/scripts/common/{active_task,task_store}.py`, then runs
`apply-grok-fixes.sh --only scripts`. Matt skills:

```bash
npx skills@latest add mattpocock/skills --agent <requested agents> --yes
```

`--no-skills` skips that. The installer does not run `/setup-matt-pocock-skills`.

After a successful install, both `AGENTS.md` and `CLAUDE.md` contain the
`get_context.py` workflow load and the `/grill-with-docs` line that creates a
planning task with `task.py create … --no-start`.

From a local checkout or the shortcut:

```bash
trellis-matt install ~/my-project -u your-name --claude --codex --grok
```

Windows, from cmd or PowerShell, using this checkout:

```bat
scripts\grok-fixes\trellis-matt.cmd install %USERPROFILE%\my-project -u your-name --claude --codex --grok
```

Or, with the shortcut already installed, clone branch `main` and use it even
if a local checkout exists:

```bash
trellis-matt install ~/my-project -u your-name --from-github --claude --codex --grok
```

`--from-github` clones `https://github.com/samiya782/trellis-workflow.git`
branch `main` (override with `TRELLIS_MATT_REPO` / `TRELLIS_MATT_BRANCH`).
Re-running `install` in a project that already has `.trellis/` skips
`trellis init` and copies the overlays again.

In the project directory, run `grok --trust` once before a Grok session.

## Local deploy on Windows and WSL

This is the full local path, from a clean machine to a project you can actually
use. Use this checkout when it is ahead of GitHub; the `curl` / `irm` one-liners
install whatever is currently on `origin/main`.

### What you need first

On both Windows and WSL (or Linux): Git, Python 3.9+, Node.js (`npx`), and the
Trellis CLI at exactly **0.7.0-beta.4**. Install the CLI with the same command
on both, and do not upgrade past that version:

```bash
npm install -g @mindfoldhq/trellis@0.7.0-beta.4
```

Check each tool before you continue:

```bash
git --version
python3 --version      # Windows: python --version  or  py -3 --version
node --version
npx --version
trellis --version      # must print 0.7.0-beta.4
```

The installer looks up Python as `python3`, then `python`, then `py -3`.

If `trellis` is missing on WSL or Linux, it is often under mise's Node, for
example `~/.local/share/mise/installs/node/lts/bin`. Add that directory to
`PATH`, or use a login shell (`bash -lc 'trellis --version'`).

Windows also needs [Git for Windows](https://git-scm.com/download/win), so
`C:\Program Files\Git\bin\bash.exe` exists. The launcher does not call
`C:\Windows\System32\bash.exe`, which starts WSL.

Optional clients, only the ones you will use: Claude Code, Codex, Grok Build,
codefree-o, and/or CodeFree Space. CodeFree Space is a Windows or macOS app;
there is no Linux GUI. Linux does not need that app installed. The same project
files are what the app would scan.

### From this checkout

On WSL or Linux, from the `trellis-workflow` checkout (for example
`~/trellis`):

```bash
scripts/grok-fixes/install-shortcut.sh
# uninstall: scripts/grok-fixes/install-shortcut.sh --uninstall
trellis-matt install ~/my-project -u your-name --claude --codex --grok
```

`install-shortcut.sh` writes a `trellis-matt` symlink into `~/.local/bin`.
If you have not installed the shortcut yet, call
`scripts/grok-fixes/oneclick.sh` or `scripts/grok-fixes/trellis-matt` with the
same arguments.

Add `--codefree-o` and/or `--codefree-space` when you want those clients.
They are opt-in and are not part of the default three. Official `trellis init`
has no flag for them.

On Windows, from cmd or PowerShell, without opening a Git Bash window:

```bat
scripts\grok-fixes\install-shortcut.cmd
trellis-matt install %USERPROFILE%\my-project -u your-name --claude --codex --grok
```

`install-shortcut.cmd` writes `trellis-matt.cmd` and `trellis-matt.ps1` into a
user-writable directory already on PATH, or `%USERPROFILE%\.local\bin`. It does
not need Administrator. If that directory is not on PATH, the command prints
the directory to add. You can also run `scripts\grok-fixes\trellis-matt.cmd` or
`scripts\grok-fixes\oneclick.ps1` directly.

Cache for a GitHub clone (only when you pass `--from-github`, or when you use
the published one-liner): `~/.cache/trellis-matt/workflow` on WSL/Linux, or
`%LOCALAPPDATA%\trellis-matt\workflow` on Windows. A dirty cache is left alone
and the command stops. Override with `TRELLIS_MATT_CLONE_DIR`.

### After install, confirm it worked

In the new project directory:

1. Both `AGENTS.md` and `CLAUDE.md` contain `get_context.py`, `grill-with-docs`,
   and `task.py create … --no-start`.
2. Dual review is present:

```bash
python3 .agents/skills/trellis-dual-review/dual_review.py verify-install .
python3 .agents/skills/trellis-dual-review/dual_review.py self-test
```

   On Windows, `python` or `py -3` is fine if `python3` is missing.

3. For Grok Build, run `grok --trust` once in the project directory.
4. For codefree-o, use `codefree-o debug skill` and `codefree-o debug config`.
   Do not use `codefree-o skill` for this check; that command can open a login
   prompt and wait. Log in first if the debug commands say you are not signed
   in. You should see the trellis skills, including `trellis-dual-review`, and
   the slash commands `/trellis-start`, `/trellis-continue`,
   `/trellis-finish-work`, and `/trellis-dual-review`.
5. For CodeFree Space, open the folder in the Windows or macOS app. There is
   no Linux GUI; the files above are what the app scans.

### Common problems

- **`UnicodeDecodeError: 'gbk'` on Windows.** The installer must read and write
  text as UTF-8. Update to a checkout that includes that fix and re-run
  `trellis-matt install` (or `apply` in an existing project).
- **`trellis: command not found` on WSL or Linux.** mise's Node is not on
  `PATH`. Use a login shell, or add the mise Node `bin` directory.
- **`codefree-o` hangs.** You are probably not logged in, or you ran
  `codefree-o skill` instead of `debug skill`. Log in, then use the debug
  commands, with a timeout if you are scripting the check.
- **The wrong bash on Windows.** If a script suddenly starts WSL, you invoked
  `C:\Windows\System32\bash.exe`. Use `trellis-matt.cmd` or Git for Windows
  `bash.exe`.
- **Windows Git refuses a WSL checkout.** Work inside WSL for the WSL
  checkout. Do not point Windows Git at `/home/...` unless you mean to.
- **Network failures from `npm` or `trellis`.** Set `HTTP_PROXY` and
  `HTTPS_PROXY` if this machine uses a local proxy.

### Existing project

`trellis-matt apply` in a project that already has `.trellis/` copies the
overlay again, including the dual-review skill, and upserts the grill and
dual-review blocks into `AGENTS.md` and `CLAUDE.md`. It does not re-run
`trellis init`.

## Dual review

Install copies `.agents/skills/trellis-dual-review/` into every project.
Depending on the clients you asked for, it also writes:

- Grok Build: `.grok/commands/trellis-dual-review.md` (`/trellis-dual-review`)
- Claude Code: `.claude/commands/trellis/dual-review.md` (`/trellis:dual-review`)
- codefree-o: `.codefree-o/command/trellis-dual-review.md` (`/trellis-dual-review`)
- CodeFree Space and Codex: the shared skill under `.agents/skills/`

This is a merge gate, not Matt's `code-review` skill. Two independent
reviewers look at the same tip SHA: @dr eggbot, and a read-only Grok
CloudAgent (`grok-4.7`, `xhigh`, never Auto). The implementer does not review
their own work.

Prepare the two prompts on any OS (this does not call the reviewers):

```bash
python3 .agents/skills/trellis-dual-review/dual_review.py prepare \
  --tip <ref-or-sha> --base main --pr <N> --url <url> --branch <branch> \
  --background "<failure and a minimal repro>" \
  --claimed-cause "<implementer's claim, which a reviewer may discard>" \
  --banned "<the project's banned items>"
```

The files land in `.trellis/.runtime/dual-review/` (gitignored). A coordinating
Grok Bot that can reach the reviewers then sends those prompts and waits. Other
clients should give the files to the user and stop; they must not claim the
review ran.

A change may merge only when all four are true: both reviewers report no Must
findings on that same tip; CI is green and `mergeable_state` is `clean` (or the
project has no CI, said plainly); the original failure passes on the user's
machine and the default path still works; the user has authorized a squash
merge. Should findings do not block; they are collected for a later PR. A new
Must fix gets a new tip and both reviewers look again.

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

`trellis-matt apply` now **copies** from the source checkout before applying
script patches 0001–0002:

- `.trellis/workflow.md`, `docs/agents/matt-flow.md`, `docs/agents/issue-tracker.md`
- `.grok/commands/trellis-{start,continue,finish-work}.md`
- SessionStart `new`/`load` matchers into `.claude/settings.json`
- Upserts a Matt/grill block (`<!-- TRELLIS-GROK:MATT-START -->`) into **both**
  `AGENTS.md` (Claude Code) and project `CLAUDE.md` (Grok Build loads this via
  `agents_md_files`, not `AGENTS.md`), including `/grill-with-docs` entry
  bootstrap (`get_context` + `task.py create --no-start`). Creates `CLAUDE.md`
  when missing so Grok has somewhere to inject the block.
- Copies the dual-review skill and helper, plus the matching client command
  when `.grok/commands`, `.claude/commands/trellis`, or `.codefree-o` already
  exists, and upserts a short `<!-- TRELLIS-GROK:DUAL-REVIEW-START -->` block
  into both `AGENTS.md` and `CLAUDE.md`.

Patches 0003–0004 remain for reference / older installs, but apply no longer
depends on them for the grok-layer files (those patches go stale when the
source docs evolve, which previously made apply report "already applied"
while bootstrap text was still missing).

## Grok loads CLAUDE.md not AGENTS.md (2026-11-01)

Grok Build session `prompt_context.agents_md_files` only includes project
`CLAUDE.md` (and optional `~/.claude/CLAUDE.md`). The Matt/grill bootstrap that
lives in `AGENTS.md` was invisible to Grok until `trellis-matt apply` also
upserted the same `<!-- TRELLIS-GROK:MATT-START -->` block into `CLAUDE.md`.
Keep both files in sync; do not remove the AGENTS.md copy (Claude Code still
reads it).
