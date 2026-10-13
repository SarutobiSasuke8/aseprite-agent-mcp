"""Reproduce the original generated courier demo without any network calls."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from PIL import Image

from aseprite_mcp.tools.generated import assemble_animation, import_generated_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="proof", help="New workspace-relative output prefix; existing bundles are refused")
    prefix = parser.parse_args().output_prefix
    root = Path(__file__).resolve().parents[1]
    demo = root / "examples" / "generated-demo"
    os.environ["ASEPRITE_MCP_WORKSPACE"] = str(demo)
    # The image model supplied an evenly spaced 2x2 pose sheet. Splitting is
    # deterministic preparation, not four independently generated characters.
    with Image.open(demo / "before.png") as source:
        for i, (x, y) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
            source.crop((x * source.width // 2, y * source.height // 2,
                         (x + 1) * source.width // 2, (y + 1) * source.height // 2)).save(demo / f"pose-{i + 1}.png")
    base_dir, idle_dir = f"{prefix}-base", f"{prefix}-idle"
    base = import_generated_image("pose-1.png", base_dir, 32, 32, colours=16)
    result = assemble_animation([f"pose-{i + 1}.png" for i in range(4)], idle_dir, 32, 48,
                                colours=16, outline="#152b32", durations_ms=[180, 140, 180, 140])
    with Image.open(demo / idle_dir / "sheet.png") as sheet:
        sheet.resize((sheet.width * 6, sheet.height * 6), Image.Resampling.NEAREST).save(demo / f"{prefix}-after-preview.png")
    frames = []
    for i in range(4):
        with Image.open(demo / idle_dir / "frames" / f"{i + 1:03}.png") as frame:
            frames.append(frame.convert("RGBA").resize((192, 288), Image.Resampling.NEAREST))
    frames[0].save(demo / f"{prefix}-idle-preview.gif", save_all=True, append_images=frames[1:],
                   duration=[180, 140, 180, 140], loop=0, disposal=2)
    print(json.dumps({"base": base[0], "idle": result[0]}, indent=2))


if __name__ == "__main__":
    main()
