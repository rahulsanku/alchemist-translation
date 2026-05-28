"""
Compiles all glossary YAMLs + style rules into prompts/translation-context.md.
Run this whenever you update any glossary file.

Usage: python scripts/build_context.py
"""

from pathlib import Path
import re

ROOT = Path(__file__).parent.parent
GLOSSARY_DIR = ROOT / "glossary"
OUT = ROOT / "prompts" / "translation-context.md"

SECTIONS = [
    ("characters", "Characters"),
    ("places",     "Places & Regions"),
    ("sects",      "Sects & Organizations"),
    ("techniques", "Techniques & Arts"),
    ("items",      "Items & Materials"),
    ("realms",     "Realms & States"),
]


def load_entries(name: str) -> list[dict]:
    """Parse glossary YAML with regex — immune to unquoted colons in notes values."""
    text = (GLOSSARY_DIR / f"{name}.yml").read_text(encoding="utf-8")
    entries = []
    # Each entry starts with "  - chinese: <value>"
    for block in re.split(r"\n  - ", text):
        if not block.startswith("chinese:"):
            continue
        entry = {}
        lines = block.splitlines()
        # First line: "chinese: <value>"
        entry["chinese"] = lines[0].split(":", 1)[1].strip()
        # Remaining lines: "    key: value"
        for line in lines[1:]:
            m = re.match(r"\s+(english|notes):\s*(.+)", line)
            if m:
                entry[m.group(1)] = m.group(2).strip()
        if "chinese" in entry and "english" in entry:
            entries.append(entry)
    return entries


def fmt(entry: dict) -> str:
    return f"- {entry['chinese']} → **{entry['english']}**"


def build():
    lines = [
        "# Translation Reference",
        "",
        "Single authoritative source for all established renderings. Do not deviate.",
        "",
    ]

    for key, label in SECTIONS:
        lines += [f"## {label}", ""]
        for entry in load_entries(key):
            lines.append(fmt(entry))
        lines.append("")

    lines += [
        "## Style Rules",
        "",
        "- Names: keep in pinyin",
        "- Technique names: mythic, cultivation-oriented English",
        "- Preserve Daoist/Buddhist atmosphere and cultivation tone",
        "- Prioritize readability over literalism; keep prose fluid",
        "- Combat: fast-paced, tense, preserve technique names exactly",
        "- Dialogue: preserve personality, hierarchy, master/disciple tone",
        "- Never summarize, omit paragraphs, or flatten cultivation exposition",
        "- Unknown terms: flag inline as `[TERM?]`",
        "",
    ]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    size_kb = OUT.stat().st_size // 1024
    print(f"Done — {OUT.name} ({size_kb} KB, {len(lines)} lines)")


if __name__ == "__main__":
    build()
