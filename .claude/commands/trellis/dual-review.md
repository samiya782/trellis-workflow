# Dual Review

Independent merge-gate review of a pinned git tip. This is not Matt's
`code-review` skill. Load and follow
`.agents/skills/trellis-dual-review/SKILL.md`.

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

3. Claude Code cannot dispatch @dr eggbot or a Grok CloudAgent. Give the
   user the two prompt files under `.trellis/.runtime/dual-review/` and the
   checklist, and stop. Do not claim the review ran.

Must findings block the merge. Should findings are recorded and left for a
later PR unless the user asks to fix them now. Merge only when both
reviewers report no Must on this same tip, CI is green (or the project has
none, said plainly), the original failure passes on the user's machine, and
the user has authorized a squash merge.
