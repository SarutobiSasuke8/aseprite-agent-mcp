import asyncio
import hashlib

import pytest
from PIL import Image, ImageDraw

from aseprite_mcp.core.errors import WorkspaceError
from aseprite_mcp.tools import generated as g


def pose(size=16, offset=0):
    image = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(image)
    draw.rectangle((5 + offset, 4, 9 + offset, 12), fill=(20, 160, 180, 255))
    draw.point((7 + offset, 5), fill=(255, 160, 20, 255))
    return image


def test_agent_unit_generated_shared_palette_binary_alpha_and_determinism():
    images = [pose(), pose(offset=2)]
    images[0].putpixel((0, 0), (200, 180, 100, 15))
    frames, palette, transforms = g.clean_frames(images, 16, 16, colours=2, alignment="bounding-box")
    assert len(palette) <= 2
    for frame in frames:
        assert set(frame.getchannel("A").get_flattened_data()) <= {0, 255}
        assert frame.getchannel("A").getbbox()[3] == 16
    again, same_palette, same_transforms = g.clean_frames(images, 16, 16, colours=2, alignment="bounding-box")
    assert [f.tobytes() for f in frames] == [f.tobytes() for f in again]
    assert palette == same_palette and transforms == same_transforms


def test_agent_unit_generated_border_removal_keeps_enclosed_colour():
    image = Image.new("RGBA", (7, 7), "white")
    ImageDraw.Draw(image).rectangle((1, 1, 5, 5), fill="black")
    image.putpixel((3, 3), (255, 255, 255, 255))
    clean = g.remove_background(image, "#ffffff", 0, 128)
    assert clean.getpixel((0, 0))[3] == 0
    assert clean.getpixel((3, 3)) == (255, 255, 255, 255)


def test_agent_unit_generated_majority_and_outline():
    image = Image.new("RGBA", (4, 4), "red")
    image.putpixel((0, 0), (0, 0, 255, 255))
    assert g.downsample(image, (1, 1), "majority").getpixel((0, 0)) == (255, 0, 0, 255)
    frames, palette, _ = g.clean_frames([pose()], 16, 16, palette=["#14a0b4", "#ffa014"], outline="#000000")
    assert len(palette) == 3
    assert frames[0].getpixel((4, 4)) == (0, 0, 0, 255)


def test_agent_unit_generated_anchor_alignment_and_clipping():
    frames, _, _ = g.clean_frames([pose(), pose(offset=2)], 16, 16, alignment="anchor", anchors=[[7, 12], [9, 12]])
    assert frames[0].tobytes() == frames[1].tobytes()
    with pytest.raises(ValueError, match="clip"):
        g.clean_frames([pose()], 16, 16, alignment="anchor", anchors=[[0, 0]])
    with pytest.raises(ValueError, match="anchors require"):
        g.clean_frames([pose()], 16, 16, anchors=[[7, 12]])


@pytest.mark.parametrize("kwargs", [
    {"width": 0}, {"height": 257}, {"width": True}, {"colours": 0},
    {"palette": []}, {"palette": ["red"]}, {"alpha_threshold": 0},
    {"method": "linear"}, {"background_tolerance": -1}, {"outline": "bad"},
])
def test_agent_unit_generated_invalid_cleanup(kwargs):
    args = {"width": 16, "height": 16, **kwargs}
    with pytest.raises(ValueError):
        g.clean_frames([pose()], **args)


def test_agent_unit_generated_limits_and_input_integrity(tmp_path, monkeypatch):
    monkeypatch.setenv("ASEPRITE_MCP_WORKSPACE", str(tmp_path))
    source = tmp_path / "source.png"
    pose().save(source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert g.load_png("source.png").size == (16, 16)
    with pytest.raises(WorkspaceError):
        g.load_png("../source.png")
    with pytest.raises(ValueError, match="empty"):
        g.clean_frames([Image.new("RGBA", (16, 16))], 16, 16)
    with pytest.raises(ValueError, match="million"):
        g.clean_frames([pose()] * 17, 256, 256)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest


def test_agent_unit_generated_no_output_when_engine_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("ASEPRITE_MCP_WORKSPACE", str(tmp_path))
    pose().save(tmp_path / "source.png")
    def fail(*args, **kwargs):
        raise RuntimeError("synthetic engine failure")
    monkeypatch.setattr(g, "run_lua", fail)
    with pytest.raises(RuntimeError, match="synthetic"):
        g.import_generated_image("source.png", "failed", 16, 16)
    assert not (tmp_path / "failed").exists()
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "keep.txt").write_text("keep")
    with pytest.raises(ValueError, match="exists"):
        g.import_generated_image("source.png", "existing", 16, 16)
    assert (existing / "keep.txt").read_text() == "keep"


def test_agent_unit_generated_default_tool_schema():
    from aseprite_mcp.agent_server import configure, mcp
    configure()
    tools = {tool.name: tool for tool in asyncio.run(mcp.list_tools())}
    assert {"import_generated_image", "assemble_animation"} <= tools.keys()
    assert tools["assemble_animation"].inputSchema["properties"]["alignment"]["enum"] == ["bounding-box", "anchor", "none"]
    for name in ("assemble_animation", "import_generated_image"):
        assert tools[name].inputSchema["properties"]["palette_first"]["type"] == "boolean"


def test_agent_unit_generated_palette_first_majority_counts_shade_clusters():
    image = Image.new("RGBA", (3, 3), (240, 30, 30, 255))
    # Five close teals outvote four identical reds only after palette snapping.
    for i in range(5):
        image.putpixel((i % 3, i // 3), (10 + i, 160, 180, 255))
    kwargs = {"method": "majority", "palette": ["#0aa0b4", "#f01e1e"]}
    old, _, _ = g.clean_frames([image], 1, 1, **kwargs)
    new, palette, _ = g.clean_frames([image], 1, 1, palette_first=True, **kwargs)
    assert old[0].getpixel((0, 0)) == (240, 30, 30, 255)
    assert new[0].getpixel((0, 0)) == (10, 160, 180, 255)
    assert palette == ["#0aa0b4", "#f01e1e"]
    assert g.clean_frames([image], 1, 1, palette_first=True, **kwargs)[0][0].tobytes() == new[0].tobytes()


def test_agent_unit_generated_hires_palette_anchor_and_source_preservation():
    images = [pose(256), pose(256, offset=2)]
    before = [hashlib.sha256(im.tobytes()).hexdigest() for im in images]
    frames, palette, _ = g.clean_frames(images, 128, 128, colours=48, palette_first=True,
                                      method="majority", alignment="anchor", anchors=[[8, 12], [10, 12]])
    assert len(palette) <= 48
    assert all(frame.size == (128, 128) for frame in frames)
    assert all(set(frame.getchannel("A").get_flattened_data()) <= {0, 255} for frame in frames)
    assert frames[0].tobytes() == frames[1].tobytes()
    assert [hashlib.sha256(im.tobytes()).hexdigest() for im in images] == before
    with pytest.raises(ValueError, match="boolean"):
        g.clean_frames(images, 128, 128, palette_first="yes")


def test_agent_unit_generated_sparse_source_palette_sampling():
    image = Image.new("RGBA", (512, 512))
    image.putpixel((1, 1), (20, 160, 180, 255))
    frames, palette = g.quantize_frames([image], 48, None, sample_limit=65_536)
    assert palette == ["#14a0b4"]
    assert frames[0].getpixel((1, 1)) == (20, 160, 180, 255)
