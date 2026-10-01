"""The shared FastMCP application instance.

Defined in its own module so every tool module can `from ..app import mcp`
without creating an import cycle with `server.py`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from .core import config
from .core.workspace_lock import workspace_lock

INSTRUCTIONS = """\
This server drives Aseprite (a pixel-art / sprite editor) headlessly to create and
edit sprite files (.aseprite/.ase), draw pixel art, build animations, manage
palettes, and export to PNG/GIF/sprite sheets.

Workflow notes:
  * Relative filenames are resolved inside the server's workspace directory;
    absolute paths require opt-in and must stay inside configured allowed roots. Most tools return the resolved path.
  * Sprites are real files on disk. Edits open the file, modify it, and save.
  * Frames are 1-based. Colours accept "#RRGGBB", "#RRGGBBAA", "r,g,b", "r,g,b,a",
    "index:N" (for indexed sprites), or a few names (black, white, red, green,
    blue, yellow, cyan, magenta, transparent, ...).
  * Call `render_preview` to get a PNG image of your work so you can see the result
    before continuing. Call `get_sprite_info` for the structured state of a sprite.
  * Prefer ase_apply_and_preview for atomic edits with image feedback, then
    ase_validate_asset_contract and ase_export_phaser for verified production bundles.
  * Recommended first step for a new asset: `create_sprite`, then draw, then preview.
"""

class WorkspaceMCP(FastMCP):
    async def call_tool(self, name, arguments):
        # Cover the entire workflow, including reads, edits, preview and export.
        # Non-blocking acquisition avoids stalling this event loop on contention.
        with workspace_lock(config.workspace()):
            return await super().call_tool(name, arguments)


mcp = WorkspaceMCP("aseprite-agent", instructions=INSTRUCTIONS)
