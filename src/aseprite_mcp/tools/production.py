"""Verified workflows built on the attributed headless Aseprite engine."""
from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
import time
from pathlib import Path

from mcp.server.fastmcp import Image as MCPImage
from PIL import Image, ImageDraw
from pydantic import Field

from ..app import mcp
from ..core import config
from ..core.contract import AssetContract, StrictModel, rgba_hash, validate_frames
from ..core.models import ColorSpec
from ..core.publication import publish_directory
from ..core.runner import run_lua
from .batch import OPERATIONS_HELP, apply_operations
from .inspect import render_preview

MAX_SHEET_PIXELS = 16_777_216


def read_master(filename: str):
    src = config.resolve(filename)
    if src.suffix.lower() not in {".aseprite", ".ase"}:
        raise ValueError("Use an editable .aseprite or .ase master")
    with tempfile.TemporaryDirectory(prefix="aseagent_", dir=config.workspace()) as tmp:
        info = run_lua('''
        local s = open_sprite(ARG.src)
        if s.width * s.height * #s.frames > 16777216 then error("Master exceeds 16 million pixels") end
        for i, f in ipairs(s.frames) do
          local im = Image(s.width, s.height, ColorMode.RGB)
          im:clear()
          im:drawSprite(s, i)
          im:saveAs(ARG.folder .. "/" .. i .. ".png")
        end
        RESULT = sprite_info(s)
        ''', {"src": src.as_posix(), "folder": Path(tmp).as_posix()})
        frames = []
        for i in range(1, info["frameCount"] + 1):
            with Image.open(Path(tmp) / f"{i}.png") as im:
                frames.append(im.convert("RGBA"))
    return info, frames


def _contract(contract) -> AssetContract:
    if isinstance(contract, AssetContract):
        return contract
    return AssetContract.model_validate(contract)


@mcp.tool()
def ase_validate_asset_contract(filename: str, contract: AssetContract) -> dict:
    """Reopen a native master and check every frame against a contract.

    Checks frame count, cell size, that each row's tag covers exactly its frames in
    order with the expected playback, binary alpha, palette membership, empty frames,
    and optional per-row foot/centre drift. Unknown contract fields are rejected.
    Rows are laid out in contract order starting at frame 1. Passing proves geometry
    and colours, not art quality: still review with ase_preview_animation.
    """
    spec = _contract(contract)
    info, frames = read_master(filename)
    return validate_frames(info, frames, spec)


@mcp.tool(description=(
    "Atomically apply typed batch operations to a native master, then return the result "
    "and a nearest-neighbour PNG of `frame` at `scale` (1-16). Save succeeds before the "
    "preview; a preview failure is reported as saved, not rolled back.\n\n" + OPERATIONS_HELP
))
def ase_apply_and_preview(filename: str, operations: list[dict], frame: int = 1, scale: int = 4) -> list:
    if config.resolve(filename).suffix.lower() not in {".aseprite", ".ase"}:
        raise ValueError("Edits require an editable master")
    if not 1 <= scale <= 16:
        raise ValueError("scale must be 1..16")
    result = apply_operations(filename, operations)
    try:
        return [result, render_preview(filename, frame=frame, scale=scale)]
    except Exception as exc:
        return [{**result, "saved": True, "preview_error": str(exc), "visual_review_required": True}]


def _background(size: tuple[int, int], background: str | None, cell: int) -> Image.Image:
    if background and background != "checker":
        c = ColorSpec.parse(background).as_dict()
        if "index" in c:
            raise ValueError("background must be an RGB colour, not a palette index")
        return Image.new("RGBA", size, (c["r"], c["g"], c["b"], c.get("a", 255)))
    sheet = Image.new("RGBA", size, (204, 204, 204, 255))
    draw = ImageDraw.Draw(sheet)
    step = max(2, cell)
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            if (x // step + y // step) % 2:
                draw.rectangle([x, y, x + step - 1, y + step - 1], fill=(170, 170, 170, 255))
    return sheet


@mcp.tool()
def ase_preview_animation(
    filename: str,
    scale: int = 4,
    background: str | None = "checker",
    by_tag: bool = True,
) -> list:
    """Return a labelled contact sheet of every frame, scaled with nearest-neighbour.

    With by_tag (default) each tag gets its own row, labelled with its name, frame
    range, playback and the frame numbers; untagged frames share a final row. The
    background is a checkerboard so transparency is visible, or any colour.
    Also returns the sprite info (frame timing in seconds, tags). This is a review
    sheet, not proof that the motion reads well.

    Args:
        scale: 1-16 pixel magnification.
        background: "checker" (default), a colour such as "#202020", or null for transparent.
        by_tag: One row per tag (True) or a plain 8-column grid (False).
    """
    if not 1 <= scale <= 16:
        raise ValueError("scale must be 1..16")
    info, frames = read_master(filename)
    w, h = info["width"], info["height"]
    rows: list[tuple[str, list[int]]] = []
    if by_tag and info.get("tags"):
        tagged: set[int] = set()
        for t in info["tags"]:
            span = list(range(t["from"], t["to"] + 1))
            tagged.update(span)
            rows.append((f'{t["name"]} {t["from"]}-{t["to"]} {t.get("aniDir", "forward")}', span))
        rest = [i for i in range(1, len(frames) + 1) if i not in tagged]
        if rest:
            rows.append(("untagged", rest))
    else:
        cols = min(8, len(frames))
        for start in range(0, len(frames), cols):
            span = list(range(start + 1, min(start + cols, len(frames)) + 1))
            rows.append((f"frames {span[0]}-{span[-1]}", span))
    gap, label_h = 2, 12
    cell_w, cell_h = w * scale, h * scale
    cols = max(len(span) for _, span in rows)
    width = max(cols * (cell_w + gap) + gap, 160)
    height = len(rows) * (label_h + cell_h + gap) + gap
    if width * height > MAX_SHEET_PIXELS:
        raise ValueError("Preview exceeds 16 million pixels; reduce scale")
    sheet = Image.new("RGBA", (width, height), (40, 40, 40, 255))
    draw = ImageDraw.Draw(sheet)
    y = gap
    for label, span in rows:
        draw.text((gap, y), label, fill=(235, 235, 235, 255))
        y += label_h
        for col, number in enumerate(span):
            x = gap + col * (cell_w + gap)
            bg = _background((cell_w, cell_h), background, scale * 4) if background else None
            big = frames[number - 1].resize((cell_w, cell_h), Image.Resampling.NEAREST)
            if bg is not None:
                bg.alpha_composite(big)
                big = bg
            sheet.paste(big, (x, y))
            draw.text((x + 2, y + 1), str(number), fill=(255, 255, 0, 255))
        y += cell_h + gap
    out = io.BytesIO()
    sheet.save(out, format="PNG")
    return [info, MCPImage(data=out.getvalue(), format="png")]


def _loader(atlas_key: str, prefix_with_key: bool) -> str:
    anim_key = "`${KEY}:${a.key}`" if prefix_with_key else "a.key"
    return (
        "// Call preloadAsset in preload(), createAnimations in create().\n"
        f"const KEY = {json.dumps(atlas_key)};\n"
        "export function preloadAsset(scene, base) {\n"
        "  scene.load.atlas(KEY, `${base}/sheet.png`, `${base}/atlas.json`);\n"
        "  scene.load.json(`${KEY}-animations`, `${base}/animations.json`);\n"
        "}\n"
        "export function createAnimations(scene) {\n"
        "  for (const a of scene.cache.json.get(`${KEY}-animations`)) {\n"
        "    // Phaser frame duration is added to its base frame duration.\n"
        "    const base = Math.min(...a.frames.map(f => f.duration));\n"
        f"    scene.anims.create({{key: {anim_key}, repeat: a.repeat, yoyo: a.yoyo,\n"
        "      frameRate: 1000 / base,\n"
        "      frames: a.frames.map(f => ({...f, duration: f.duration - base}))});\n"
        "  }\n"
        "}\n"
    )


def _build_bundle(atlas_key: str, members: list[tuple[str, AssetContract, dict, list]],
                  output_directory: str, replace: bool, prefix_with_key: bool,
                  extra_files: dict, qa_target: dict) -> dict:
    """Lay out validated members as stacked row blocks, verify, and publish."""
    target = config.resolve(output_directory)
    if target.exists() and not replace:
        raise ValueError("Bundle directory already exists; choose a new directory or pass replace=true")
    width = max(max(r.frames for r in spec.rows) * spec.cell.width for _, spec, _, _ in members)
    height = sum(len(spec.rows) * spec.cell.height for _, spec, _, _ in members)
    if width * height > MAX_SHEET_PIXELS:
        raise ValueError("Sheet exceeds 16 million pixels")
    sheet = Image.new("RGBA", (width, height))
    atlas, animations, placements = {}, [], []
    top = 0
    for filename, spec, info, frames in members:
        w, h = spec.cell.width, spec.cell.height
        index = 0
        for y, row in enumerate(spec.rows):
            sequence = []
            for x in range(row.frames):
                im = frames[index]
                key = f"{row.name}_{x:02d}" if prefix_with_key else f"{spec.name}/{row.name}_{x:02d}"
                px, py = x * w, top + y * h
                sheet.paste(im, (px, py))
                placements.append((filename, index, px, py, w, h, frames[index]))
                atlas[key] = {"frame": {"x": px, "y": py, "w": w, "h": h}, "rotated": False,
                              "trimmed": False, "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h},
                              "sourceSize": {"w": w, "h": h}}
                sequence.append({"key": atlas_key, "frame": key,
                                 "duration": round(info["frames"][index]["duration"] * 1000)})
                index += 1
            anim_key = row.name if prefix_with_key else f"{spec.name}:{row.name}"
            animations.append({"key": anim_key, "frames": sequence, "repeat": row.repeat,
                               "yoyo": row.playback == "pingpong"})
        top += len(spec.rows) * h
    # Stage beside the destination, verify, then publish with a no-clobber rename.
    with tempfile.TemporaryDirectory(prefix=".aseagent-export-", dir=target.parent) as tmp:
        bundle = Path(tmp) / "bundle"
        bundle.mkdir()
        sheet.save(bundle / "sheet.png")
        reopened = {}
        for filename, spec, info, frames in members:
            r_info, r_frames = read_master(filename)
            if r_info != info or len(r_frames) != len(frames):
                raise RuntimeError(f"Master {filename} changed during export; retry")
            reopened[filename] = r_frames
        with Image.open(bundle / "sheet.png") as decoded:
            decoded = decoded.convert("RGBA")
            for filename, i, x, y, w, h, original in placements:
                again = reopened[filename][i]
                if rgba_hash(again) != rgba_hash(original) or \
                        decoded.crop((x, y, x + w, y + h)).tobytes() != again.tobytes():
                    raise RuntimeError(f"RGBA roundtrip mismatch in {filename} frame {i + 1}")
        metadata = {"frames": atlas, "meta": {"image": "sheet.png",
                                              "size": {"w": sheet.width, "h": sheet.height}, "scale": "1"}}
        roundtrip = {"passed": True, "frames_compared": len(placements), "sheet_rgba_sha256": rgba_hash(sheet)}
        qa_target["roundtrip"] = roundtrip
        files = {"atlas.json": metadata, "animations.json": animations, **extra_files}
        for name, value in files.items():
            (bundle / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        (bundle / "loader.js").write_text(_loader(atlas_key, prefix_with_key), encoding="utf-8")
        _publish(bundle, target, replace)
    return {"output_directory": str(target), "roundtrip": roundtrip,
            "animations": [a["key"] for a in animations]}


def _publish(bundle: Path, target: Path, replace: bool) -> None:
    if not target.exists():
        publish_directory(bundle, target)
        return
    if not replace:
        raise ValueError("Bundle directory already exists")
    if not (target / "atlas.json").is_file() or not (target / "sheet.png").is_file():
        raise ValueError("Refusing to replace a directory that is not an exported bundle")
    old = target.with_name(f".{target.name}.asemcp-old-{os.getpid()}-{int(time.time())}")
    os.rename(target, old)
    try:
        publish_directory(bundle, target)
    except Exception:
        os.rename(old, target)
        raise
    shutil.rmtree(old, ignore_errors=True)


@mcp.tool()
def ase_export_phaser(filename: str, output_directory: str, contract: AssetContract,
                      replace: bool = False) -> dict:
    """Validate a native master and export a Phaser bundle directory.

    Writes sheet.png (one row per contract row), a Phaser hash atlas, animations.json
    (per-frame timing, repeat and yoyo from the contract), qa.json, contract.json and
    loader.js. The master and the written PNG are reopened and every RGBA pixel is
    compared before publishing. Animations are named "<contract name>:<row tag>".
    An existing directory is only replaced with replace=true, and only if it is a
    previous bundle; the swap is a rename, so a failed export leaves the old one intact.
    """
    spec = _contract(contract)
    info, frames = read_master(filename)
    qa = validate_frames(info, frames, spec)
    if not qa["passed"]:
        return {"ok": False, "qa": qa, "written": False}
    target = config.resolve(output_directory)
    if target.exists() and not replace:
        raise ValueError("Bundle directory already exists; choose a new directory or pass replace=true")
    result = _build_bundle(spec.name, [(filename, spec, info, frames)], output_directory, replace,
                           True, {"qa.json": qa, "contract.json": spec.model_dump()}, qa)
    return {"ok": True, "output_directory": result["output_directory"], "qa": qa,
            "animations": result["animations"],
            "files": ["sheet.png", "atlas.json", "animations.json", "qa.json", "contract.json", "loader.js"]}


class CastMember(StrictModel):
    filename: str = Field(description="Native .aseprite master for this character.")
    contract: AssetContract


@mcp.tool()
def ase_export_cast_atlas(name: str, members: list[CastMember], output_directory: str,
                          replace: bool = False) -> dict:
    """Validate several character masters and export them as ONE Phaser atlas.

    Each member is validated against its own contract; if any fails, nothing is
    written and every failure is returned. Characters are stacked as row blocks in
    one sheet.png. Atlas frames are "<character>/<tag>_<nn>" and animations are
    "<character>:<tag>", all under the atlas key `name`. Every frame of every master
    is reopened and compared pixel-for-pixel with the written sheet before publishing.
    """
    import re
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", name):
        raise ValueError("name must start with a letter and use letters, digits, _ or -")
    if not 1 <= len(members) <= 64:
        raise ValueError("members must list 1..64 characters")
    parsed = [m if isinstance(m, CastMember) else CastMember.model_validate(m) for m in members]
    names = [m.contract.name for m in parsed]
    if len(set(names)) != len(names):
        raise ValueError("each member's contract name must be unique")
    loaded, reports, failed = [], {}, False
    for m in parsed:
        info, frames = read_master(m.filename)
        qa = validate_frames(info, frames, m.contract)
        reports[m.contract.name] = qa
        failed = failed or not qa["passed"]
        loaded.append((m.filename, m.contract, info, frames))
    if failed:
        return {"ok": False, "written": False,
                "qa": {k: {"passed": v["passed"], "failures": v["failures"]} for k, v in reports.items()}}
    contracts = {m.contract.name: m.contract.model_dump() for m in parsed}
    cast_qa: dict = {"schema": "aseprite-agent.cast-qa.v1", "passed": True, "members": reports}
    result = _build_bundle(name, loaded, output_directory, replace, False,
                           {"qa.json": cast_qa, "contract.json": contracts}, cast_qa)
    return {"ok": True, "output_directory": result["output_directory"],
            "characters": names, "animations": result["animations"], "roundtrip": result["roundtrip"],
            "files": ["sheet.png", "atlas.json", "animations.json", "qa.json", "contract.json", "loader.js"]}
