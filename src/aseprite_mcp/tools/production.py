"""Verified workflows built on the attributed headless Aseprite engine."""
from __future__ import annotations

import io
import json
import os
import tempfile
from pathlib import Path
from PIL import Image
from mcp.server.fastmcp import Image as MCPImage
from ..app import mcp
from ..core import config
from ..core.runner import run_lua
from ..core.contract import AssetContract, validate_frames, rgba_hash
from .batch import apply_operations
from .inspect import render_preview


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


@mcp.tool()
def ase_validate_asset_contract(filename: str, contract: dict) -> dict:
    """Reopen a native master and check every frame: geometry, tags, alpha, palette, empty frames and optional per-tag foot/centre drift. Unknown contract fields are rejected. Art quality still needs visual review."""
    spec = AssetContract.model_validate(contract)
    info, frames = read_master(filename)
    return validate_frames(info, frames, spec)


@mcp.tool()
def ase_apply_and_preview(filename: str, operations: list[dict], frame: int = 1) -> list:
    """Atomically apply typed batch operations to a native master, then return state and a nearest-neighbour PNG. Save succeeds before preview; a preview failure is reported as saved, not rolled back."""
    if config.resolve(filename).suffix.lower() not in {".aseprite", ".ase"}:
        raise ValueError("Edits require an editable master")
    result = apply_operations(filename, operations)
    try:
        return [result, render_preview(filename, frame=frame, scale=4)]
    except Exception as exc:
        return [{**result, "saved": True, "preview_error": str(exc), "visual_review_required": True}]


@mcp.tool()
def ase_preview_animation(filename: str, scale: int = 4) -> list:
    """Return a contact-sheet PNG of every frame using nearest-neighbour scaling, with native frame timing and tag metadata. This is a review sheet, not a claim of correct motion."""
    if not 1 <= scale <= 8:
        raise ValueError("scale must be 1..8")
    info, frames = read_master(filename)
    cols = min(8, len(frames))
    sheet = Image.new("RGBA", (info["width"] * cols, info["height"] * ((len(frames)+cols-1)//cols)))
    if sheet.width * sheet.height * scale * scale > 16_777_216:
        raise ValueError("Preview exceeds 16 million pixels; reduce scale")
    for i, im in enumerate(frames):
        sheet.paste(im, ((i % cols)*im.width, (i//cols)*im.height))
    out = io.BytesIO()
    sheet.resize((sheet.width*scale, sheet.height*scale), Image.Resampling.NEAREST).save(out, format="PNG")
    return [info, MCPImage(data=out.getvalue(), format="png")]


@mcp.tool()
def ase_export_phaser(filename: str, output_directory: str, contract: dict) -> dict:
    """Validate a native master and export a new bundle directory: row sheet, Phaser hash atlas, per-frame animation timing, QA and loader JS. Reopen master and PNG, compare every decoded RGBA pixel before publishing. Existing directories are never overwritten."""
    spec = AssetContract.model_validate(contract)
    target = config.resolve(output_directory)
    if target.exists():
        raise ValueError("Bundle directory already exists; choose a new directory")
    info, frames = read_master(filename)
    qa = validate_frames(info, frames, spec)
    if not qa["passed"]:
        return {"ok": False, "qa": qa, "written": False}
    cols, rows = max(r.frames for r in spec.rows), len(spec.rows)
    w, h = spec.cell.width, spec.cell.height
    if cols*w*rows*h > 16_777_216:
        raise ValueError("Sheet exceeds 16 million pixels")
    sheet = Image.new("RGBA", (cols*w, rows*h))
    atlas, animations, placements = {}, [], []
    index = 0
    for y, row in enumerate(spec.rows):
        sequence = []
        for x in range(row.frames):
            im = frames[index]
            key = f"{row.direction}_{x:02d}"
            sheet.paste(im, (x*w, y*h))
            placements.append((x*w, y*h))
            atlas[key] = {"frame": {"x": x*w, "y": y*h, "w": w, "h": h}, "rotated": False,
                          "trimmed": False, "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h},
                          "sourceSize": {"w": w, "h": h}}
            sequence.append({"key": spec.name, "frame": key, "duration": round(info["frames"][index]["duration"]*1000)})
            index += 1
        animations.append({"key": row.direction, "frames": sequence, "repeat": -1})
    # Stage alongside destination, verify, then publish with a no-clobber directory rename.
    with tempfile.TemporaryDirectory(prefix=".aseagent-export-", dir=target.parent) as tmp:
        bundle = Path(tmp) / "bundle"
        bundle.mkdir()
        sheet.save(bundle / "sheet.png")
        reopened_info, reopened = read_master(filename)
        if reopened_info != info or len(reopened) != len(frames):
            raise RuntimeError("Master changed during export; retry")
        with Image.open(bundle / "sheet.png") as decoded:
            decoded = decoded.convert("RGBA")
            for i, (x, y) in enumerate(placements):
                if rgba_hash(reopened[i]) != rgba_hash(frames[i]) or decoded.crop((x,y,x+w,y+h)).tobytes() != reopened[i].tobytes():
                    raise RuntimeError(f"RGBA roundtrip mismatch in frame {i+1}")
        metadata = {"frames": atlas, "meta": {"image": "sheet.png", "size": {"w": sheet.width, "h": sheet.height}, "scale": "1"}}
        qa["roundtrip"] = {"passed": True, "frames_compared": len(frames), "sheet_rgba_sha256": rgba_hash(sheet)}
        for name, value in (("atlas.json", metadata), ("animations.json", animations), ("qa.json", qa), ("contract.json", spec.model_dump())):
            (bundle/name).write_text(json.dumps(value, indent=2)+"\n", encoding="utf-8")
        # Duration is per frame; frameRate supplies a zero base duration using explicit total duration.
        loader = '''// Call preloadAsset in preload(), createAnimations in create().
export function preloadAsset(scene, base) {
  scene.load.atlas(KEY, `${base}/sheet.png`, `${base}/atlas.json`);
  scene.load.json(`${KEY}-animations`, `${base}/animations.json`);
}
export function createAnimations(scene) {
  for (const a of scene.cache.json.get(`${KEY}-animations`)) {
    // Phaser frame duration is added to its base frame duration.
    const base = Math.min(...a.frames.map(f => f.duration));
    scene.anims.create({key: `${KEY}:${a.key}`, repeat: a.repeat,
      frameRate: 1000 / base,
      frames: a.frames.map(f => ({...f, duration: f.duration - base}))});
  }
}
'''.replace("KEY", json.dumps(spec.name))
        (bundle/"loader.js").write_text(loader, encoding="utf-8")
        # mkdir is the no-clobber reservation; rollback only our reservation on failure.
        target = config.resolve(output_directory)
        target.mkdir()
        try:
            for p in bundle.iterdir():
                os.replace(p, target/p.name)
        except Exception:
            import shutil
            shutil.rmtree(target)
            raise
    return {"ok": True, "output_directory": str(target), "qa": qa,
            "files": ["sheet.png", "atlas.json", "animations.json", "qa.json", "contract.json", "loader.js"]}
