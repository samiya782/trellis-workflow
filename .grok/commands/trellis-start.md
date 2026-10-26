# Start Session

Grok Build does not run the `SessionStart` hook, so load the compact context
yourself. Grok does run the project's `.claude/settings.json`
`UserPromptSubmit`/`PreToolUse`/`PostToolUse` hooks, but their
`additionalContext` is not guaranteed to reach the model; treat the commands
below as the authoritative context load.

Run `python3 ./.trellis/scripts/get_context.py` for identity, active task and Git
state, then `python3 ./.trellis/scripts/get_context.py --mode phase` for this
project's authoritative routing and authorization rules. Report any full
`Trellis update available:` line verbatim.

Use an exact task path when continuing existing work; read its contract,
authorization and latest progress. Do not infer permission or next action from
status alone; a task listed as active or `in_progress` (for example the
`00-bootstrap-guidelines` task written by `trellis init`) is not a request to
work on it. No active task is normal for small settled work. Use the loaded
workflow to decide whether a task or discovery is needed.

Before coding, discover applicable spec layers with `get_context.py --mode
packages`, then use `trellis-before-dev` or a context-loaded `trellis-implement`
sub-agent (`spawn_subagent`, first prompt line `Active task: <path>`). Load step
details with `get_context.py --mode phase --step <X.Y> --platform grok` only when
needed. Do not preload the full workflow, README, every guide or validation
history.
