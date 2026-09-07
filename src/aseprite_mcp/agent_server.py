"""Local-first stdio entry point with a curated default tool surface."""
from __future__ import annotations
import asyncio
from .server import mcp
from .tools import production  # noqa: F401

# These inherited tools expand user/document names into filesystem paths or start
# GUI processes. Keep them unavailable until output expansion has its own audit.
DISABLED = {
    "export_frames", "export_layers", "export_tags", "export_layer", "export_game_asset_bundle",
    "export_godot_spriteframes", "build_asset_from_spec", "open_in_editor",
}


def configure():
    for name in DISABLED:
        try:
            mcp.remove_tool(name)
        except Exception:
            pass


def main():
    configure()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
