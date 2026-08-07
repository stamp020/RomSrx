# Send your latest changes to GitHub.
#
# Run it, type what you changed, done. Nothing here creates a release - that
# is release.ps1. This just saves your work.

$ErrorActionPreference = "Stop"
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

Write-Host ""
git status --short
Write-Host ""

git diff --quiet
$dirty = $LASTEXITCODE -ne 0
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { $dirty = $true }

# Committed but never pushed counts as something to send too - otherwise a
# failed push leaves work stranded with this script insisting all is well.
git rev-parse --abbrev-ref '@{upstream}' 2>&1 | Out-Null
$hasUpstream = $LASTEXITCODE -eq 0
$ahead = 0
if ($hasUpstream) { $ahead = @(git rev-list '@{upstream}..HEAD').Count }

if (-not $dirty -and $ahead -eq 0 -and $hasUpstream) {
    Write-Host "Nothing to send - everything is already on GitHub." -ForegroundColor Green
    exit 0
}

if ($dirty) {
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
