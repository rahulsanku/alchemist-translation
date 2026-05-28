"""
Scans drafts/ for lines with untranslated Chinese characters and fixes them
in-place via targeted DeepSeek API calls. Only operates on the drafts/ folder.

Each affected line is sent with a small window of surrounding context so
DeepSeek can translate the Chinese portion naturally. The rest of the file
is untouched.

Usage:
    python fix_drafts.py                     # fix all drafts
    python fix_drafts.py --chapters 775,778  # fix specific chapters
    python fix_drafts.py --dry-run           # show issues without fixing

Requirements:
    pip install openai
    Set DEEPSEEK_API_KEY environment variable
"""

import argparse
import asyncio
import os
import re
from pathlib import Path

from openai import AsyncOpenAI

ROOT = Path(__file__).parent
DRAFTS_DIR = ROOT / "drafts"

CHINESE_RE = re.compile(r"[一-鿿㐀-䶿豈-﫿]")
CONTEXT_LINES = 3
CONCURRENCY = 5
MODEL = "deepseek-chat"

FIX_PROMPT = """\
You are editing an English translation of a Chinese xianxia cultivation novel.
The excerpt below contains one line marked with >>> and <<<.
That line has one or more untranslated Chinese words or characters mixed into otherwise English prose.

Your job: replace every Chinese character in that marked line with appropriate English that fits the context.
Keep every non-Chinese word on that line exactly as-is.
The output must contain zero Chinese characters.
Return ONLY the corrected line — no >>> or <<< markers, no explanation, nothing else."""


async def fix_line(
    client: AsyncOpenAI,
    sem: asyncio.Semaphore,
    lines: list[str],
    target_idx: int,
) -> tuple[int, str | None]:
    start = max(0, target_idx - CONTEXT_LINES)
    end = min(len(lines), target_idx + CONTEXT_LINES + 1)

    block = []
    for i in range(start, end):
        text = lines[i].rstrip()
        block.append(f">>> {text} <<<" if i == target_idx else text)

    async with sem:
        try:
            resp = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": FIX_PROMPT},
                    {"role": "user", "content": "\n".join(block)},
                ],
                temperature=0.1,
                max_tokens=500,
            )
            corrected = resp.choices[0].message.content.strip()
            # Strip markers if the model echoed them back
            corrected = corrected.replace(">>>", "").replace("<<<", "").strip()
            return target_idx, corrected
        except Exception as exc:
            print(f"    ERROR on line {target_idx + 1}: {exc}")
            return target_idx, None


async def fix_file(
    client: AsyncOpenAI, sem: asyncio.Semaphore, filepath: Path
) -> int:
    lines = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
    affected = [i for i, line in enumerate(lines) if CHINESE_RE.search(line)]
    if not affected:
        return 0

    print(f"  {filepath.name} — {len(affected)} line(s) to fix")

    results = await asyncio.gather(*[fix_line(client, sem, lines, i) for i in affected])

    fixed = 0
    for idx, corrected in results:
        if corrected is None:
            continue
        if CHINESE_RE.search(corrected):
            print(f"    [{idx + 1}] WARNING: model did not remove Chinese — skipping")
            continue
        original = lines[idx].rstrip("\n\r")
        ending = lines[idx][len(original):]  # preserve \n or \r\n
        lines[idx] = corrected + ending
        print(f"    [{idx + 1}] {original.strip()[:70]}")
        print(f"         → {corrected.strip()[:70]}")
        fixed += 1

    filepath.write_text("".join(lines), encoding="utf-8")
    return fixed


async def run(filepaths: list[Path], dry_run: bool = False) -> None:
    # Scan phase — find files with issues before touching anything
    to_fix: dict[Path, list[tuple[int, str]]] = {}
    for fp in sorted(filepaths):
        lines = fp.read_text(encoding="utf-8").splitlines()
        hits = [(i, line) for i, line in enumerate(lines) if CHINESE_RE.search(line)]
        if hits:
            to_fix[fp] = hits

    if not to_fix:
        print("All drafts are clean — no Chinese characters found.")
        return

    total = sum(len(v) for v in to_fix.values())
    print(f"Found {total} line(s) with Chinese across {len(to_fix)} file(s).\n")

    if dry_run:
        for fp, hits in to_fix.items():
            print(f"  {fp.name}:")
            for line_num, line in hits:
                print(f"    line {line_num + 1}: {line.strip()[:80]}")
        return

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("ERROR: DEEPSEEK_API_KEY environment variable not set")

    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    sem = asyncio.Semaphore(CONCURRENCY)

    results = await asyncio.gather(*[fix_file(client, sem, fp) for fp in to_fix])
    print(f"\nDone — fixed {sum(results)} line(s) across {len(to_fix)} file(s).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix untranslated Chinese terms in drafts/ files"
    )
    parser.add_argument(
        "--chapters", help="Comma-separated chapter numbers e.g. 775,778"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print issues without making any changes",
    )
    args = parser.parse_args()

    if args.chapters:
        nums = [int(x.strip()) for x in args.chapters.split(",")]
        filepaths = [
            DRAFTS_DIR / f"ch{n}.md"
            for n in nums
            if (DRAFTS_DIR / f"ch{n}.md").exists()
        ]
        missing = [n for n in nums if not (DRAFTS_DIR / f"ch{n}.md").exists()]
        if missing:
            print(f"Warning: not found in drafts/: {missing}")
    else:
        filepaths = sorted(DRAFTS_DIR.glob("*.md"))

    if not filepaths:
        raise SystemExit("No matching draft files found in drafts/.")

    asyncio.run(run(filepaths, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
