# Send your latest changes to GitHub.
#
# Run it, type what you changed, done. Nothing here creates a release - that
# is release.ps1. This just saves your work.

# "Continue", not "Stop": PowerShell 5.1 turns a native command's stderr into
# an error record, and git writes ordinary warnings there. $LASTEXITCODE is
# what decides whether something worked.
$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
$repoUrl = "https://github.com/stamp020/RomSrx"

function Fail($message) {
    Write-Host ""
    Write-Host $message -ForegroundColor Red
    exit 1
}

Set-Location $root

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "Git is not installed, or not on PATH. Get it from https://git-scm.com/download/win"
}
if (-not (Test-Path (Join-Path $root ".git"))) {
    Fail "This folder is not a git repository yet. Run tools\first-push.bat once."
}

# All of this runs before the question below. Never pipe a git command to
# Out-Null: it takes the console's stdin with it and the Read-Host that
# follows answers itself with nothing.
$outstanding = @(git status --porcelain)
$dirty = $outstanding.Count -gt 0

Write-Host ""
if ($dirty) { $outstanding | ForEach-Object { Write-Host "  $_" } }

# Committed but never pushed counts as something to send too - otherwise a
# failed push leaves work stranded with this script insisting all is well.
# `for-each-ref` is used rather than `rev-parse @{upstream}`, which writes an
# error to stderr when there is no upstream yet.
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
$upstream = (@(git for-each-ref --format='%(upstream:short)' "refs/heads/$branch") -join "").Trim()
$hasUpstream = [bool]$upstream
$ahead = 0
if ($hasUpstream) { $ahead = @(git rev-list "$upstream..HEAD").Count }

if (-not $dirty -and $ahead -eq 0 -and $hasUpstream) {
    Write-Host "Nothing to send - everything is already on GitHub." -ForegroundColor Green
    exit 0
}

if ($dirty) {
    Write-Host ""
    $message = (Read-Host "Describe what changed").Trim()
    if (-not $message) { $message = "Update" }
    git add -A
    if ($LASTEXITCODE -ne 0) { Fail "git add failed." }
    git commit -m $message
    if ($LASTEXITCODE -ne 0) { Fail "git commit failed." }
} else {
    Write-Host "$ahead commit(s) already made, not yet on GitHub." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Pushing..."
if ($hasUpstream) { git push } else { git push -u origin HEAD }
if ($LASTEXITCODE -ne 0) {
    Fail "Push failed - read the message above. Nothing was lost; your work is committed here."
}

Write-Host ""
Write-Host "Sent. $repoUrl" -ForegroundColor Green
