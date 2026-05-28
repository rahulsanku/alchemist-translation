"""
Batch translate raw chapters via DeepSeek API into drafts/chNNN.md.
Claude then polishes each draft locally (no API cost).

Usage:
    python translate_batch.py --start 761 --end 800
    python translate_batch.py --chapters 761,762,763

Requirements:
    pip install openai
    Set DEEPSEEK_API_KEY environment variable
"""

import argparse
import asyncio
import os
from pathlib import Path

from openai import AsyncOpenAI

ROOT = Path(__file__).parent
RAWS_DIR = ROOT / "raws"
DRAFTS_DIR = ROOT / "drafts"
TRANSLATED_DIR = ROOT / "translated"
CONTEXT_FILE = ROOT / "prompts" / "translation-context.md"

CONCURRENCY = 8   # parallel requests — stay under DeepSeek's rate limits
MODEL = "deepseek-chat"  # DeepSeek-V3

SYSTEM_PROMPT = """\
You are a professional Chinese-to-English translator for a xianxia cultivation web novel called "The Alchemist" (炼丹师).
Your task is to translate each chapter from Chinese into fluent English prose.

{context}

Rules:
- Translate from Chinese to English. The output must be entirely in English.
- Follow ALL glossary entries exactly. Never invent alternate renderings.
- Flag any unrecognised term inline as [TERM?] so the editor can catch it.
- Output ONLY the translated Markdown. Use # for the chapter title, no preamble or notes.
- Keep the prose fluid and readable; preserve the cultivation/Daoist atmosphere.
- Do not summarise, merge, or skip any paragraph.
"""


async def translate_one(client: AsyncOpenAI, sem: asyncio.Semaphore, ch_num: int, context: str) -> None:
    raw_path = RAWS_DIR / f"ch{ch_num}.txt"
    draft_path = DRAFTS_DIR / f"ch{ch_num}.md"
    translated_path = TRANSLATED_DIR / f"ch{ch_num}.md"

    if translated_path.exists():
        print(f"  ch{ch_num} — already translated, skipping")
        return
    if draft_path.exists():
        print(f"  ch{ch_num} — draft already exists, skipping")
        return
    if not raw_path.exists():
        print(f"  ch{ch_num} — raw file not found, skipping")
        return

    raw_text = raw_path.read_text(encoding="utf-8")
    system = SYSTEM_PROMPT.format(context=context)

    async with sem:
        try:
            print(f"  ch{ch_num} — requesting...")
            resp = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Translate the following chapter from Chinese to English:\n\n{raw_text}"},
                ],
                temperature=0.2,
            )
            text = resp.choices[0].message.content.strip()
            draft_path.write_text(text, encoding="utf-8")
            tok = resp.usage.total_tokens if resp.usage else "?"
            cost = resp.usage.total_tokens * 0.0000008 if resp.usage else 0  # rough ~$0.8/M blended
            print(f"  ch{ch_num} — done  ({tok} tokens, ~${cost:.4f})")
        except Exception as exc:
            print(f"  ch{ch_num} — ERROR: {exc}")


async def run(chapter_nums: list[int]) -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("ERROR: DEEPSEEK_API_KEY environment variable not set")

    DRAFTS_DIR.mkdir(exist_ok=True)
    context = CONTEXT_FILE.read_text(encoding="utf-8")

    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    sem = asyncio.Semaphore(CONCURRENCY)

    print(f"Translating {len(chapter_nums)} chapter(s) with concurrency={CONCURRENCY}\n")
    await asyncio.gather(*[translate_one(client, sem, n, context) for n in chapter_nums])
    print(f"\nDone. Drafts in: {DRAFTS_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch translate chapters via DeepSeek")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--start", type=int, help="First chapter number")
    group.add_argument("--chapters", help="Comma-separated chapter numbers e.g. 761,762,763")
    parser.add_argument("--end", type=int, help="Last chapter number (used with --start)")
    args = parser.parse_args()

    if args.start is not None:
        end = args.end if args.end is not None else args.start
        chapters = list(range(args.start, end + 1))
    else:
        chapters = [int(x.strip()) for x in args.chapters.split(",")]

    asyncio.run(run(chapters))


if __name__ == "__main__":
    main()
