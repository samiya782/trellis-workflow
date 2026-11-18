# Run oneclick.sh from PowerShell. Git for Windows bash is used internally.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $here "invoke-git-bash.cmd") (Join-Path $here "oneclick.sh") @args
exit $LASTEXITCODE
