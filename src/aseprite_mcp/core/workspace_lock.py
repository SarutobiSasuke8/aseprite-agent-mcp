"""Fail-fast advisory locking for cooperating MCP servers on a local workspace."""
from __future__ import annotations

import errno
import os
from contextlib import contextmanager
from pathlib import Path

from .errors import WorkspaceError

LOCK_NAME = ".aseprite-agent.lock"


class WorkspaceBusyError(WorkspaceError):
    """Another MCP call owns this workspace; retry after it completes."""


@contextmanager
def workspace_lock(workspace: Path):
    # Never unlink this file: replacing its inode would split POSIX lock ownership.
    with (workspace / LOCK_NAME).open("a+b") as handle:
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                raise WorkspaceBusyError(
                    "Workspace busy: another MCP call is running. Retry after it completes."
                ) from exc
            raise
        try:
            # Windows byte-range locks may extend beyond EOF. Initialise only
            # after acquiring the lock, so a contender never writes our byte.
            if os.fstat(handle.fileno()).st_size == 0:
                handle.write(b"\0")
                handle.flush()
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
