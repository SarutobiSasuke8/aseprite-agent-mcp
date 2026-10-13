# Verification

## Generated PNG pipeline - 2026-10-13

Windows, Python 3.11 and a locally built Aseprite: `uv run python -m pytest
--run-aseprite` passed all 319 tests with no skips. Ruff and the generated tool
reference check passed. Both archives passed `check_distribution.py`.

The new tests cover shared palettes, binary alpha, deterministic majority ties,
border-connected background removal, enclosed details, outlines, explicit
anchors, clipping refusal, path confinement, source integrity, bounds,
no-clobber output and engine failure before publication. A real editor test
reopens the generated master and verifies every frame, tag range and timing.
A subsequent real stdio MCP regression verifies both new tools return JSON and
image content and refuse repeated output directories. The 2 generated-pipeline
integration tests pass together after that addition.

`scripts/generated_sprite_demo.py` completed from the original image-model pose
sheet, producing a cleaned base and a 4-frame idle. The committed base and idle
masters, exported PNGs, JSON and reopened-master renders are in
`examples/generated-demo/`. A second run with the `proof` prefix completed and
verified the same sheet RGBA hash. Those repeat-run outputs are local evidence,
not a second committed demo. The source and 6x frame preview were inspected.
The third pose changes the face/silhouette slightly: this remains an art-review
limitation, not a production animation claim. No release, public upload or
real-game integration was performed.

## Readiness sweep - 2026-10-01

The candidate remains a private, unreleased alpha. On Windows, all **270 tests
passed** with `pytest --run-aseprite`; no integration tests were skipped. This
includes 17 new file-safety regressions exercising OS locks, competing writers,
process termination, MCP cancellation, reserved lock paths, write/rename failure,
destination races, changed-master rejection and preview limits before allocation.

Fresh `scripts/proof_stdio.py` runs passed both from the editable checkout and
from a wheel installed into a new virtual environment. Both used the local
self-built Aseprite `1.x-dev`, discovered 109 tools, created 16 distinct frames,
reopened the native master and verified every exported RGBA cell. Both passed
rollback, traversal, overwrite and damaged-contract checks. New cross-process
MCP contention checks returned a tool error while locked and succeeded in the
same stdio session after release. The fresh wheel resolved MCP 1.30.0 within the
declared range; the locked checkout uses MCP 1.29.1.

The fresh contact sheet was visually inspected. The Phaser 3.90.0 fixture,
pointed at this run using `?proof=readiness-proof-2026-10-01`, reported that all
16 frames played across four animations. The fixture now accepts a constrained
proof-directory name, so a new run can be played without replacing old evidence.

Local receipts are ignored under `workspace/readiness-proof-2026-10-01/` and
`workspace/wheel-proof-2026-10-01/`. Both wheel and source archives passed the
distribution boundary and licence checks. The unit/package CI matrix now covers
Windows, Linux and macOS; it deliberately does not claim real-editor coverage.

Termination tests prove absent-or-complete final-directory visibility around
publication and lock release after interpreter termination. They do not simulate
power loss or qualify network filesystems. The lock coordinates MCP calls using
the same workspace, not the GUI or direct Python calls. An orphaned Aseprite
process must finish before retrying after an unexpected server exit. Artist
review, real-game proof and broader inherited-tool limits remain open.

## Local verification - 2026-09-07

Runtime: self-built Aseprite reporting `1.x-dev`; Python 3.11.15, MCP 1.29.1,
Pillow 12.3.0. This confirms local capability, not commercial-licence entitlement
or compatibility with every released Aseprite version.

Full local regression result: **253 passed** with `pytest --run-aseprite` (116.84 seconds). No integration skips. Both wheel and source distribution built and passed the distribution boundary/licence checks.

`scripts/proof_stdio.py` completed over MCP stdio with 109 available tools:

- 16 distinct 16×16 frames, four tags, editable master and saved/reopened copy.
- Palette and binary-alpha checks passed; foot and centre drift were zero.
- 64×64 row sheet; all sixteen decoded RGBA cells matched the reopened master.
- Native and contact-sheet PNG feedback, animated GIF, atlas, animations and QA.
- Failed batch left master bytes identical; traversal and bundle overwrite refused.
- Wrong-palette, partial-alpha and shifted-foot fixture rejected before export.

The Phaser 3.90.0 browser fixture displayed:
“PASS — atlas loaded; all 16 frames played across four animations.”
The contact sheet was visually inspected: hard pixel edges, consistent canvas and
bounds. This synthetic fixture demonstrates pipeline integrity, not good walking
motion or production art readiness.

Generated proof files live in ignored `workspace/proof-final/`. Reproduce them
with the README commands; use a new output directory when rerunning.
The default pytest command intentionally skips Aseprite integration tests. The
release lane must explicitly pass `--run-aseprite` with a working executable.

Upstream licence/source inspection preceded copying. The original planning files
contain local/private context and are excluded from distribution archives. Public
Git publication still needs a separate full-tree review.
