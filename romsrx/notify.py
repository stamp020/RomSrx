"""Windows notifications, sent by the app rather than by the page.

The page has always asked the browser for these, and in an ordinary browser
that works. This app is not an ordinary browser: its window is Edge WebView2
driven by pywebview, and the Notification API is one of the things a hosted
WebView does not hand out - there is no notification permission to grant,
because there is no browser chrome to grant it in. So a download finished and
nothing appeared, with no error anywhere to say why.

Windows will show one if it is asked in its own language, but which language
matters. The obvious one is the WinRT toast API, and it is the wrong one here:
a toast is filed under an AppUserModelID, Windows silently drops toasts from
an id it has never been told about, and telling it means writing a shortcut
into the Start menu at install time. Borrowing PowerShell's own id looked like
a way round that and is not - PowerShell is not registered as a notification
source either, so the call succeeds, returns nothing, and shows nothing. Which
is exactly what it did.

A tray balloon has no such problem. Windows generates an id for the icon
itself the first time it sees one - the NotifyIconGeneratedAumid entries in
the notification settings are precisely that - so it needs no registration, no
installer, and no shortcut. Modern Windows draws it as an ordinary toast.

The toast API is still tried afterwards, for the case where somebody has
registered this app properly, and the whole thing is a courtesy either way:
the page has already said the same words in its own window.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import threading
from ctypes import wintypes

from .paths import resource

_lock = threading.Lock()
_state: dict = {"hwnd": None, "icon": None, "added": False, "keep": []}

# -- the little bit of Win32 this needs ------------------------------------

NIM_ADD, NIM_MODIFY, NIM_DELETE = 0, 1, 2
NIF_ICON, NIF_TIP, NIF_INFO = 0x02, 0x04, 0x10
NIIF_INFO = 0x01
IDI_APPLICATION = 32512
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x0010


class _WNDCLASSW(ctypes.Structure):
    _fields_ = [("style", wintypes.UINT),
                ("lpfnWndProc", ctypes.c_void_p),
                ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON),
                ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
                ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR)]


class _NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("hWnd", wintypes.HWND),
                ("uID", wintypes.UINT), ("uFlags", wintypes.UINT),
                ("uCallbackMessage", wintypes.UINT), ("hIcon", wintypes.HICON),
                ("szTip", wintypes.WCHAR * 128),
                ("dwState", wintypes.DWORD), ("dwStateMask", wintypes.DWORD),
                ("szInfo", wintypes.WCHAR * 256),
                ("uVersion", wintypes.UINT),
                ("szInfoTitle", wintypes.WCHAR * 64),
                ("dwInfoFlags", wintypes.DWORD),
                ("guidItem", ctypes.c_byte * 16),
                ("hBalloonIcon", wintypes.HICON)]


def available() -> bool:
    """Only Windows has the thing this talks to."""
    return sys.platform == "win32"


def _icon(user32):
    """The app's own icon where the build carries one, Windows' default
    otherwise. A notification wearing a generic cog says nothing about who
    sent it."""
    try:
        path = resource("assets", "icon.ico")
        if path and os.path.exists(path):
            user32.LoadImageW.restype = wintypes.HICON
            found = user32.LoadImageW(None, str(path), IMAGE_ICON, 0, 0,
                                      LR_LOADFROMFILE)
            if found:
                return found
    except Exception:  # noqa: BLE001 - the fallback below is always there
        pass
    user32.LoadIconW.restype = wintypes.HICON
    return user32.LoadIconW(None, ctypes.c_wchar_p(IDI_APPLICATION))


def _tray_window():
    """A hidden window and a tray icon, made once and kept.

    Kept because the icon is the notification's identity: adding and removing
    it for every message would have Windows treat each one as a new source,
    and the balloon would be filed - or dropped - differently every time.
    """
    if _state["hwnd"]:
        return _state["hwnd"]

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)

    proc_type = ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND,
                                   wintypes.UINT, ctypes.c_ulonglong,
                                   ctypes.c_longlong)
    user32.DefWindowProcW.restype = ctypes.c_longlong
    user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT,
                                      ctypes.c_ulonglong, ctypes.c_longlong]
    proc = proc_type(user32.DefWindowProcW)

    kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE
    hinst = kernel32.GetModuleHandleW(None)

    cls = _WNDCLASSW()
    cls.lpfnWndProc = ctypes.cast(proc, ctypes.c_void_p)
    cls.hInstance = hinst
    cls.lpszClassName = "RomSrxNotifyWindow"
    user32.RegisterClassW(ctypes.byref(cls))

    user32.CreateWindowExW.restype = wintypes.HWND
    user32.CreateWindowExW.argtypes = [
        wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
    hwnd = user32.CreateWindowExW(0, cls.lpszClassName, "RomSrx", 0,
                                  0, 0, 0, 0, None, None, hinst, None)
    if not hwnd:
        return None

    # Both are held for the life of the process: the window procedure because
    # ctypes would otherwise collect the callback out from under Windows, and
    # the class because it names the procedure.
    _state["keep"] = [proc, cls, user32, shell32]
    _state["icon"] = _icon(user32)
    _state["hwnd"] = hwnd

    data = _NOTIFYICONDATAW()
    data.cbSize = ctypes.sizeof(_NOTIFYICONDATAW)
    data.hWnd = hwnd
    data.uID = 1
    data.uFlags = NIF_ICON | NIF_TIP
    data.hIcon = _state["icon"]
    data.szTip = "RomSrx"
    _state["added"] = bool(shell32.Shell_NotifyIconW(NIM_ADD,
                                                     ctypes.byref(data)))
    return hwnd


def _balloon(title: str, body: str) -> bool:
    try:
        with _lock:
            hwnd = _tray_window()
            if not hwnd or not _state["added"]:
                return False
            shell32 = _state["keep"][3]
            data = _NOTIFYICONDATAW()
            data.cbSize = ctypes.sizeof(_NOTIFYICONDATAW)
            data.hWnd = hwnd
            data.uID = 1
            data.uFlags = NIF_INFO | NIF_ICON
            data.hIcon = _state["icon"]
            # Windows truncates both itself, but doing it here keeps the
            # structure honest rather than relying on that.
            data.szInfoTitle = title[:63]
            data.szInfo = body[:255]
            data.dwInfoFlags = NIIF_INFO
            return bool(shell32.Shell_NotifyIconW(NIM_MODIFY,
                                                  ctypes.byref(data)))
    except Exception:  # noqa: BLE001 - a silent desktop is not an app error
        return False


# -- the toast, for a copy of this that has been registered properly -------

_AUMID = ("{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}"
          "\\WindowsPowerShell\\v1.0\\powershell.exe")

_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
$tpl = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent(
    [Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$texts = $tpl.GetElementsByTagName('text')
$texts.Item(0).AppendChild($tpl.CreateTextNode($env:ROMSRX_TOAST_TITLE)) > $null
$texts.Item(1).AppendChild($tpl.CreateTextNode($env:ROMSRX_TOAST_BODY)) > $null
$toast = [Windows.UI.Notifications.ToastNotification]::new($tpl)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(
    $env:ROMSRX_TOAST_AUMID).Show($toast)
"""


def _toast(title: str, body: str) -> None:
    """The strings go through the environment rather than into the script
    text. They are game names off a disk - brackets, quotes, dollar signs,
    whatever a preservation set felt like - and pasting one of those into a
    PowerShell command is a quoting bug and an injection at the same time."""
    env = dict(os.environ)
    env["ROMSRX_TOAST_TITLE"] = title
    env["ROMSRX_TOAST_BODY"] = body
    env["ROMSRX_TOAST_AUMID"] = _AUMID
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive",
             "-ExecutionPolicy", "Bypass", "-Command", "-"],
            input=_SCRIPT.encode("utf-8"),
            env=env, timeout=20, creationflags=flags,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except Exception:  # noqa: BLE001
        pass


def _run(title: str, body: str) -> None:
    if _balloon(title, body):
        return
    _toast(title, body)


def send(title: str, body: str) -> bool:
    """Show one, on a thread of its own.

    Answers whether it was worth trying rather than whether Windows drew it -
    only the person looking at the screen can say that, which is what the
    Test button in Settings is for.
    """
    title, body = str(title or "").strip(), str(body or "").strip()
    if not available() or not (title or body):
        return False
    threading.Thread(target=_run, args=(title, body), daemon=True).start()
    return True
