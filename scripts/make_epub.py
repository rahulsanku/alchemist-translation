"""
make_epub.py — Bundle translated chapters into an EPUB.

Usage:
    python make_epub.py 750 1000
    python make_epub.py 750 1000 --output my_book.epub
"""

import argparse
import os
import re
import sys

import markdown
from ebooklib import epub

TRANSLATED_DIR = os.path.join(os.path.dirname(__file__), "..", "translated")


def chapter_sort_key(num_str: str) -> float:
    """Allow fractional chapters like 715.5."""
    return float(num_str)


def find_chapters(start: int, end: int) -> list[tuple[float, str]]:
    """Return sorted (num, filepath) pairs for chapters in [start, end]."""
    pattern = re.compile(r"^ch(\d+(?:\.\d+)?)\.md$")
    found = []
    for fname in os.listdir(TRANSLATED_DIR):
        m = pattern.match(fname)
        if not m:
            continue
        num = float(m.group(1))
        if start <= num <= end:
            found.append((num, os.path.join(TRANSLATED_DIR, fname)))
    found.sort(key=lambda x: x[0])
    return found


def extract_title(content: str, num: float) -> str:
    """Pull the first # heading as the chapter title, fallback to Chapter N."""
    m = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    n = int(num) if num == int(num) else num
    return f"Chapter {n}"


def md_to_html(content: str) -> str:
    return markdown.markdown(
        content,
        extensions=["extra", "sane_lists"],
    )


def build_epub(chapters: list[tuple[float, str]], output_path: str, start: int, end: int) -> None:
    book = epub.EpubBook()
    book.set_identifier(f"alchemist-ch{start}-ch{end}")
    book.set_title(f"The Alchemist God — Chapters {start}–{end}")
    book.set_language("en")
    book.add_author("Translated Edition")

    epub_chapters = []
    for num, path in chapters:
        with open(path, encoding="utf-8") as f:
            raw = f.read().lstrip("﻿")

        title = extract_title(raw, num)
        html_body = md_to_html(raw)

        n_display = int(num) if num == int(num) else num
        file_name = f"ch{n_display}.xhtml"

        chapter = epub.EpubHtml(title=title, file_name=file_name, lang="en")
        chapter.content = f"<html><body>{html_body}</body></html>"
        book.add_item(chapter)
        epub_chapters.append(chapter)

    book.toc = tuple(epub_chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = ["nav"] + epub_chapters

    epub.write_epub(output_path, book)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bundle translated chapters into an EPUB.")
    parser.add_argument("start", type=int, help="First chapter number (inclusive)")
    parser.add_argument("end", type=int, help="Last chapter number (inclusive)")
    parser.add_argument("--output", "-o", help="Output .epub filename")
    args = parser.parse_args()

    chapters = find_chapters(args.start, args.end)
    if not chapters:
        print(f"No translated chapters found between {args.start} and {args.end}.")
        sys.exit(1)

    output = args.output or f"alchemist_ch{args.start}-ch{args.end}.epub"
    print(f"Bundling {len(chapters)} chapters ({chapters[0][0]:.10g}-{chapters[-1][0]:.10g}) -> {output}")

    build_epub(chapters, output, args.start, args.end)
    print("Done.")


if __name__ == "__main__":
    main()
