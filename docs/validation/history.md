# Read-only cross-project history research — 2026-09-29

## Method and limits

Used the real `trellis-session-insight` skill and installed `trellis mem projects`, `list`, `search`, and `context` commands. Read narrowly selected native JSONL records to distinguish injected skill bodies, final answers, user commands, developer workflow state, and actual tool calls. All reference repositories stayed read-only; no environment files or credentials were read. During that history-research phase, only the temporary report was written; the coordinator later authorized this sanitized copy and separate runtime regression tests.

Sampled three real project histories: `/home/samiya/srd/InduPolicy`, `/home/samiya/PythonProject/srd/pfyh_ai_energy_analysis`, and `/home/samiya/srd/LHZHSQ/LHZHSQ-backend`, plus this integration repository's earlier research sessions. Native stores actually inspected were `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` and `~/.claude/projects/<encoded-project>/<uuid>.jsonl`. No new Claude harness execution occurred.

`trellis mem` warns that retained pre-compaction Codex history can contain user messages without assistant replies and some inter-agent payloads are encrypted. Child sessions can also repeat inherited user history. Thus search hit counts and numbers of stored sessions are NOT counts of user interruptions or independent executions. The observations below reference raw record line numbers where practical.

## Observed command handoffs and reasons

### InduPolicy: actual local Matt skills and publication backend

Native session `01a0c347-cda4-7bf0-ab97-b1d232207c0c`, file:
`/home/samiya/.codex/sessions/2026/09/21/rollout-2026-09-21T02-24-17-01a0c347-cda4-7bf0-ab97-b1d232207c0c.jsonl`.

- Raw line 204: assistant final answer says eight Wayfinder decision tickets are complete and the next stage is formal specification, ticketing, implementation.
- Line 211: human sends `$to-spec trellis-task:09-20-four-role-policy-match-advice-wayfinder-map`.
- Line 374: assistant final answer publishes PRD/design, reports `planning` and `matt_ready_for_agent=true`, and gives the exact next `$to-tickets trellis-task:09-21-four-role-policy-match-advice-spec` command.
- Line 381: human repeats that command. The next real skill body names `/home/samiya/srd/InduPolicy/.agents/skills/to-tickets/SKILL.md`, with upstream `disable-model-invocation: true`; this is actual project-local skill selection, not a workflow merely mentioning its name.
- Line 383: injected developer workflow state says a different historical task (`cross-repo-acceptance-performance`) is active and explicitly demands human invocation of `implement`, separate report-only checks, and a fresh explicit skill on failure. This demonstrates effective injected policy, not just unused Markdown. The instructions themselves explain stage handoffs and repair handoffs.
- Lines 401–403: proposed ten-ticket breakdown and final answer waiting for approval of granularity/blockers; line 410 human confirms. This is a substantive upstream `to-tickets` approval step, distinct from repeating a stage name.
- Line 797: ticket publication final answer identifies the first ready ticket; line 816 user separately requests execution of all ten tickets in order. No `$implement` invocation occurs at that handoff in the selected raw records; assistant then proceeds based on ordinary execution authorization (line 822).
- Line 834: assistant notices injected historical task state does not match user-selected work and chooses the explicitly requested first ticket. Resume logic must distinguish current task pointer from requested ticket and avoid workers changing the shared pointer.

Observed: three stage transitions required additional user turns in this sequence (to-spec, to-tickets, execute list), plus one material ticket-breakdown confirmation. This is NOT a claim that all three were avoidable: the retained pre-compaction history does not prove an earlier authorization covering execution. The spec→tickets turn is nevertheless a concrete command handoff without a new product decision in the assistant's final answer.

Durable corroboration: `/home/samiya/srd/InduPolicy/.trellis/tasks/09-21-four-role-policy-match-advice-spec/task.json` contains `matt_publication_kind=spec`, `matt_publication_ref=trellis-task:09-21-four-role-policy-match-advice-spec`, `matt_spec_artifacts=prd.md,design.md`, `matt_ready_for_agent=true`, `planning_route=Matt-Skills`, and the child ticket list. Current task status is completed; the old transcript truthfully captured its earlier planning state. These metadata are publication/lifecycle evidence, not proof that every acceptance criterion passed.

### PythonProject energy: Codex already can continue after bounded authorization

Native session `019facca-e955-78e0-907c-96283b537617`, file:
`/home/samiya/.codex/sessions/2026/07/29/rollout-2026-07-29T00-33-27-019facca-e955-78e0-907c-96283b537617.jsonl`.

`trellis mem context <id> --grep autopilot --turns 4 --around 1 --max-chars 14000` exposed:

- Turn 419: user explicitly chooses `$grill-with-docs` for two sortable report columns, asking to execute automatically once boundaries are settled.
- Turn 420: native supplied skill body is real but resolves to global `/home/samiya/.codex/skills/skills/skills/engineering/grill-with-docs/SKILL.md`, NOT this project's local integration.
- Turn 444: assistant summarizes formula, missing values, sort order, tree preservation, mobile behavior and snapshot origin; asks final understanding confirmation. It explicitly says no ADR is warranted for a reversible local interaction rule, but updates the glossary.
- Turn 445: user confirms and authorizes automatic execution.
- Turn 446: assistant begins implementation, code review and end-to-end QA, without requiring `$to-spec`, `$to-tickets`, `$implement` manual commands.
- The same session's native records contain actual tool invocations: 44 `spawn_agent`, 273 `wait_agent`, 46 `list_agents`, 43 `send_message`, 18 `followup_task`. Examples: spawn lines 98, 832, 836, 846. These counts are historical runtime tool evidence, not a claim that all workers overlapped or succeeded. Many inter-agent payloads cannot be recovered.

This disproves the broad claim that Codex necessarily requires a manual command for every stage. It does NOT establish that the current Trellis+Matt local integration auto-chains every real downstream Matt skill. The historic execution used a global skill and an autopilot-style workflow, and no current tests were rerun here.

Relevant durable artifacts read: archived `.trellis/tasks/archive/2026-08/07-31-meter-load-type-tickets/prd.md` points at approved `.scratch/meter-load-type-column/spec.md` and five per-ticket files, with `Open Questions: None`. It duplicates substantial feature requirements in the Trellis PRD; canonical references can reduce this overhead. `.trellis/workspace/ycg/journal-1.md` has dated completion/commit records for Aug 5, 24 and 27. These are historical claims, not fresh quality validation.

Current energy project's `.trellis/workflow.md` still has the same hard stops: line 124 says separate human-owned boundaries and never auto-chain; lines 182/190 and 356/371 demand new explicit implement after failures. The previous successful auto-continuation therefore cannot validate that newer restrictive workflow.

### LHZHSQ: planning-only boundaries can be intentional

Read `.trellis/tasks/08-14-visit-task-backend-wayfinder/prd.md` and the developer journal. The Wayfinder map explicitly says it is planning only, forbids `task.py start` and business implementation, and terminates at implementation-ready decisions. Its seven archived decisions cover persistence, permissions, API cutover, materialization, migration, and test strategy. Here an execution stop follows a real authorization boundary and should be preserved. Do not globally treat every Wayfinder handoff as a bug.

Native Codex search also finds actual globally resolved grill skill bodies, e.g. session `019face6-76b1-78f1-89d6-ba6b9fd22234`, July 29. This corroborates historical use, not current local discovery correctness.

## Existing Claude evidence and honest limits

Inspected native Claude session `1d12cf98-b806-4dd4-8859-235c3c53cd2e` at `/home/samiya/.claude/projects/-home-samiya-srd-InduPolicy/1d12cf98-b806-4dd4-8859-235c3c53cd2e.jsonl`:

- Line 35 explicitly reports Trellis SessionStart loaded.
- Line 6986 records actual `Skill` tool invocation of `trellis-brainstorm`, after material migration/automatic-publication boundaries are settled.
- Native counts include 1,139 Bash, 77 Read, 26 Write, 7 Edit, 6 AskUserQuestion, 1 Skill calls. No native Agent invocation in this sampled main transcript; do not infer parallel Claude implementation from prose.

Energy Claude session `aa786965-f37c-431c-8d77-4c99cfedcee1`, `/home/samiya/.claude/projects/-home-samiya-PythonProject-srd-pfyh-ai-energy-analysis/aa786965-f37c-431c-8d77-4c99cfedcee1.jsonl`, reports SessionStart at line 33; native counts are 43 Bash, 3 Edit, 1 AskUserQuestion. These observations show existing Claude startup/workflow usage, not a rerun of the harness or validation of all baseline improvements.

This repository has two native Claude transcripts on Sept 29 (`d5d4076b-fe3f-4325-9dcb-46c18cc86ac2`, `869cb663-109f-4120-a98f-b9ce0d69da5b`). They contain local plugin/uninstall command interaction, no implementation or integration-validation tool evidence. They cannot substantiate a claim that Claude tested this baseline. Preserve checked-in Claude changes and distinguish source compatibility from actual runtime evidence.

## Earlier integration intent versus the new target

`trellis mem context 019ff493-cca2-7d81-b60d-3353d072195c --grep boundary ...` recovers an earlier user acceptance request that explicitly wanted each human-only Matt skill separately invoked and the workflow to stop at those boundaries. It also includes an assistant's claimed 913→415-line reduction and static parsing checks. Treat those as historical claims until independently measured; they were optimizing a different interaction contract. The present user request deliberately changes that contract after explicit Matt entry and scoped authorization.

## Current research child context observation

This default research child inherited the session's bootstrap/workflow-state developer text, including `no_task`; it did not receive a task-specific curated JSONL block. Its explicit first tool calls loaded `trellis-start`, `trellis-session-insight`, and `get_context.py`, which confirmed no selected task at that moment. It has callable collaboration spawn/followup/message tools (four total slots described), and did not spawn additional workers. This is only an observation of this default read-only child, not proof about role-specific `trellis-implement` native injection.

## Practical implications

1. Separate explicit entry choice and material decisions from stage names. Existing workflow and injected state demonstrably create manual handoffs and force new implement commands for repair.
2. Preserve planning-only scope. Existing Wayfinder maps prove automatic continuation must honor authorized destinations.
3. Permission prompts were not the cause at the evidenced spec→tickets handoff; no denied tool or runtime permission event separates the final answer and the human command.
4. Do not count inherited/compacted turns or skill-injection messages as human interruptions. Record actual ordinary prompt, material question, user answer, stage command, tool call, and runtime denial separately in fresh fixtures.
5. Prior Codex delegation exists as native tools; concurrent overlap and file ownership need fresh execution evidence, not inference from tool counts.
