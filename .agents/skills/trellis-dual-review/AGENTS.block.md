<!-- TRELLIS-GROK:DUAL-REVIEW-START -->
Before a merge, run dual review (`/trellis-dual-review`, or Claude Code
`/trellis:dual-review`, skill `.agents/skills/trellis-dual-review`). Two
independent reviewers must both report no Must findings on the same tip.
Should findings do not block. Do not merge unless the user has authorized
a squash merge. If you cannot reach the reviewers, write the prompts with
`python3 .agents/skills/trellis-dual-review/dual_review.py prepare --tip <ref> --base <ref>`
and give them to the user.
<!-- TRELLIS-GROK:DUAL-REVIEW-END -->
