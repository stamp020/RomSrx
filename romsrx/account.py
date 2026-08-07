"""archive.org sign-in, so login-only sources can be downloaded.

The password is used once to obtain a session and is never stored or logged
by this app - the `internetarchive` library writes the resulting cookies and
S3 keys to its own config file (ia.ini) in the user's profile.

Each person running the app signs in with their own account; nothing is
bundled with the build.
"""

from __future__ import annotations

import os


class AccountError(Exception):
    """Sign-in failed for a reason worth showing the user."""


def _library():
    """Import the optional dependency, with a useful message if it's absent."""
    try:
        import internetarchive  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - depends on install
        raise AccountError(
            "The 'internetarchive' package isn't installed. Run: "
            "python -m pip install internetarchive"
        ) from exc
    return internetarchive


def config_path() -> str | None:
    """Where the credentials file lives, if we can determine it."""
    try:
        from internetarchive.config import parse_config_file  # noqa: PLC0415
        found = parse_config_file()
        if found and found[0] and os.path.exists(found[0]):
            return found[0]
    except Exception:  # noqa: BLE001 - fall through to the usual locations
        pass
    for candidate in ("~/.config/internetarchive/ia.ini", "~/.config/ia.ini",
                      "~/.ia"):
        path = os.path.expanduser(candidate)
        if os.path.exists(path):
            return path
    return None


def status() -> dict:
    """Whether we're signed in, and as whom."""
    try:
        internetarchive = _library()
    except AccountError as exc:
        return {"available": False, "signed_in": False, "email": None,
                "error": str(exc)}

    try:
        session = internetarchive.get_session()
        signed_in = bool(session.cookies.get("logged-in-sig"))
        return {
            "available": True,
            "signed_in": signed_in,
            "email": getattr(session, "user_email", None) if signed_in else None,
            "config": config_path() if signed_in else None,
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001 - never break the page over this
        return {"available": True, "signed_in": False, "email": None,
                "error": str(exc)[:200]}


def login(email: str, password: str) -> dict:
    """Exchange credentials for a stored session. Password is not retained."""
    email = (email or "").strip()
    if not email or not password:
        raise AccountError("Enter both your archive.org email and password.")

    internetarchive = _library()
    try:
        internetarchive.configure(email, password)
    except Exception as exc:  # noqa: BLE001 - library raises several types
        message = str(exc)
        if "authentication" in message.lower() or "password" in message.lower():
            raise AccountError("archive.org rejected that email or password.") from exc
        raise AccountError(f"Sign-in failed: {message[:200]}") from exc

    result = status()
    if not result["signed_in"]:
        raise AccountError("Sign-in completed but no session was stored.")
    return result


def logout() -> dict:
    """Forget the stored session by removing the credentials file."""
    path = config_path()
    if path:
        try:
            os.remove(path)
        except OSError as exc:
            raise AccountError(f"Could not remove {path}: {exc}") from exc
    return {"available": True, "signed_in": False, "email": None, "error": None}
