"""Test the health_check self-test tool (requires Aseprite; auto-skips otherwise)."""

import asyncio

from aseprite_mcp.tools import health


def test_health_check_round_trip():
    from aseprite_mcp.agent_server import configure

    configure("all")  # registry state is process-wide; pin the profile under test
    out = asyncio.run(health.health_check())
    assert out["aseprite_found"] is True
    assert out["can_create_sprite"] is True
    assert out["can_export_png"] is True
    assert out["ok"] is True
    assert out["tools_registered"] >= 100
    assert out["aseprite_version"]
