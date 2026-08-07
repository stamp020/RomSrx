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

param([switch]$NoPause)

# PyInstaller writes its progress to stderr, which PowerShell turns into a
# terminating error under "Stop" - so the build is run under "Continue" and
# success is judged by the exit code instead.
$ErrorActionPreference = "Continue"
$python = "C:\Python314\python.exe"
$root = $PSScriptRoot
$log = Join-Path $root "build.log"

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
        Write-Host "Press Enter to close..." -ForegroundColor DarkGray
        try { Read-Host | Out-Null } catch { }
    }
    exit $code
}

# -- checks worth making before a two-minute build ------------------------

if (-not (Test-Path $python)) {
    Finish 1 "Python not found at $python - edit `$python at the top of this script." "Red"
}

& $python -c "import PyInstaller" 2>$null
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
