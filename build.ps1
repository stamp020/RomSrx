# Builds dist\RomSrx\RomSrx.exe
#
# The index (romsrx.db) is deliberately NOT bundled - it is data, not code,
# and it changes every time you reindex. It gets copied next to the .exe at
# the end so the app ships ready to use, and the app moves it into the user
# folder the first time it runs.
#
# ia.ini is never bundled: credentials live in each user's own profile.
#
# Launched by double-clicking or "Run with PowerShell", the window closes the
# moment the script ends - so a failure would flash past unread. Everything is
# therefore written to build.log as well, and the window waits for a keypress
# before closing. Pass -NoPause when running it from another script.

# -RequireWebview turns the pywebview warning below into a refusal. Meant for
# the release workflow: a build that quietly lost its native window is a fine
# thing to sit through locally and a terrible thing to publish, and nobody
# reads a CI log that says "Done".
param([switch]$NoPause, [string]$Python, [switch]$RequireWebview)

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
try:
    import libtorrent
    print("libtorrent " + str(libtorrent.__version__))
except Exception as exc:
    print("libtorrent-failed %s: %s" % (type(exc).__name__, exc))
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
        Torrent = $text -match "(?m)^libtorrent "
        Why = $why
    }
}

# Naming one with -Python settles it. The search below is for when you
# haven't: preferring some other interpreter because it happens to have
# pywebview would quietly build with something you didn't ask for, and the
# whole point of the switch is to say which one to use.
$candidates = @()
if ($Python) {
    $candidates += $Python
} else {
    $onPath = Get-Command python -ErrorAction SilentlyContinue
    if ($onPath) { $candidates += $onPath.Source }
    $candidates += "C:\Python314\python.exe"
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        # Every interpreter the launcher knows, not just the default one.
        # `py -3` answers with whichever is default, so a second install -
        # the one put there precisely because it can host libtorrent - was
        # never even offered as a candidate, and the build kept choosing the
        # interpreter that could do less.
        $listed = & py -0p 2>$null
        if ($LASTEXITCODE -eq 0) {
            foreach ($line in $listed) {
                # Lines look like " -V:3.13          C:\path\python.exe", with
                # a * marking the default. Take the path off the end.
                if ("$line" -match '([A-Za-z]:\\[^*]+?python\.exe)\s*$') {
                    $candidates += $Matches[1].Trim()
                }
            }
        }
        $viaLauncher = & py -3 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $viaLauncher) { $candidates += "$viaLauncher".Trim() }
    }
}

$found = @()
foreach ($candidate in ($candidates | Select-Object -Unique)) {
    $info = Test-Python $candidate
    if ($info) { $found += $info }
}
# Both, then the window alone, then whatever there is. libtorrent is what
# fetches from MiNERVA, and it publishes no wheel for every Python - so on a
# machine with two interpreters the one that can do the most wins, rather
# than whichever happened to be first on PATH.
$chosen = ($found | Where-Object { $_.Webview -and $_.Torrent } | Select-Object -First 1)
if (-not $chosen) { $chosen = ($found | Where-Object { $_.Webview } | Select-Object -First 1) }
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

if (-not $chosen.Torrent) {
    Say ""
    Say "libtorrent is missing, so this build cannot fetch from MiNERVA." "Yellow"
    Say "Everything else works; MiNERVA games will offer their magnet instead." "Yellow"
    Say "It publishes no wheel for Python 3.14. To turn the feature on, install" "Yellow"
    Say "Python 3.13 alongside and give it what this app needs:" "Yellow"
    Say "    py -3.13 -m pip install -r requirements.txt pyinstaller libtorrent" "Yellow"
    Say "This script then prefers it on its own." "Yellow"
    Say ""
}

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

    if ($RequireWebview) {
        Finish 1 @"
Refusing to build: this would ship without a native window.
    "$python" -m pip install -r requirements.txt
"@ "Red"
    }
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

# -- does the frontend even parse? ----------------------------------------
#
# Before anything is bundled, because a syntax error in app.js builds
# perfectly cleanly and ships an app that opens to a blank window: the only
# check that existed was that the file is present. Skipped where Node is not
# installed - it is a convenience here, and CI checks it on both platforms.
$node = (Get-Command node -ErrorAction SilentlyContinue)
if ($node) {
    foreach ($js in Get-ChildItem (Join-Path $root "web\*.js")) {
        & node --check $js.FullName 2>&1 | Tee-Object -FilePath $log -Append
        if ($LASTEXITCODE -ne 0) {
            Finish 1 "$($js.Name) does not parse - see above." "Red"
        }
    }
    Say "Checked: the frontend parses." "DarkGray"
} else {
    Say "Node not installed, so the frontend was not syntax-checked." "DarkGray"
}

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

# The index now lives with the user's other files rather than beside the .exe,
# so that is where a built copy is taken from. Still copied into dist: a build
# handed to someone else arrives ready to use, and the app moves it into place
# the first time it starts. The old location is still checked, for a working
# copy that predates the move.
$index = Join-Path $env:APPDATA "RomSrx\romsrx.db"
if (-not (Test-Path $index)) { $index = Join-Path $root "romsrx.db" }
if (Test-Path $index) {
    Copy-Item $index (Join-Path $dist "romsrx.db") -Force
    $mb = (Get-Item $index).Length / 1MB
    Say ("Copied the index alongside the .exe ({0:N0} MB, from {1})" -f $mb, $index) "Green"
} else {
    Say "No romsrx.db found - the app will start empty and need an index run." "Yellow"
}

$size = (Get-ChildItem $dist -Recurse -File | Measure-Object Length -Sum).Sum / 1MB
Finish 0 ("Done: {0}\RomSrx.exe  ({1:N0} MB total)" -f $dist, $size) "Green"
