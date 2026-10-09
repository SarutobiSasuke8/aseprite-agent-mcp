"""Integration tests for the cast tools and real end-to-end exports.

Requires Aseprite; runs only under `pytest --run-aseprite`.
"""

import json
from pathlib import Path

import pytest

from aseprite_mcp.core.errors import LuaToolError
from aseprite_mcp.tools import batch, cast, frames, inspect, production, sprite, tags

RED, BLUE, GREEN, CLEAR = "#ff0000ff", "#0000ffff", "#00ff00ff", "#00000000"
KEY = {"r": "#ff0000", "b": "#0000ff"}


def _pixels(name, frame=1):
    return inspect.get_pixels(name, frame=frame)["pixels"]


def _walker(name):
    """4x4 sprite, two frames tagged walk_right, an arrow pointing right."""
    sprite.create_sprite(name, 4, 4)
    cast.draw_pixel_rows(name, ["r...", "rr..", "rrb.", "...."], KEY)
    frames.add_frame(name, duration_ms=150, copy_from=1)
    batch.apply_operations(name, [{"op": "offset_cel", "args": {"frame": 2, "dx": 1, "dy": 0}}])
    tags.add_tag(name, "walk_right", 1, 2)


def test_draw_pixel_rows_paints_exact_pixels():
    sprite.create_sprite("c/rows.aseprite", 4, 3)
    cast.draw_pixel_rows("c/rows.aseprite", ["rb..", ".r.b"], KEY, y=1)
    rows = _pixels("c/rows.aseprite")
    assert rows[0] == [CLEAR] * 4
    assert rows[1] == [RED, BLUE, CLEAR, CLEAR]
    assert rows[2] == [CLEAR, RED, CLEAR, BLUE]


def test_draw_pixel_rows_rejects_unknown_character():
    sprite.create_sprite("c/typo.aseprite", 4, 4)
    with pytest.raises(Exception, match="not in key"):
        cast.draw_pixel_rows("c/typo.aseprite", ["rz"], KEY)


def test_out_of_range_frame_is_an_error_not_a_clamp():
    sprite.create_sprite("c/strict.aseprite", 4, 4)
    with pytest.raises(Exception, match="out of range"):
        cast.draw_pixel_rows("c/strict.aseprite", ["r"], KEY, frame=5)
    assert _pixels("c/strict.aseprite") == [[CLEAR] * 4] * 4


def test_missing_layer_error_lists_layers():
    sprite.create_sprite("c/layers.aseprite", 4, 4)
    with pytest.raises(LuaToolError, match="Layers \\(bottom to top\\)"):
        cast.draw_pixel_rows("c/layers.aseprite", ["r"], KEY, layer="nope")


def test_layer_index_given_as_digits_string():
    sprite.create_sprite("c/index.aseprite", 4, 4)
    out = cast.draw_pixel_rows("c/index.aseprite", ["r"], KEY, layer="1")
    assert out["ok"] if "ok" in out else True
    assert _pixels("c/index.aseprite")[0][0] == RED


def test_offset_and_copy_cel_ops():
    _walker("c/walk.aseprite")
    assert _pixels("c/walk.aseprite", 2)[2] == [CLEAR, RED, RED, BLUE]
    batch.apply_operations("c/walk.aseprite", [
        {"op": "add_frame", "args": {}},
        {"op": "copy_cel", "args": {"from_frame": 1, "to_frame": 3}},
    ])
    assert _pixels("c/walk.aseprite", 3) == _pixels("c/walk.aseprite", 1)


def test_derive_mirrored_tag_flips_frames_and_keeps_other_tags():
    _walker("c/mirror.aseprite")
    out = cast.derive_mirrored_tag("c/mirror.aseprite", "walk_right", "walk_left")
    assert (out["from"], out["to"]) == (3, 4)
    info = inspect.get_sprite_info("c/mirror.aseprite")
    ranges = {t["name"]: (t["from"], t["to"]) for t in info["tags"]}
    assert ranges == {"walk_right": (1, 2), "walk_left": (3, 4)}
    assert [round(f["duration"] * 1000) for f in info["frames"]] == [100, 150, 100, 150]
    for src, dst in ((1, 3), (2, 4)):
        assert [list(reversed(r)) for r in _pixels("c/mirror.aseprite", src)] == _pixels("c/mirror.aseprite", dst)
    with pytest.raises(LuaToolError, match="already exists"):
        cast.derive_mirrored_tag("c/mirror.aseprite", "walk_right", "walk_left")


def test_copy_frames_from_reuses_empty_first_frame():
    _walker("c/base.aseprite")
    sprite.create_sprite("c/hero.aseprite", 4, 4)
    out = cast.copy_frames_from("c/hero.aseprite", "c/base.aseprite", source_tag="walk_right", new_tag="walk_right")
    assert out["reused_empty_first_frame"] is True
    info = inspect.get_sprite_info("c/hero.aseprite")
    assert info["frameCount"] == 2
    assert [(t["name"], t["from"], t["to"]) for t in info["tags"]] == [("walk_right", 1, 2)]
    assert _pixels("c/hero.aseprite", 2) == _pixels("c/base.aseprite", 2)


def test_recolor_sprite_to_new_file_swaps_and_reports():
    _walker("c/blue.aseprite")
    out = cast.recolor_sprite("c/blue.aseprite", {"#ff0000": "#0000ff", "#0000ff": "#ff0000", "#123456": "#00ff00"},
                              output="c/red.aseprite")
    counts = {r["color"]: r["pixels"] for r in out["replaced"]}
    assert counts["#ff0000"] == 10 and counts["#0000ff"] == 2
    assert out["unmatched"] == ["#123456"]
    assert _pixels("c/blue.aseprite")[2] == [RED, RED, BLUE, CLEAR]  # original untouched
    assert _pixels("c/red.aseprite")[2] == [BLUE, BLUE, RED, CLEAR]
    with pytest.raises(Exception, match="already exists"):
        cast.recolor_sprite("c/blue.aseprite", {"#ff0000": "#00ff00"}, output="c/red.aseprite")


def test_crash_safe_save_leaves_no_temporary_files(_workspace):
    _walker("c/clean.aseprite")
    folder = Path(_workspace) / "c"
    assert not list(folder.glob("*.asemcp-*"))


def _contract(name, playback="forward"):
    return {"name": name, "cell": {"width": 4, "height": 4},
            "rows": [{"tag": "walk_right", "frames": 2, "playback": playback},
                     {"tag": "walk_left", "frames": 2, "repeat": 0}],
            "palette": ["#ff0000", "#0000ff", "#00ff00"]}


def test_phaser_export_end_to_end_with_real_master(tmp_path):
    _walker("c/export.aseprite")
    cast.derive_mirrored_tag("c/export.aseprite", "walk_right", "walk_left")
    out_dir = tmp_path / "bundle"
    result = production.ase_export_phaser("c/export.aseprite", str(out_dir), _contract("hero"))
    assert result["ok"] and result["qa"]["roundtrip"]["frames_compared"] == 4
    anims = json.loads((out_dir / "animations.json").read_text())
    assert [(a["key"], a["repeat"], a["yoyo"]) for a in anims] == [("walk_right", -1, False), ("walk_left", 0, False)]
    assert 'const KEY = "hero"' in (out_dir / "loader.js").read_text()
    with pytest.raises(ValueError, match="already exists"):
        production.ase_export_phaser("c/export.aseprite", str(out_dir), _contract("hero"))
    again = production.ase_export_phaser("c/export.aseprite", str(out_dir), _contract("hero"), replace=True)
    assert again["ok"] and not list(tmp_path.glob(".bundle.asemcp-old-*"))


def test_pingpong_contract_requires_matching_tag(tmp_path):
    _walker("c/pp.aseprite")
    cast.derive_mirrored_tag("c/pp.aseprite", "walk_right", "walk_left")
    qa = production.ase_validate_asset_contract("c/pp.aseprite", _contract("pp", playback="pingpong"))
    assert not qa["passed"]
    assert qa["failures"][0]["rule"] == "tag_direction"


def test_cast_atlas_stacks_characters_in_one_sheet(tmp_path):
    from PIL import Image

    _walker("c/a.aseprite")
    cast.derive_mirrored_tag("c/a.aseprite", "walk_right", "walk_left")
    cast.recolor_sprite("c/a.aseprite", {"#ff0000": "#00ff00"}, output="c/b.aseprite")
    out_dir = tmp_path / "cast"
    result = production.ase_export_cast_atlas("town", [
        {"filename": "c/a.aseprite", "contract": _contract("nezu")},
        {"filename": "c/b.aseprite", "contract": _contract("kakei")},
    ], str(out_dir))
    assert result["ok"] and result["roundtrip"]["frames_compared"] == 8
    assert "kakei:walk_left" in result["animations"]
    atlas = json.loads((out_dir / "atlas.json").read_text())
    assert atlas["frames"]["kakei/walk_right_00"]["frame"] == {"x": 0, "y": 8, "w": 4, "h": 4}
    with Image.open(out_dir / "sheet.png") as im:
        assert im.size == (8, 16)
    failing = production.ase_export_cast_atlas("town2", [
        {"filename": "c/a.aseprite", "contract": {**_contract("nezu"), "palette": ["#ff0000"]}},
    ], str(tmp_path / "never"))
    assert failing["ok"] is False and not (tmp_path / "never").exists()
