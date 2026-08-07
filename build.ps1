# Builds dist\RomSrx\RomSrx.exe
#
# The index (romsrx.db) is deliberately NOT bundled - it is data, not code,
# and it changes every time you reindex. It gets copied next to the .exe at
# the end so the app ships ready to use.
#
# ia.ini is never bundled: credentials live in each user's own profile.
#
# Launched by double-clicking or "Run with PowerShell", the window closes the
# moment the script ends - so a failure would flash past unread. Everything is
# therefore written to build.log as well, and the window waits for a keypress
# before closing. Pass -NoPause when running it from another script.

param([switch]$NoPause, [string]$Python)

# PyInstaller writes its progress to stderr, which PowerShell turns into a
# terminating error under "Stop" - so the build is run under "Continue" and
# success is judged by the exit code instead.
$ErrorActionPreference = "Continue"
$root = $PSScriptRoot
$log = Join-Path $root "build.log"

# Whatever `python` means here, rather than one fixed path. A pinned
# C:\Python314 works on the machine it was written on and nowhere else - the
# GitHub runner installs Python under hostedtoolcache, so a hardcoded path
# fails the build before it starts. Order: -Python argument, then PATH, then
# the usual Windows install as a last resort.
if (-not $Python) {
    $onPath = Get-Command python -ErrorAction SilentlyContinue
    $Python = if ($onPath) { $onPath.Source } else { "C:\Python314\python.exe" }
}
$python = $Python

# A transcript would only catch this script's own lines - PyInstaller's output
# goes straight past it - so the log is written by hand instead.
Set-Content -Path $log -Value "RomSrx build $(Get-Date -Format s)" -Encoding utf8

function Say($message, $colour = "Gray") {
    Write-Host $message -ForegroundColor $colour
    Add-Content -Path $log -Value $message -Encoding utf8
}

function Finish($code, $message, $colour) {
    Say ""
    Say $message $colour
    Write-Host "Full output: $log" -ForegroundColor DarkGray
    if (-not $NoPause) {
        Write-Host ""
        Write-Host "Press any key to close..." -ForegroundColor DarkGray
        # Read the console directly. Read-Host goes through stdin, which the
        # PyInstaller pipeline above may have left closed - the window would
        # then shut instantly, which is the very thing this is here to stop.
        try { $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") }
        catch { try { Read-Host } catch { } }
    }
    exit $code
}

# -- checks worth making before a two-minute build ------------------------

if (-not (Test-Path $python)) {
    Finish 1 "Python not found at $python. Install Python, or point this at it: build.ps1 -Python C:\path\to\python.exe" "Red"
}
Say "Using $python" "DarkGray"

# Captured into a variable rather than redirected to the console: PowerShell
# 5.1 wraps a native command's stderr in error records, and Python's traceback
# would otherwise bury the plain-English message below.
$probe = & $python -c "import PyInstaller" 2>&1
if ($LASTEXITCODE -ne 0) {
    Finish 1 "PyInstaller isn't installed for $python. Run: `"$python`" -m pip install pyinstaller" "Red"
}

# The build wipes dist\, and Windows won't let it delete files the running app
# has open. This is the usual reason a build dies seconds after starting.
$running = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -like (Join-Path $root "dist\*") }
if ($running) {
    $ids = ($running | ForEach-Object { $_.Id }) -join ", "
    Finish 1 "RomSrx is still running (PID $ids). Close the app and run this again." "Red"
}

# -- build ----------------------------------------------------------------

Say "Building RomSrx..." "Cyan"

# PyInstaller reports progress on stderr, hence 2>&1 - which is also why the
# exit code, not $?, decides whether this worked.
#
# Each line is turned into plain text before being shown or stored. Piping
# straight to Tee-Object would write UTF-16 (it takes no -Encoding on
# PowerShell 5.1) and mangle the log, and letting the shell render the stderr
# lines itself buries each one in a block of error formatting.
$output = & $python -m PyInstaller --noconfirm --clean --onedir --windowed `
    --name RomSrx `
    --icon "$root\assets\icon.ico" `
    --add-data "$root\web;web" `
    --add-data "$root\assets;assets" `
    --add-data "$root\sources.json;." `
    --collect-all webview `
    --collect-all internetarchive `
    --collect-all py7zr `
    "$root\main.py" 2>&1 | ForEach-Object {
        $line = $_.ToString()
        Write-Host $line
        $line
    }
Add-Content -Path $log -Value $output -Encoding utf8

if ($LASTEXITCODE -ne 0) {
    Finish $LASTEXITCODE "PyInstaller failed (exit $LASTEXITCODE) - see the log for why." "Red"
}

$dist = Join-Path $root "dist\RomSrx"

if (Test-Path (Join-Path $root "romsrx.db")) {
    Copy-Item (Join-Path $root "romsrx.db") (Join-Path $dist "romsrx.db") -Force
    Say "Copied index alongside the .exe" "Green"
} else {
    Say "No romsrx.db found - the app will start empty and need an index run." "Yellow"
}

$size = (Get-ChildItem $dist -Recurse -File | Measure-Object Length -Sum).Sum / 1MB
Finish 0 ("Done: {0}\RomSrx.exe  ({1:N0} MB total)" -f $dist, $size) "Green"
