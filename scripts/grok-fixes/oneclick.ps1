# One-click Trellis + Matt setup for Claude Code, Codex, and Grok Build.
# Opt-in: --codefree-o and --codefree-space (CodeFree Space). They are not
# part of the no-flag default.
#
# From this checkout, in PowerShell:
#   .\oneclick.ps1 $env:USERPROFILE\my-project -u NAME --claude --codex --grok
#   .\oneclick.ps1 $env:USERPROFILE\my-project -u NAME --codefree-o --codefree-space
#
# From GitHub, with no checkout and no trellis-grok command:
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/samiya782/trellis-workflow/grok/scripts/grok-fixes/oneclick.ps1))) "$env:USERPROFILE\my-project" -u your-name --claude --codex --grok
#
# A copy run without neighboring oneclick.sh / invoke-git-bash.cmd clones
# https://github.com/samiya782/trellis-workflow branch grok, then runs that
# clone's oneclick.sh through Git for Windows bash.exe. It does not call
# C:\Windows\System32\bash.exe. Cache: TRELLIS_GROK_CLONE_DIR, or
# %LOCALAPPDATA%\trellis-grok\workflow.
# Do not add a param() block: install flags such as -u, --claude,
# --codefree-o, and --codefree-space must stay in $args. The launcher
# forwards @args to invoke-git-bash.cmd.
$ErrorActionPreference = "Stop"

function Get-ScriptHere {
    foreach ($candidate in @($PSCommandPath, $MyInvocation.MyCommand.Path, $PSScriptRoot)) {
        if (-not $candidate) { continue }
        $here = if (Test-Path -LiteralPath $candidate -PathType Container) {
            $candidate
        } else {
            Split-Path -Parent $candidate
        }
        if (
            $here -and
            (Test-Path -LiteralPath (Join-Path $here "oneclick.sh")) -and
            (Test-Path -LiteralPath (Join-Path $here "invoke-git-bash.cmd"))
        ) {
            return $here
        }
    }
    return $null
}

function Get-CloneDir {
    if ($env:TRELLIS_GROK_CLONE_DIR) {
        return $env:TRELLIS_GROK_CLONE_DIR
    }
    $base = $env:LOCALAPPDATA
    if (-not $base) {
        $base = Join-Path $env:USERPROFILE "AppData\Local"
    }
    return (Join-Path $base "trellis-grok\workflow")
}

$here = Get-ScriptHere
if (-not $here) {
    $repo = if ($env:TRELLIS_GROK_REPO) { $env:TRELLIS_GROK_REPO } else { "https://github.com/samiya782/trellis-workflow.git" }
    $branch = if ($env:TRELLIS_GROK_BRANCH) { $env:TRELLIS_GROK_BRANCH } else { "grok" }
    $dest = Get-CloneDir
    $here = Join-Path $dest "scripts\grok-fixes"
    if (-not (Test-Path -LiteralPath (Join-Path $here "trellis-grok"))) {
        if (Test-Path -LiteralPath $dest) {
            throw "error: $dest exists but has no scripts/grok-fixes/trellis-grok"
        }
        $parent = Split-Path -Parent $dest
        if ($parent -and -not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Force -Path $parent | Out-Null
        }
        Write-Host "--- clone $repo branch $branch -> $dest"
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            throw "git is not on PATH. Install Git for Windows first."
        }
        & git clone --depth 1 --branch $branch $repo $dest
        if ($LASTEXITCODE -ne 0) {
            throw "git clone failed: $LASTEXITCODE"
        }
    }
}

$launcher = Join-Path $here "invoke-git-bash.cmd"
$sh = Join-Path $here "oneclick.sh"
if (-not (Test-Path -LiteralPath $launcher)) { throw "missing $launcher" }
if (-not (Test-Path -LiteralPath $sh)) { throw "missing $sh" }
& $launcher $sh @args
exit $LASTEXITCODE
