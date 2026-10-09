# Aseprite Agent MCP

Local-first pixel-art authoring and verified game-asset export over MCP stdio.

**Status: local alpha, unreleased.** A controlled MIT derivative of
[MalloyTheDev/aseprite-mcp](https://github.com/MalloyTheDev/aseprite-mcp), pinned to
`8caabf9ce240a040ca2c94d3d7366c9d8dd63653`. See [NOTICE](NOTICE),
[LICENSE](LICENSE) and [UPSTREAM_INVENTORY.json](UPSTREAM_INVENTORY.json).
The inherited Python namespace remains `aseprite_mcp`; the package and command are `aseprite-agent-mcp`.

112 tools cover native documents, pixel drawing, layers, cels, frames, palettes,
tags, slices, transforms, tilemaps, inspection and exports. The production path
adds atomic edits with image feedback, strict typed asset contracts, labelled
all-frame previews, character-cast tools and Phaser bundles verified against
reopened native masters. By default the server exposes a 40-tool `core` profile
(see [Tool profiles](#tool-profiles)). See the generated
[tool reference](docs/TOOLS.md) for exact schemas.

## Install and run

Install Python 3.10+, uv, and your own Aseprite with Lua scripting support.
Aseprite is a separately licensed runtime; no editor binary is included.

```powershell
uv sync --locked --group dev
$env:ASEPRITE_PATH = 'C:\path\to\aseprite.exe'
$env:ASEPRITE_MCP_WORKSPACE = 'C:\path\to\assets'
uv run --no-sync aseprite-agent-mcp
```

The command speaks MCP on stdin/stdout and waits for a client. Diagnostic logs go
to stderr. Use [mcp-config.example.json](mcp-config.example.json) in a client after
replacing its placeholder paths. This project does not modify client settings.

## Tool profiles

Every tool description and schema costs the agent context, so the server exposes a
profile chosen by `ASEPRITE_MCP_TOOLS`, a comma-separated list of names:

| Value | Exposes |
| --- | --- |
| `core` (default) | 40 tools: create, draw, animate, preview, validate, export and the cast tools |
| `all` | Every supported tool (112) |
| a group | One tool module, e.g. `tilemap`, `effects`, `slices`, `palette`, `workflow` |
| a tool name | One extra tool, e.g. `core,add_outline` |

Unknown names stop the server at startup. The groups are listed at the top of the
[tool reference](docs/TOOLS.md).

| Variable | Default | Meaning |
| --- | --- | --- |
| `ASEPRITE_PATH` | auto-detect | Aseprite executable |
| `ASEPRITE_MCP_WORKSPACE` | `workspace/` in the project | Root for relative paths |
| `ASEPRITE_MCP_TOOLS` | `core` | Tool profile, as above |
| `ASEPRITE_MCP_LOCK_WAIT` | `15` | Seconds a call waits for a busy workspace (0 fails at once) |
| `ASEPRITE_MCP_TIMEOUT` | `90` | Seconds per Aseprite process |
| `ASEPRITE_MCP_ALLOW_ABSOLUTE` | off | Allow absolute path syntax inside allowed roots |
| `ASEPRITE_AGENT_ALLOWED_ROOTS` | `[]` | JSON list of extra roots |

## Recommended workflow

1. `health_check` proves the local CLI and Lua path can create and export.
2. `create_sprite` creates an editable `.aseprite` master.
3. `ase_apply_and_preview` applies a typed batch in one transaction and returns a
   rendered PNG. A failed operation leaves the file unchanged. A later preview
   failure explicitly reports that the edit was saved.
4. `ase_preview_animation` shows every frame without smoothing.
5. `ase_validate_asset_contract` checks geometry, frame count, exact tag ranges,
   tag playback, palette membership, binary alpha, empty frames and optional
   per-row foot/centre drift. Unknown fields are errors.
6. `ase_export_phaser` creates a bundle directory with sheet PNG, hash atlas JSON,
   animation timing, loader JS, contract and QA. It reopens the master and exported
   PNG and compares every frame's RGBA pixels before publishing. An existing
   directory is rejected unless `replace=true`, which swaps a previous bundle by
   rename. The native master remains.

### Building a cast of characters

1. `draw_pixel_rows` paints a whole frame from text rows and a colour key, e.g.
   `rows=["..oo..", ".oxxo."]`, `key={"o": "#203040", "x": "#f0c060"}`. Unknown
   characters are errors; `.` and space are skipped.
2. Animate with the `copy_cel` and `offset_cel` batch ops (bobs and steps without
   redrawing) and tag each animation.
3. `derive_mirrored_tag` creates `walk_left` from `walk_right`.
4. `save_sprite_as` a template, then `recolor_sprite` it into each character, or start
   characters from a shared base with `copy_frames_from`.
5. `ase_preview_animation` shows one labelled row per tag over a checkerboard.
6. `ase_export_cast_atlas` validates every master against its own contract and
   writes one Phaser atlas: frames `<character>/<tag>_<nn>`, animations
   `<character>:<tag>`.

Edits save through a sibling temporary file and a rename, so a killed Aseprite
process cannot leave a half-written master. Frame numbers must exist: an
out-of-range frame is an error, never clamped to the nearest frame.
All frames are 1-based. A contract row names an exact contiguous animation tag.
Palette entries are inline hex colours, not arbitrary file paths. Hide reference
layers before final validation/export: locked layers are still visible pixels.

```json
{
  "name": "robot",
  "cell": {"width": 16, "height": 16},
  "rows": [
    {"tag": "walk_down", "frames": 4},
    {"tag": "idle", "frames": 2, "playback": "pingpong"},
    {"tag": "sleep", "frames": 2, "repeat": 0, "check_anchor": false}
  ],
  "alpha": "binary",
  "palette": ["#315c88", "#8bd5ed", "#223344"],
  "anchor": {"max_foot_drift": 0.0, "max_center_drift": 0.0}
}
```

## Verification

```powershell
uv run pytest
uv run pytest --run-aseprite
uv run python scripts/proof_stdio.py --output ./workspace/proof-final
```

Use a fresh output directory for each proof run. The proof talks to the server
through a real MCP stdio client, creates 16 distinct synthetic frames, compares a
saved/reopened master, exports a sheet and GIF, tests rollback and overwrite/path
rejection, and confirms that a deliberately damaged asset cannot pass export QA.
It writes `proof.json` and visual artifacts. See [verification](docs/VERIFICATION.md).

To play that output in Phaser 3.90.0:

```powershell
npm ci --prefix examples/phaser --ignore-scripts
uv run python -m http.server 8795 --bind 127.0.0.1
```

Open `http://127.0.0.1:8795/examples/phaser/`. The page reports success only after
all four frames in all four animations have played. It uses a local npm dev
dependency; the MCP itself has no network dependency after installation.
For a fresh run under `workspace/my-proof`, use
`http://127.0.0.1:8795/examples/phaser/?proof=my-proof` to play that run's output.

## Boundaries and current limits

- Stdio only; no live-editor bridge or network listener in the MCP server.
- Paths are confined to the workspace and explicitly configured allowed roots.
  `ASEPRITE_MCP_ALLOW_ABSOLUTE=1` allows absolute syntax, never unrestricted access.
  Additional roots: `ASEPRITE_AGENT_ALLOWED_ROOTS='["/absolute/asset/root"]'`.
- Traversal, symlink escapes, unsafe Windows device/stream paths and filename
  template expansion are rejected. Some inherited tools are deliberately hidden.
- This is a local trusted-user tool, not an OS sandbox. Do not let untrusted local
  processes swap symlinks or edit the same master concurrently. MCP calls sharing
  a workspace use an OS advisory lock; a concurrent call waits up to
  `ASEPRITE_MCP_LOCK_WAIT` seconds, then fails with "Workspace busy". All servers writing
  shared assets must use the same workspace, including when using extra roots.
  Direct Python calls, the editor GUI and other programs do not take this lock.
- QA compares composite RGBA pixels. It does not prove artistic quality, correct
  anatomy/motion, palette-index identity, anchor semantics or absence of smoothing
  within an allowed palette. Anchor checks suit grounded same-subject animation.
- The test fixture is procedural evidence, not production walk-cycle art.
- Phaser bundles are validated in staging and published with one atomic,
  no-overwrite directory rename on supported local Windows, Linux and macOS
  filesystems. Unsupported rename semantics fail closed. Process termination
  leaves the final path absent or complete; it can leave a hidden staging folder.
  This does not guarantee durability through power loss or network filesystem behaviour.
- Live-editor turn Undo, private project contracts, broader resampling/fringe
  checks, formal visual golden baselines and public publication remain work.

[Security](SECURITY.md) · [Roadmap](ROADMAP.md) · [Changes](CHANGELOG.md)
