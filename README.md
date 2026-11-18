# Trellis + Matt Pocock Skills

Normal Trellis is the default. Explicitly invoking a Matt skill selects the Matt
route for that work item. Small work stays light: ordinary edits, bug reports,
`/grill-me` discussions and direct `/implement` runs create no Trellis task. At a
user-only skill boundary, the agent is meant to save context, give the next
command and pause. See the evidence note below for what has actually been run.

## Set up a new project

You do not need a `trellis-matt` command already installed. The one-liners
below download this repository's `main` branch and run the installer.

Requirements: Git, Python 3, Node/npx, and the `trellis` CLI at exactly
**0.7.0-beta.4**, plus the clients you install: Claude Code, Codex, Grok
Build, codefree-o, and/or CodeFree Space. Install that exact CLI on Linux or
Windows, and do not upgrade past it:

```bash
npm install -g @mindfoldhq/trellis@0.7.0-beta.4
```

Python is resolved as `python3`, then `python`, then `py -3`. On Windows,
install [Git for Windows](https://git-scm.com/download/win) so
`C:\Program Files\Git\bin\bash.exe` exists. The launcher does not call
`C:\Windows\System32\bash.exe`, which starts WSL.
Under another Trellis version, merge their changes into that version's generated
files instead of copying over them.

### Linux or WSL

```bash
curl -fsSL https://raw.githubusercontent.com/samiya782/trellis-workflow/main/scripts/grok-fixes/oneclick.sh \
  | bash -s -- ~/my-project -u your-name --claude --codex --grok
```

### Windows (PowerShell)

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/samiya782/trellis-workflow/main/scripts/grok-fixes/oneclick.ps1))) "$env:USERPROFILE\my-project" -u your-name --claude --codex --grok
```

The script clones branch `main` on first run (cache:
`~/.cache/trellis-matt/workflow` on Linux, `%LOCALAPPDATA%\trellis-matt\workflow`
on Windows, or `TRELLIS_MATT_CLONE_DIR`). Pass any combination of
`--claude`, `--codex`, and `--grok`. With no platform flags, it installs all
three. `--codefree-o` and `--codefree-space` are extra and opt-in; they are
not part of that default. `--no-skills` skips `npx skills@latest add mattpocock/skills`.
It does not run `/setup-matt-pocock-skills`. After a successful install, both
`AGENTS.md` and `CLAUDE.md` contain the grill / `get_context.py` /
`task.py create … --no-start` bootstrap.

In the new project directory, run `grok --trust` once before a Grok session.

### CodeFree Space and codefree-o

Official `trellis init` at 0.7.0-beta.4 has no flag for these clients. Do not
pass a made-up `--codefree` flag to it. This checkout's installer writes the
project files they already load:

- Both read `AGENTS.md`, `CLAUDE.md`, and `.agents/skills/`.
- codefree-o also loads `.codefree-o/command/trellis-start.md`,
  `trellis-continue.md`, and `trellis-finish-work.md` as `/trellis-start`,
  `/trellis-continue`, and `/trellis-finish-work`.
- CodeFree Space has no project command directory. Open the folder in the
  Windows or macOS app. There is no Linux GUI; the same files are what the
  app scans. Linux does not need the desktop app installed.
- Neither client gets a SessionStart hook. `AGENTS.md` tells the agent to run
  `get_context.py`. codefree-o reads `AGENTS.md` and stops before `CLAUDE.md`
  when `AGENTS.md` exists, so the bootstrap has to be in `AGENTS.md`.
  `CLAUDE.md` is still written for CodeFree Space and for Claude Code / Grok.
- The installer does not write a project `codefree.json`.
- Matt skills go through the skills CLI agent name `codex`, because that name
  fills `.agents/skills`. That is not `trellis init --codex` unless you also
  passed `--codex`.

The `curl` and PowerShell one-liners above call the scripts published on
branch `main`. For CodeFree Space and codefree-o, from this checkout:

```bash
scripts/grok-fixes/oneclick.sh ~/my-project -u your-name --codefree-o --codefree-space
```

```powershell
.\scripts\grok-fixes\oneclick.ps1 "$env:USERPROFILE\my-project" -u your-name --codefree-o --codefree-space
```

`--no-skills` when `.agents/skills` already has the Matt skills. You can
combine the new flags with `--claude`, `--codex`, or `--grok`. Passing only
the new flags still creates `.trellis/` and does not leave a `.codex/`,
`.claude/`, `.grok/`, or `.opencode/` tree behind.

### If you already have this checkout

On Linux or WSL, from this checkout or after `scripts/grok-fixes/install-shortcut.sh`:

```bash
trellis-matt install ~/my-project -u your-name --claude --codex --grok
```

On Windows, from cmd or PowerShell, without opening a Git Bash window:

```bat
scripts\grok-fixes\trellis-matt.cmd install %USERPROFILE%\my-project -u your-name --claude --codex --grok
scripts\grok-fixes\install-shortcut.cmd
trellis-matt install %USERPROFILE%\my-project -u your-name --claude --codex --grok
```

`install-shortcut` writes `trellis-matt.cmd` and `trellis-matt.ps1` into a
user-writable directory that is already on PATH, or `%USERPROFILE%\.local\bin`.
It does not need Administrator. If that directory is not on PATH, the command
prints the directory to add. PowerShell can also run
`scripts\grok-fixes\trellis-matt.ps1` or `scripts\grok-fixes\oneclick.ps1`.

To force the file source to be a fresh GitHub clone even when a local
checkout exists:

```bash
trellis-matt install ~/my-project -u your-name --from-github --claude --codex --grok
```

`--from-github` clones `https://github.com/samiya782/trellis-workflow` branch
`main`. A dirty cache is left alone and the command stops.

`trellis-matt init` is unchanged: it always passes `--grok`, forwards extra
`trellis init` flags, and does not install Matt skills. `status`, `dry-run`,
`apply`, `revert`, and `update` are unchanged. Details:
[docs/grok-fixes/INSTALL.md](docs/grok-fixes/INSTALL.md#one-click-install-claude-code-codex-and-grok-build).

## Files that make up this setup

Matt's skills are installed unmodified by the standard installer. Trellis files
come from `trellis init`. This integration is a small layer of local files:

| File | Purpose |
| --- | --- |
| [.trellis/workflow.md](.trellis/workflow.md) | Phase Index, routes and hook breadcrumbs. Replaces the stock workflow, including its per-turn task-consent prompt |
| [docs/agents/matt-flow.md](docs/agents/matt-flow.md) | Matt entry, record size per entry skill, handoff/resume, delegation, review |
| [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md) | Matt publication backend on Trellis tasks; this is the file `/setup-matt-pocock-skills` would otherwise write |
| `AGENTS.md` (paragraph after the Trellis block) | Points agents at the workflow and `docs/agents/` |
| `.claude/hooks/{session-start,inject-subagent-context}.py`, `.claude/commands/trellis/{continue,finish-work}.md` | Claude Code context loading, worker task binding, resume and closeout |
| `.codex/config.toml`, `.codex/hooks/{session-start,inject-subagent-context}.py`, `.codex/agents/trellis-{check,implement,research}.toml` | The same for Codex |
| `.grok/skills/`, `.grok/agents/`, `.grok/commands/` | Generated by `trellis init --grok`. The skills installer symlinks Matt skills into `.grok/skills`. Grok Build skips `SessionStart` but runs the other `.claude/settings.json` hooks, so the aligned `.grok/commands/trellis-{start,continue,finish-work}.md` load context with `get_context.py` |
| `.agents/skills/trellis-{start,continue,finish-work}/SKILL.md` | Trellis start/resume/closeout skills aligned with this workflow. Codex, codefree-o, and CodeFree Space all read this directory |
| `.codefree-o/command/trellis-{start,continue,finish-work}.md` | codefree-o slash commands generated from those skills at install (`--codefree-o` only) |

`docs/validation/`, `tests/` and this README document and test this checkout.
New projects don't need them.

### Manual steps

From the new project's root, with this checkout at `~/trellis`:

```bash
git init                                   # skip if already a repository
trellis init -u your-name --claude --codex --grok
npx skills@latest add mattpocock/skills --agent claude-code codex grok --yes

R=~/trellis
for f in .trellis/workflow.md docs/agents/matt-flow.md docs/agents/issue-tracker.md
do mkdir -p "$(dirname "$f")" && cp "$R/$f" "$f"; done
```

Drop `--claude`, `--codex`, or `--grok` for a platform you are not installing,
and drop the matching name from `--agent`. The three copied files are the shared
integration. `trellis init` writes each platform's own skills, commands, and
hooks. Grok's copy is `.grok/`.

In the project directory, run `grok --trust` once before a Grok session. The
flag is accepted by Grok Build 1.0.67 and is omitted from `grok --help`. It
records the folder in `~/.grok/trusted_folders.toml`. `grok inspect --json` then
reports `projectTrusted: true`, loads `AGENTS.md`, and lists the project skills.
An untrusted folder leaves those unloaded. The checked Grok runs below used a
trusted folder.

Claude Code and Codex in this checkout also use customized context files. Copy
them when you want that previously tested behavior:

```bash
for f in .claude/hooks/session-start.py .claude/hooks/inject-subagent-context.py \
  .claude/commands/trellis/continue.md .claude/commands/trellis/finish-work.md \
  .codex/config.toml .codex/hooks/session-start.py .codex/hooks/inject-subagent-context.py \
  .codex/agents/trellis-check.toml .codex/agents/trellis-implement.toml \
  .codex/agents/trellis-research.toml .agents/skills/trellis-start/SKILL.md \
  .agents/skills/trellis-continue/SKILL.md .agents/skills/trellis-finish-work/SKILL.md \
  .grok/commands/trellis-start.md .grok/commands/trellis-continue.md \
  .grok/commands/trellis-finish-work.md .trellis/scripts/common/active_task.py \
  .trellis/scripts/common/task_store.py
do mkdir -p "$(dirname "$f")" && cp "$R/$f" "$f"; done
```

Skip the `.claude`, `.codex` or `.grok` files for a platform you didn't initialize.
`active_task.py` and `task_store.py` are Trellis-managed scripts. These copies
add Grok's `GROK_SESSION_ID` so `task.py start` writes a session pointer under
Grok, and make `task.py archive` repoint `implement.jsonl`/`check.jsonl` entries
into the moved task. `trellis update` reports them as modified. Instead of
copying them (and the `.grok/commands` files) you can run
`$R/scripts/grok-fixes/apply-grok-fixes.sh --target .`, which checks the Trellis
version, backs up, patches and runs a smoke test; see
[docs/grok-fixes/INSTALL.md](docs/grok-fixes/INSTALL.md), which also covers
`trellis update -s`/`-n` and re-applying after an update. Then add this paragraph to `AGENTS.md`
after the Trellis-managed block. Edits outside that block survive `trellis update`.
The Grok runs below used init's `AGENTS.md` unchanged; it already points at
`.trellis/workflow.md`, which the copy replaces:

```markdown
For work in this project, load the compact workflow with
`python3 .trellis/scripts/get_context.py --mode phase` before choosing a route.
It governs local orchestration even when bundled skill examples prescribe extra
stages. Matt entry/resume details: `docs/agents/matt-flow.md`; publication:
`docs/agents/issue-tracker.md`.
A user-invoked Matt skill such as `grill-me` is not edit authority: once it settles
buildable scope, end with the exact next command (`/implement <scope>`, Codex
`$implement <scope>`) and pause.
```

Check that `python3 .trellis/scripts/get_context.py --mode phase` mentions
"explicitly invokes a Matt skill". Then review and commit the result, and start a
fresh agent session. Codex hooks also need `features.hooks = true` in
`~/.codex/config.toml` and a one-time `/hooks` approval, as `trellis init` reports.

Don't run `/setup-matt-pocock-skills` for this layout: `docs/agents/issue-tracker.md`
already configures Trellis tasks as the tracker. Rerun it only to switch to a
hosted tracker. When adopting these files into an existing project, keep its
custom hooks and instructions and merge entry points rather than replacing them.
`trellis update` reports the files above as user modifications. Review its
changes and keep the local edits.

## Quick deploy (Grok shortcut)

```bash
~/trellis/scripts/grok-fixes/install-shortcut.sh   # Linux: ~/.local/bin/trellis-matt
trellis-matt status
trellis-matt dry-run
trellis-matt apply                 # or: trellis-matt init -u your-name
trellis-matt install ~/my-project -u your-name --claude --codex --grok
trellis-matt update                # safe upgrade path (creates .new; keeps workflow.md)
```

Windows, from cmd or PowerShell:

```bat
scripts\grok-fixes\install-shortcut.cmd
trellis-matt status
trellis-matt install %USERPROFILE%\my-project -u your-name --claude --codex --grok
```

Details: [docs/grok-fixes/INSTALL.md](docs/grok-fixes/INSTALL.md#quick-deploy-trellis-matt-shortcut).
Slash command in Grok: `/trellis-matt-deploy`.

## Update the Matt skills

Rerun the same `npx skills@latest add mattpocock/skills …` command for current
upstream skills. The standard installer manages skill contents, metadata, links
and `skills-lock.json`. This integration needs no policy patches, wrappers,
pinned revision or copy mode. Review installer changes and refresh the runtime's
skill catalog. An upstream update can add or remove skills or change their
invocation policy.

## Use

Pick the entry by the situation. Codex uses `$skill`. Claude Code and Grok use `/skill`.

| Situation | You type | What happens |
| --- | --- | --- |
| Small, clear change | A plain request, e.g. "Correct the typo in the help text and run the check. Leave it uncommitted." | Normal Trellis: edit, check, report. No task |
| Bug report: you describe the symptom, not the fix | A plain request, e.g. "`textstats` prints 4 words for `hello   world`; fix it." | Stock `diagnosing-bugs`: reproduce, then fix, then a regression test. No task |
| Small idea to settle before building | `/grill-me <idea>` | Stateless interview: no task, glossary or ADR. Ends with an `/implement <scope>` command for you to run |
| Small settled build | `/implement <scope>` | Builds directly with `tdd` and `code-review`. No spec, tickets or task |
| Feature that deserves a durable record | `/grill-with-docs <idea>` | Interview with `GLOSSARY.md`/ADRs. A minimal Trellis task carries the handoff |
| Published spec with tickets | `/implement-spec <task>` | Works the tickets as a task graph on an integration branch. Without a spec it stops and offers `/implement` |
| Uncertainty spanning sessions | `/wayfinder <goal>` | Planning only, until you authorize delivery |

Stock `/implement` commits to the current branch. Agents have treated invoking
it as commit permission. Say "leave it uncommitted" in the request to prevent
that. The installed `code-review` reviews `<fixed-point>...HEAD`, so without a
commit, review stays pending. Recorded authorization for larger work reads like:

> Implement the agreed scope. Choose routine engineering details, fix and recheck
> defects, and leave all changes uncommitted. Do not push.

When a needed skill requires user invocation, the agent gives the actual next
command and pauses. Stateful entries (`grill-with-docs`, `wayfinder`) reference a
task path:

```text
/implement .trellis/tasks/09-29-csv-import      # Codex: $implement …
```

Same-session small work references the agreed scope instead. Handoffs keep the
answers and authorization already given. Specification, ticketing, retro and
spec updates are selected when useful, not a mandatory pipeline. Stock `retro`
requires user invocation. If an update removes a needed skill, the agent reports
it instead of reconstructing it.

Resume with the exact task reference, `$trellis-continue` in Codex, or
`/trellis:continue` in Claude Code. Grok uses
`/trellis-continue` (the aligned `.grok/commands/trellis-continue.md`). Resume recovers task progress and any pending
skill command; it does not itself invoke a user-only Matt skill. `/grill-me` and
other task-free work have nothing to resume after the session ends. Closeout
retains planning/no-commit boundaries, reconciles prior archives and journal
entries, and uses explicit no-auto-commit lifecycle calls.

## Runtime limits and evidence

Skill discovery, invocation controls and tool permissions are separate. A file
read is an ordinary loading mechanism where the harness permits it; it cannot
bypass a user-only invocation boundary. Claude Code uses the upstream
`disable-model-invocation` frontmatter; Codex uses upstream `agents/openai.yaml`
policy, including `allow_implicit_invocation`. Do not infer Codex controls from
Claude frontmatter. Project trust and hook approval are also
separate. Keep existing hook registrations, avoid duplicates, and verify actual
instruction/context loading in the runtime being used.

Grok Build loads a skill by reading its `SKILL.md`. It has no Skill tool. A skill
with `disable-model-invocation: true` stays out of the model catalog and remains
a slash command. In the `/grill-me` run below, the slash command injected the
skill body, and the agent read `grilling/SKILL.md` from disk.

Independent ready tickets can run in parallel when tools and file ownership
permit. The coordinator joins results, owns task lifecycle and shared Git
operations, and fixes verified defects within the recorded repair budget.
Codex workers explicitly validate and load their dispatched task context when
native events lack the dispatch prompt. That loads task data; it does not grant
permission to invoke a skill.

In Claude Code, `implement-spec` workers that must call `tdd` run as general-purpose
agents, because `trellis-implement` has no Skill tool. Their worktrees don't contain
uncommitted planning files, so the dispatch gives absolute paths to the spec and
ticket in the main checkout. Workers leave edits uncommitted; the coordinator
reviews, commits and merges. The coordinator resolves merge conflicts itself,
without asking, and reports how. Code that git merges without a conflict can still
be wrong. In the recorded run, git flagged the option definitions as conflicting.
It merged the output dispatch without a conflict, and that merged code dropped the
`--min-length` filter from `--json`. Review the merged code, not only the conflict
hunks.

The current `code-review` installation reviews `<fixed-point>...HEAD`, which
excludes uncommitted edits. Review requiring a commit stays pending without commit
permission. Check the installed skill's contract after updates, and never count
an empty diff as acceptance of working-tree changes.

[Current stock-installation evidence](docs/validation/stock-installation.md)
records the installer run, installed policies, a seeded Codex handoff check and
Claude Code checks:
- **`grill-with-docs` handoff:** the first run implemented inline. After a
  routing fix, one retest recorded a task, returned `/implement <task>` and paused,
  and one fresh session recovered it.
- **Small-task routes (2026-10-05):** the first bug-report run fixed the bug
  without `diagnosing-bugs`. After a wording fix, the plain small-change and
  bug-report routes each passed 4 of 4 headless Claude Code runs. `/grill-me` →
  `/implement` and `/implement-spec` without a spec passed once each.
- **Durable routes (2026-10-05, Claude Code, once each):** passed.
  - `/grill-with-docs` recorded a task and paused with `/to-spec <task>`.
  - A fresh session recovered that command.
  - `/to-spec` and `/to-tickets` published a spec and three tickets.
  - `/wayfinder` published a map and resolved a research ticket, without code.
- **`/implement-spec` on that spec (once):** passed. It built three tickets in
  parallel worktrees with `tdd` and integrated them on a branch. It reviewed with
  `code-review`, fixed two findings and archived the tickets. At the user's
  request, a second review found no spec issues and four minor style issues;
  those were fixed. The branch was then merged and the task closed out with
  `/trellis:finish-work`.
- **New-project setup:** the procedure above was run once in a scratch project.
- **Grok Build (2026-10-23), once each, headless `grok -p`:** passed for the
  two plain routes and one explicit `/grill-me` below. Fixture
  `/home/samiya/tmp/trellis-matt-nPv9`,
  built with `trellis init -u fixture --claude --codex --grok -y` (the `-y`
  skips prompts), skills installer **1.7.4** (`38` skills, symlinked to Grok
  Build), and the three-file copy. Grok **1.0.67**, model **grok-4.7-build**,
  `--permission-mode bypassPermissions` so the shell check could run. The
  Claude/Codex overlay files were not copied. No new Trellis task was created.
  - **Normal route** `0ba8b991-a72f-4eb3-b563-35200dc49b72`: "Correct the typo in
    the textstats help text and run the relevant check. Leave it uncommitted."
    It read the copied workflow and `trellis-before-dev`, changed `Usge` to
    `Usage`, and the 2 tests passed. Uncommitted. 9 turns, $0.16.
  - **Bug report** `979f8e90-cf6f-4821-976c-8f30cd152e2c`: "textstats prints 4
    words for `hello   world`; fix it. Leave it uncommitted." It read
    `diagnosing-bugs` before editing the counter, reproduced 4 words, added a
    failing regression test, then counted with `split()`. 3 tests passed.
    Uncommitted. 13 turns, $0.35.
  - **`/grill-me`** `afdb7e75-25b6-439a-af62-d93f46bb61e4`: "Should textstats
    treat punctuation as part of a word?" The slash command injected the skill.
    The agent read `grilling/SKILL.md`, asked one question, and left the source
    unedited. An untracked `__pycache__` remained from importing the module.
    5 turns, $0.19. The model catalog omitted
    `disable-model-invocation` skills (`grill-with-docs`, `implement`,
    `to-spec`, `wayfinder`, `retro`, and the other user-only Matt skills) and
    still listed `diagnosing-bugs` and `tdd`.
- **Grok Build 1.0.70 (2026-10-26), headless, `grok-4.7-build-fast`:** fixtures
  under `/home/samiya/tmp/trellis-matt-val-20261026/`. Passed: typo, bug report,
  `/grill-with-docs` (one `--no-start` task), `/wayfinder` (map plus three
  planning children), resume by task path, `/trellis-continue`, `/implement`,
  `/implement-spec` without a spec (offers `/implement`, no task). After the Grok
  command, `matt-flow.md`, `AGENTS.md` and `active_task.py` fixes: `/trellis-start`
  creates no task and doesn't adopt `00-bootstrap-guidelines`; `/to-tickets` plus
  `/implement-spec` dispatch `trellis-implement` with `Active task:` and write a
  `grok_<session>` pointer; `/trellis-finish-work` archives child then parent with
  `--no-commit` and journals with `--no-commit`; `/grill-me` edits nothing and ends
  with `/implement <scope>`. Headless runs can't answer `ask_user_question`, so
  the agent took the recommended ticket breakdown. The upstream gap where `task.py
  archive` didn't rewrite `implement.jsonl`/`check.jsonl` paths into a
  later-archived parent (so `task.py validate` failed on archived children) is
  fixed on branch `grok` (`scripts/grok-fixes`, patch 0002).
- **Grok Build 1.0.70 (2026-10-26), interactive TUI, `grok-4.7-build-fast`:**
  fixture `recheck-tui`; `/to-tickets` → `/implement-spec` → `/trellis-finish-work`,
  then archiving the parent with `--no-commit`. Passed: two planning children,
  implementation without a commit, `grok_<session>` pointer, archive without a
  commit, archived children repointed to the archived parent's `prd.md` and
  `task.py validate` passing. Gaps: `/to-tickets` confirmed in plain text rather
  than `ask_user_question`, and Grok skipped workflow step 1.4 (`task.py start`)
  until prompted. Audit: [docs/validation/2026-10-26-grok](docs/validation/2026-10-26-grok/INDEX.md).
- **Not run:** Codex with the current routing text (preliminary runs are
  recorded in the evidence).

Earlier [validation reports](docs/validation/README.md) describe the historical
patched setup and independent runtime fixes; they do not establish automatic
end-to-end delivery with the current stock installation.
