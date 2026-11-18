# Run trellis-grok from PowerShell. Git for Windows bash is used internally.
# cmd and PowerShell can also type: trellis-grok.cmd
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $here "invoke-git-bash.cmd") (Join-Path $here "trellis-grok") @args
exit $LASTEXITCODE
