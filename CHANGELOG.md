# Changelog

## 0.1.0 â€” local, unreleased â€” 2026-09-07

- Imported 74 source/test files from the MIT upstream; exact original hashes and
  commit are recorded in UPSTREAM_INVENTORY.json. Original copyright is preserved.
- Added the aseprite-agent-mcp stdio entry point and a curated 109-tool surface.
- Added strict asset contracts, composite RGBA/alpha/palette/anchor checks,
  all-frame nearest-neighbour previews, and atomic edit-plus-preview workflow.
- Added Phaser row-sheet/hash-atlas export with per-frame timing, master reopen,
  decoded pixel comparison, new-directory protection and QA reports.
- Tightened configured roots, traversal/stream/device/template handling, protected
  native masters from export overwrites, bounded new canvases and production QA.
- Treat nonzero Aseprite exit as failure even if a result sentinel was printed.
- Constrained MCP SDK to <2 after reproducing the FastMCP import incompatibility.
- Added MCP stdio proof, negative fixtures, Phaser playback fixture, test coverage,
  install/configuration documentation, provenance and package boundary checks.

This derivative does not claim that the inherited general drawing engine was
written from scratch. No live-bridge source has been incorporated.
