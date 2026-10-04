"""Real process/OS regressions; these do not need an Aseprite installation."""
import asyncio
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import pytest
from PIL import Image

from aseprite_mcp.core import config
from aseprite_mcp.core.errors import WorkspaceError
from aseprite_mcp.core.publication import publish_directory
from aseprite_mcp.core.workspace_lock import LOCK_NAME, WorkspaceBusyError, workspace_lock


def kill_child(process):
    # Windows venv python.exe may be a launcher with a real interpreter child.
    # Kill only this test-owned process tree, not merely the launcher.
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       check=True, capture_output=True, timeout=10)
    else:
        process.kill()
    process.wait(timeout=10)


@contextmanager
def child(code, folder, *args):
    process = subprocess.Popen([sys.executable, "-c", code, str(folder), *args],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 15
        while not (folder / "ready").exists():
            if process.poll() is not None:
                pytest.fail(f"Child exited before ready: {process.communicate()}")
            if time.monotonic() > deadline:
                pytest.fail("Child did not become ready")
            time.sleep(0.01)
        yield process
    finally:
        if process.poll() is None:
            kill_child(process)
        process.communicate(timeout=10)


LOCK_HOLDER = '''
import sys, time
from pathlib import Path
from aseprite_mcp.core.workspace_lock import workspace_lock
folder = Path(sys.argv[1])
with workspace_lock(folder):
    (folder / "ready").write_text("ready")
    time.sleep(30)
'''


def test_cross_process_contention_and_kill_release(tmp_path):
    with child(LOCK_HOLDER, tmp_path) as process:
        with pytest.raises(WorkspaceBusyError, match="Workspace busy"):
            with workspace_lock(tmp_path):
                pytest.fail("Contending process acquired workspace")
        kill_child(process)
        with workspace_lock(tmp_path):
            assert (tmp_path / LOCK_NAME).exists()
    # Lock file persists; ownership is an OS lock, never a stale PID sentinel.
    with workspace_lock(tmp_path):
        pass


def test_exception_releases_lock_and_distinct_workspaces_are_independent(tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(RuntimeError, match="failed operation"):
        with workspace_lock(tmp_path), workspace_lock(other):
            raise RuntimeError("failed operation")
    with workspace_lock(tmp_path):
        with pytest.raises(WorkspaceBusyError):
            with workspace_lock(tmp_path):
                pytest.fail("Re-entrant writer acquired workspace")


@pytest.mark.parametrize("name", [LOCK_NAME, LOCK_NAME.upper(), f"nested/{LOCK_NAME}/asset.png"])
def test_lock_path_cannot_be_selected_by_tool(tmp_path, monkeypatch, name):
    monkeypatch.setenv("ASEPRITE_MCP_WORKSPACE", str(tmp_path))
    with pytest.raises(WorkspaceError, match="Reserved workspace lock"):
        config.resolve(name)


def test_mcp_dispatch_owns_lock_through_await_and_releases_on_cancel(tmp_path, monkeypatch):
    from aseprite_mcp.app import WorkspaceMCP
    monkeypatch.setenv("ASEPRITE_MCP_WORKSPACE", str(tmp_path))
    app = WorkspaceMCP("locking-test")

    async def exercise():
        started = asyncio.Event()
        @app.tool()
        async def held() -> str:
            started.set()
            await asyncio.Event().wait()
            return "unreachable"
        task = asyncio.create_task(app.call_tool("held", {}))
        await asyncio.wait_for(started.wait(), timeout=5)
        try:
            with pytest.raises(WorkspaceBusyError):
                await app.call_tool("held", {})
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        with workspace_lock(tmp_path):
            pass
    asyncio.run(exercise())


@pytest.mark.parametrize("existing", ["empty-directory", "nonempty-directory", "file"])
def test_publish_never_clobbers_existing_destination(tmp_path, existing):
    source, target = tmp_path / "staged", tmp_path / "published"
    source.mkdir()
    (source / "new").write_text("new")
    if existing == "file":
        target.write_text("original")
    else:
        target.mkdir()
        if existing == "nonempty-directory":
            (target / "original").write_text("original")
    with pytest.raises(OSError):
        publish_directory(source, target)
    assert (source / "new").read_text() == "new"
    if existing == "file":
        assert target.read_text() == "original"
    elif existing == "empty-directory":
        assert list(target.iterdir()) == []
    else:
        assert [p.name for p in target.iterdir()] == ["original"]


@pytest.mark.parametrize("phase", ["before", "after"])
def test_process_death_leaves_final_absent_or_complete(tmp_path, phase):
    code = '''
import sys, time
from pathlib import Path
from aseprite_mcp.core.publication import publish_directory
folder = Path(sys.argv[1])
staged = folder / "stage"
staged.mkdir()
for index in range(6):
    (staged / str(index)).write_text(str(index))
if sys.argv[2] == "after":
    publish_directory(staged, folder / "final")
(folder / "ready").write_text("ready")
time.sleep(30)
'''
    with child(code, tmp_path, phase) as process:
        kill_child(process)
    target = tmp_path / "final"
    if phase == "before":
        assert not target.exists()
        assert len(list((tmp_path / "stage").iterdir())) == 6
    else:
        assert {p.name: p.read_text() for p in target.iterdir()} == {str(i): str(i) for i in range(6)}


@pytest.fixture
def exporter(tmp_path, monkeypatch):
    from aseprite_mcp.tools import production
    monkeypatch.setenv("ASEPRITE_MCP_WORKSPACE", str(tmp_path))
    spec = {"name": "robot", "cell": {"width": 8, "height": 8},
            "rows": [{"direction": "down", "frames": 1}], "palette": ["#ff0000"]}
    frame = Image.new("RGBA", (8, 8))
    frame.paste((255, 0, 0, 255), (2, 2, 6, 7))
    info = {"width": 8, "height": 8, "frameCount": 1,
            "frames": [{"duration": 0.1}], "tags": [{"name": "down", "from": 1, "to": 1}]}
    monkeypatch.setattr(production, "read_master", lambda _: (info, [frame.copy()]))
    master = tmp_path / "robot.aseprite"
    master.write_bytes(b"native master sentinel")
    return production, spec, master


@pytest.mark.parametrize("failure", ["metadata-write", "publish", "competing-directory", "changed-master"])
def test_export_failure_preserves_master_and_destination(exporter, tmp_path, monkeypatch, failure):
    production, spec, master = exporter
    if failure == "metadata-write":
        write_text = Path.write_text
        def fail_metadata(path, *args, **kwargs):
            if path.name == "qa.json":
                raise OSError("injected write failure")
            return write_text(path, *args, **kwargs)
        monkeypatch.setattr(Path, "write_text", fail_metadata)
    elif failure in {"publish", "competing-directory"}:
        def fail_publication(source, target):
            if failure == "competing-directory":
                target.mkdir()
                (target / "other-writer").write_text("keep")
                return publish_directory(source, target)
            raise OSError("injected rename failure")
        monkeypatch.setattr(production, "publish_directory", fail_publication)
    else:
        original = production.read_master
        calls = 0
        def changed_master(name):
            nonlocal calls
            calls += 1
            info, frames = original(name)
            if calls == 2:
                frames[0].putpixel((0, 0), (255, 0, 0, 255))
            return info, frames
        monkeypatch.setattr(production, "read_master", changed_master)
    with pytest.raises((OSError, RuntimeError)):
        production.ase_export_phaser("robot.aseprite", "final", spec)
    assert master.read_bytes() == b"native master sentinel"
    if failure == "competing-directory":
        assert [p.name for p in (tmp_path / "final").iterdir()] == ["other-writer"]
        assert (tmp_path / "final" / "other-writer").read_text() == "keep"
    else:
        assert not (tmp_path / "final").exists()
    assert not list(tmp_path.glob(".aseagent-export-*"))


def test_export_publishes_all_verified_files(exporter, tmp_path):
    production, spec, master = exporter
    result = production.ase_export_phaser("robot.aseprite", "final", spec)
    assert result["ok"] and result["qa"]["roundtrip"]["passed"]
    assert sorted(p.name for p in (tmp_path / "final").iterdir()) == sorted(result["files"])
    assert master.read_bytes() == b"native master sentinel"
    assert not list(tmp_path.glob(".aseagent-export-*"))


def test_preview_rejects_oversized_sheet_before_allocation(exporter, monkeypatch):
    production, _, _ = exporter
    monkeypatch.setattr(production, "read_master", lambda _: ({"width": 4096, "height": 4096}, [object()]))
    def no_allocation(*args, **kwargs):
        pytest.fail("Allocated oversized preview")
    monkeypatch.setattr(Image, "new", no_allocation)
    with pytest.raises(ValueError, match="Preview exceeds"):
        production.ase_preview_animation("robot.aseprite", scale=8)
