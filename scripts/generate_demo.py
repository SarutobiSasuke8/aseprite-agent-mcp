"""Generate the README's procedural example GIF without third-party art."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/demo/synthetic-robot.gif"
COLOURS = {"body": "#315c88", "face": "#8bd5ed", "edge": "#223344"}


def frame(step: int) -> Image.Image:
    image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    bounce = step % 2
    draw.rectangle((4, 3 - bounce, 11, 9 - bounce), fill=COLOURS["edge"])
    draw.rectangle((5, 4 - bounce, 10, 8 - bounce), fill=COLOURS["body"])
    draw.point((6, 5 - bounce), fill=COLOURS["face"])
    draw.point((9, 5 - bounce), fill=COLOURS["face"])
    draw.rectangle((3, 10 - bounce, 12, 12 - bounce), fill=COLOURS["body"])
    draw.rectangle((4 + (step % 2), 13 - bounce, 6 + (step % 2), 15 - bounce), fill=COLOURS["edge"])
    draw.rectangle((9 - (step % 2), 13 - bounce, 11 - (step % 2), 15 - bounce), fill=COLOURS["edge"])
    return image.resize((128, 128), Image.Resampling.NEAREST)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    images = [frame(i) for i in range(4)]
    images[0].save(OUT, save_all=True, append_images=images[1:], duration=140, loop=0, disposal=2)
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
