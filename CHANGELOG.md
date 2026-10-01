# Changelog

## Unreleased - 2026-10-01

- Hold a fail-fast OS workspace lock around every complete MCP tool call; reserve
  its path and release ownership on completion, cancellation and process exit.
- Publish verified Phaser bundles with one no-overwrite directory rename, so
  process termination cannot expose a partially published bundle. Unsupported
  exclusive-rename semantics fail closed; power-loss durability remains unproven.
- Add process contention, termination, write/rename failure, destination race,
  master-change, cancellation and preview-allocation regressions.
- Reject oversized contact sheets before allocation, exercise lock contention and
  recovery over MCP stdio, and add macOS to the unit/package CI matrix.
- Correct inherited beta package metadata to alpha. No release or promotion.

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
