"""Local-first stdio entry point with a curated, profile-selected tool surface.

The exposed tools are chosen by ``ASEPRITE_MCP_TOOLS``, a comma-separated list of
group names and/or individual tool names:

  * ``core`` (default): the create -> draw -> animate -> preview -> validate -> export path.
  * ``all``: every tool except the permanently disabled ones.
  * a module group such as ``tilemap``, ``effects``, ``slices`` or ``workflow``.
  * a single tool name, e.g. ``core,add_outline``.

Unknown names fail at startup rather than silently exposing less than asked for.
"""
from __future__ import annotations

import os

from .server import mcp
from .tools import production  # noqa: F401

# These inherited tools expand user/document names into filesystem paths or start
# GUI processes. Keep them unavailable until output expansion has its own audit.
DISABLED = frozenset({
    "export_frames", "export_layers", "export_tags", "export_layer", "export_game_asset_bundle",
    "export_godot_spriteframes", "build_asset_from_spec", "open_in_editor",
    # These plan for build_asset_from_spec, which is disabled, so they would point nowhere.
    "plan_asset_spec", "validate_asset_spec",
})

# The default surface: enough to build, animate, check and ship a character sheet.
CORE = frozenset({
    # discovery and inspection
    "health_check", "list_sprites", "get_sprite_info", "get_pixels", "render_preview",
    # documents
    "create_sprite", "save_sprite_as",
    # atomic production edits
    "ase_apply_and_preview", "apply_operations",
    # drawing
    "draw_pixels", "draw_pixel_rows", "draw_rectangle", "draw_line", "fill_area",
    "draw_symmetric_pixels", "mirror_layer", "flip_sprite",
    # structure
    "add_layer", "rename_layer", "set_layer_properties",
    "add_frame", "remove_frame", "set_frame_duration", "copy_cel", "set_cel_position",
    "add_tag", "set_tag", "remove_tag", "derive_mirrored_tag", "copy_frames_from",
    # palette
    "get_palette", "set_palette", "load_palette", "replace_color", "recolor_sprite",
    # review, validation and export
    "ase_preview_animation", "export_onion_skin", "ase_validate_asset_contract",
    "ase_export_phaser", "ase_export_cast_atlas",
})

ENV_VAR = "ASEPRITE_MCP_TOOLS"


def tool_groups() -> dict[str, set[str]]:
    """Every registered, non-disabled tool keyed by its module group, plus core/all."""
    groups: dict[str, set[str]] = {}
    for name, tool in mcp._tool_manager._tools.items():
        if name in DISABLED:
            continue
        groups.setdefault(tool.fn.__module__.rsplit(".", 1)[-1], set()).add(name)
    everything = set().union(*groups.values()) if groups else set()
    groups["all"] = everything
    groups["core"] = set(CORE) & everything
    return groups


def selected_tools(spec: str | None) -> set[str]:
    groups = tool_groups()
    everything = groups["all"]
    wanted: set[str] = set()
    unknown: list[str] = []
    for raw in (spec or "core").split(","):
        item = raw.strip()
        if not item:
            continue
        if item in groups:
            wanted |= groups[item]
        elif item in everything:
            wanted.add(item)
        else:
            unknown.append(item)
    if unknown:
        names = ", ".join(sorted(k for k in groups if k not in ("all", "core")))
        raise ValueError(
            f"{ENV_VAR} has unknown group or tool name(s): {', '.join(unknown)}. "
            f"Use core, all, a tool name, or one of these groups: {names}."
        )
    return wanted


_FULL_REGISTRY: dict | None = None


def configure(spec: str | None = None) -> set[str]:
    """Remove disabled and unselected tools; return the exposed tool names.

    Idempotent: each call starts again from the full registry, so tests and callers
    can apply different profiles in one process.
    """
    global _FULL_REGISTRY
    if _FULL_REGISTRY is None:
        _FULL_REGISTRY = dict(mcp._tool_manager._tools)
    mcp._tool_manager._tools = dict(_FULL_REGISTRY)
    registered = set(_FULL_REGISTRY)
    missing = DISABLED - registered
    if missing:
        # A renamed tool would otherwise silently escape the disabled list.
        raise RuntimeError(f"DISABLED names no registered tool: {', '.join(sorted(missing))}")
    keep = selected_tools(spec if spec is not None else os.environ.get(ENV_VAR))
    missing_core = CORE - registered
    if missing_core:
        raise RuntimeError(f"CORE names no registered tool: {', '.join(sorted(missing_core))}")
    for name in registered - keep:
        mcp.remove_tool(name)
    return keep


def main():
    configure()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
