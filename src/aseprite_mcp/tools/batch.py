"""Batch operation runner — apply many edits to one sprite in a single Aseprite
process, atomically.

`apply_operations` validates the op list (pure Python), then — unless `dry_run` —
opens the sprite once, runs every op inside one `app.transaction`, and saves only if
all succeed. Any failure aborts the whole batch (rollback) and saves nothing. This
collapses multi-launch agent workflows (add layer -> draw -> add frame -> tag) into a
single, all-or-nothing call.
"""

from __future__ import annotations

import json

from ..app import mcp
from ..core import oplib
from ..core.manifest import sprite_summary, workflow_manifest
from ..core.runner import LuaToolError, run_lua
from .common import lua_path, resolve_path


def _structured_batch_error(message: str) -> LuaToolError | None:
    """If a Lua failure carries our structured batch JSON, turn it into a clear error."""
    try:
        info = json.loads(message)
    except (ValueError, TypeError):
        return None
    if isinstance(info, dict) and "failed_op_index" in info:
        return LuaToolError(
            f"Batch aborted at op {info['failed_op_index']} ({info.get('failed_op')}): "
            f"{info.get('error')} — the sprite was not modified (rolled back)."
        )
    return None


OPERATIONS_HELP = (
    'Each operation is {"op": "<name>", "args": {...}}. Ops run in order against the same '
    "open sprite, so later ops see earlier ones (add a layer, then draw on it). Coordinates "
    "are pixels from the top-left (0,0); frames are 1-based and must exist; layer is a name "
    "or 1-based index and defaults to the top layer; durations are milliseconds. "
    "'?' marks an optional arg.\n" + oplib.describe_ops()
)

APPLY_DESCRIPTION = (
    "Apply a list of edit operations to a sprite in one atomic, single-process batch. "
    "If any op fails, the whole batch is rolled back, nothing is saved, and the error names "
    "the failing op index. dry_run=true checks the list without launching Aseprite (shape "
    "only; a missing layer still fails on a real run). Returns a workflow_manifest.v1 with a "
    "per-op operations list.\n\n" + OPERATIONS_HELP
)


@mcp.tool(description=APPLY_DESCRIPTION)
def apply_operations(filename: str, operations: list[dict], dry_run: bool = False) -> dict:
    """Apply edit operations atomically. See APPLY_DESCRIPTION for the op vocabulary."""
    normalized = oplib.validate_operations(operations)  # raises ValidationFailed on bad shape

    if dry_run:
        return workflow_manifest(
            "batch",
            operations=[
                {"index": i, "op": op["op"], "status": "planned", "summary": oplib.summarize(op)}
                for i, op in enumerate(normalized)
            ],
            dry_run=True,
            suggested_next_actions=["Re-run with dry_run=false to apply these atomically."],
        )

    path = resolve_path(filename)
    try:
        result = run_lua(oplib.BATCH_LUA_BODY, {"src": lua_path(path), "operations": normalized})
    except LuaToolError as exc:
        structured = _structured_batch_error(str(exc))
        if structured is not None:
            raise structured from exc
        raise

    return workflow_manifest(
        "batch",
        sprite=sprite_summary(result["sprite"]),
        operations=result.get("operations", []),
        suggested_next_actions=[
            f"Review it: ase_preview_animation('{filename}').",
            f"Check it against a contract: ase_validate_asset_contract('{filename}', contract).",
        ],
    )
