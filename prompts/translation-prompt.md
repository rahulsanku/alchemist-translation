# Translation Prompt Template

Use this prompt when translating a new chapter.

---

You are translating a Chinese xianxia webnovel into polished English prose.

## Rules

- Preserve all meaning.
- Keep cultivation terms consistent.
- Translate naturally, not literally.
- Keep character names in pinyin.
- Do not summarize.
- Maintain the tone of a professional webnovel translation.
- Keep realm names recognizable.
- Explain obscure cultural references only if necessary.
- Preserve humor, combat flow, and internal monologue.
- Do not censor or simplify cultivation terminology.

Never:
- summarize chapters
- omit repeated cultivation exposition
- westernize names
- simplify cultivation systems
- remove inner monologue
- flatten hierarchical speech

Always:
- preserve tone
- maintain continuity
- preserve cultivation atmosphere
- preserve Daoist concepts where appropriate

See `notes/style-guide.md` for naming, combat, and dialogue conventions.

## Glossary Reference

Use these files as authoritative. Do not deviate from established renderings.

| File | Contains |
|------|----------|
| `glossary/characters.yml` | Named characters |
| `glossary/places.yml` | Locations and regions |
| `glossary/sects.yml` | Sects and organizations |
| `glossary/techniques.yml` | Combat and cultivation techniques |
| `glossary/items.yml` | Pills, herbs, artifacts, weapons |
| `glossary/realms.yml` | Cultivation realm/stage ladder |

## New Terminology

When a term has no glossary entry:
1. Transliterate it and flag inline with `[TERM?]`
2. Add a row to `notes/unresolved-terms.md`
3. Once confirmed, add the entry to the appropriate `glossary/*.yml` file

## Input / Output

- Raw source: `raws/chXXX.txt`
- Draft output: `translated/chXXX.md`
- Polished final: `chapters/chXXX.md`

## Context

- Previous chapter summary: [paste or describe]
- Unresolved terms from last chapter: [list here]

## Chapter to Translate

[Paste raw Chinese text here]
