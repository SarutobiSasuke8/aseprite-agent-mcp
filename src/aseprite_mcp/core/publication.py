"""Publish a staged directory atomically without replacing any destination."""
from __future__ import annotations

import ctypes
import errno
import os
import sys
from pathlib import Path


def publish_directory(source: Path, destination: Path) -> None:
    """Same-filesystem rename with exclusive destination creation, or fail closed.

    This gives atomic visibility, not durability through power loss. Callers must
    finish all writes and verification before publication and stage beside target.
    """
    if sys.platform == "win32":
        # Windows rename refuses an existing destination, including an empty dir.
        os.rename(source, destination)
        return

    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        rename = libc.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                            ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1)
    elif sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        rename = libc.renamex_np
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(os.fsencode(source), os.fsencode(destination), 4)
    else:
        raise OSError(errno.ENOTSUP, "Atomic no-overwrite directory publication unavailable")
    if result != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(destination))
