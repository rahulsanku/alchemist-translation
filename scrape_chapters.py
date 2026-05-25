"""
Scraper for 69shuba.com — downloads raw chapter text into raws/chNNN.txt files.
Uses a real Chromium browser (Playwright) to bypass anti-bot protection.

Usage:
    # Download ch559-700 starting from a known URL, following next-chapter buttons:
    python scrape_chapters.py --start 559 --url "https://www.69shuba.com/txt/47135/36894996" --end 700

Requirements:
    pip install playwright beautifulsoup4
    python -m playwright install chromium
"""

import argparse
import time
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page

BOOK_ID = "47135"
BASE_URL = "https://www.69shuba.com"
RAWS_DIR = Path(__file__).parent / "raws"

DELAY = 2.0  # seconds between chapter requests

NEXT_SELECTORS = [
    "a.next_chapter",
    "a.next",
    ".p_next a",
    "a[rel='next']",
    "a:has-text('下一章')",   # "next chapter" in Chinese
    "a:has-text('下一页')",   # "next page"
]


def extract_chapter_text(soup: BeautifulSoup) -> str:
    for selector in ["div.txtnav", "div#content", "div.content", "div.chapter-content", "div#chaptercontent"]:
        el = soup.select_one(selector)
        if el:
            for tag in el(["script", "style"]):
                tag.decompose()
            return el.get_text("\n", strip=True)
    divs = soup.find_all("div")
    if divs:
        best = max(divs, key=lambda d: len(d.get_text()))
        for tag in best(["script", "style"]):
            tag.decompose()
        return best.get_text("\n", strip=True)
    return ""


def find_next_url(page: Page) -> str | None:
    """Try each known selector to find the next-chapter link."""
    for selector in NEXT_SELECTORS:
        try:
            el = page.query_selector(selector)
            if el:
                href = el.get_attribute("href")
                if href and f"/txt/{BOOK_ID}/" in href:
                    return href if href.startswith("http") else BASE_URL + href
        except Exception:
            continue
    return None


def cmd_download(start_ch: int, start_url: str, end_ch: int):
    total = end_ch - start_ch + 1
    print(f"Will download ch{start_ch}–ch{end_ch} ({total} chapters)\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        current_url = start_url

        for ch_num in range(start_ch, end_ch + 1):
            out_path = RAWS_DIR / f"ch{ch_num}.txt"

            if out_path.exists() and out_path.stat().st_size > 0:
                print(f"  ch{ch_num} — already has content, skipping")
                # still need to navigate to get the next URL
                if ch_num < end_ch:
                    page.goto(current_url, wait_until="domcontentloaded", timeout=30000)
                    nxt = find_next_url(page)
                    if not nxt:
                        print(f"  ch{ch_num} — could not find next-chapter link, stopping")
                        break
                    current_url = nxt
                    time.sleep(DELAY)
                continue

            try:
                page.goto(current_url, wait_until="domcontentloaded", timeout=30000)
                soup = BeautifulSoup(page.content(), "html.parser")
                text = extract_chapter_text(soup)

                if not text:
                    print(f"  ch{ch_num} — WARNING: no text extracted from {current_url}")
                else:
                    out_path.write_text(text, encoding="utf-8")
                    print(f"  ch{ch_num} — {len(text)} chars saved  ({current_url})")

                if ch_num < end_ch:
                    nxt = find_next_url(page)
                    if not nxt:
                        print(f"  ch{ch_num} — could not find next-chapter link, stopping")
                        break
                    current_url = nxt

            except Exception as e:
                print(f"  ch{ch_num} — ERROR: {e}")

            time.sleep(DELAY)

        browser.close()
    print("\nDone.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True, help="Starting file number (e.g. 559)")
    parser.add_argument("--end", type=int, required=True, help="Ending file number (e.g. 700)")
    parser.add_argument("--url", required=True, help="URL of the first chapter to download")
    args = parser.parse_args()

    cmd_download(args.start, args.url, args.end)


if __name__ == "__main__":
    main()


