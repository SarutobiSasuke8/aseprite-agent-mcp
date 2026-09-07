"""Strict, portable asset contracts and decoded RGBA validation."""
from __future__ import annotations

import hashlib
from typing import Literal
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Cell(StrictModel):
    width: int = Field(ge=1, le=1024)
    height: int = Field(ge=1, le=1024)


class Row(StrictModel):
    direction: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,47}$")
    frames: int = Field(ge=1, le=64)


class Anchor(StrictModel):
    max_foot_drift: float = Field(default=0.0, ge=0, le=1024)
    max_center_drift: float = Field(default=0.0, ge=0, le=1024)


class AssetContract(StrictModel):
    name: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
    cell: Cell
    rows: list[Row] = Field(min_length=1, max_length=16)
    alpha: Literal["binary", "any"] = "binary"
    palette: list[str] = Field(default_factory=list, max_length=256)
    anchor: Anchor | None = None
    allow_empty: bool = False

    @model_validator(mode="after")
    def consistent(self):
        import re
        names = [r.direction for r in self.rows]
        if len(set(names)) != len(names):
            raise ValueError("row directions must be unique")
        if sum(r.frames for r in self.rows) * self.cell.width * self.cell.height > 16_777_216:
            raise ValueError("contract exceeds 16 million pixels")
        if any(not re.fullmatch(r"#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", c) for c in self.palette):
            raise ValueError("palette entries must be #RRGGBB or #RRGGBBAA")
        return self


def rgba_hash(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def validate_frames(info: dict, frames: list[Image.Image], contract: AssetContract) -> dict:
    failures, measurements = [], []
    def fail(rule, **details):
        failures.append({"rule": rule, **details})
    expected = sum(r.frames for r in contract.rows)
    if len(frames) != expected:
        fail("frame_count", expected=expected, actual=len(frames))
    colors = {c.lower() + ("ff" if len(c) == 7 else "") for c in contract.palette}
    for i, original in enumerate(frames, 1):
        im = original.convert("RGBA")
        if im.size != (contract.cell.width, contract.cell.height):
            fail("cell_geometry", frame=i, actual=list(im.size))
        pixels = list(im.get_flattened_data())
        partial = sum(1 for p in pixels if p[3] not in (0, 255))
        if contract.alpha == "binary" and partial:
            fail("binary_alpha", frame=i, pixels=partial)
        wrong = sorted({"#%02x%02x%02x%02x" % p for p in pixels if p[3] and colors and "#%02x%02x%02x%02x" % p not in colors})
        if wrong:
            fail("palette_membership", frame=i, colors=wrong[:16])
        bbox = im.getchannel("A").getbbox()
        if bbox is None and not contract.allow_empty:
            fail("empty_frame", frame=i)
        measurements.append({"frame": i, "bounds": list(bbox) if bbox else None,
                             "foot": bbox[3] if bbox else None,
                             "center": (bbox[0] + bbox[2]) / 2 if bbox else None,
                             "rgba_sha256": rgba_hash(im)})
    cursor = 1
    tags = {t["name"]: t for t in info.get("tags", [])}
    for row in contract.rows:
        last = cursor + row.frames - 1
        tag = tags.get(row.direction)
        if not tag or tag.get("from") != cursor or tag.get("to") != last:
            fail("tag_layout", tag=row.direction, expected=[cursor, last])
        elif tag.get("aniDir", "forward") != "forward":
            fail("tag_direction", tag=row.direction, expected="forward")
        measured = [m for m in measurements[cursor-1:last] if m["bounds"]]
        if measured and contract.anchor:
            for field, limit in (("foot", contract.anchor.max_foot_drift), ("center", contract.anchor.max_center_drift)):
                drift = max(m[field] for m in measured) - min(m[field] for m in measured)
                if drift > limit:
                    fail("anchor_" + field + "_drift", tag=row.direction, actual=drift, maximum=limit)
        cursor = last + 1
    return {"schema": "aseprite-agent.qa.v1", "passed": not failures, "contract": contract.name,
            "failures": failures, "frames": measurements,
            "visual_review_required": True,
            "limits": ["Bounds measure anchors only for grounded same-subject frames.",
                       "Binary alpha and palette checks do not prove animation or artistic quality."]}
