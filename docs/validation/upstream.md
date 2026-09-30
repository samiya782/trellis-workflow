# Upstream and Codex compatibility evidence — 2026-09-29

Research owner: upstream subagent. Research clones stayed under `/tmp`; this report was copied into the repository after the read-only research phase. No global settings, reference projects, commits, or network publication changed. This report records observed source/document facts and proposals separately from runtime validation. The same subagent subsequently implemented the metadata adapter and its isolated unit tests.

## Pinned sources

| Source | Revision / version | Local evidence |
| --- | --- | --- |
| Matt skills current HEAD | `d81f3a183412e71a5b1e84ca21bc1a35eea03a60` (2026-09-29, release v1.3 merge) | `/tmp/trellis-upstream-matt` |
| OMC current HEAD | `9fd35ece5d6de65b511bf43b55e42c499e4fc194` (2026-09-22) | `/tmp/trellis-upstream-omc` |
| Installed Codex CLI | `codex-cli 0.159.0` (executed `codex --version`) | official source tag `rust-v0.159.0`, SHA `377f7f557a6bdea0f3a2d26d4d899c66db4789d0` |
| Codex current HEAD | `193632d2448f6b0e9860faab8d6495124e266772` | `/tmp/trellis-upstream-codex`; relevant parser/loader/model/provider files byte-identical to installed-version tag |
| Official skill docs | fetched 2026-09-29 | `https://developers.openai.com/codex/skills/` redirects to `https://learn.chatgpt.com/docs/build-skills`; local markdown `/tmp/trellis-official-skills.txt` |
| Official delegation docs | fetched 2026-09-29 | `https://developers.openai.com/codex/multi-agent/` redirects to `https://learn.chatgpt.com/docs/agent-configuration/subagents`; local markdown `/tmp/trellis-official-subagents.md` |

Immutable source links:
- Matt: https://github.com/mattpocock/skills/tree/d81f3a183412e71a5b1e84ca21bc1a35eea03a60
- OMC: https://github.com/Yeachan-Heo/oh-my-claudecode/tree/9fd35ece5d6de65b511bf43b55e42c499e4fc194
- Codex: https://github.com/openai/codex/tree/377f7f557a6bdea0f3a2d26d4d899c66db4789d0

## Local versus current Matt source

Compared each entire installed `.claude/skills/<name>/SKILL.md` and `agents/openai.yaml` against current upstream, not merely lock entries.

| Skill | Body identical | Metadata identical | Current path / note |
| --- | --- | --- | --- |
| grill-with-docs | yes | yes | `skills/engineering/grill-with-docs` |
| wayfinder | yes | yes | `skills/engineering/wayfinder` |
| to-spec | yes | yes | `skills/engineering/to-spec` |
| to-tickets | yes | yes | `skills/engineering/to-tickets` |
| implement | yes | yes | `skills/engineering/implement` |
| code-review | yes | yes | `skills/engineering/code-review` |
| retro | yes | yes | moved from lock's `skills/in-progress/retro` to `skills/engineering/retro` |
| writing-for-agents | yes | yes | `skills/productivity/writing-for-agents` |
| implement-spec | **no** | **no** | moved from `skills/in-progress/implement-spec` to `skills/engineering/implement-spec` |

`skills-lock.json` uses per-skill computed hashes and source paths; it does not give a single immutable upstream commit. The moved `retro` path is stale but its installed body is current. The installed `implement-spec` requires creating a draft PR immediately; current upstream makes PR conditional on tracker/user requirements, creates it after the first merge, and otherwise supports local ticket closure. Current upstream still expects per-ticket worktrees, an integration branch, TDD, merge subagents, and final review. Excluding it from a minimal adapter is a scope decision, not evidence that the current upstream requires pushing.

## Codex policy is distinct from Claude policy

Official docs establish repository `.agents/skills` discovery, explicit `$skill` invocation, implicit matching by description, progressive loading of full bodies, and `agents/openai.yaml`'s `policy.allow_implicit_invocation` setting (true by default). False disables implicit matching; it does not disable explicit use. The initial catalog has a documented context budget. Symlinked skill directories are supported. These are authoring/discovery controls, not runtime filesystem or network permissions.

The installed-version source settles the frontmatter ambiguity:
- `codex-rs/skills/src/parser.rs:7`: `SkillFrontmatter` parses name, description, and metadata; it has no `disable-model-invocation` field and no `deny_unknown_fields` attribute. Claude's field is ignored by this parser.
- `codex-rs/skills/src/model.rs:23`: `allows_implicit_invocation` reads policy from metadata and defaults true.
- `codex-rs/ext/skills/src/provider/host.rs:148`: false policy hides the skill from the model-facing catalog.
- `codex-rs/ext/skills/src/loader/metadata.rs:53`: policy is read from `agents/openai.yaml`.

The relevant four parser/model/host-loader/provider files are byte-identical between the installed tag and fetched current HEAD. This is source verification, not proof that every app host runs that CLI build.

Installed Matt entries `grill-with-docs`, `wayfinder`, `to-spec`, `to-tickets`, `implement`, and `retro` set false in OpenAI metadata. `code-review`, `tdd`, `grilling`, `domain-modeling`, `research`, and `writing-for-agents` do not. Reading an arbitrary file is not evidence of catalog discovery; fresh-session catalog and load evidence remain necessary.

### Minimum supported reversible adaptation

Install complete authentic skills into independent `.agents/skills/<name>` directories using the supported installer, pin source, preserve SKILL.md and supporting resources, and override only Codex metadata for selected automatic downstream stages. Keep entry skills explicit-only. Retain `.claude` skill directories and metadata unchanged. Record the adaptation so reinstall/update can deterministically reapply or remove it. Scope-gating belongs in the project continuation workflow; globally exposing downstream names must not silently select Matt for normal work.

**Avoid a SKILL.md-only symlink with separate local metadata.** The installed-version host loader canonicalizes the skill path (`host.rs:195`), then finds `agents/openai.yaml` beside the canonical path (`host.rs:353`). A `.agents` SKILL.md link to `.claude` therefore reads `.claude` policy, defeating the separate override. Full directory symlinks similarly share metadata. Independent copies spend disk/source duplication but prevent cross-platform metadata coupling and are the supported editable-install shape. Directory symlinks can be appropriate for skills whose metadata needs no override, but mixing installation layouts adds maintenance complexity.

The Matt README explicitly describes skills.sh installs as editable copies. Changing platform metadata while preserving complete original skills is an adaptation of real skills, not replacement methodology. Do not weaken runtime permission settings to obtain continuation.

## Where interruptions actually originate in skill source

| Point | Source behavior | Appropriate integration treatment |
| --- | --- | --- |
| Entry | grill-with-docs invokes real grilling + domain-modeling | Explicit user choice; ensure dependencies installed/read |
| to-spec | synthesize existing conversation, confirm test seams | Reuse settled seam decision; ask only unresolved material seam questions |
| to-tickets | quiz granularity/blocking edges until approval | Existing authorization can cover a previously settled graph; do not fabricate human answers |
| implement | use TDD where possible, run checks, call code-review, then commit | Explicit scope and commit authorization need carrying into the skill |
| code-review | asks for fixed point if absent; asks for spec if unfound | Coordinator supplies pinned base + exact complete spec paths |
| retro | suggests environment improvements from actual session sources | Examine evidence; findings can be empty; adoption is a separate authorized action |
| wayfinder | planning by default, charting ends a session, at most one nonresearch decision per session | Preserve HITL boundaries and multi-session semantics; transition into authorized delivery when planning is complete, not a fake autonomous interview |

The existing publication backend additionally requires separate human activation, manual frontier-child choice, explicit implement re-invocation after review failure, and repeated completion approval. Those are local workflow choices, not Codex platform requirements. They are direct candidates for scoped standing authorization and automatic continuation.

## Review and commit ordering

Actual upstream `code-review` captures `git diff <fixed-point>...HEAD` plus `git log <fixed-point>..HEAD`. Both are commit-oriented. Its description mentions work-in-progress, but implementation rejects an empty committed diff and does not inspect uncommitted edits. Actual upstream `implement` calls review before committing. Therefore a fresh uncommitted implementation can be absent from the required review input. This is a verified source incompatibility; the parent should experimentally demonstrate it in a disposable fixture.

Minimal options to validate:
1. With commit authorization, make a local checkpoint first, run genuine review with an explicit base and spec, repair, recheck affected behavior, then review new committed changes and finish authorized closeout.
2. Without commit authorization, collect uncommitted diff explicitly as a documented adapter override; this changes review input semantics and must be labeled. Do not claim a successful upstream HEAD comparison covered the working tree.

Avoid duplicated generic review: Matt supplies Standards/Spec analysis; Trellis supplies relevant executable checks and required project contracts. Have one coordinator combine findings, bound repair attempts, and rerun checks affected by repairs. Preserve the distinct Standards/Spec output axes required by Matt.

## Retro and update-spec

The real retro loads `writing-for-agents`, reads primary session evidence, and proposes improvements in environment/navigation/checks/standards/tool use. It recommends deterministic checks for mechanical mistakes and reserves human-readable standards for judgment. It does not require inventing a lesson or modifying specs.

Trellis `trellis-update-spec` captures reusable implementation contracts and conventions. The useful relationship is conditional: a retro finding about an undocumented durable contract can trigger update-spec; a mechanical mistake can instead become a regression check; no meaningful finding means neither artificial document nor extra approval. Running both mechanically after every ticket duplicates analysis/context.

## OMC lessons, not a dependency

`skills/autopilot/SKILL.md` and `src/hooks/autopilot/enforcement.ts` implement bounded continuation. QA has a cycle cap and repeated-error stop; validation fixes and retries have a cap; cancellation preserves recoverable state. The source distinguishes stage evidence from merely receiving an output, binds state to an owner session, and guards transitions. Existing validated plans can bypass expansion/planning.

`skills/team/SKILL.md` coordinates a ready frontier, file/module ownership, dependencies, review/fix loops, resume, and lead-assigned owners because its task surface does not provide atomic claiming. It gives one primary loop authority, persists lightweight handoffs, and refuses corrupt/ambiguous state. These principles transfer cleanly: main coordinator is the sole task-lifecycle writer; workers own disjoint implementation files; integration starts only after blockers pass. Completion and reviewer events are evidence inputs, not permission to mutate shared state from every worker.

Its actual team APIs are Claude-specific (implicit teams, Agent/Task, team task surface, environment flags); its stop enforcement is hook/runtime code. They are not evidence that Codex supports the same API or that copying its prose creates durable automatic continuation. No OMC runtime was executed here.

## Native delegation observations and limits

This researcher is a real child spawned by the parent via this runtime's `collaboration.spawn_agent`, with shared filesystem and native `send_message` communication. The runtime exposes create/followup/message/wait/interrupt/list collaboration tools; no Claude Skill tool is present. Child saw the supplied project skill catalog and developer bootstrap, read trellis-start itself, and invoked shell/web tools normally. This is real delegated research, not proof of fresh-session native task JSONL injection or of concurrent implementation.

Official delegation docs say applicable project/skill instructions or direct requests can authorize delegation, custom agents live in `.codex/agents`, children inherit runtime sandbox/approval choices, and unavailable noninteractive approvals fail back to the coordinator. Actual tool presence and observed child events are stronger runtime evidence than stale feature-flag recipes. This run's parent/children share files; task-state coordination must be explicit. The user already requested parallel agent work here.

Remaining validation: fresh ordinary Codex requests, catalog visibility after metadata adaptation, actual skill body reads/dependency loads, uninterrupted scope-to-delivery, two concurrent workers plus dependent integration, repair/recheck bounds, resume state, disposable commit/archive ordering, context bytes/tokens, and interruption count. No claims of those successes are made by this research report.
