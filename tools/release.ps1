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

param([switch]$DryRun)

$ErrorActionPreference = "Stop"
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

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "Git is not installed, or not on PATH. Get it from https://git-scm.com/download/win"
}
if (-not (Test-Path (Join-Path $root ".git"))) {
    Fail "Not a git repository yet - run tools\first-push.bat."
}

# Releasing on top of unsaved work would leave those changes out of the build,
# which is a confusing way to lose one.
git diff --quiet
$dirty = $LASTEXITCODE -ne 0
git diff --cached --quiet
if ($dirty -or $LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "You have changes that have not been sent yet:" -ForegroundColor Yellow
    Write-Host ""
    git status --short
    Write-Host ""
    Fail "Run tools\push.bat first, then come back."
}

# The version is in double quotes - matching on single ones is what made this
# print "=" instead of a version number.
$text = Get-Content $initPath -Raw
$match = [regex]::Match($text, '__version__\s*=\s*"([^"]+)"')
if (-not $match.Success) { Fail "Could not find __version__ in $initPath" }
$current = $match.Groups[1].Value

Write-Host ""
Write-Host "Current version: $current" -ForegroundColor Cyan
$next = (Read-Host "New version (e.g. 0.2.0)").Trim().TrimStart("v", "V")
if (-not $next) { Fail "Nothing entered - stopping." }
if ($next -notmatch '^\d+\.\d+(\.\d+)?$') {
    Fail "'$next' isn't a version number. Use something like 0.2.0."
}

# A tag that already exists would be rejected by the push, after the commit
# has been made - easier to catch now. Re-releasing the current version is
# fine as long as it was never tagged, which is the case for the first one.
git rev-parse -q --verify "refs/tags/v$next" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Fail "Version v$next has already been released." }

Write-Host ""
Write-Host "This will publish v$next and offer it to everyone running RomSrx." -ForegroundColor Yellow
if ($DryRun) { Write-Host "(dry run - nothing will actually change)" -ForegroundColor DarkGray }
if ((Read-Host "Type yes to continue") -ne "yes") {
    Write-Host "Stopped. Nothing was changed."
    exit 0
}

if ($next -ne $current) {
    if ($DryRun) {
        Write-Host "  would: set __version__ to $next" -ForegroundColor DarkGray
    } else {
        $updated = [regex]::Replace($text, '__version__\s*=\s*"[^"]+"', "__version__ = `"$next`"")
        Set-Content -Path $initPath -Value $updated -NoNewline -Encoding utf8
    }
    Run "commit the version bump" { git add romsrx/__init__.py; git commit -m "Release v$next" }
} else {
    Write-Host "Version is already $next - tagging the current commit." -ForegroundColor DarkGray
}

Run "tag v$next"        { git tag "v$next" }
Run "push commits"      { git push }
Run "push the tag"      { git push origin "v$next" }

Write-Host ""
Write-Host "Tagged v$next and pushed." -ForegroundColor Green
Write-Host "GitHub is building it now - about five minutes:"
Write-Host "  $repoUrl/actions"
Write-Host ""
Write-Host "When it finishes the release appears here:"
Write-Host "  $repoUrl/releases"
