# Fresh Codex baseline evidence

## Scope and isolation

Baseline source: git HEAD ca67648 (Trellis 0.7.0-beta.4 committed installation). Disposable git archive fixtures under /tmp, local git author, no remotes/pushes, no root changes. Runtime codex-cli 0.159.0, global selected model gpt-6-astra, --sandbox workspace-write, no permission/hook bypass flags and no global settings changes. Date 2026-09-29.

Fixtures:
- /tmp/trellis-matt-baseline-106pzk51
- /tmp/trellis-matt-stage-boundary-iu8xc0yy

Commands use codex exec --sandbox workspace-write --cd FIXTURE --json --color never --output-last-message FINAL PROMPT, stdout to JSONL and stderr separately. Linked variants add per-invocation -c 'projects."FIXTURE".trust_level="trusted"'. This does not trust copied hooks. Linked fixture uses .agents/skills/<name> symlinks to complete unchanged .claude/skills/<name> copies from HEAD. No metadata override. Initial archive omitted ignored .trellis/.developer; linked runs initialized local developer fixture before execution.

## Observed tests

| Test | Thread | Result |
|---|---|---|
| Normal small README request | 01a0ee1a-64a3-7e00-9cdd-26318a24a2e9 | Requested direct edit completed; diff check; no task/commit/interruption. |
| Explicit Matt entry, no Codex source installed | 01a0ee1a-c88a-7ec2-95e8-809833a17fe2 | Stopped: skill missing/undiscoverable. No implementation. |
| Same entry with project symlinks | 01a0ee1b-d83e-7c33-9ea0-ecaa9c50ac80 | Genuine grill-with-docs skill expansion + reads grilling/domain-modeling; one optional validation question. Subsequently silently selected Trellis with Matt discovery, so implementation is NOT evidence of automatic Matt delivery. Completed 6 tests, glossary and no-commit archive. Cumulative input tokens 743,127 (677,504 cached), output 6,238. This successful code delivery is still not Matt-route delivery. |
| Explicit two-agent read-only runtime probe | 01a0ee1c-542d-72c0-9b0a-0815a53db40b | Two actual spawn_agent calls, both completed, results integrated. |

Normal prompt: Fix the spelling of automaticaly to automatically if present in README.md. If it is absent, add a single final sentence: Small changes can be checked automatically. Make this small documentation edit directly; no commit is needed.

Missing-source prompt: $grill-with-docs Add a small Python utility that returns the area of a rectangle from its width and height and rejects negative inputs. Keep the public function rectangle_area(width, height), use standard library unittest, and keep this entirely local. I authorize task creation and implementation after any material questions are settled; no commit is needed.

Linked prompt adds root geometry.py, int/float, zero allowed, ValueError negatives, tests/test_geometry.py. It did not explicitly repeat 'Matt route'; the model changed route to Trellis with explicitly invoked grill-with-docs discovery. This is a fidelity failure despite successful source loading and implementation authorization.

Runtime probe prompt: Use two agents in parallel for a read-only check: one reads README.md and reports its top heading; the other reads AGENTS.md and reports the directory containing development instructions. Do not create a task or edit files. Report each agent result.

## Actual parallel evidence

Native transcripts contain spawn_agent calls (CLI JSONL itself omits those and only emits collab waits). Two child session_meta records name parent 01a0ee1c-542d-72c0-9b0a-0815a53db40b:
- /root/read_readme, child 01a0ee1c-791a-7c93-97b2-c5bb78b0711d: start 17:00:38.559Z, end 17:00:48.900Z.
- /root/read_agents, child 01a0ee1c-8904-7be0-b552-24af028b30d7: start 17:00:42.632Z, end 17:00:56.026Z.
- Execution lifetime overlap 6.268 seconds. Their shell calls did not overlap; these were concurrent independent agents, not a parallel build benchmark.

Native transcripts are ~/.codex/sessions/2026/09/29/rollout-<time>-<thread>.jsonl. Dispatch prompt text is encrypted by runtime; evidence should cite callable name/result and child provenance, not reproduce ciphertext.

## Context and interruption measurements

Baseline workflow 24,133 characters / 415 lines / ~6,033 tokens using chars/4 ESTIMATE. README before normal addition 33,290 characters (post-addition 33,335). Phase index actually loaded 5,923 characters (~1,481 tokens ESTIMATE). start skill 2,824 chars; before-dev 2,638.

Normal run read workflow + README in a single 57,423-character shell output and 65,569 total shell output characters across seven commands. Avoidable user interruptions 0. CLI reports cumulative input_tokens 96,186, cached_input_tokens 68,352, output_tokens 593. These are cumulative billed/request usage across turns, NOT unique prompt/context size.

Missing-source run total shell outputs 63,080 chars across six commands. One blocking response (installation/discovery). Cumulative input_tokens 112,191; cached 83,584; output 1,284.

No workflow-state/bootstrap hook injection appeared in native developer messages in original untrusted or per-invocation-trusted linked fixtures. The linked explicit disabled skill appeared as a separate user skill-expansion message (382 chars), not in ordinary catalog. Before links, initial skill-bearing developer block was 9,741 chars; after linking all installed Matt skills, 13,657 chars (+3,916), with only implicitly invocable skill entries included in normal catalog. Catalog size is distinct from actual file reads.

## Runtime limitations independently observed

codex features list on 0.159.0 reports hooks stable true, multi_agent stable true, multi_agent_v2 stable false. Project comments requiring global hook enablement are stale for this version. Project trust and individual hook trust remain separate: copied hooks did not inject context without bypasses. Ordinary task behavior therefore tested child/manual loading fallback, not hook integration.

The old workflow explicitly says every grill/wayfinder/to-spec/to-tickets/implement stage is human-owned and never auto-chain. Metadata of entry and downstream stages has allow_implicit_invocation: false. These are independently inspectable policy barriers; mere workflow references do not make runtime invocation automatic.

Raw stdout/stderr/final evidence files: /tmp/trellis-matt-baseline-normal.*, /tmp/trellis-matt-baseline-matt.*, /tmp/trellis-matt-baseline-linked.*, /tmp/trellis-matt-delegation.*, /tmp/trellis-matt-boundary.*. Do not copy native full transcripts into auto-loaded guidance.

## Explicit old-route boundary reproduction

Second ordinary prompt explicitly selected the Matt route and fully settled input behavior, authorized task creation and delivery, prohibited commits. Fresh old-workflow fixture with unmodified real skill links: thread 01a0ee1f-2d5a-7bc3-8ecc-d906d9f1f75a.

Observed final: "No material questions remain"; implementation not started; demands `$to-spec .trellis/tasks/09-29-rectangle-area/discovery.md`; directly cites workflow line 124, "Present the exact next command and stop; never auto-chain them."

Classification: one avoidable workflow-stage interruption, not missing decision, permission, skill source or Codex inability. The same agent had already read real grilling/domain-modeling and created discovery artifacts. Cumulative input 352,799, cached 320,000, output 4,068. Actual resume with the demanded `$to-spec` command was run to measure the later boundary documented below.

## Review/commit ordering: real failure experiment

Thread 01a0ee21-b61f-7ef3-bd28-86431b8d5ec4 explicitly invoked real `$code-review HEAD` against already delivered but uncommitted geometry.py/tests/test_geometry.py and the archived PRD. The agent loaded the real skill, confirmed HEAD resolves, ran the prescribed `git diff HEAD...HEAD`, observed an empty diff and untracked source/tests, and stopped before review subagents. Final explicitly says no findings, edits or commits. Thus review-before-checkpoint cannot validate that implementation with this upstream skill. stdout /tmp/trellis-matt-uncommitted-review.jsonl. This is observed execution, not only reading the skill text.

## First minimal integrated fixture

/tmp/trellis-matt-integrated-1sm02trs starts from ca67648 plus changed AGENTS, workflow, matt-flow/backend docs, trellis-start/continue, 12 genuine upstream project Codex skills at d81f3a1. Only to-spec/to-tickets/implement/retro openai.yaml allow_implicit_invocation flags were changed false->true. Entry metadata remained explicit. No new hook trust. Base main plus feature/geometry branch pre-created. Root task/runtime were not copied.

Ordinary prompt: $grill-with-docs Use the Matt route to build a tiny Python rectangle toolkit. Put rectangle_area(width, height) in areas.py and rectangle_perimeter(width, height) in perimeters.py; these can be developed independently. Then add rectangle_summary(width, height) in rectangle.py returning a dict with area and perimeter by calling both helpers. Accept finite int/float dimensions, allow zero, reject either negative dimension with ValueError; other types and non-finite values are outside scope. Use standard-library unittest with separate test modules. I authorize local task creation, implementation, tests, local commits, and archival after delivery; choose routine engineering details. Work on the existing feature/geometry branch with main as its base. Keep everything local.

Fresh thread 01a0ee21-5a61-7073-97e5-5d77452e5809 loaded the real entry/grilling/domain-modeling and then to-spec/to-tickets/implement automatically without another user message. It identified no unresolved material question and created one parent and three children sequentially as coordinator. Completion is recorded in the final result below.

Actual phase-index output shrank from 5,923 to 1,337 chars (77.4%). This fixture intentionally retained old README as the minimal first edit; the agent read a 35,874-char README+index output, so workflow shrink does not alone establish reduction in total loaded context. It also read a 38,285-char combined guides/specs/review/TDD output. Record these residual loads when interpreting overall counts.

## Second baseline handoff after approval

The actual `$to-spec` resume wrote prd.md plus design.md under the old backend and asked explicit confirmation of the public-function unittest seam. Cumulative input 796,389, cached 738,688, output 9,840. The test then answered: Approved: the specification and the proposed public-function unittest seam match my expectations. Continue the authorized local delivery using the Matt route. Do not commit.

The next final published the local specification but demanded `$to-tickets trellis-task:09-29-rectangle-area` and again cited old workflow line 124. Nothing implemented or committed. Thus **two actual avoidable manual skill-command interruptions** are observed, plus **one separate upstream testing-seam confirmation**. Remaining old-stage manual commands are statically specified but not claimed as executed. The simple old and three-part new scenario differ in scope/authorization detail, so their total token counts are diagnostic, not a controlled performance benchmark.

## Integrated worker evidence (intermediate observation)

Coordinator spawned `/root/area` at 17:09:24.206Z and `/root/perimeter` at 17:09:36.491Z, both fork_turns=none. Child IDs: 01a0ee24-7e75-77a0-b853-de6a93cb7182 and 01a0ee24-ae72-7870-ac10-b231170604aa. Workers explicitly read real implement/TDD, own task JSON/PRD/implement.jsonl, parent PRD/ledger, and applicable guidelines. They are not merely role-named agents; transcript reads show the actual methodology and fallback context.

Area completed at 17:12:08.385Z with 5 tests and actual red evidence (initial missing module then seven negative-validation failures), then green; edits limited to areas.py/test_areas.py. It reported no Git/task/shared mutations. Perimeter overlapped with area for at least 151.894 seconds and shows its own red/green sequence. Coordinator has not yet begun dependent summary; helper acceptance/checkpoint is required in its ledger.

## Natural runtime pause, permission probe, fresh resume

Initial integrated thread finished implementation with all 18 tests passing, after both independent workers joined and before any committed review/archive. It attempted an exact-owned-file Git checkpoint but sandbox rejected .git/index.lock with read-only filesystem. Its compound shell command returned 0 only because final rev-parse succeeded; the agent correctly inspected unchanged HEAD, recorded no commit/review PASS, and continued remaining authorized code/checks. It recorded helper acceptance against SHA-256 working-file snapshots and kept review/closeout pending. No manual methodology handoff occurred. Cumulative coordinator input 1,509,546, cached 1,421,696, output 12,590 (workers separate; not a unique-context count).

The attempted test watcher looked for a real checkpoint and summary absent before sending SIGINT. No checkpoint existed; it timed out and sent **no signal**. The session instead ended at its actual permission boundary with durable task/authorization/evidence.

`codex exec --sandbox workspace-write` injected approval policy never. The observed Git barrier cannot be removed by workflow consent. A separate clean disposable permission probe used the supported `codex exec --approve-for-me` flag. Thread 01a0ee2a-82eb-7252-92e2-585b45695e9e created hello.txt, then invoked runtime-approved escalation for exact `git add -- hello.txt && git commit --only ... -- hello.txt`; auto_review accepted it, producing local commit f30b47db0b20220cbb5d84843ff6820567fe0666. Final checks confirmed exact bytes and only that file committed. No bypass flags, hook trust override, or global edits. Native developer instructions explicitly identify approvals_reviewer auto_review.

For resume, after all initial workers/session had finished, test setup changed areas.py from `width < 0 or height < 0` to `width < 0 and height < 0`; focused unittest failure was independently confirmed (record /tmp/trellis-matt-seeded-regression.json). An untracked unrelated-note.txt was created with recorded hash. A **fresh** Codex session then ran with --approve-for-me and this ordinary prompt:

Resume the rectangle toolkit task at .trellis/tasks/09-29-rectangle-toolkit. I changed areas.py and its negative-input tests are failing; repair that regression, then finish the previously authorized delivery. Keep unrelated-note.txt untouched and uncommitted.

No skill/stage commands or optimization instructions were in that resume prompt. Original route, scope and commit/archive authorization must be recovered from durable task artifacts. /tmp/trellis-matt-resume.* captures the completed evidence summarized below.

## Fresh-resume progress: actual repair and committed review

Fresh resume thread 01a0ee2c-d723-79e1-9842-0959d9c50a98 recovered the recorded Matt route/scope/commit/archive permission, loaded real implement and code-review, reproduced the seeded failing negative tests, restored areas.py to its previously verified SHA-256, and ran all 18 tests successfully. It independently fingerprinted unrelated-note.txt.

The guarded runtime allowed exact-owned-file checkpoint commit 03c1199, `feat: deliver rectangle toolkit with dimension validation`, with unrelated-note.txt still untracked. Real Standards and Spec reviews then ran as distinct concurrent native agents, fork_turns=none:
- Standards: 01a0ee2f-b87c-7413-9c54-7fcb1b974d6b, started 17:21:40.012Z.
- Spec: 01a0ee2f-fbc1-7df2-bc6d-02348389020c, started 17:21:57.250Z.
Coordinator subsequently reported both axes PASS, zero findings on 03c1199, and began authorized child-before-parent archival. Final verification is recorded below. No new user response was supplied in this fresh session.

## Measured skill-context tradeoff

Pure `<skills_instructions>` block lengths from native fresh-session developer messages (not estimates): baseline without Codex Matt skills 7,706 chars / 18 skill entries; old full .claude skill symlink set 11,628 chars / 34 entries; minimal genuine integrated 12-skill set with four downstream metadata changes 9,866 chars / 28 entries. Resume has the same 9,866-char skill block. Installing the required Matt set adds 2,160 chars over no-Matt baseline; it saves 1,762 chars compared with linking the entire available upstream skill collection. Permission text is excluded from these numbers. Phase index reduction 5,923→1,337 chars offsets that added capability overhead, but real skill body reads still dominate the full task context.

## Final integrated/resume result — independently checked

Fresh resume completed with no further user input, no stage-command handoff, no new approval question, 18 passing tests, real Standards PASS/0 and Spec PASS/0 on checkpoint 03c1199, and authorized local closeout commit a65c8c84b468c3325d4743780ca887d872597c4a (`chore: archive rectangle toolkit and record delivery review`). All four desired tasks archived children-first; unrelated bootstrap task untouched. Archived context pointers were repaired and all four validations passed. Session journal updated with --no-commit and included only in the authorized closeout commit. No push/merge/remote.

Independent final audit (/tmp/trellis-matt-final-audit.json) confirms: all four native states completed and delivery metadata delivered; exact publication references preserved; all JSONL context targets exist; final six Python source/test files unchanged from reviewed03c1199; areas.py matches pre-mutation SHA; unrelated-note.txt matches the injected user-file hash, is untracked and absent from commits; only that unrelated file remains in git status. Main stays at fixture baseline874fed0.

Review-agent overlap is **28.699 seconds** (Standards17:21:40.012–17:22:25.949Z; Spec17:21:57.250–17:22:47.577Z). Implementation workers overlap **151.849 seconds** using actual child start17:09:36.536 and area finish17:12:08.385; earlier dispatch-time estimate151.894 differed by45ms. Perimeter finished17:13:14.244. Dependent test_rectangle.py first edit17:14:32.528 and rectangle.py17:15:08.143, both after both helper workers and coordinator's13-test acceptance. Actual concurrently ready work is distinguished from the later sequential dependent composition.

Native runtime error evidence: at17:11:33.320 the area child delivered `Agent errored: Selected model is at capacity. Please try a different model.` Coordinator called followup_task(area) at17:11:46.226, retained its files, and received successful final at17:12:08.385 without a user command. This Codex-capacity interruption was recovered automatically.

Fresh-resume cumulative coordinator usage: input1,317,364; cached1,244,544; output9,378. Do not call that unique context or combine it with measured character reductions as a token-savings benchmark. Child calls have separate usage. One seeded repair/recheck cycle is observed; three-consecutive-failure termination was not stress-tested. Hook injection remains untested in these copied fixtures because individual hooks were unapproved; child-side explicit context loading is observed. No Claude harness was launched.

Final reusable evidence files: `/tmp/trellis-matt-baseline.md`, `/tmp/trellis-matt-baseline.evidence.json` (sanitized commands/source reads/agent records), `/tmp/trellis-matt-final-audit.json`, `/tmp/trellis-matt-seeded-regression.json`. Detailed raw fixture stdout/finals remain /tmp and native transcript IDs are recorded. No root or reference-project files were written by this tester.
