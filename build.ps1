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

# Which interpreter to build with.
#
# Picking whatever `python` happens to mean is not enough: a Store stub, or a
# second install without pywebview, produces a build that silently loses its
# native window and opens a browser instead. So every candidate is asked what
# it actually has, and the first one carrying both PyInstaller and pywebview
# wins. A candidate with PyInstaller but no pywebview is the fallback, and it
# says so loudly rather than quietly shipping the wrong thing.
# A failed import is reported rather than swallowed. "except Exception: pass"
# could only ever produce "pywebview is not installed", which is wrong - and
# misleading - whenever it is installed but unimportable: a half-finished
# upgrade, a missing pythonnet, or an install that landed in the per-user
# site-packages while this build runs somewhere that can't see it.
function Test-Python($path) {
    if (-not $path -or -not (Test-Path $path)) { return $null }

    # Written to a file rather than handed to `python -c`. A multi-line program
    # on the command line has to survive PowerShell's native-argument quoting,
    # which eats embedded quotes and leading indentation - turning the probe
    # into a SyntaxError that looks, from out here, exactly like a missing
    # package. Running a file has no such hazard, and it also keeps the project
    # folder off sys.path so nothing there can shadow a real import.
    $probe = Join-Path ([IO.Path]::GetTempPath()) "romsrx-probe.py"
    Set-Content -Path $probe -Encoding ascii -Value @'
import PyInstaller
print("pyi")
try:
    import webview
    print("webview " + webview.__file__)
except Exception as exc:
    print("webview-failed %s: %s" % (type(exc).__name__, exc))
'@
    $out = & $path $probe 2>&1
    $code = $LASTEXITCODE
    Remove-Item $probe -ErrorAction SilentlyContinue
    if ($code -ne 0) { return $null }

    $text = ($out | ForEach-Object { "$_" }) -join "`n"
    $why = ""
    if ($text -match "(?m)^webview-failed (.+)$") { $why = $Matches[1] }
    return [pscustomobject]@{
        Path = $path
        Webview = $text -match "(?m)^webview "
        Why = $why
    }
}

$candidates = @()
if ($Python) { $candidates += $Python }
$onPath = Get-Command python -ErrorAction SilentlyContinue
if ($onPath) { $candidates += $onPath.Source }
$candidates += "C:\Python314\python.exe"
$launcher = Get-Command py -ErrorAction SilentlyContinue
if ($launcher) {
    $viaLauncher = & py -3 -c "import sys; print(sys.executable)" 2>$null
    if ($LASTEXITCODE -eq 0 -and $viaLauncher) { $candidates += "$viaLauncher".Trim() }
}

$found = @()
foreach ($candidate in ($candidates | Select-Object -Unique)) {
    $info = Test-Python $candidate
    if ($info) { $found += $info }
}
$chosen = ($found | Where-Object { $_.Webview } | Select-Object -First 1)
if (-not $chosen) { $chosen = ($found | Select-Object -First 1) }
$python = if ($chosen) { $chosen.Path } else { $null }

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

if (-not $python) {
    Finish 1 @"
No Python with PyInstaller was found. Install it:
    python -m pip install -r requirements.txt pyinstaller
Or point this at the right interpreter:
    build.ps1 -Python C:\path\to\python.exe
"@ "Red"
}
Say "Using $python" "DarkGray"

if (-not $chosen.Webview) {
    Say "" "Yellow"
    # "No module named 'webview'" is the only case where it really is absent.
    # Anything else means it is there and broken, and saying "not installed"
    # would send you off to reinstall something you already have.
    if ($chosen.Why -and $chosen.Why -notmatch "No module named 'webview'") {
        Say "WARNING: pywebview is installed but this interpreter cannot import it:" "Yellow"
        Say "  $($chosen.Why)" "Yellow"
    } else {
        Say "WARNING: pywebview is not installed for this interpreter." "Yellow"
    }
    Say "The app will build, but it will open in your browser instead of its" "Yellow"
    Say "own window. Fix with:  `"$python`" -m pip install -r requirements.txt" "Yellow"
    Say "" "Yellow"
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
# `clr` is pulled in by name at runtime by pywebview's Windows backend, so
# PyInstaller's import scan never sees it and leaves it out. Without it the
# window can't be created and the app quietly falls back to a browser.
$extra = @()

# What the .exe says about itself in its properties. An unsigned Windows
# binary with a completely blank version resource is one of the things
# SmartScreen and antivirus heuristics weigh, because that is what a freshly
# compiled dropper looks like; a real program says its name and version. This
# does not replace signing, but it costs nothing and removes one reason to be
# suspicious. Generated so the numbers follow romsrx.__version__.
$versionFile = Join-Path $root "build\version-info.txt"
& $python (Join-Path $root "tools\version_info.py") $versionFile 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0 -and (Test-Path $versionFile)) {
    $extra += @("--version-file", $versionFile)
    Say "Stamping version info into the executable" "DarkGray"
} else {
    Say "WARNING: could not generate version info - the .exe will have blank" "Yellow"
    Say "         properties, which makes a false virus flag more likely." "Yellow"
}

& $python -c "import clr" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { $extra += @("--hidden-import", "clr") }
& $python -c "import clr_loader" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { $extra += @("--collect-all", "clr_loader") }
& $python -c "import pythonnet" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { $extra += @("--collect-all", "pythonnet") }

# --noupx is deliberate and load-bearing. PyInstaller uses UPX automatically
# whenever it finds it on PATH, and a UPX-packed executable is flagged by a
# great many antivirus engines on the packing alone - compression is what
# malware uses to hide its contents from a scanner. It saves a few MB and
# costs the download its reputation. Never worth it here.
$output = & $python -m PyInstaller --noconfirm --clean --onedir --windowed --noupx `
    --name RomSrx `
    --icon "$root\assets\icon.ico" `
    --add-data "$root\web;web" `
    --add-data "$root\assets;assets" `
    --add-data "$root\sources.json;." `
    --collect-all webview `
    --collect-all internetarchive `
    --collect-all py7zr `
    @extra `
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

# -- did we actually get what we asked for? -------------------------------
#
# PyInstaller reports success even when it has quietly dropped something it
# couldn't find. These are the pieces whose absence isn't obvious until the
# app is running, so they are checked here rather than discovered later.
$missing = @()
if (-not (Test-Path (Join-Path $dist "RomSrx.exe"))) { $missing += "RomSrx.exe" }
if (-not (Test-Path (Join-Path $dist "_internal\web\app.js"))) { $missing += "the web frontend" }
if (-not (Test-Path (Join-Path $dist "_internal\sources.json"))) { $missing += "sources.json" }
if ($missing.Count) {
    Finish 1 ("Build finished but is missing: " + ($missing -join ", ")) "Red"
}

if ($chosen.Webview -and -not (Test-Path (Join-Path $dist "_internal\webview"))) {
    Finish 1 @"
Build finished, but pywebview did not make it into the bundle - the app would
open in a browser instead of its own window. Try again; if it persists, run:
    "$python" -m pip install --force-reinstall pywebview
"@ "Red"
}
Say "Checked: executable, frontend, sources, native window support." "DarkGray"

if (Test-Path (Join-Path $root "romsrx.db")) {
    Copy-Item (Join-Path $root "romsrx.db") (Join-Path $dist "romsrx.db") -Force
    Say "Copied index alongside the .exe" "Green"
} else {
    Say "No romsrx.db found - the app will start empty and need an index run." "Yellow"
}

$size = (Get-ChildItem $dist -Recurse -File | Measure-Object Length -Sum).Sum / 1MB
Finish 0 ("Done: {0}\RomSrx.exe  ({1:N0} MB total)" -f $dist, $size) "Green"
