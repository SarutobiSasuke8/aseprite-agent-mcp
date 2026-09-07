# Security and operating boundary

The supported entry point is `aseprite-agent-mcp`, a stdio-only local tool. No
arbitrary-Lua MCP tool, telemetry, remote fetch or live bridge is exposed.
Operator environment variables choose the executable and filesystem roots.
Treat configuration as trusted code: do not populate it from source documents.

User paths are canonicalized before filesystem operations. Absolute path opt-in
does not disable root checks. Traversal, symlink escapes, NTFS alternate streams,
Windows device names and filename templates are rejected. Export QA validates
before writing a new destination directory; existing bundles are never replaced.

Temporary scripts/images are internal implementation files, not user-selected
paths. This confinement is not an operating-system sandbox: a hostile process
running as the same user can race path checks or mutate files. Run one writer per
workspace; do not share it with an untrusted local process. Aseprite loads files
using its own parser, so keep the editor updated and avoid hostile native files.

The contract pipeline caps decoded input at 16 million pixels; new canvases at
one million pixels; previews at 16 million scaled pixels. Inherited tools have
varying limits. Timeouts kill the direct Aseprite subprocess, but are not a global
resource quota. Run large or untrusted workloads in an OS sandbox.

Hidden tools: export_frames, export_layers, export_tags, export_layer,
export_game_asset_bundle, export_godot_spriteframes, build_asset_from_spec,
open_in_editor. The attributed source stays available for regression work; it is
not the supported public tool contract. Use the new verified Phaser exporter.

Report issues privately to the repository owner before public disclosure.
Public release is pending; no vulnerability-report endpoint has been configured.
