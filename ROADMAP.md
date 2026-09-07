# Roadmap

## Implemented locally

- [x] Attributed, pinned MIT headless baseline and per-file reuse inventory.
- [x] Aseprite CLI/Lua create, save, reopen, render and native master proof.
- [x] Broad drawing, palettes, layers, cels, frames, tags and slice coverage.
- [x] Atomic edits with explicit preview feedback.
- [x] Strict game contracts: geometry, tags, palette, alpha, empty cells, anchor drift.
- [x] Verified row-sheet export and Phaser atlas/animation loader.
- [x] Synthetic 16-frame MCP stdio proof and actual Phaser playback.
- [x] Packaging, local test lane, CI definition and operating documentation.

## Next production pass

- [ ] Real artist-reviewed directional walk cycle and versioned visual golden files.
- [ ] Snapshot/concurrent-writer locking and broader inherited-tool resource limits.
- [ ] Durable regression coverage for partial bundle writes and host crashes.
- [ ] Dedicated resampling, fringe, stray-pixel and palette-index checks.
- [ ] Private consumer asset contract and a real game asset proof.
- [ ] Safe per-layer/per-tag output expansion before restoring hidden exporters.

## Optional live-editor milestone

- [ ] Evaluate the live bridge separately; retain any adopted licence notices.
- [ ] Token-authenticated loopback bridge, reconnection, contention and one-turn Undo.

## Publication gate

- [ ] Select public repository identity and perform full source privacy review.
- [ ] Confirm runtime distribution/licence posture independently of local execution.
- [ ] Bundle workflow skills, release CI, registry metadata and publish only after review.
