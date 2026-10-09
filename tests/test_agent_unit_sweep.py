"""Pure-Python checks for tool profiles, contracts, batch ops, limits and locking."""
import asyncio
import json
import time

import pytest
from pydantic import ValidationError

from aseprite_mcp.core import oplib
from aseprite_mcp.core.contract import AssetContract
from aseprite_mcp.core.errors import ValidationFailed


def _names():
    from aseprite_mcp.agent_server import mcp
    return {t.name for t in asyncio.run(mcp.list_tools())}


def test_agent_unit_default_profile_is_core_and_complete():
    from aseprite_mcp.agent_server import CORE, DISABLED, configure
    exposed = configure(None)
    assert exposed == set(CORE)
    assert _names() == set(CORE)
    assert not _names() & DISABLED


def test_agent_unit_profiles_combine_groups_and_tools():
    from aseprite_mcp.agent_server import CORE, configure
    exposed = configure("core, tilemap, add_outline")
    assert {"create_tilemap_layer", "set_tiles", "add_outline"} <= exposed
    assert set(CORE) <= exposed
    assert "desaturate" not in exposed
    everything = configure("all")
    assert len(everything) >= 100 and _names() == everything
    configure(None)


def test_agent_unit_unknown_profile_name_fails_loudly():
    from aseprite_mcp.agent_server import configure
    with pytest.raises(ValueError, match="unknown group or tool name"):
        configure("core,not_a_tool")
    configure(None)


def test_agent_unit_server_main_routes_through_curated_profile():
    import inspect

    from aseprite_mcp import server
    assert "agent_server" in inspect.getsource(server.main)


def test_agent_unit_contract_tag_alias_and_row_options():
    c = AssetContract.model_validate({
        "name": "hero", "cell": {"width": 8, "height": 8},
        "rows": [{"tag": "idle", "frames": 2, "playback": "pingpong", "repeat": 0},
                 {"direction": "sleep", "frames": 1, "check_anchor": False}]})
    assert [r.name for r in c.rows] == ["idle", "sleep"]
    with pytest.raises(ValidationError, match="exactly one of tag or direction"):
        AssetContract.model_validate({"name": "x", "cell": {"width": 1, "height": 1},
                                      "rows": [{"tag": "a", "direction": "a", "frames": 1}]})
    with pytest.raises(ValidationError, match="unique"):
        AssetContract.model_validate({"name": "x", "cell": {"width": 1, "height": 1},
                                      "rows": [{"tag": "a", "frames": 1}, {"direction": "a", "frames": 1}]})


def test_agent_unit_contract_schema_is_published_to_agents():
    from aseprite_mcp.agent_server import configure, mcp
    configure(None)
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    schema = json.dumps(tools["ase_validate_asset_contract"].inputSchema)
    assert "playback" in schema and "check_anchor" in schema
    assert "pixel_rows" in tools["ase_apply_and_preview"].description


def test_agent_unit_pixel_rows_validation():
    ok = oplib.validate_operations([{"op": "pixel_rows", "args": {"rows": [".a", "a."], "key": {"a": "red"}}}])
    assert ok[0]["args"]["key"]["a"]["r"] == 255
    with pytest.raises(ValidationFailed, match="not in key"):
        oplib.validate_operations([{"op": "pixel_rows", "args": {"rows": ["ab"], "key": {"a": "red"}}}])
    with pytest.raises(ValidationFailed, match="single characters"):
        oplib.validate_operations([{"op": "pixel_rows", "args": {"rows": ["a"], "key": {"ab": "red"}}}])
    with pytest.raises(ValidationFailed, match="at most 256"):
        oplib.validate_operations([{"op": "pixel_rows", "args": {"rows": ["a"] * 257, "key": {"a": "red"}}}])


def test_agent_unit_canvas_and_text_limits():
    from aseprite_mcp.core.limits import check_canvas
    from aseprite_mcp.tools import text
    with pytest.raises(ValidationFailed, match="exceeds"):
        check_canvas(65535, 65535)
    with pytest.raises(ValueError, match="scale must be"):
        text.draw_text("x.aseprite", "W", 0, 0, "red", scale=100000)


def test_agent_unit_lock_wait_retries_then_succeeds(tmp_path, monkeypatch):
    """A busy workspace is retried, not failed, while the wait budget lasts."""
    from aseprite_mcp import app as app_module
    from aseprite_mcp.core.workspace_lock import WorkspaceBusyError
    monkeypatch.setenv("ASEPRITE_MCP_LOCK_WAIT", "5")
    attempts = []

    class FakeLock:
        def __init__(self, _):
            pass

        def __enter__(self):
            attempts.append(time.monotonic())
            if len(attempts) < 3:
                raise WorkspaceBusyError("busy")

        def __exit__(self, *exc):
            return False

    async def fake_call(self, name, arguments):
        return "done"

    monkeypatch.setattr(app_module, "workspace_lock", FakeLock)
    monkeypatch.setattr(app_module.FastMCP, "call_tool", fake_call)
    result = asyncio.run(app_module.mcp.call_tool("health_check", {}))
    assert result == "done" and len(attempts) == 3


def test_agent_unit_lock_wait_zero_fails_fast(monkeypatch):
    from aseprite_mcp import app as app_module
    from aseprite_mcp.core.workspace_lock import WorkspaceBusyError
    monkeypatch.setenv("ASEPRITE_MCP_LOCK_WAIT", "0")

    class BusyLock:
        def __init__(self, _):
            pass

        def __enter__(self):
            raise WorkspaceBusyError("busy")

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(app_module, "workspace_lock", BusyLock)
    with pytest.raises(WorkspaceBusyError):
        asyncio.run(app_module.mcp.call_tool("health_check", {}))


@pytest.fixture
def cast_exporter(tmp_path, monkeypatch):
    from PIL import Image

    from aseprite_mcp.tools import production
    monkeypatch.setenv("ASEPRITE_MCP_WORKSPACE", str(tmp_path))

    def master(colour):
        frame = Image.new("RGBA", (4, 4))
        frame.paste(colour, (1, 1, 3, 4))
        info = {"width": 4, "height": 4, "frameCount": 1, "frames": [{"duration": 0.1}],
                "tags": [{"name": "idle", "from": 1, "to": 1, "aniDir": "forward"}]}
        return info, [frame]

    masters = {"a.aseprite": master((255, 0, 0, 255)), "b.aseprite": master((0, 0, 255, 255))}
    monkeypatch.setattr(production, "read_master",
                        lambda name: (masters[name][0], [f.copy() for f in masters[name][1]]))
    for name in masters:
        (tmp_path / name).write_bytes(b"master")
    contract = lambda n: {"name": n, "cell": {"width": 4, "height": 4},  # noqa: E731
                          "rows": [{"tag": "idle", "frames": 1}]}
    return production, contract


def test_agent_unit_cast_atlas_layout_and_replace(cast_exporter, tmp_path):
    production, contract = cast_exporter
    members = [{"filename": "a.aseprite", "contract": contract("red")},
               {"filename": "b.aseprite", "contract": contract("blue")}]
    out = production.ase_export_cast_atlas("town", members, "cast")
    assert out["ok"] and out["animations"] == ["red:idle", "blue:idle"]
    atlas = json.loads((tmp_path / "cast" / "atlas.json").read_text())
    assert atlas["frames"]["blue/idle_00"]["frame"]["y"] == 4
    with pytest.raises(ValueError, match="already exists"):
        production.ase_export_cast_atlas("town", members, "cast")
    again = production.ase_export_cast_atlas("town", members, "cast", replace=True)
    assert again["ok"] and not list(tmp_path.glob(".cast.asemcp-old-*"))
    with pytest.raises(ValueError, match="unique"):
        production.ase_export_cast_atlas("town", [members[0], members[0]], "other")


def test_agent_unit_replace_refuses_non_bundle_directory(cast_exporter, tmp_path):
    production, contract = cast_exporter
    (tmp_path / "precious").mkdir()
    (tmp_path / "precious" / "notes.txt").write_text("keep")
    with pytest.raises(ValueError, match="not an exported bundle"):
        production.ase_export_cast_atlas("town", [{"filename": "a.aseprite", "contract": contract("red")}],
                                         "precious", replace=True)
    assert (tmp_path / "precious" / "notes.txt").read_text() == "keep"


@pytest.mark.parametrize("name", ["CON .txt", "COM¹.png", "CONIN$.png", "conout$", "LPT³.aseprite"])
def test_agent_unit_reserved_device_names_rejected(name, tmp_path, monkeypatch):
    from aseprite_mcp.core import config
    from aseprite_mcp.core.errors import WorkspaceError
    monkeypatch.setenv("ASEPRITE_MCP_WORKSPACE", str(tmp_path))
    with pytest.raises(WorkspaceError):
        config.resolve(name)


@pytest.mark.skipif(__import__("os").name != "nt", reason="root-relative paths are a Windows form")
def test_agent_unit_root_relative_path_rejected(tmp_path, monkeypatch):
    from aseprite_mcp.core import config
    from aseprite_mcp.core.errors import WorkspaceError
    monkeypatch.setenv("ASEPRITE_MCP_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("ASEPRITE_MCP_ALLOW_ABSOLUTE", "0")
    with pytest.raises(WorkspaceError, match="Root-relative"):
        config.resolve(r"\Assets\x.png")
    assert config.resolve("ok/hero.aseprite").name == "hero.aseprite"
