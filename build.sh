#!/usr/bin/env bash
# Builds dist/RomSrx/RomSrx on Linux and macOS.
#
# The Windows equivalent is build.ps1. Two differences worth knowing:
#
#  * --add-data uses ':' here and ';' on Windows.
#  * There is no --windowed or --icon: both are Windows/macOS-only, and a
#    .ico is not a Linux icon format.
#
# pywebview is not bundled on Linux (see requirements.txt), so the app opens
# the system browser instead of a native window. That is deliberate - it keeps
# the build working on machines without WebKitGTK, the Steam Deck included.

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python="${PYTHON:-python3}"
log="$root/build.log"

say() { printf '%s\n' "$*" | tee -a "$log"; }

: > "$log"
say "RomSrx build $(date -Is)"

if ! command -v "$python" >/dev/null 2>&1; then
    say "ERROR: $python not found. Set PYTHON=/path/to/python3 and retry."
    exit 1
fi

if ! "$python" -c "import PyInstaller" >/dev/null 2>&1; then
    say "ERROR: PyInstaller not installed. Run: $python -m pip install -r requirements.txt pyinstaller"
    exit 1
fi

# tkinter is a separate package on most distributions and the folder pickers
# need it. Worth saying now rather than leaving the user with dead buttons.
if ! "$python" -c "import tkinter" >/dev/null 2>&1; then
    say "WARNING: tkinter is missing - the folder and file pickers will do"
    say "         nothing. Install it (Debian/Ubuntu: sudo apt install python3-tk)."
fi

collect=(--collect-all internetarchive --collect-all py7zr)
if "$python" -c "import webview" >/dev/null 2>&1; then
    collect+=(--collect-all webview)
    say "pywebview found - bundling the native window."
else
    say "pywebview absent - the app will open the system browser."
fi

say "Building RomSrx..."
"$python" -m PyInstaller --noconfirm --clean --onedir \
    --name RomSrx \
    --add-data "$root/web:web" \
    --add-data "$root/assets:assets" \
    --add-data "$root/sources.json:." \
    "${collect[@]}" \
    "$root/main.py" 2>&1 | tee -a "$log"

dist="$root/dist/RomSrx"

# Rename conflicting OpenSSL libraries to use system versions
# This fixes library conflicts on Steam Deck and other Linux distributions
find "$dist/_internal" -name "libcrypto.so.3" -exec mv {} {}.bak \; 2>/dev/null || true
find "$dist/_internal" -name "libssl.so.3" -exec mv {} {}.bak \; 2>/dev/null || true

if [ -f "$root/romsrx.db" ]; then
    cp "$root/romsrx.db" "$dist/romsrx.db"
    say "Copied index alongside the executable"
else
    say "No romsrx.db found - the app will start empty and need an index run."
fi

say ""
say "Done: $dist/RomSrx  ($(du -sh "$dist" | cut -f1) total)"
say "Full output: $log"
