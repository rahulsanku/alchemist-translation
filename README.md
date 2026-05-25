# Alchemist Translation

Translation workspace for:
长生从炼丹宗师开始
(An Alchemist's Path to Eternity)

## Structure

- `chapters/` → finalized polished chapters
- `raws/` → raw Chinese source text
- `translated/` → draft translations
- `glossary/` → canonical terminology
- `prompts/` → translation prompts
- `notes/` → continuity and lore tracking

## Workflow

1. Add raw Chinese chapters to `raws/`
2. Generate draft translations into `translated/`
3. Edit polished chapters into `chapters/`
4. Update glossary entries consistently
5. Track unresolved terminology in notes

## Translation Rules

- Preserve meaning over literal phrasing
- Use fluent English webnovel prose
- Keep names consistent
- Preserve cultivation terminology
- Avoid excessive localization
- Do not summarize or omit paragraphs
- Keep Chinese names in pinyin unless otherwise specified

You are translating a Chinese xianxia webnovel into polished English prose.

Rules:
- Preserve all meaning.
- Keep cultivation terms consistent.
- Translate naturally, not literally.
- Keep character names in pinyin.
- Do not summarize.
- Maintain the tone of a professional webnovel translation.
- Keep realm names recognizable.
- Explain obscure cultural references only if necessary.
- Use glossary files as authoritative.
- Preserve humor, combat flow, and internal monologue.
- Do not censor or simplify cultivation terminology.

When encountering new terminology:
- add unresolved terms to `notes/unresolved-terms.md`
- maintain continuity with prior chapters

Example Entry:
```yaml
chinese: 示例
pinyin: Shili
english: Example
type: character
first_seen: chapter-1
status: active
notes: Example notes
```
