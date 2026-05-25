# An Alchemist's Path to Eternity

Translation workspace for **长生从炼丹宗师开始**.

## Structure

```
chapters/
  raws/         raw Chinese chapter files
  translated/   polished English translations
glossary/
  terms.md      cultivation realms, techniques, items, sects
  characters.md character database
notes/
  style-guide.md    translation style rules
  unresolved-terms.md  terms pending review
prompts/
  translate.md  chapter translation prompt template
```

## Workflow

1. Drop the raw Chinese chapter into `chapters/raws/` (e.g. `ch001.txt`).
2. Use `prompts/translate.md` as the base prompt, filling in context from the previous chapter.
3. Save the translated output to `chapters/translated/` (e.g. `ch001.md`).
4. Update `glossary/terms.md` and `glossary/characters.md` with any new entries.
5. Log unresolved or uncertain terms in `notes/unresolved-terms.md`.
