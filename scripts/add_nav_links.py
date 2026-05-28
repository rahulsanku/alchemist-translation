#!/usr/bin/env python3
"""Add previous/next chapter navigation links to all translated chapter files."""

import os
import re
from pathlib import Path

TRANSLATED_DIR = Path(__file__).parent.parent / "translated"
NAV_MARKER = "<!-- nav-links -->"


def extract_chapter_num(filename: str) -> float:
    match = re.match(r"ch(\d+(?:\.\d+)?)\.md$", filename)
    if match:
        return float(match.group(1))
    return float("inf")


def make_nav_section(prev_file: str | None, next_file: str | None) -> str:
    parts = []
    if prev_file:
        parts.append(f"[← Previous Chapter]({prev_file})")
    if next_file:
        parts.append(f"[Next Chapter →]({next_file})")
    nav_line = " | ".join(parts)
    return f"\n---\n\n{NAV_MARKER}\n{nav_line}\n"


def main():
    files = sorted(
        [f.name for f in TRANSLATED_DIR.glob("ch*.md")],
        key=extract_chapter_num,
    )

    updated = 0
    skipped = 0

    for i, filename in enumerate(files):
        path = TRANSLATED_DIR / filename
        content = path.read_text(encoding="utf-8")

        if NAV_MARKER in content:
            skipped += 1
            continue

        prev_file = files[i - 1] if i > 0 else None
        next_file = files[i + 1] if i < len(files) - 1 else None

        nav = make_nav_section(prev_file, next_file)
        content = content.rstrip() + nav
        path.write_text(content, encoding="utf-8")
        updated += 1

    print(f"Done. Updated: {updated}, Already had nav: {skipped}, Total: {len(files)}")


if __name__ == "__main__":
    main()
