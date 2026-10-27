# Trellis Grok Deploy

Quick-deploy the modified Trellis + Matt Grok fixes into this project.

1. Run in the project root (or pass DIR):
   `trellis-grok status`
2. Preview:
   `trellis-grok dry-run`
3. **Stop and wait for the user to confirm** before applying. Do not apply on your own.
4. Only after explicit confirmation, run:
   `trellis-grok apply`
5. Report the status output and any smoke-test summary.

If `trellis-grok` is missing, install once from the grok checkout:
`~/trellis/scripts/grok-fixes/install-shortcut.sh`

For a brand-new project use `trellis-grok init [DIR] -u <name>` instead (then Matt skills + `grok --trust`).
For a safe Trellis upgrade path use `trellis-grok update` (creates `.new`, protects `workflow.md`).
