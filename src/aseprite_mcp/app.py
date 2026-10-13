"""The shared FastMCP application instance.

Defined in its own module so every tool module can `from ..app import mcp`
without creating an import cycle with `server.py`.
"""

from __future__ import annotations

import asyncio
import os
import time

from mcp.server.fastmcp import FastMCP

from .core import config
from .core.workspace_lock import WorkspaceBusyError, workspace_lock

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
  * Coordinates are pixels with (0,0) at the top-left. Frame numbers must exist;
    out-of-range frames are errors, not clamped. Layers are a name or 1-based index.
  * Call `render_preview` to get a PNG image of your work so you can see the result
    before continuing. Call `get_sprite_info` for the structured state of a sprite
    (its frame durations are in seconds; tool inputs use milliseconds).
  * Prefer ase_apply_and_preview for atomic edits with image feedback, then
    ase_validate_asset_contract and ase_export_phaser for verified production bundles.
  * Recommended first step for a new asset: `create_sprite`, then draw, then preview.
  * For model-generated PNG poses, use `import_generated_image` or
    `assemble_animation`: palette cleanup, binary alpha, alignment and verified
    native master/sheet bundles. Review the preview for artistic consistency.

Building a cast of characters:
  1. Draw one base character. `draw_pixel_rows` paints a whole frame from text rows.
  2. Animate it: add frames, use `copy_cel` / `offset_cel` ops for bobs and steps,
     tag each animation (idle, walk_right, ...).
  3. `derive_mirrored_tag` makes walk_left from walk_right.
  4. Save copies with `save_sprite_as`, then `recolor_sprite` each into a new character,
     or start characters from a shared base with `copy_frames_from`.
  5. Review with `ase_preview_animation` (one labelled row per tag), validate each master
     against its contract, then `ase_export_cast_atlas` for one shared Phaser atlas.

The tool list is a profile chosen by the server operator (ASEPRITE_MCP_TOOLS); if a tool
named here is missing, it is outside the current profile.
"""

def lock_wait_seconds() -> float:
    """How long a call waits for a busy workspace before failing (ASEPRITE_MCP_LOCK_WAIT)."""
    try:
        value = float(os.environ.get("ASEPRITE_MCP_LOCK_WAIT", "15"))
    except ValueError:
        return 15.0
    return min(max(value, 0.0), 300.0)


class WorkspaceMCP(FastMCP):
    async def call_tool(self, name, arguments):
        # Cover the entire workflow, including reads, edits, preview and export.
        # Acquisition is non-blocking; contention is retried with an async sleep so
        # the event loop never stalls, up to ASEPRITE_MCP_LOCK_WAIT seconds.
        deadline = time.monotonic() + lock_wait_seconds()
        while True:
            acquired = False
            try:
                with workspace_lock(config.workspace()):
                    acquired = True
                    return await super().call_tool(name, arguments)
            except WorkspaceBusyError:
                if acquired or time.monotonic() >= deadline:
                    raise
            await asyncio.sleep(0.2)


mcp = WorkspaceMCP("aseprite-agent", instructions=INSTRUCTIONS)
