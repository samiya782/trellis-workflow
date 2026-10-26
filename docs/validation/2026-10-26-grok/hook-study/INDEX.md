# Hook study: Trellis Claude-compat hooks under Grok Build, and the skipped `task.py start`

Date: 2026-10-26 23:28 to 2026-10-27 00:25 (UTC+8). The WSL clock is PDT, so raw
logs show 08:28 to 09:25 -07:00.
Tooling: grok 1.0.70, model `grok-4.7-build-fast`, Trellis 0.7.0-beta.4, `--always-approve` with deny rules
(`git commit/push/reset/checkout/stash`, `rm -rf`).
All runs used disposable fixtures under `~/tmp/trellis-grok-val-20261026/`. The `~/trellis` tree was
not touched until the verified fix commit.

Question (user, pt8u): did the Claude-compat hooks cause Grok to skip `task.py start`
(workflow 1.4)? How does the original, unmodified Trellis compare?

## Fixtures
| fixture | content |
|---|---|
| `hs-tpl-orig` | stock `trellis init --claude --grok -y -u fixture` plus a seeded `planning` task `10-26-textstats-top` with an approved PRD. |
| `hs-tpl-ours` | the branch-`grok` state, with Matt skills, AGENTS.md Matt rules, `docs/agents/matt-flow.md` and the trimmed workflow. Same seeded task. |
| `hs-tpl-fix` | ours plus activation rule v1 (`scripts/apply_fix.py`). |
| `hs-tpl-fix2` | ours plus activation rule v2 (`scripts/apply_fix2.py`). This version is committed on `grok` as `057d5f1`. |

Each hook command is wrapped by `scripts/trace_wrapper.py` (`wrap_hooks.sh`). The wrapper logs the event, the
payload and the hook stdout, then passes everything through unchanged. "off" runs drop the
`hooks` key from `.claude/settings.json`. `grok inspect --json` lists 9 hooks for "on" runs and 0 for "off" runs
(`runs/*/inspect.json`).

## Human-proxy messages
All of these were answered by the assistant on behalf of the user. They are logged in `runs/*/interactions.log`.
- M1 `/trellis-continue .trellis/tasks/10-26-textstats-top`
- M2 `The PRD is approved as complete. You are authorized to implement this task now. Do not commit and do not push.`
  In the orig runs, M2 was typed into the ask_user free-text option.
- M3 `/implement .trellis/tasks/10-26-textstats-top`. It was sent only when Grok stopped at the user-only Matt
  `implement` boundary and asked for that exact command (ours, fix r3/r4, fix2). This is a protocol deviation, recorded here.
No other nudges were given. Nobody mentioned `task.py start` to Grok.

## 1. Hook fire table (hooks ON; source: `runs/*/hook-trace.log`, `hook-trace.d/`)
| hook | event / matcher | fires on Grok? | stdout | reaches the model? |
|---|---|---|---|---|
| `session-start.py` | SessionStart `startup`/`clear`/`compact` | **never**: Grok sends `new`/`load` | none | no |
| `inject-workflow-state.py` | UserPromptSubmit | yes, on every prompt | 383 to 564 B `<workflow-state>` | **no**: Grok discards the stdout of an allowing UserPromptSubmit hook (`10-hooks.md`). The tag is absent from every chat_history.* |
| `inject-subagent-context.py` | PreToolUse `Task`, aliased by Grok to `spawn_subagent` | yes, on each trellis-implement / trellis-check spawn | **0 B** | **no**: the payload has `tool_name: spawn_subagent`. The hook only accepts task/agent/subagent, so it exits silently. A replay with `tool_name: Task` returns 26 KB of `updatedInput` (`evidence/replay-Task.out` vs `evidence/replay-spawn_subagent.out`). |
| `inject-spec-context.py` | PostToolUse Read/Edit/Write, aliased to `read_file`/`search_replace`/`write` | yes, many times | always 0 B | **no**: the hook filters on the Claude names Read/Edit/Write/MultiEdit and the key `tool_input.file_path` |
| `statusline.py`, `.codex/hooks` | n/a | not loaded by Grok | n/a | n/a |

\* `ours-on-r2` contains the literal string `<workflow-state>` once. It sits inside a grep tool_result over
`.trellis/config.yaml` and is not hook output.

Grok's native tool names in these runs: `run_terminal_command, read_file, grep, list_dir, search_replace, write,
spawn_subagent, ask_user_question, get_command_or_subagent_output`.

Subagent prompts (`evidence/subagent-prompts.txt`) are 9.4 to 11.8 K chars with hooks on and with hooks off. Their "Active task"/PRD
references come from the coordinator's own prompt, never from the hook.

**Net: on Grok, zero bytes of Trellis hook context reach the model, in both fixtures, so "hooks on" vs "off" is a null treatment.**

## 2. Behaviour comparison (`evidence/comparison.md`, `runs/*/analysis.json`)
| fixture | hooks | runs | `task.py start` ran before any product edit / worker | notes |
|---|---|---|---|---|
| orig | on | 2 | **2/2** | the stock continue command offers "Approve and start". Workers: trellis-implement, then trellis-check |
| orig | off | 2 | **2/2** | same |
| ours | on | 4 | **3/4** | r1 implemented inline after M3 with no start; the task stayed `planning` and Grok hand-edited task.json |
| ours | off | 2 | **2/2** | start came right before the first edit, after M3 |
| fix v1 | on | 4 | **4/4** | but r1/r2 read M2 as "authorized delivery" and implemented without the user-only `/implement`, which is a boundary regression |
| fix v2 | on | 2 | **2/2** | the boundary held: both waited for M3, then ran start first |

Pointers: ours/fix runs wrote `.trellis/.runtime/sessions/grok_<sid>.json`. The stock orig runs wrote a pointer once
(`grok-<sid>.json`, r1); stock Trellis on Grok has no stable session identity (the bug fixed by grok-fixes 0001).

## 3. Verdict
The hypothesis that the hooks caused the skipped start is **not supported**. None of the hook output reaches Grok's model in any run,
and ours skipped start with hooks on (1/4) while also running start with hooks on (3/4). The original Trellis ran start 4/4 with
or without hooks, because its stock `trellis-continue` command and workflow show the start step directly
in the chat route. The intermittent skip in ours comes from the Matt route: delivery is handed to the user-only
`implement` skill, and before this fix neither that skill, `matt-flow.md` nor AGENTS.md tied a
`task.py start` to it. The workflow.md 1.4 step existed but was not linked to `/implement`.

## 4. Fix (committed on `grok`, local only)
`057d5f1` changes AGENTS.md (+4) and docs/agents/matt-flow.md (+2). The patch is `scripts/apply_fix2.py`. When the user *types*
`/implement` for a task still in `planning`, the first action is `task.py start` plus a `current --source` check. An
approval or authorization message does not replace the command. v1's "(or any authorized delivery)" wording was dropped
because it led Grok to bypass the boundary. grok-fixes patch 0004 is still detected as "already applied"
(`git apply --reverse --check` passes).

## 5. Upstream-relevant (report only; not submitted)
Trellis Claude hooks are inert on Grok Build:
- the SessionStart matchers never match `new`/`load`;
- UserPromptSubmit stdout is dropped (it would need `systemMessage` or another Grok channel);
- `inject-subagent-context.py` does not recognize `spawn_subagent`;
- `inject-spec-context.py` does not recognize `read_file`/`search_replace`/`write` or the `target_file`/`path` keys.
A possible Grok-native shim is a `.grok/hooks/*.json` PreToolUse hook on `spawn_subagent` that calls the
subagent hook with `tool_name` mapped to `Task`. It has not been built or committed.

## Layout
- `runs/<run>/`: inspect.json, analysis.json, interactions.log (proxy answers marked), tmux-final-screen.txt,
  tmux-scrollback.txt, session-id.txt, chat_history.trimmed.jsonl (system prompt omitted, values >2000 chars truncated),
  hook-trace.log, and hook-trace.d/ (all PreToolUse records, the first UserPromptSubmit and the first PostToolUse records).
- `evidence/`: comparison.md, analyze-all.txt, subagent-prompts.txt, boundary-and-activation-excerpts.txt,
  replay-*.out, inspect-tpl-*.json, orig-init.log
- `scripts/`: every harness script used.
Secrets: the redaction pass (`scripts/collect.py`) found 0 matches. A grep for ctx7sk/xai keys is clean.
