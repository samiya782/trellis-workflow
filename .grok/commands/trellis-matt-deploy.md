# Trellis Grok Deploy

Quick-deploy the modified Trellis + Matt Grok fixes into this project.

1. Run in the project root (or pass DIR):
   `trellis-matt status`
2. Preview:
   `trellis-matt dry-run`
3. **Stop and wait for the user to confirm** before applying. Do not apply on your own.
4. Only after explicit confirmation, run:
   `trellis-matt apply`
5. Report the status output and any smoke-test summary.

If `trellis-matt` is missing, install once from the grok checkout:
`~/trellis/scripts/grok-fixes/install-shortcut.sh`

For a brand-new project use `trellis-matt init [DIR] -u <name>` instead (then Matt skills + `grok --trust`).
For a safe Trellis upgrade path use `trellis-matt update` (creates `.new`, protects `workflow.md`).
