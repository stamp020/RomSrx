"""Entry point for the packaged desktop app (PyInstaller builds this).

Started with no arguments - which is how double-clicking it starts it - this
opens the app window. Started with any, it hands over to the command line, so
a packaged build can still be asked things like `RomSrx.exe checksources`
without needing Python installed.
"""

import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        from romsrx.__main__ import main
    else:
        from romsrx.app import main
    main()
