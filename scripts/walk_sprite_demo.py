"""Reproduce the generated walk demo, without image-model or network calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw

from aseprite_mcp.tools.generated import assemble_animation, clean_frames, remove_background


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="walk-128", help="Use a new prefix for a repeat proof")
    parser.add_argument("--height", type=int, default=128, help="Target cell height, in pixels")
    parser.add_argument("--colours", type=int, default=48, help="Shared opaque palette cap")
    args = parser.parse_args()
    if args.height < 64 or args.height > 256 or args.colours < 32 or args.colours > 48:
        parser.error("Demo height must be 64..256 and colours 32..48")
    demo = Path(__file__).resolve().parents[1] / "examples" / "walk-demo"
    os.environ["ASEPRITE_MCP_WORKSPACE"] = str(demo)
    source = demo / "source.png"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    filenames = []
    with Image.open(source) as sheet:
        if sheet.size != (1536, 1024):
            raise ValueError("Expected the original 4x2, 384x512-cell pose sheet")
        for i in range(8):
            x, y = i % 4, i // 4
            cell = sheet.crop((x * 384, y * 512, (x + 1) * 384, (y + 1) * 512)).convert("RGBA")
            bounds = remove_background(cell, None, 0, 128).getchannel("A").getbbox()
            # All frames use one 384x424 crop and scale. Reposition each source
            # baseline at y=416 without scaling its body or erasing natural bob.
            top = bounds[3] - 1 - 416
            pose = cell.crop((0, top, 384, top + 424))
            filename = f"pose-{i + 1}.png"
            pose.save(demo / filename)
            filenames.append(filename)
    width = round(384 * args.height / 424)
    inputs = dict(width=width, height=args.height, tag="walk", duration_ms=100,
                  alignment="anchor", anchors=[[220, 416]] * 8, method="majority",
                  colours=args.colours, palette_first=True)
    result = assemble_animation(filenames, args.output_prefix, **inputs)[0]
    frames = []
    for i in range(8):
        with Image.open(demo / args.output_prefix / "frames" / f"{i + 1:03}.png") as frame:
            frames.append(frame.convert("RGBA"))
    # Shared palette, source, sampling and feet anchor: only the grid changes.
    with Image.open(demo / filenames[0]) as first:
        small = clean_frames([first.convert("RGBA")], 58, 64, method="majority",
                             palette=result["palette"], palette_first=True,
                             alignment="anchor", anchors=[[220, 416]])[0][0]
    compare = Image.new("RGBA", (952, 560), (31, 37, 44, 255))
    compare.alpha_composite(small.resize((464, 512), Image.Resampling.NEAREST), (12, 32))
    compare.alpha_composite(frames[0].resize((464, 512), Image.Resampling.NEAREST), (488, 32))
    draw = ImageDraw.Draw(compare)
    draw.text((12, 8), f"64px grid, {args.colours}-colour palette cap", fill="white")
    draw.text((488, 8), f"{args.height}px grid, {args.colours}-colour palette cap", fill="white")
    draw.text((12, 546), "Same source, palette, majority and feet anchor; equal display size", fill="white")
    compare.save(demo / f"{args.output_prefix}-comparison.png")
    preview = [frame.resize((width * 3, args.height * 3), Image.Resampling.NEAREST) for frame in frames]
    preview[0].save(demo / f"{args.output_prefix}-preview.gif", save_all=True,
                    append_images=preview[1:], duration=100, loop=0, disposal=2)
    contact = Image.new("RGBA", (width * 4, args.height * 2))
    for i, frame in enumerate(frames):
        contact.paste(frame, ((i % 4) * width, (i // 4) * args.height))
    contact.resize((contact.width * 3, contact.height * 3), Image.Resampling.NEAREST).save(
        demo / f"{args.output_prefix}-contact.png")
    summary = {**result, "source_sha256": before, "source_unchanged": before == hashlib.sha256(source.read_bytes()).hexdigest(),
               "parameters": inputs, "bounds": [list(frame.getchannel("A").getbbox()) for frame in frames],
               "foot_rows": [frame.getchannel("A").getbbox()[3] - 1 for frame in frames],
               "artist_review_required": True, "real_game_proof": False}
    (demo / f"{args.output_prefix}-proof.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
