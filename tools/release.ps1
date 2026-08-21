# Publish a new version so people can update to it.
#
# The logic lives here rather than in release.bat because it has to edit a
# file and run several commands: cmd's quoting and its ^ line continuation
# fall apart the moment either gets involved. release.bat just launches this.
#
# What happens: the version in romsrx\__init__.py is bumped, committed and
# tagged, then the tag is pushed. GitHub Actions notices the tag, builds
# Windows and Linux, and attaches both to a new release.
#
# The version and the tag must agree - that is how the app knows an update
# exists - which is why this sets both rather than trusting you to.
#
# Two rules keep the prompts working in a real console window:
#
#   * No `| Out-Null` on a git command. Piping a native command hands it the
#     console's stdin, and it does not always give it back - the next
#     Read-Host then returns nothing at all instead of waiting.
#   * No `2>$null` either. PowerShell 5.1 turns a redirected native stderr
#     into an error record, which under "Stop" ends the script - and git
#     writes ordinary warnings to stderr. Hence "Continue", with $LASTEXITCODE
#     deciding what worked, exactly as build.ps1 does.
#   * Nothing is asked once answers start being collected. Every check that
#     needs git runs before the first question.
#
# The tests run before the version is written, so a release that cannot pass
# them leaves the tree exactly as it was. -SkipTests exists for the case where
# you have just run them yourself.

param([switch]$DryRun, [switch]$SkipTests)

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
$initPath = Join-Path $root "romsrx\__init__.py"
$repoUrl = "https://github.com/stamp020/RomSrx"

function Fail($message) {
    Write-Host ""
    Write-Host $message -ForegroundColor Red
    exit 1
}

function Run($description, [scriptblock]$command) {
    if ($DryRun) { Write-Host "  would: $description" -ForegroundColor DarkGray; return }
    & $command
    if ($LASTEXITCODE -ne 0) { Fail "Failed: $description" }
}

Set-Location $root

# ---- everything that touches git happens up here, before any question ----

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "Git is not installed, or not on PATH. Get it from https://git-scm.com/download/win"
}
if (-not (Test-Path (Join-Path $root ".git"))) {
    Fail "Not a git repository yet - run tools\first-push.bat."
}

# Releasing on top of unsaved work would leave those changes out of the build,
# which is a confusing way to lose one. `status --porcelain` answers this in
# one call and, unlike `diff --quiet`, tells us *what* is outstanding.
$outstanding = @(git status --porcelain)
if ($outstanding.Count) {
    Write-Host ""
    Write-Host "You have changes that have not been sent yet:" -ForegroundColor Yellow
    Write-Host ""
    $outstanding | ForEach-Object { Write-Host "  $_" }
    Write-Host ""
    Fail "Run tools\push.bat first, then come back."
}

# Read once, compare in PowerShell later - so no git call sits between the
# two questions below.
$existingTags = @(git tag)

# The version is in double quotes; matching on single ones is what once made
# this print "=" instead of a version number.
$text = Get-Content $initPath -Raw
$match = [regex]::Match($text, '__version__\s*=\s*"([^"]+)"')
if (-not $match.Success) { Fail "Could not find __version__ in $initPath" }
$current = $match.Groups[1].Value

# ---- questions ----

Write-Host ""
Write-Host "Current version: $current" -ForegroundColor Cyan
if ($existingTags.Count) {
    Write-Host "Already released: $($existingTags -join ', ')" -ForegroundColor DarkGray
}
Write-Host ""
Write-Host "The next version will be published and offered to everyone" -ForegroundColor Yellow
Write-Host "running RomSrx. Leave it blank to stop without changing anything." -ForegroundColor Yellow
if ($DryRun) { Write-Host "(dry run - nothing will actually change)" -ForegroundColor DarkGray }
Write-Host ""

$next = (Read-Host "New version (e.g. 0.2.0)").Trim().TrimStart("v", "V")
if (-not $next) { Write-Host "Stopped. Nothing was changed."; exit 0 }
if ($next -notmatch '^\d+\.\d+(\.\d+)?$') {
    Fail "'$next' isn't a version number. Use something like 0.2.0."
}
# Re-releasing the current version is fine as long as it was never tagged,
# which is the case for the very first release.
if ($existingTags -contains "v$next") {
    Fail "Version v$next has already been released."
}

# The suite, before anything is written, committed, tagged or pushed.
#
# It was not run here at all, which is how a byte-order mark in __init__.py
# came to be tagged and pushed before anything noticed - the check that
# catches it has existed the whole time and ran for the first time in CI,
# after the release existed. A release that cannot pass its own tests should
# not become a tag somebody can download.
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "Running the tests..." -ForegroundColor DarkGray
    $python = (Get-Command py -ErrorAction SilentlyContinue)
    if ($python) { & py -3 tests/run_all.py } else { & python tests/run_all.py }
    if ($LASTEXITCODE -ne 0) {
        Fail "The tests failed. Nothing has been changed - fix them and run this again."
    }
}

$answer = (Read-Host "Publish v$next? Type yes to go ahead").Trim()
if ($answer -ne "yes") {
    Write-Host "Stopped. Nothing was changed."
    exit 0
}

# ---- doing it ----

if ($next -ne $current) {
    if ($DryRun) {
        Write-Host "  would: set __version__ to $next" -ForegroundColor DarkGray
    } else {
        $updated = [regex]::Replace($text, '__version__\s*=\s*"[^"]+"', "__version__ = `"$next`"")
        # Written through .NET rather than Set-Content, and the reason is
        # worth spelling out because it cost a release:
        #
        #   Windows PowerShell 5.1  -Encoding utf8  ->  UTF-8 WITH a BOM
        #   PowerShell 7            -Encoding utf8  ->  UTF-8 without one
        #
        # This script runs under whichever is on the machine, and under 5.1
        # every bump quietly prepended a byte-order mark to __init__.py. A BOM
        # is not whitespace to Python's parser - `ast.parse` on the file dies
        # with "invalid non-printable character U+FEFF" - so the release built,
        # was tagged, was pushed, and only then failed in CI.
        #
        # UTF8Encoding($false) means "UTF-8, no BOM" in both.
        [System.IO.File]::WriteAllText(
            $initPath, $updated, (New-Object System.Text.UTF8Encoding $false))
    }
    Run "commit the version bump" { git add romsrx/__init__.py; git commit -m "Release v$next" }
} else {
    Write-Host "Version is already $next - tagging the current commit." -ForegroundColor DarkGray
}

Run "tag v$next"   { git tag "v$next" }
Run "push commits" { git push }
Run "push the tag" { git push origin "v$next" }

Write-Host ""
Write-Host "Tagged v$next and pushed." -ForegroundColor Green
Write-Host "GitHub is building it now - about five minutes:"
Write-Host "  $repoUrl/actions"
Write-Host ""
Write-Host "When it finishes the release appears here:"
Write-Host "  $repoUrl/releases"
