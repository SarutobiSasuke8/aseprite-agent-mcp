import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from PIL import Image, ImageDraw

from aseprite_mcp.tools.generated import assemble_animation, import_generated_image


def test_generated_real_master_sheet_and_timing(tmp_path, monkeypatch):
    monkeypatch.setenv("ASEPRITE_MCP_WORKSPACE", str(tmp_path))
    paths = []
    for i in range(4):
        image = Image.new("RGBA", (32, 32))
        ImageDraw.Draw(image).rectangle((9 + i, 5, 18 + i, 26), fill=(10, 140, 160, 255))
        name = f"pose-{i}.png"
        image.save(tmp_path / name)
        paths.append(name)
    base = import_generated_image(paths[0], "base", 16, 16)[0]
    assert base["verified"]
    result = assemble_animation(paths, "idle", 16, 16, durations_ms=[90, 110, 130, 150])[0]
    assert result["verified"] and result["frames"] == 4
    assert (tmp_path / "idle/master.aseprite").is_file()
    data = json.loads((tmp_path / "idle/sheet.json").read_text())
    assert [frame["duration"] for frame in data["frames"].values()] == [90, 110, 130, 150]
    assert data["meta"]["frameTags"][0]["to"] == 3
    for i in range(4):
        with Image.open(tmp_path / f"idle/frames/{i + 1:03}.png") as clean:
            with Image.open(tmp_path / f"idle/verify/{i + 1}.png") as reopened:
                assert clean.convert("RGBA").tobytes() == reopened.convert("RGBA").tobytes()


def test_generated_stdio_content_and_no_clobber(tmp_path):
    image = Image.new("RGBA", (16, 16))
    ImageDraw.Draw(image).rectangle((4, 3, 10, 12), fill=(20, 160, 180, 255))
    image.save(tmp_path / "pose.png")
    async def proof():
        params = StdioServerParameters(command=sys.executable, args=["-m", "aseprite_mcp.agent_server"],
            env={**os.environ, "ASEPRITE_MCP_WORKSPACE": str(tmp_path),
                 "ASEPRITE_MCP_TOOLS": "core", "ASEPRITE_MCP_ALLOW_ABSOLUTE": "0",
                 "ASEPRITE_AGENT_ALLOWED_ROOTS": "[]"})
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                for name, inputs in [
                    ("import_generated_image", {"filename": "pose.png", "output_directory": "base"}),
                    ("assemble_animation", {"filenames": ["pose.png", "pose.png"], "output_directory": "idle"}),
                ]:
                    result = await session.call_tool(name, inputs)
                    assert not result.isError, result
                    assert any(item.type == "image" for item in result.content)
                    assert any(item.type == "text" and '"verified": true' in item.text for item in result.content)
                    again = await session.call_tool(name, inputs)
                    assert again.isError
    asyncio.run(proof())
