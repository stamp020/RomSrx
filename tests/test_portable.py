"""Code that has to import on a platform it will never run on.

Half a dozen modules here only do anything on Windows - the registry scan, the
taskbar button, the emulator hunt. That is fine. What is not fine is importing
the machinery at the top of the file, because `import winreg` and `from ctypes
import wintypes` both raise on Linux and macOS, and server.py imports its
dependencies unconditionally. One such line meant the app could not start at
all anywhere but Windows, and the Linux half of the release build went red for
two releases running before it was found.

So the rule is checked here instead of remembered: a Windows-only import goes
inside the function that needs it, where the platform has already been
established. The parse below is deliberately blunt - it looks at where the
import is written, not at what guards it - because "it is inside an if" is
exactly the reasoning that produced the outage. `if TYPE_CHECKING:` is the one
exception, since that block never runs.

The second half checks the other side of the same coin: that the parts which
are Windows-only answer politely rather than raising when they find themselves
somewhere else.

Nothing here touches the network or the disk beyond reading the source.
"""
import ast
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import taskbar  # noqa: E402

# Importing any of these on a machine without a Win32 API raises.
WINDOWS_ONLY = {"winreg", "msvcrt", "_winapi", "win32api", "win32con",
                "win32gui", "pythoncom", "comtypes"}

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


def report(label, bad, note):
    global ok, fail  # noqa: PLW0603
    if not bad:
        ok += 1
        print(f"  pass  {label}")
        return
    fail += 1
    print(f"  FAIL  {label}\n          {note}")
    for line in sorted(bad):
        print(f"            {line}")


def top_level_windows_imports(path: Path):
    """Windows-only imports written at the top level of one module."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bad = []
    for node in tree.body:                    # top level only, by construction
        stack = [node]
        # An `if TYPE_CHECKING:` block never runs, so what is in it cannot
        # raise; anything else at the top level does run on import.
        if isinstance(node, ast.If):
            text = ast.dump(node.test)
            if "TYPE_CHECKING" in text:
                continue
            stack = list(ast.walk(node))
        for item in stack:
            if isinstance(item, ast.Import):
                for alias in item.names:
                    root = alias.name.split(".")[0]
                    if root in WINDOWS_ONLY or alias.name == "ctypes.wintypes":
                        bad.append(f"{path.name}:{item.lineno}  import {alias.name}")
            elif isinstance(item, ast.ImportFrom):
                mod = item.module or ""
                if mod.split(".")[0] in WINDOWS_ONLY:
                    bad.append(f"{path.name}:{item.lineno}  from {mod} import …")
                if mod == "ctypes" and any(a.name == "wintypes"
                                           for a in item.names):
                    bad.append(f"{path.name}:{item.lineno}  "
                               "from ctypes import wintypes")
    return bad


print("what the modules import on the way in")
bad = []
for path in sorted((ROOT / "romsrx").glob("*.py")):
    bad.extend(top_level_windows_imports(path))
report("nothing Windows-only is imported at module level", bad,
       "these raise on Linux and macOS, and stop the app starting there:")

# The point of the rule, stated as the thing it protects.
print("\nand whether the package imports at all")
loaded = []
for path in sorted((ROOT / "romsrx").glob("*.py")):
    if path.stem == "__main__":
        continue
    __import__(f"romsrx.{path.stem}")
    loaded.append(path.stem)
check("every module imports", len(loaded) > 20, True)

print("\nthe Windows-only parts, told they are somewhere else")
real = taskbar.available
taskbar.available = lambda: False
taskbar._state.update({"window": None, "api": None, "hwnd": None,
                       "dead": False, "title": None})
try:
    check("the taskbar reports nothing to draw on", taskbar.progress(1, 2), False)
    check("...and clearing it is still safe", taskbar.clear(), None)
    check("a title with no window is refused, not fatal", taskbar.title("x"), False)
    # The COM side is asked directly, since progress() answers before it gets
    # there: this is the call that would raise if wintypes were touched.
    check("the COM side declines to build itself", taskbar._api(), None)
    check("...and does not try again every second", taskbar._state["dead"], True)
finally:
    taskbar.available = real
    taskbar._state.update({"api": None, "hwnd": None, "dead": False,
                           "title": None})

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
