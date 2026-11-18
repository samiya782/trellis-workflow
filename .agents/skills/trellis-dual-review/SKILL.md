---
name: trellis-dual-review
description: "Independent dual review of a pinned git tip (usually a PR) by two reviewers: @dr eggbot and a read-only Grok CloudAgent. Use when the user asks for 双审, dual review, or a merge gate on a PR or tip."
---

# Dual review

Two independent reviewers look at the **same tip SHA**. The agent that wrote
the code does not review it. This is not Matt's `code-review` skill (Standards
vs Spec in one session). Dual review is a merge gate.

## When to use

The user asks for 双审, dual review, or a review before merge. Also use it
when a PR or tip is otherwise ready to land.

## 1. Pin the tip first

Resolve and write down:

- the PR number and URL, or "no PR yet"
- the branch name
- the **full 40-character tip SHA**
- the **full 40-character base SHA** (usually `main`)
- the implementer agent URL, if any
- the failure or change under review, with a minimal repro snippet
- the implementer's claimed root cause, labelled as something a reviewer may discard
- the project's banned items (see below)

If a ref does not resolve or the diff is empty, stop here. Do not start a review.

You can fill the two prompt files with the helper. It runs on Windows, WSL, and
Linux, and it reads and writes UTF-8:

```bash
python3 .agents/skills/trellis-dual-review/dual_review.py prepare \
  --pr <N> --url <url> --branch <branch> \
  --tip <ref-or-sha> --base main \
  --implementer <cursor.com/agents/bc-…> \
  --background "<what failed, with a minimal repro>" \
  --claimed-cause "<what the implementer says>" \
  --banned "<project banned items>"
```

On Windows, `python` or `py -3` is fine if `python3` is missing. The helper
writes three UTF-8 files under `.trellis/.runtime/dual-review/` (gitignored)
and prints their paths. Re-review of a fixed tip also takes `--prev-must "…"`.

Confirm the install with:

```bash
python3 .agents/skills/trellis-dual-review/dual_review.py verify-install .
python3 .agents/skills/trellis-dual-review/dual_review.py self-test
```

## 2. The two reviewers

- **Reviewer A: @dr eggbot** (id `aaaaa495-296c-45b3-82c2-0fa9211be10f`).
  Send the Chinese prompt with `SendToAgent`, `priority: true`. Eggbot opens
  its own read-only review (it uses Grok 4.7 xhigh) and sends the conclusion
  back.
- **Reviewer B: Grok.** Open a read-only `CloudAgent` on the same tip. Set the
  model to `grok-4.7` and the effort to `xhigh`. Do not use Auto; some regions
  reject it. The implementer agent is a third party and must not review.

If you cannot call `SendToAgent` or `CloudAgent` (Claude Code, Codex,
codefree-o, Grok Build, or any other client): run the helper, give the user
the two prompt files and the checklist, and stop. Do not claim the review
ran. Do not @-mention reviewers you cannot actually reach.

After you have dispatched both reviews, stay quiet. Do not nag. When both
conclusions are back, tell the user in one or two sentences, in their
language: whether Must was empty on both sides, the CI status if the project
has CI, and the next step.

## 3. Prompt templates

The helper fills these. If you write them by hand, keep the four rules:
write the exact tip SHA; mark the implementer's claim as dismissible; require
file or path evidence on every finding; paste the banned items into the Grok
prompt.

### Eggbot (Chinese)

```
请交叉审查 PR #<N>（独立 Must/Should，不要合、不要改代码、不要在 GitHub 留言除非发现 Must 需要钉在 PR 上）。

- PR: <url>
- 分支: <branch>
- tip: <完整 40 位 SHA>
- base: main <完整 SHA>
- 实现代理: <cursor.com/agents/bc-…>

背景：<哪次实测 FAIL / 什么现象，带最小复现片段>。实现方称根因是 <…>。请你独立核实，并按 Must / Should 回报。
```

On a re-review, add: `上次 Must 是 <X>，请核实是否修好、是否引入新问题。`

### Grok CloudAgent (English prompt, Chinese output)

```
READ-ONLY review of PR #<N> on <url>. Do not modify files, do not commit, do not push, and do not merge or comment on GitHub. If a branch is created, leave it with zero new commits.

Review tip <SHA> (branch <branch>) against base main <SHA>.

This is a generic fix for <the failure, with the minimal repro snippet>. The implementer says <claimed root cause>. Verify independently; you may discard that explanation.

Output a structured review in Chinese with:
1) exact commit reviewed
2) Must findings (ship-blocking), each with file/path evidence
3) Should findings (non-blocking), same standard
4) what looks solid
Do not implement fixes. Do not propose changing <the project's banned items>.
```

On a re-review, add that the previous Must findings were `<X>`, and ask
whether they are fixed and whether anything new appeared.

## 4. Grades

- **Must**: blocks the merge. A real regression or a missed fix, a broken
  default path, a safety or data issue, a banned-item violation, or a change
  that only hides the symptom. Every item needs evidence.
- **Should**: does not block. Park it and do not fix it in the current PR
  unless the user asks. Examples: a test-fixture gap, a corner case, a very
  long input.
- **Nice**: style, comments, small test extras. Optional.

## 5. Gate (all four, or do not merge)

1. Both reviewers report no Must findings on **the same tip**.
2. CI is green and `mergeable_state` is `clean`, when the project has CI. If
   there is no CI, say so explicitly; do not invent a status.
3. On the user's machine, in the real environment, retest the original
   failure: it is now a pass, and the default path still works.
4. Merge with squash, and only when the user has authorized that merge. A
   standing auto-loop permission is the only case where the coordinator
   merges without asking again. Soft Should findings do not block.

## 6. After a review

- If there is a Must: the implementer fixes only Must and pushes a new tip.
  **Both** reviewers re-review that new SHA. Re-run CI and the local retest.
- If there are only Should findings: do not start another review round.
  Follow the gate above. Collect Should items for a later, dedicated PR.

## Banned items

Put the project's own banned items into the Grok prompt. Read them from this
skill, `AGENTS.md`, `CLAUDE.md`, or the project docs. Do not invent any.

For the `trellis-workflow` checkout itself they include:

- do not commit or push to upstream `mindfold-ai/trellis`
- do not force-push
- do not commit `scripts/grok-fixes/trellis-grok.bak-20261028`
- do not upgrade official Trellis past `@mindfoldhq/trellis@0.7.0-beta.4`
- do not merge unless the user has authorized it
