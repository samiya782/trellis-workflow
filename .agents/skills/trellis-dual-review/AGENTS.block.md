<!-- TRELLIS-GROK:DUAL-REVIEW-START -->
Before a merge, run dual review (`/trellis-dual-review`, skill
`.agents/skills/trellis-dual-review`). Two independent reviewers must both
report no Must findings on the same tip. Should findings do not block.
Do not merge unless the user has authorized it. If you cannot reach the
reviewers, write the prompts with
`python3 .agents/skills/trellis-dual-review/dual_review.py prepare` and
give them to the user.
<!-- TRELLIS-GROK:DUAL-REVIEW-END -->
