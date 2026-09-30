# Fresh normal-work and retrospective regression

Executed 2026-09-29 with codex-cli 0.159.0, default configured model `gpt-6-astra`, and the local Trellis 0.7.0-beta.4 runtime. These are actual Codex subprocess runs, not simulated skill calls. No Claude harness was run.

## Isolation and input

Fixture: `/tmp/trellis-normal-retro-3854ukj_`; baseline fixture commit: `ee614a49fbc20727cf9493afa8b30d0f11c14500`. Built from repository `ca67648` plus the current AGENTS, README, workflow/config, Codex hooks/roles/config, project skills, docs/agents, adapter scripts and tests. Root task/runtime/workspace state was excluded, and fixture developer identity was initialized locally. The snapshot contains all 12 genuine Matt skills with project Codex metadata overrides; the checked-in Claude sources were retained.

Each run used `codex exec --sandbox workspace-write --cd <fixture> --json --color never --output-last-message <file>` and per-invocation `-c 'projects."<fixture>".trust_level="trusted"'`. No global settings, permission bypass, hook bypass, explicit model override, remote or push was used. The fixture has local Git identity only.

The normal request was exactly the earlier baseline request:

> Fix the spelling of automaticaly to automatically if present in README.md. If it is absent, add a single final sentence: Small changes can be checked automatically. Make this small documentation edit directly; no commit is needed.

The retrospective request was an ordinary fresh explicit invocation against that completed session:

> $retro Review this completed session: /home/samiya/.codex/sessions/2026/09/29/rollout-2026-09-29T10-10-03-01a0ee25-17ab-7d33-8b84-41f0cd11fdbd.jsonl. Suggest improvements and leave source files unchanged.

Neither session received the optimization request, injected stage reminders, synthetic human answers, or steering follow-ups.

## Normal request: observed delivery

Thread `01a0ee25-17ab-7d33-8b84-41f0cd11fdbd`; native transcript:
`~/.codex/sessions/2026/09/29/rollout-2026-09-29T10-10-03-01a0ee25-17ab-7d33-8b84-41f0cd11fdbd.jsonl`.

The agent loaded the compact Phase Index and the real adapted `trellis-start` skill, identified the normal direct-edit route, read README and session state, applied the requested fallback sentence, and ran `git diff --check` plus a focused diff. It ended with a self-contained completion report. Only README changed; no task, commit, unnecessary delegation, or user question occurred. Avoidable user interruptions: **0**, matching the baseline normal request's **0**.

The native initial skills-bearing developer block is 11,900 characters. Its catalog includes genuine `implement`, `to-spec`, `to-tickets`, `retro`, `code-review`, and `writing-for-agents`; explicit-entry `grill-with-docs` is absent from the ordinary catalog, as expected. This is catalog/discovery evidence, not proof that those skills executed in this normal request.

No `<workflow-state>` or `<trellis-bootstrap>` hook-generated developer block appeared in either fresh native transcript. The agent explicitly ran the context CLI. These tests therefore validate the documented manual-loading fallback under copied, unapproved hooks, not native hook injection. Per-project config trust did not establish individual hook trust.

### Measured context and output

The previous baseline raw CLI file `/tmp/trellis-matt-baseline-normal.jsonl` was independently recounted rather than relying only on its summary.

| Metric | Earlier baseline | Current fixture | Interpretation |
|---|---:|---:|---|
| Completed shell commands | 7 | 5 | Actual executed commands |
| Sum of shell output characters | 65,569 | 13,877 | 78.8% reduction; includes repeated output/diff, not unique context |
| Sum of shell output UTF-8 bytes | 65,623 | 13,877 | Actual emitted bytes |
| Cumulative input tokens | 96,186 | 76,151 | 20.8% reduction in this pair of runs; cumulative across requests |
| Cumulative cached input tokens | 68,352 | 54,912 | Runtime usage report |
| Output tokens | 593 | 426 | Runtime usage report |
| Avoidable user interruptions | 0 | 0 | Neither run needed another user turn |

Current completed command outputs were: phase index **1,337** chars/bytes; start skill **1,241**; README **10,273**; session context **663**; diff check/diff **363**. The full 8,331-byte workflow was **not** read by the normal agent. The baseline had printed the complete workflow plus README in one 57,423-character command output. A README literal search could still avoid much of the remaining load.

Do not add catalog characters, shell output and cumulative input tokens into a single context-size number: they describe different quantities. The original baseline's reported skills-bearing developer block was 9,741 characters; the current 11,900-character block is larger because genuine downstream skills are now discoverable. That catalog tradeoff coexists with the measured reduction in explicit file/context output. Character/4 token conversions below are estimates, not tokenizer counts.

## Retrospective: actual skills and results

Fresh thread `01a0ee26-1126-7360-8bbe-9adb418da90b`; native transcript:
`~/.codex/sessions/2026/09/29/rollout-2026-09-29T10-11-07-01a0ee26-1126-7360-8bbe-9adb418da90b.jsonl`.

Observed evidence:

- Native line 11 is a real user skill-expansion message for project-local `retro` (4,483 characters).
- Native line 14 is `functions.exec` as a `custom_tool_call`, including an actual `exec_command` reading `.agents/skills/retro/SKILL.md` and `.agents/skills/writing-for-agents/SKILL.md`. The latter was genuinely loaded, not inferred from the skill's dependency text. This Codex runtime used file reads; no Claude-style `Skill` tool invocation is claimed.
- The agent parsed the actual normal session's native records, inspected project checks and Git hook/CI configuration, ran the adapter policy check, and ran **17 existing unit tests**, all passing.
- It ranked two recommendations: automate the already documented regression checks through CI, and use a targeted literal README search for tiny edits. It explicitly recognized that the original edit succeeded and received appropriate verification.
- It recommended keeping the working direct-edit route. There was no mandatory task, new methodology artifact, or added repository rule.
- It did **not** invoke `trellis-update-spec` or edit `.trellis/spec/`. That is appropriate here: the requested result was suggestions, the observed opportunities concern environment/check wiring and tool economy, and no newly established engineering contract required preservation. No artificial lesson was manufactured to force a spec update. These recommendations remain unimplemented; neither requires retro to become an implementation stage.

Retrospective cost: **21 completed shell commands**, **135,859 output characters / 135,895 UTF-8 bytes**, **312,011 cumulative input tokens** (265,728 cached), **3,324 output tokens**. It read a large native transcript and inspected existing checks, so its overhead exceeded that of the small edit. This is evidence for keeping retro on demand; it is not evidence that every successful typo fix benefits from an automatic retrospective. The final recommendation's approximately 2,569-token README figure is a character/4 estimate.

## Final filesystem audit and limits

After both runs, fixture `git status --porcelain` was exactly ` M README.md`; the fixture HEAD was unchanged and there were no task directories. The only diff remains the normal request's single appended sentence. Retro left source unchanged. Hash inventories remained identical for **103 fixture Claude files** and **104 root Claude files**; the root's extra local file was not copied into the fixture. No root source/task/configuration was changed by these runs.

These two runs validate small normal work and a real requested retro with its writing dependency. They do not establish automatic retro triggering, an executed update-spec phase, native hook trust, or Claude harness compatibility. The integration's other delivery/delegation/resume experiments are recorded separately.

Raw temporary evidence:

- `/tmp/trellis-normal-final.{jsonl,stderr,txt}` and `...-prompt.txt`
- `/tmp/trellis-retro-final.{jsonl,stderr,txt}` and `...-prompt.txt`
- `/tmp/trellis-normal-retro-state.json` (fixture identities, source hashes, native paths and metric audit)

Native transcripts were inspected locally, not copied into automatically loaded guidance. This document contains sanitized observations only.

## Post-retro targeted-read regression

The coordinator adopted one bounded suggestion by changing the Phase Index small-work line to prefer `rg`, matching context, and no full-guide reads. CI wiring remained a recommendation; no artificial spec update was added. Only current README and workflow were recopied into the same disposable fixture, then committed as a new fixture-only baseline (`f4b8bb6ce891d24d693a6671d10371504097418d`). A fresh Codex session received the **identical ordinary normal request**, with no optimization instructions or stage reminders. Retro was not rerun.

Thread `01a0eeca-119c-7830-8df2-352c52d3dfd1`; native transcript: `~/.codex/sessions/2026/09/29/rollout-2026-09-29T13-10-15-01a0eeca-119c-7830-8df2-352c52d3dfd1.jsonl`.

Observed result: correct README-only sentence, `git diff --check` passed, zero user questions/tasks/commits. However, the agent still read the **entire README** using `cat README.md`, initiated together with start-skill and phase-index reads. It had not yet consumed the targeted-read instruction when it selected that read. Therefore this workflow-line change **did not demonstrate further loaded-context reduction** in the actual regression. Do not report its expected saving as an observed result.

| Metric | Before targeted-read line | After targeted-read line |
|---|---:|---:|
| Completed shell commands | 5 | 4 |
| Shell output characters | 13,877 | 13,742 |
| Shell output UTF-8 bytes | 13,877 | 13,742 |
| Cumulative input tokens | 76,151 | 58,115 |
| Cached input tokens | 54,912 | 36,992 |
| Output tokens | 426 | 522 |
| Avoidable user interruptions | 0 | 0 |

README was also refreshed from the current checkout for this third run (10,752 bytes), so the counts are a before/after observation, not a controlled estimate of the one-line instruction's causal effect. Both current runs remain much smaller in explicit shell output than the original 65,569-character baseline. Their cumulative token usage varies with turn layout and caching and is not a measurement of unique context.

Post-run audit: only README is modified; fixture HEAD still equals the new fixture baseline, and no task was created. The earlier two-run unchanged-HEAD audit refers to their original baseline, before this explicitly authorized fixture setup commit. Raw third-run evidence is `/tmp/trellis-normal-targeted.{jsonl,stderr,txt}`; updated measurements and exact native path are in `/tmp/trellis-normal-retro-state.json`.

## Loading-order correction: always-loaded literal-read pointer

The workflow-only attempt above exposed a loading-order problem: the model selected broad reads before receiving the on-demand instruction. The coordinator restored the Phase Index to **1,337 characters** and placed the targeted literal-edit pointer in always-loaded AGENTS instead. No skill methodology, global setting or runtime permission control changed.

Only current AGENTS, workflow and README were copied into the disposable fixture, replacing the preceding fixture-owned README edit. New fixture baseline: `c722c8c1856f8c8ccc8f21ec83927a8faff5fda2`. Fresh thread `01a0eecb-9808-7f20-885c-57a22f311587` again received the **identical ordinary spelling request** without optimization instructions or reminders. Native transcript: `~/.codex/sessions/2026/09/29/rollout-2026-09-29T13-11-55-01a0eecb-9808-7f20-885c-57a22f311587.jsonl`.

**Observed: the targeted read occurred.** The agent ran `rg -n -F 'automaticaly' README.md`; its exit 1 and empty output mean the expected no-match result, not a failed task. It then read only the last 25 lines, loaded the compact phase index, appended the exact sentence, and checked both whitespace and the focused diff. No full README, full workflow, or start-skill body was read in this run. There were zero task creations, human questions, handoffs, or agent-created commits.

| Terminal command | Output characters / UTF-8 bytes |
|---|---:|
| Literal `rg` search | 0 |
| `tail -n 25 README.md` | 1,355 |
| Compact phase index | 1,337 |
| `git diff --check -- README.md` | 0 |
| Focused README diff | 363 |
| **Total** | **3,055** |

This is **95.3% less terminal output than the original 65,569-character baseline**, and 78.0% less than the first integrated 13,877-character run. The full README now contained 10,752 bytes, so the improvement is observed selection of a smaller read, not a shorter target file. No unique-context or latency reduction is inferred solely from those output counts.

The runtime reported 53,245 cumulative input tokens (41,856 cached) and 340 output tokens. That is a 44.6% cumulative-input reduction from the original 96,186-token baseline in this pair of runs; turn layout and caching still prevent treating it as unique context size. The five completed command records include the expected no-match search.

The source audit again found exactly ` M README.md`, unchanged fixture HEAD relative to this new baseline, no tasks, and unchanged fixture Claude hashes. Raw evidence: `/tmp/trellis-normal-pointer.{jsonl,stderr,txt}` plus the updated state audit. This successful loading-order correction receives credit independently of the failed workflow-only attempt; no further retro or spec update was forced.
