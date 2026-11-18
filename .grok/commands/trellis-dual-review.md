# Dual Review

Independent merge-gate review of a pinned git tip. This is not Matt's
`code-review` skill. Load and follow
`.agents/skills/trellis-dual-review/SKILL.md`.

User arguments: $ARGUMENTS

## Do this

1. Pin the full 40-character tip SHA and the base SHA (usually `main`). If
   the ref is bad or the diff is empty, stop.
2. Write the two prompts with the helper (UTF-8, works on Windows, WSL, and
   Linux):

```bash
python3 .agents/skills/trellis-dual-review/dual_review.py prepare \
  --tip <ref-or-sha> --base main --pr <N> --url <url> --branch <branch> \
  --background "<failure and minimal repro>" \
  --claimed-cause "<implementer's claim, dismissible>" \
  --banned "<project banned items>"
```

   Use `python` or `py -3` if `python3` is missing.

3. If you can call `SendToAgent` and `CloudAgent`: send the Chinese eggbot
   prompt to @dr eggbot (id `aaaaa495-296c-45b3-82c2-0fa9211be10f`,
   `priority: true`), and open a read-only Grok CloudAgent with model
   `grok-4.7`, effort `xhigh` (never Auto). Stay quiet until both return.
4. If you cannot call those tools: give the user the two prompt files and
   the checklist, and stop. Do not claim the review ran.

Must findings block the merge. Should findings are recorded and left for a
later PR unless the user asks to fix them now. Merge only when both
reviewers report no Must on this same tip, CI is green (or the project has
none, said plainly), the original failure passes on the user's machine, and
the user has authorized a squash merge.
