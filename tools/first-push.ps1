# One-time setup: connects this folder to your GitHub repository and sends
# everything up for the first time.
#
# Before running: create the repository at https://github.com/new
#   - Name it RomSrx
#   - Leave "Add a README" and everything else UNTICKED. An empty repo is what
#     this expects; anything already in it will collide.
#
# Afterwards use push.bat for changes and release.bat for releases.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$repo = "https://github.com/stamp020/RomSrx.git"

function Fail($message) {
    Write-Host ""
    Write-Host $message -ForegroundColor Red
    exit 1
}

Set-Location $root

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "Git is not installed, or not on PATH. Get it from https://git-scm.com/download/win"
}

git remote get-url origin 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Already connected to GitHub - use push.bat instead." -ForegroundColor Yellow
    exit 0
}

Write-Host "Setting up $repo"
Write-Host ""

# Git refuses to commit without these, and the error it gives is cryptic.
$who = (git config --global user.name) 2>$null
$mail = (git config --global user.email) 2>$null
if (-not $who -or -not $mail) {
    Write-Host "Git needs to know who you are. Run these two lines, then try again:"
    Write-Host ""
    Write-Host '  git config --global user.name "Your Name"'
    Write-Host '  git config --global user.email "you@example.com"'
    Fail "Not configured."
}

if (-not (Test-Path (Join-Path $root ".git"))) { git init | Out-Null }
git branch -M main
git add -A

Write-Host ""
Write-Host "These files will be sent:"
git status --short
Write-Host ""
Write-Host "(romsrx.db, dist\ and build\ are deliberately left out - see .gitignore."
Write-Host " The index is 84 MB of data GitHub would reject anyway, and it is rebuilt"
Write-Host " with: python -m romsrx index)"
Write-Host ""

if ((Read-Host "Type yes to send this to GitHub") -ne "yes") {
    Write-Host "Stopped. Nothing was sent."
    exit 0
}

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "RomSrx"
    if ($LASTEXITCODE -ne 0) { Fail "git commit failed." }
}

git remote add origin $repo
if ($LASTEXITCODE -ne 0) { Fail "Could not add the remote." }

git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Fail @"
Push failed - read the message above.
A common one: the repository already has files in it. Either empty it on
GitHub, or run: git pull --rebase origin main
"@
}

Write-Host ""
Write-Host "Done. Your code is at https://github.com/stamp020/RomSrx" -ForegroundColor Green
Write-Host ""
Write-Host "Next: run tools\release.bat to publish the first downloadable version."
