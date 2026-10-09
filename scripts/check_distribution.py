"""Inspect built archives without extracting them; keep machine and private context out.

Usage: python scripts/check_distribution.py [dist_dir]

Generic machine-path patterns are built in. Project- or owner-specific strings
(names, private project titles) are deliberately NOT stored in this public file:
put them one per line in an untracked `.private-patterns` file at the repository
root, or in the ASEPRITE_MCP_PRIVATE_PATTERNS environment variable separated by
`;`. Only archives for the current package version are checked, so stale builds
in dist/ cannot hide or fake a result.
"""
from __future__ import annotations

import os
import re
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GENERIC = [
    re.compile(rb"[A-Za-z]:\\\\?Users\\\\?[A-Za-z0-9._-]+"),  # Windows profile paths
    re.compile(rb"/(?:home|Users)/[a-z][a-z0-9._-]+/"),       # POSIX home directories
]
FORBIDDEN_NAMES = ["BUILD_PLAN.md", "AGENTS.md", "node_modules", "workspace/", ".private-patterns"]


def private_patterns() -> list[bytes]:
    raw: list[str] = []
    local = ROOT / ".private-patterns"
    if local.is_file():
        raw += local.read_text(encoding="utf-8").splitlines()
    raw += os.environ.get("ASEPRITE_MCP_PRIVATE_PATTERNS", "").split(";")
    return [p.strip().encode("utf-8") for p in raw if p.strip() and not p.lstrip().startswith("#")]


def version() -> str:
    text = (ROOT / "src" / "aseprite_mcp" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if not match:
        raise SystemExit("Could not read __version__")
    return match.group(1)


def entries(archive: Path):
    if archive.suffix == ".whl":
        with zipfile.ZipFile(archive) as z:
            return [(n, z.read(n)) for n in z.namelist()]
    with tarfile.open(archive) as t:
        return [(m.name, t.extractfile(m).read()) for m in t.getmembers() if m.isfile()]


def main() -> int:
    dist = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist"
    ver = version()
    archives = [a for a in dist.glob("*") if ver in a.name and (a.suffix == ".whl" or a.name.endswith(".tar.gz"))]
    if len(archives) < 2:
        raise SystemExit(f"Build the wheel and sdist for version {ver} first (found {len(archives)})")
    private = private_patterns()
    for archive in archives:
        files = entries(archive)
        assert any(n.endswith("NOTICE") for n, _ in files), f"NOTICE missing in {archive.name}"
        assert any(n.endswith("LICENSE") for n, _ in files), f"LICENSE missing in {archive.name}"
        for name, data in files:
            assert not any(p in name for p in FORBIDDEN_NAMES), f"{name} must not ship"
            if name.endswith("check_distribution.py"):
                continue  # its regexes describe the generic patterns themselves
            for pattern in GENERIC:
                hit = pattern.search(data)
                assert hit is None, f"Machine path {hit.group(0)!r} in {name}"
            for p in private:
                assert p not in data, f"Private pattern in {name}"
    print(f"Distribution boundary and licence checks passed for {ver} "
          f"({len(archives)} archives, {len(private)} private patterns)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
