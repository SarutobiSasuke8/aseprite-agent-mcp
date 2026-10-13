"""Bounded generated-PNG cleanup with editable, verified Aseprite bundles."""
from __future__ import annotations

import hashlib
import io
import json
import re
import tempfile
from collections import Counter, deque
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import Image as MCPImage
from PIL import Image, ImageFilter

from ..app import mcp
from ..core import config
from ..core.publication import publish_directory
from ..core.runner import run_lua

MAX_INPUT_PIXELS = 4_194_304
MAX_FRAME_PIXELS = 65_536
MAX_TOTAL_PIXELS = 1_048_576
MAX_TOTAL_INPUT_PIXELS = 16_777_216


def _integer(value, low, high, name):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in {low}..{high}")
    return value


def _rgb(colour):
    if not isinstance(colour, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", colour):
        raise ValueError("Colours must be #RRGGBB")
    return tuple(bytes.fromhex(colour[1:]))


def load_png(filename: str) -> Image.Image:
    path = config.resolve(filename)
    if path.suffix.lower() != ".png":
        raise ValueError("Inputs must be PNG files")
    with Image.open(path) as image:
        if image.format != "PNG" or getattr(image, "n_frames", 1) != 1:
            raise ValueError("Input must be a single-frame PNG")
        if image.width * image.height > MAX_INPUT_PIXELS:
            raise ValueError("Input exceeds four million pixels")
        return image.convert("RGBA")


def load_poses(filenames):
    images, pixels = [], 0
    for filename in filenames:
        image = load_png(filename)
        pixels += image.width * image.height
        if pixels > MAX_TOTAL_INPUT_PIXELS:
            raise ValueError("Input poses exceed sixteen million total pixels")
        images.append(image)
    return images


def remove_background(image, background, tolerance, alpha_threshold):
    """Remove only border-connected matching colour; preserve enclosed details."""
    _integer(tolerance, 0, 255, "background_tolerance")
    _integer(alpha_threshold, 1, 255, "alpha_threshold")
    result = image.copy()
    pixels = result.load()
    if background is not None:
        colour = _rgb(background)
        queue = deque([(x, 0) for x in range(image.width)] +
                      [(x, image.height - 1) for x in range(image.width)] +
                      [(0, y) for y in range(image.height)] +
                      [(image.width - 1, y) for y in range(image.height)])
        seen = bytearray(image.width * image.height)
        while queue:
            x, y = queue.popleft()
            if not (0 <= x < image.width and 0 <= y < image.height):
                continue
            index = y * image.width + x
            if seen[index]:
                continue
            seen[index] = 1
            pixel = pixels[x, y]
            if pixel[3] and max(abs(pixel[i] - colour[i]) for i in range(3)) > tolerance:
                continue
            pixels[x, y] = (0, 0, 0, 0)
            queue.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
    # Quantisation must never turn invisible RGB values into visible colours.
    result.putdata([(*p[:3], 255) if p[3] >= alpha_threshold else (0, 0, 0, 0)
                    for p in result.get_flattened_data()])
    if result.getchannel("A").getbbox() is None:
        raise ValueError("Cleanup leaves an empty frame")
    return result


def downsample(image, size, method):
    if method == "nearest":
        return image.resize(size, Image.Resampling.NEAREST)
    if method != "majority":
        raise ValueError("method must be nearest or majority")
    if size[0] > image.width or size[1] > image.height:
        raise ValueError("majority is a downsample method; use nearest to upscale")
    result = Image.new("RGBA", size)
    pixels = image.load()
    for y in range(size[1]):
        for x in range(size[0]):
            x0, x1 = x * image.width // size[0], (x + 1) * image.width // size[0]
            y0, y1 = y * image.height // size[1], (y + 1) * image.height // size[1]
            counts = Counter(pixels[sx, sy] for sy in range(y0, y1) for sx in range(x0, x1))
            # Lexicographic tie-break makes repeated runs byte-stable.
            result.putpixel((x, y), min(counts, key=lambda c: (-counts[c], c)))
    return result


def quantize_frames(frames, colours, palette, sample_limit=None):
    _integer(colours, 1, 256, "colours")
    if palette is not None:
        if not 1 <= len(palette) <= 256:
            raise ValueError("palette must contain 1..256 colours")
        rgb = list(dict.fromkeys(_rgb(c) for c in palette))
    else:
        stride = max(1, (sum(frame.width * frame.height for frame in frames) + sample_limit - 1) // sample_limit) \
            if sample_limit else 1
        pixels = [p[:3] for frame in frames for i, p in enumerate(frame.get_flattened_data())
                  if p[3] and i % stride == 0]
        # A thin opaque feature can fall between sample positions. Include one
        # visible pixel per frame so a sparse sprite still has a palette.
        if sample_limit:
            for frame in frames:
                first = next((p[:3] for p in frame.get_flattened_data() if p[3]), None)
                if first is not None:
                    pixels.append(first)
        if not pixels:
            raise ValueError("No opaque pixels to quantize")
        sample = Image.new("RGB", (len(pixels), 1))
        sample.putdata(pixels)
        indexed = sample.quantize(colors=colours, method=Image.Quantize.MEDIANCUT,
                                  dither=Image.Dither.NONE)
        used = sorted(set(indexed.get_flattened_data()))
        flat = indexed.getpalette()
        rgb = [tuple(flat[i * 3:i * 3 + 3]) for i in used]
    mapping = {}
    result = []
    for frame in frames:
        data = []
        for pixel in frame.get_flattened_data():
            if not pixel[3]:
                data.append((0, 0, 0, 0))
                continue
            colour = pixel[:3]
            if colour not in mapping:
                mapping[colour] = min(rgb, key=lambda c: (sum((a - b) ** 2 for a, b in zip(c, colour)), c))
            data.append((*mapping[colour], 255))
        cleaned = Image.new("RGBA", frame.size)
        cleaned.putdata(data)
        result.append(cleaned)
    return result, ["#" + bytes(c).hex() for c in rgb]


def clean_frames(images, width, height, method="nearest", colours=16, palette=None,
                 background=None, background_tolerance=0, alpha_threshold=128,
                 outline=None, alignment="none", anchors=None, palette_first=False):
    _integer(width, 1, 256, "width")
    _integer(height, 1, 256, "height")
    if not 1 <= len(images) <= 128 or width * height * len(images) > MAX_TOTAL_PIXELS:
        raise ValueError("Use 1..128 frames and at most one million output pixels")
    if alignment not in {"none", "bounding-box", "anchor"}:
        raise ValueError("alignment must be none, bounding-box or anchor")
    if method not in {"nearest", "majority"}:
        raise ValueError("method must be nearest or majority")
    if not isinstance(palette_first, bool):
        raise ValueError("palette_first must be a boolean")
    prepared = [remove_background(im, background, background_tolerance, alpha_threshold) for im in images]
    # Generated antialiasing can give every source pixel a different RGBA value.
    # Snap the shared source palette first so majority votes count colour clusters
    # instead of treating every near-identical shade as a separate candidate.
    source_palette = palette
    if palette_first:
        prepared, source_palette = quantize_frames(prepared, colours, palette, sample_limit=65_536)
    transforms = []
    if alignment == "anchor":
        if not anchors or len(anchors) != len(images) or any(im.size != images[0].size for im in images):
            raise ValueError("anchor alignment needs same-size images and one [x,y] anchor per frame")
        for anchor, im in zip(anchors, images):
            if len(anchor) != 2:
                raise ValueError("Each anchor must be [x,y]")
            _integer(anchor[0], 0, im.width - 1, "anchor x")
            _integer(anchor[1], 0, im.height - 1, "anchor y")
    elif anchors is not None:
        raise ValueError("anchors require anchor alignment")
    if alignment == "bounding-box":
        boxes = [im.getchannel("A").getbbox() for im in prepared]
        # One scale for the whole animation. Per-frame scaling would erase motion.
        max_width = max(b[2] - b[0] for b in boxes)
        max_height = max(b[3] - b[1] for b in boxes)
        margin = 1 if outline else 0
        if width <= 2 * margin or height <= 2 * margin:
            raise ValueError("Grid too small for outline")
        scale = min((width - 2 * margin) / max_width, (height - 2 * margin) / max_height)
        frames = []
        for im, box in zip(prepared, boxes):
            crop = im.crop(box)
            size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
            small = downsample(crop, size, method)
            offset = ((width - small.width) // 2, height - margin - small.height)
            canvas = Image.new("RGBA", (width, height))
            canvas.paste(small, offset)
            frames.append(canvas)
            transforms.append({"source_bounds": list(box), "offset": list(offset), "scale": scale})
    else:
        frames = [downsample(im, (width, height), method) for im in prepared]
        for index, frame in enumerate(frames):
            offset = (0, 0)
            if alignment == "anchor":
                im, anchor = images[index], anchors[index]
                offset = (width // 2 - anchor[0] * width // im.width,
                          height - 2 - anchor[1] * height // im.height)
                box = frame.getchannel("A").getbbox()
                if box is None or box[0] + offset[0] < 0 or box[1] + offset[1] < 0 or \
                        box[2] + offset[0] > width or box[3] + offset[1] > height:
                    raise ValueError("Anchor alignment would clip the sprite; use a larger padded input")
                canvas = Image.new("RGBA", (width, height))
                canvas.paste(frame, offset)
                frames[index] = canvas
            transforms.append({"offset": list(offset), "source_size": list(images[index].size)})
    if any(frame.getchannel("A").getbbox() is None for frame in frames):
        raise ValueError("Downsampling leaves an empty frame")
    frames, actual_palette = quantize_frames(frames, colours, source_palette)
    if outline:
        colour = _rgb(outline)
        for index, frame in enumerate(frames):
            mask = frame.getchannel("A").filter(ImageFilter.MaxFilter(3))
            border = Image.new("RGBA", frame.size, (*colour, 255))
            border.putalpha(mask)
            frames[index] = Image.alpha_composite(border, frame)
        if outline.lower() not in actual_palette:
            actual_palette.append(outline.lower())
    return frames, actual_palette, transforms


def _write_bundle(frames, output_directory, tag, durations, palette, transforms):
    target = config.resolve(output_directory)
    if target.exists():
        raise ValueError("Output directory already exists; use a new directory")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", tag):
        raise ValueError("tag must start with a letter and use letters, digits, _ or -")
    if len(durations) != len(frames):
        raise ValueError("One duration is required per frame")
    for duration in durations:
        _integer(duration, 1, 60_000, "duration_ms")
    width, height = frames[0].size
    with tempfile.TemporaryDirectory(prefix=".aseagent-generated-", dir=target.parent) as tmp:
        stage = Path(tmp) / "bundle"
        stage.mkdir()
        (stage / "frames").mkdir()
        paths = []
        sheet = Image.new("RGBA", (width * len(frames), height))
        entries = {}
        for i, frame in enumerate(frames):
            path = stage / "frames" / f"{i + 1:03}.png"
            frame.save(path)
            paths.append(path.as_posix())
            sheet.paste(frame, (i * width, 0))
            entries[f"{tag}_{i + 1:03}"] = {"frame": {"x": i * width, "y": 0, "w": width, "h": height},
                                            "duration": durations[i]}
        sheet.save(stage / "sheet.png")
        # Use only supported Lua APIs. All paths are internally staged and bounded.
        (stage / "verify").mkdir()
        info = run_lua('''
        local s = Sprite(ARG.width, ARG.height, ColorMode.RGB)
        s.layers[1].name = "Generated poses"
        for i, path in ipairs(ARG.paths) do
          if i > 1 then s:newEmptyFrame() end
          local image = Image{fromFile=path}
          s:newCel(s.layers[1], i, image, Point(0, 0))
          s.frames[i].duration = ARG.durations[i] / 1000
        end
        local tag = s:newTag(1, #s.frames)
        tag.name = ARG.tag
        local pal = Palette(#ARG.palette)
        for i, colour in ipairs(ARG.palette) do pal:setColor(i - 1, mkcolor(colour)) end
        s:setPalette(pal)
        s:saveAs(ARG.master)
        s:close()
        local reopened = app.open(ARG.master)
        for i, frame in ipairs(reopened.frames) do
          local rendered = Image(reopened.width, reopened.height, ColorMode.RGB)
          rendered:clear()
          rendered:drawSprite(reopened, i)
          rendered:saveAs(ARG.verify .. "/" .. i .. ".png")
        end
        RESULT = sprite_info(reopened)
        ''', {"width": width, "height": height, "paths": paths, "durations": durations,
              "tag": tag, "master": (stage / "master.aseprite").as_posix(),
              "palette": [dict(zip(("r", "g", "b"), _rgb(c))) for c in palette],
              "verify": (stage / "verify").as_posix()})
        if info["frameCount"] != len(frames):
            raise RuntimeError("Reopened master frame count mismatch")
        if len(info["tags"]) != 1 or info["tags"][0]["name"] != tag or \
                info["tags"][0]["from"] != 1 or info["tags"][0]["to"] != len(frames):
            raise RuntimeError("Reopened master tag mismatch")
        if any(abs(frame["duration"] * 1000 - duration) > 0.01
               for frame, duration in zip(info["frames"], durations)):
            raise RuntimeError("Reopened master frame durations differ")
        for i, frame in enumerate(frames):
            with Image.open(stage / "verify" / f"{i + 1}.png") as again:
                if again.convert("RGBA").tobytes() != frame.tobytes():
                    raise RuntimeError("Reopened master pixels differ")
        with Image.open(stage / "sheet.png") as again:
            if again.convert("RGBA").tobytes() != sheet.tobytes():
                raise RuntimeError("Sheet PNG roundtrip differs")
        metadata = {"frames": entries, "meta": {"image": "sheet.png", "size": {"w": sheet.width, "h": height},
                    "frameTags": [{"name": tag, "from": 0, "to": len(frames) - 1, "direction": "forward"}],
                    "palette": palette, "transforms": transforms}}
        (stage / "sheet.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        report = {"verified": True, "frames": len(frames), "width": width, "height": height,
                  "palette": palette, "sheet_rgba_sha256": hashlib.sha256(sheet.tobytes()).hexdigest(),
                  "files": ["master.aseprite", "sheet.png", "sheet.json", "frames/", "verify/"],
                  "visual_review_required": True}
        (stage / "qa.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        publish_directory(stage, target)
    preview = sheet.resize((sheet.width * 4, sheet.height * 4), Image.Resampling.NEAREST)
    data = io.BytesIO()
    preview.save(data, format="PNG")
    return [{**report, "output_directory": output_directory}, MCPImage(data=data.getvalue(), format="png")]


@mcp.tool()
def import_generated_image(filename: str, output_directory: str, width: int = 32, height: int = 32,
                           method: Literal["nearest", "majority"] = "nearest", colours: int = 16,
                           palette: list[str] | None = None, background: str | None = None,
                           background_tolerance: int = 0, alpha_threshold: int = 128,
                           outline: str | None = None, palette_first: bool = False) -> list:
    """Clean one PNG into a binary-alpha pixel grid, palette and editable master.

    background is an explicit #RRGGBB border-connected colour key, not semantic
    segmentation. outline adds a 1px eight-neighbour border, clipped at the cell
    edge, and may add one palette colour. N colours excludes transparency.
    New output directory only. Returns a nearest-neighbour preview for review.
    width/height support 1..256px grids. palette_first snaps the source to one
    shared palette before sampling, useful with majority on generated shading.
    """
    frames, actual_palette, transforms = clean_frames(
        [load_png(filename)], width, height, method, colours, palette, background,
        background_tolerance, alpha_threshold, outline, palette_first=palette_first)
    return _write_bundle(frames, output_directory, "base", [100], actual_palette, transforms)


@mcp.tool()
def assemble_animation(filenames: list[str], output_directory: str, width: int = 32, height: int = 32,
                       tag: str = "idle", duration_ms: int = 100, durations_ms: list[int] | None = None,
                       alignment: Literal["bounding-box", "anchor", "none"] = "bounding-box",
                       anchors: list[list[int]] | None = None,
                       method: Literal["nearest", "majority"] = "nearest", colours: int = 16,
                       palette: list[str] | None = None, background: str | None = None,
                       background_tolerance: int = 0, alpha_threshold: int = 128,
                       outline: str | None = None, palette_first: bool = False) -> list:
    """Clean 1..128 ordered PNG poses with one palette; save master, sheet and JSON.

    Bounding-box mode uses one shared scale, bottom-centres silhouettes and leaves
    an outline margin. Anchor mode scales same-size canvases and translates each
    source [x,y] to (width//2,height-2), refusing clipping. No pose synthesis is
    implied: inspect the preview for identity, timing and motion coherence.
    Output is atomically published only after master and PNG pixel verification.
    Use height=128 and colours=32..48 for detailed sprites. palette_first snaps
    one shared source palette before sampling; defaults retain the prior pipeline.
    """
    if not 1 <= len(filenames) <= 128:
        raise ValueError("filenames must contain 1..128 PNGs")
    frames, actual_palette, transforms = clean_frames(
        load_poses(filenames), width, height, method, colours,
        palette, background, background_tolerance, alpha_threshold, outline, alignment, anchors, palette_first)
    durations = durations_ms if durations_ms is not None else [duration_ms] * len(frames)
    return _write_bundle(frames, output_directory, tag, durations, actual_palette, transforms)
