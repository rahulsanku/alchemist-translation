"""
fix_nascent_soul.py — Find draft paragraphs where 'Nascent Soul' was used
but the corresponding raw Chinese paragraph contains 化神 (should be
'Divine Transformation'), then optionally replace them.

Raw files have no blank lines — each line is one paragraph.
Draft files separate paragraphs with blank lines.
Alignment is ~1:1 after skipping the title paragraph in the draft.

Usage:
    python fix_nascent_soul.py            # dry-run: write review.txt
    python fix_nascent_soul.py --fix      # apply confirmed replacements
"""

import argparse
import os
import re
import sys

DRAFTS_DIR = "drafts"
RAWS_DIR   = "raws"
REVIEW_OUT = "nascent_soul_review.txt"
WINDOW     = 3   # raw lines to search either side of the estimated position

REPLACEMENTS = [
    ("Nascent Soul great cultivator", "Divine Transformation great cultivator"),
    ("Nascent Soul great power",      "Divine Transformation great power"),
    ("Nascent Soul cultivator",       "Divine Transformation cultivator"),
    ("Nascent Soul True Lord",        "Void Refining True Lord"),
    ("Nascent Soul stage",            "Divine Transformation stage"),
    ("Nascent Soul realm",            "Divine Transformation realm"),
    ("Nascent Soul-level",            "Divine Transformation-level"),
    ("Nascent Soul",                  "Divine Transformation"),
]


def load_raw_lines(ch_num: int) -> list[str]:
    path = os.path.join(RAWS_DIR, f"ch{ch_num}.txt")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def load_draft_paras(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return [b.strip() for b in re.split(r"\n{2,}", text) if b.strip()]


def raw_window_has_huashen(raw_lines: list[str], r_idx: int) -> bool:
    lo = max(0, r_idx - WINDOW)
    hi = min(len(raw_lines), r_idx + WINDOW + 1)
    return any("化神" in line for line in raw_lines[lo:hi])


def raw_window_has_yuanying(raw_lines: list[str], r_idx: int) -> bool:
    lo = max(0, r_idx - WINDOW)
    hi = min(len(raw_lines), r_idx + WINDOW + 1)
    return any("元婴" in line for line in raw_lines[lo:hi])


def apply_replacements(text: str) -> str:
    for bad, good in REPLACEMENTS:
        text = text.replace(bad, good)
    return text


def process_chapter(draft_path: str, ch_num: int, fix: bool, log) -> int:
    raw_lines  = load_raw_lines(ch_num)
    if not raw_lines:
        return 0

    draft_paras = load_draft_paras(draft_path)
    n_draft = len(draft_paras)
    n_raw   = len(raw_lines)

    # Draft para 0 is the title; raw starts at content directly.
    # Offset by 1 so draft content para 1 ≈ raw line 0.
    def estimate_raw_idx(d_idx: int) -> int:
        content_idx = max(0, d_idx - 1)        # skip title paragraph
        # scale to raw length
        return round(content_idx * n_raw / max(n_draft - 1, 1))

    changed_paras: dict[int, str] = {}

    for d_idx, para in enumerate(draft_paras):
        if "Nascent Soul" not in para:
            continue

        r_est = estimate_raw_idx(d_idx)
        has_huashen  = raw_window_has_huashen(raw_lines, r_est)
        has_yuanying = raw_window_has_yuanying(raw_lines, r_est)

        # Only flag when 化神 is in the window AND 元婴 is NOT
        # (if both appear, the window straddles a boundary — skip to be safe)
        if not has_huashen or has_yuanying:
            continue

        new_para = apply_replacements(para)
        if new_para == para:
            continue

        changed_paras[d_idx] = new_para

        # Log for review
        for line in para.splitlines():
            if "Nascent Soul" in line:
                log.write(f"[ch{ch_num} para {d_idx}] - {line.strip()[:110]}\n")
        for line in new_para.splitlines():
            if "Divine Transformation" in line or "Void Refining" in line:
                log.write(f"[ch{ch_num} para {d_idx}] + {line.strip()[:110]}\n")
        # Show the raw window for manual verification
        lo = max(0, r_est - WINDOW)
        hi = min(len(raw_lines), r_est + WINDOW + 1)
        raw_snippet = " | ".join(raw_lines[lo:hi])[:120]
        log.write(f"  raw[{lo}-{hi-1}]: {raw_snippet}\n\n")

    if not changed_paras or not fix:
        return len(changed_paras)

    with open(draft_path, encoding="utf-8") as f:
        original = f.read()

    updated = original
    for d_idx, new_para in changed_paras.items():
        old_para = draft_paras[d_idx]
        updated  = updated.replace(old_para, new_para, 1)

    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(updated)

    return len(changed_paras)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true",
                        help="Apply replacements (default: dry-run only)")
    args = parser.parse_args()

    pattern = re.compile(r"ch(\d+(?:\.\d+)?)\.md$")
    total   = 0

    with open(REVIEW_OUT, "w", encoding="utf-8") as log:
        log.write("Nascent Soul -> Divine Transformation review\n")
        log.write("=" * 60 + "\n\n")

        for fname in sorted(os.listdir(DRAFTS_DIR)):
            m = pattern.match(fname)
            if not m:
                continue
            ch_num     = int(float(m.group(1)))
            draft_path = os.path.join(DRAFTS_DIR, fname)

            with open(draft_path, encoding="utf-8") as f:
                if "Nascent Soul" not in f.read():
                    continue

            n = process_chapter(draft_path, ch_num, args.fix, log)
            if n:
                print(f"  ch{ch_num}: {n} paragraph(s) flagged")
            total += n

    mode = "Fixed" if args.fix else "Would fix"
    print(f"\n{mode} {total} paragraph(s). See {REVIEW_OUT} for details.")
    if not args.fix and total:
        print("Review the file, then run with --fix to apply.")


if __name__ == "__main__":
    main()
