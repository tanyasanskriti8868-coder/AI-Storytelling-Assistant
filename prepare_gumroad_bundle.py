#!/usr/bin/env python3
"""Create a Gumroad-ready zip bundle from the repository."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)
ZIP_PATH = DIST / "arcanova_gumroad_source.zip"

INCLUDE = [
    "app.py",
    "config.py",
    "qwen_engine.py",
    "tts_engine.py",
    "requirements.txt",
    "build_exe.py",
    "README.md",
    "index.html",
    "quickstart · md",
    "GUMROAD_CHECKLIST.md",
]

with ZipFile(ZIP_PATH, "w", compression=ZIP_DEFLATED) as zf:
    for name in INCLUDE:
        path = ROOT / name
        if path.exists():
            zf.write(path, arcname=path.name)

print(f"Created: {ZIP_PATH}")
