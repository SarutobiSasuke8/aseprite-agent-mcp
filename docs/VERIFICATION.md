# Local verification — 2026-09-07

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
