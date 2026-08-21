"""The window title and the taskbar button, used to report progress.

The app used to try to say "your download finished" with a notification. It
never worked: the window is a hosted WebView2, which has no notification
permission to grant, and asking Windows directly meant a toast filed under an
application id Windows has never been told about, which it drops in silence.
That whole path is gone.

This is the version that cannot be dropped, because it is not a message - it
is the window itself. The title says what is happening, so the taskbar tooltip
and the alt-tab list say it too, and the taskbar button fills up behind the
icon the way a browser's does. Neither needs permission, registration, or an
installer, and neither can be turned off in a settings panel three menus deep.

Two mechanisms, deliberately independent:

  * The title goes through pywebview's own `set_title`, which is a documented
    call on a documented object. It works, or the window does not exist.

  * The progress bar is ITaskbarList3, which needs a real window handle and a
    COM interface. pywebview does not hand out the handle, so it is found by
    asking Windows which top-level windows belong to this process. If any part
    of that fails the module gives up permanently and the title carries on
    alone - a decoration on the taskbar button is not worth a broken app.

Nothing Windows-specific is imported when this module is imported. That is not
tidiness: `ctypes.wintypes` raises on Linux and macOS on import, server.py
imports this unconditionally, and a previous version of exactly this mistake
stopped the app starting on every platform but one.
"""

from __future__ import annotations

import sys
import threading

# ITaskbarList3::SetProgressState flags.
TBPF_NOPROGRESS = 0x0
TBPF_INDETERMINATE = 0x1
TBPF_NORMAL = 0x2
TBPF_ERROR = 0x4
TBPF_PAUSED = 0x8

STATES = {"none": TBPF_NOPROGRESS, "working": TBPF_INDETERMINATE,
          "normal": TBPF_NORMAL, "error": TBPF_ERROR, "paused": TBPF_PAUSED}

_lock = threading.Lock()
_state: dict = {"window": None, "api": None, "hwnd": None, "dead": False,
                "title": None}


def available() -> bool:
    """Only Windows has a taskbar button to draw into."""
    return sys.platform == "win32"


def set_window(window) -> None:
    """Told about the app's own window, once, by app.py.

    Passed in rather than looked up because app.py is the only place that
    knows which of the windows on screen is the app - the side window that
    shows RetroAchievements is not it.
    """
    _state["window"] = window


# -- the title -------------------------------------------------------------

def title(text: str) -> bool:
    """Rename the window. Answers whether there was a window to rename."""
    window = _state["window"]
    if not window or not text:
        return False
    # Only when it has actually changed. The page polls every second or two
    # while a download runs, and repainting the title bar at that rate makes
    # it flicker on some themes.
    if _state["title"] == text:
        return True
    try:
        window.set_title(text)
    except Exception:  # noqa: BLE001 - a window that has gone is not an error
        return False
    _state["title"] = text
    return True


# -- the bar on the taskbar button -----------------------------------------

def _api():
    """The COM pieces, built once and only where they exist.

    All of it - the wintypes import included - would raise on a platform with
    no Win32 API, which is why none of it is at module level.
    """
    if _state["api"] or _state["dead"]:
        return _state["api"]
    if not available():
        _state["dead"] = True
        return None
    try:
        import ctypes  # noqa: PLC0415 - see the note at the top
        from ctypes import wintypes  # noqa: PLC0415

        ole32 = ctypes.WinDLL("ole32", use_last_error=True)
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        class GUID(ctypes.Structure):
            _fields_ = [("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort),
                        ("Data3", ctypes.c_ushort),
                        ("Data4", ctypes.c_ubyte * 8)]

        _state["api"] = {"ctypes": ctypes, "wintypes": wintypes,
                         "ole32": ole32, "user32": user32,
                         "kernel32": kernel32, "GUID": GUID}
    except Exception:  # noqa: BLE001 - then there is no bar, and that is all
        _state["dead"] = True
        return None
    return _state["api"]


def _guid(api, text: str):
    """A GUID from its written form, via the OS rather than by parsing it.

    CLSIDFromString is right here and a hand-rolled parser is not: the byte
    order of a GUID is not the order it is written in, and getting that subtly
    wrong produces a call that fails at run time on the user's machine rather
    than here.
    """
    out = api["GUID"]()
    if api["ole32"].CLSIDFromString(api["ctypes"].c_wchar_p(text),
                                    api["ctypes"].byref(out)) != 0:
        raise OSError("bad GUID")
    return out


def _own_window(api):
    """This process's own top-level window.

    pywebview keeps the handle to itself, and reaching into its backend for
    one would be reaching into somebody else's internals. Asking Windows which
    visible top-level window belongs to this process is the supported version
    of the same question, and it is what the taskbar itself goes by.
    """
    ctypes, wintypes = api["ctypes"], api["wintypes"]
    user32, kernel32 = api["user32"], api["kernel32"]

    # Spelled out, because the defaults are wrong in a way that fails quietly:
    # without a restype ctypes reports a handle as a signed int, so a null
    # owner comes back as 0 rather than None and every window looks owned.
    user32.GetWindow.restype = wintypes.HWND
    user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [wintypes.HWND]

    found = []
    me = kernel32.GetCurrentProcessId()
    GW_OWNER = 4

    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def visit(hwnd, _lparam):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        # Visible, ours, and a window in its own right rather than a dialog or
        # one of the invisible message-only windows a toolkit leaves lying
        # around: only the first kind gets a button on the taskbar.
        if (owner.value == me and user32.IsWindowVisible(hwnd)
                and not user32.GetWindow(hwnd, GW_OWNER)):
            found.append(hwnd)
            return False                                # stop at the first
        return True

    user32.EnumWindows(proc(visit), 0)
    return found[0] if found else None


def _taskbar(api):
    """An ITaskbarList3, initialised, or None.

    Driven through the vtable by hand rather than with comtypes: the app ships
    as a frozen bundle, and one interface with three methods is not worth
    another dependency inside it.
    """
    if _state.get("list3"):
        return _state["list3"]
    ctypes = api["ctypes"]
    CLSID_TaskbarList = _guid(api, "{56FDF344-FD6D-11d0-958A-006097C9A090}")
    IID_ITaskbarList3 = _guid(api, "{ea1afb91-9e28-4b86-90e9-9e9f8a5eefaf}")

    api["ole32"].CoInitialize(None)
    ptr = ctypes.c_void_p()
    CLSCTX_INPROC_SERVER = 1
    if api["ole32"].CoCreateInstance(ctypes.byref(CLSID_TaskbarList), None,
                                     CLSCTX_INPROC_SERVER,
                                     ctypes.byref(IID_ITaskbarList3),
                                     ctypes.byref(ptr)) != 0 or not ptr:
        raise OSError("no ITaskbarList3")

    # IUnknown's three, then ITaskbarList's four, then the ones wanted here.
    # HrInit is slot 3; SetProgressValue and SetProgressState are 9 and 10.
    vtable = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))[0]

    def method(slot, *argtypes):
        proto = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *argtypes)
        return proto(vtable[slot])

    calls = {
        "HrInit": method(3),
        "SetProgressValue": method(9, ctypes.c_void_p,
                                   ctypes.c_ulonglong, ctypes.c_ulonglong),
        "SetProgressState": method(10, ctypes.c_void_p, ctypes.c_int),
        "Release": method(2),
    }
    if calls["HrInit"](ptr) != 0:
        raise OSError("HrInit failed")
    _state["list3"] = (ptr, calls)
    return _state["list3"]


def progress(done: int = 0, total: int = 0, state: str = "normal") -> bool:
    """Fill the taskbar button, or clear it.

    `state` is one of STATES. "none" clears the bar; "working" is the striped
    one, for work whose size is not known yet.
    """
    if not available() or _state["dead"]:
        return False
    try:
        with _lock:
            api = _api()
            if not api:
                return False
            hwnd = _state["hwnd"] or _own_window(api)
            if not hwnd:
                # Not fatal and not permanent: the window may simply not be up
                # yet, and the next poll is a second away.
                return False
            _state["hwnd"] = hwnd
            ptr, calls = _taskbar(api)
            flag = STATES.get(state, TBPF_NORMAL)
            calls["SetProgressState"](ptr, hwnd, flag)
            if flag == TBPF_NORMAL and total > 0:
                calls["SetProgressValue"](ptr, hwnd, max(0, min(done, total)),
                                          total)
            return True
    except Exception:  # noqa: BLE001 - a plain taskbar button is not a failure
        # Permanently, rather than trying again every second for the life of
        # the process: whatever is wrong with COM here will still be wrong.
        _state["dead"] = True
        return False


def clear() -> None:
    """Put the button back to normal, on the way out."""
    progress(state="none")
