"""Locating the Aseprite executable, the workspace directory, and run settings.

All of these can be overridden with environment variables so the same server
works on any machine:

    ASEPRITE_PATH            Absolute path to Aseprite.exe (or `aseprite` binary).
    ASEPRITE_MCP_WORKSPACE   Directory where relative sprite paths are resolved.
    ASEPRITE_MCP_TIMEOUT     Per-invocation timeout in seconds (default 90).
    ASEPRITE_MCP_ALLOW_ABSOLUTE  Set to 1/true to permit absolute paths inside allowed roots.
                             This never disables filesystem confinement.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .errors import AsepriteNotFoundError, WorkspaceError

# Project root = three levels up (src/aseprite_mcp/core/config.py -> repo root).
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Common install locations checked when ASEPRITE_PATH is not set and the binary
# is not on PATH. Steam, standalone installer, and scoop/winget layouts.
_CANDIDATES = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe",
    r"C:\Program Files\Steam\steamapps\common\Aseprite\Aseprite.exe",
    r"C:\Program Files\Aseprite\Aseprite.exe",
    r"C:\Program Files (x86)\Aseprite\Aseprite.exe",
    # macOS / Linux fallbacks (harmless on Windows).
    "/Applications/Aseprite.app/Contents/MacOS/aseprite",
    "/usr/bin/aseprite",
    "/usr/local/bin/aseprite",
]

_cached_exe: str | None = None


def find_aseprite() -> str:
    """Return the path to the Aseprite executable, or raise AsepriteNotFoundError
    (which is also a FileNotFoundError, for backwards compatibility)."""
    global _cached_exe
    if _cached_exe and Path(_cached_exe).exists():
        return _cached_exe

    env = os.environ.get("ASEPRITE_PATH")
    if env:
        if Path(env).exists():
            _cached_exe = env
            return env
        raise AsepriteNotFoundError(
            f"ASEPRITE_PATH is set to '{env}' but no file exists there."
        )

    on_path = shutil.which("aseprite") or shutil.which("Aseprite")
    if on_path:
        _cached_exe = on_path
        return on_path

    for candidate in _CANDIDATES:
        if Path(candidate).exists():
            _cached_exe = candidate
            return candidate

    raise AsepriteNotFoundError(
        "Could not locate Aseprite. Set the ASEPRITE_PATH environment variable to "
        "the full path of Aseprite.exe (e.g. "
        r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe)."
    )


def workspace() -> Path:
    """Directory where relative sprite filenames are resolved. Created if missing."""
    env = os.environ.get("ASEPRITE_MCP_WORKSPACE")
    base = Path(env) if env else (PROJECT_ROOT / "workspace")
    base.mkdir(parents=True, exist_ok=True)
    return base.resolve()


def allow_absolute() -> bool:
    """Whether absolute path syntax is permitted (still confined to allowed roots)."""
    return os.environ.get("ASEPRITE_MCP_ALLOW_ABSOLUTE", "").strip().lower() in (
        "1", "true", "yes", "on"
    )


def allowed_roots() -> list[Path]:
    """Workspace plus operator-configured JSON list of additional allowed roots."""
    import json
    roots = json.loads(os.environ.get("ASEPRITE_AGENT_ALLOWED_ROOTS", "[]"))
    if not isinstance(roots, list) or any(not isinstance(r, str) or not Path(r).is_absolute() for r in roots):
        raise WorkspaceError("ASEPRITE_AGENT_ALLOWED_ROOTS must be a JSON array of absolute directories")
    return [workspace().resolve(), *(Path(r).resolve() for r in roots)]


def resolve(filename: str) -> Path:
    """Resolve before mkdir; absolute opt-in never bypasses allowed roots."""
    from pathlib import PureWindowsPath
    from .workspace_lock import LOCK_NAME
    ws = workspace().resolve()
    p = Path(filename)
    win = PureWindowsPath(filename)
    if any(part.casefold() == LOCK_NAME for part in win.parts):
        raise WorkspaceError("Reserved workspace lock path")
    # Reject traversal, NTFS streams/device names and template expansion inputs.
    if not filename or ".." in win.parts or any(c in filename for c in ("\x00", "{", "}", "\n", "\r")):
        raise WorkspaceError("Path escapes the workspace or contains unsafe components")
    for part in win.parts:
        if part == win.anchor:
            continue
        stem = part.split(".")[0].upper()
        if ":" in part or part.endswith((" ", ".")) or stem in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1,10)), *(f"LPT{i}" for i in range(1,10))}:
            raise WorkspaceError("Unsafe Windows path component")
    if win.drive and not win.is_absolute():
        raise WorkspaceError("Drive-relative paths are disabled")
    if p.is_absolute() and not allow_absolute():
        raise WorkspaceError("Absolute paths are disabled; use workspace-relative paths")
    full = (p if p.is_absolute() else ws / p).resolve()
    if any(part.casefold() == LOCK_NAME for part in full.parts):
        raise WorkspaceError("Reserved workspace lock path")
    if not any(full.is_relative_to(r) for r in allowed_roots()):
        raise WorkspaceError("Path escapes the workspace and configured allowed roots")
    full.parent.mkdir(parents=True, exist_ok=True)
    return full


def timeout() -> float:
    try:
        value = float(os.environ.get("ASEPRITE_MCP_TIMEOUT", "90"))
        return value if 0 < value <= 600 else 90.0
    except ValueError:
        return 90.0
