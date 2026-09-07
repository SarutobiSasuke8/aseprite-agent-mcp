# Upstream evaluation and reuse

Selected baseline: https://github.com/MalloyTheDev/aseprite-mcp
Commit: 8caabf9ce240a040ca2c94d3d7366c9d8dd63653
Licence: MIT, copyright 2026 Brendan Malloy.

Its cohesive Lua runner, drawing/structure tools, batch engine and tests give a
substantial usable headless baseline. Source and tests were inventoried before
copying. UPSTREAM_INVENTORY.json lists the original SHA-256 of each imported file.
Local changes appear in CHANGELOG.md; hashes describe the import, not current files.

The baseline allowed an opt-in full filesystem escape and its dependency range
installed an incompatible MCP 2.x. This derivative confines absolute paths to
operator-approved roots and pins the supported MCP major version. Pattern exports
and GUI launch are excluded from the default surface pending their own review.

https://github.com/logiksecurity/ase-mcp was reviewed as a live-session architectural
candidate. No code was copied or executed; installation, token handling and Undo
remain unevaluated. This is an explicit deferred milestone, not a passed audit.

Official substrate references:
- https://www.aseprite.org/docs/cli/
- https://www.aseprite.org/api/sprite/
- https://docs.phaser.io/api-documentation/class/animations-animation

Phaser 3.90.0 and eventemitter3 are locked npm dev dependencies for the optional
browser proof. Their licence files remain under their installed packages; their
source is not vendored into the Python distribution.
