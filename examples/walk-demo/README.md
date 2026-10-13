# Hooded courier walk demo

An 8-frame side-view walk of the teal-cloak courier from `../generated-demo`.
The poses were generated together with the built-in image generation tool using
the original character sheet and `reference-canvas.png` as references. The full
prompt is in `prompt.txt`; the untouched generated output is `source.png`.

The local pipeline uses **116x128px cells**, a shared **48-colour cap**, binary
alpha, palette-first majority downsampling and explicit feet anchors. The
source poses are cropped into equal 384x424px canvases, with one shared scale.
Each source baseline is placed at y=416, then mapped to output foot row 126.
No frame is scaled independently. The hood, face and costume come from the
generated poses; the tools do not synthesize or artist-approve the movement.

- `walk-128/master.aseprite`: editable native master, one walk tag, 8 frames at 100ms.
- `walk-128/sheet.png` and `walk-128/sheet.json`: horizontal sheet and frame metadata.
- `walk-128/frames/` and `walk-128/verify/`: cleaned poses and reopened-master renders.
- `walk-128/qa.json` and `walk-128-proof.json`: native roundtrip, palette, source hash,
  dimensions and foot-row evidence.
- `walk-128-preview.gif`: looping 800ms preview at 3x nearest-neighbour display scale.
- `walk-128-contact.png`: 4x2 review sheet.
- `walk-128-comparison.png`: one frame on 64px and 128px grids, displayed at equal
  physical size with the same source, palette, sampling and anchor.

## Reproduce

Set `ASEPRITE_PATH` to a local Aseprite executable, then from the repository root:

```sh
uv sync --locked --group dev
uv run python scripts/walk_sprite_demo.py --output-prefix proof --height 128 --colours 48
uv run pytest --run-aseprite
uv run ruff check src tests scripts
uv run python scripts/generate_tools_doc.py --check
```

Use a new output prefix: existing native bundles are refused. Regeneration needs
no image-model or network call. `--height` supports 64..256 and `--colours` supports
32..48. Both MCP tools expose `width`, `height`, `colours` and `palette_first`.
The explicit palette can also be supplied to retain a chosen set of colours.
Automatic source-palette selection samples at most about 65,536 source positions
plus one visible pixel per frame, bounding palette-selection memory. All source
pixels are then snapped; small differences can remain between automatic and an
artist-supplied palette.

## Visual findings

The larger grid retains more of the eye, hood trim, clasp and sleeve detail than
the 64px version. All 8 feet baselines are at row 126. Generated head heights
still vary by about 3px, and the face, sleeve and satchel shift slightly in the
second half of the cycle (especially frames 6 to 8). The first and fifth contact
poses are similar, so the near/far-leg alternation could read more clearly.
This is useful demo art and requires artist cleanup before production use.

The file-integrity checks do not prove a shipped-game integration or fulfil
issue #4's artist-reviewed real-game proof. No release or publication was made.
