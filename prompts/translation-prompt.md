# Translation Task

You are translating a Chinese xianxia webnovel into polished English prose.

## Setup

Read `prompts/translation-context.md` — it contains all established term renderings and style rules. Do not read any other glossary or style files.

## Task

1. Read `raws/chXXX.txt`
2. Translate it fully into `translated/chXXX.md`
3. Do not summarize, skip paragraphs, or omit any content
4. For any Chinese term with no entry in the context file, flag it inline as `[TERM?]` and continue

## Output format

```markdown
# Chapter XXX: [Translated Title]

---

[Full translated text]
```

## Previous chapter context

[Paste a one-line summary of where ch(N-1) ended, or leave blank if not needed]
