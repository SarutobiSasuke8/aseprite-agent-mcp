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
- [x] Whole-call advisory workspace locking with contention, cancellation and process-exit regressions.
- [x] Atomic no-overwrite Phaser bundle publication with interrupted-write and process-termination regressions.
- [x] Preview size rejection before contact-sheet allocation; package classifier corrected to alpha.

## Next production pass

- [ ] Real artist-reviewed directional walk cycle and versioned visual golden files.
- [x] Tool profiles, cast tools, typed contracts and a cast atlas export (0.2.0).
- [x] Crash-safe saves, strict frame numbers and bounded drawing, canvas and text sizes (0.2.0).
- [ ] GUI/direct-call coordination for the remaining inherited tools.
- [ ] Power-loss durability and network filesystem qualification (separate from process-termination coverage).
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
