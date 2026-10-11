"""Checked local release fallback. Publishing requires an explicit flag and token."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="Expected release tag (defaults to v<package version>)")
    parser.add_argument("--publish", action="store_true", help="Publish to PyPI and MCP Registry")
    args = parser.parse_args()

    if output("git", "status", "--porcelain"):
        parser.error("Git tree must be clean")
    source = (ROOT / "src/aseprite_mcp/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', source)
    if match is None:
        parser.error("Cannot read package version")
    version = match.group(1)
    tag = args.tag or f"v{version}"
    if tag != f"v{version}":
        parser.error(f"Tag {tag} does not match package version {version}")
    if output("git", "tag", "--list", tag):
        tagged_head = output("git", "rev-list", "-n", "1", tag)
        if tagged_head != output("git", "rev-parse", "HEAD"):
            parser.error(f"Tag {tag} does not point at HEAD")
    if args.publish and not os.environ.get("UV_PUBLISH_TOKEN"):
        parser.error("--publish requires UV_PUBLISH_TOKEN")

    uv = shutil.which("uv")
    if not uv:
        parser.error("uv is required")
    run(uv, "sync", "--locked", "--group", "dev")
    run(uv, "run", "ruff", "check", "src", "tests", "scripts")
    run(uv, "run", "pytest")
    run(uv, "build")
    run(uv, "run", "python", "scripts/check_distribution.py")

    print(f"Ready for {tag}. No remote publication has run.")
    print("PyPI: uv publish --token <UV_PUBLISH_TOKEN>")
    print("Registry: mcp-publisher validate; mcp-publisher login github; mcp-publisher publish")
    if args.publish:
        publisher = shutil.which("mcp-publisher")
        if not publisher:
            parser.error("mcp-publisher is required for --publish")
        run(uv, "publish")
        run(publisher, "validate")
        run(publisher, "login", "github")
        run(publisher, "publish")


if __name__ == "__main__":
    main()
