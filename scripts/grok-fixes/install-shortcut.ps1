# Install the trellis-matt shortcut from PowerShell.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $here "invoke-git-bash.cmd") (Join-Path $here "install-shortcut.sh") @args
exit $LASTEXITCODE
