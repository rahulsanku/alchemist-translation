# An Alchemist's Path to Eternity

Translation workspace for **长生从炼丹宗师开始**.

## Structure

```
chapters/           in-progress or misc chapter files
raws/               raw Chinese source chapters
translated/         polished English translations

prompts/
  translation-prompt.md

glossary/
  characters.yml    named characters
  places.yml        locations and regions
  sects.yml         sects and organizations
  techniques.yml    combat, alchemy, and cultivation techniques
  items.yml         pills, herbs, artifacts, weapons
  realms.yml        cultivation realm/stage ladder

notes/
  style-guide.md    translation style rules
  unresolved-terms.md  terms pending review
  timeline.md       story event log
  lore.md           world-building and system notes
```

## Workflow

1. Drop the raw Chinese chapter into `raws/` (e.g. `ch001.txt`).
2. Use `prompts/translation-prompt.md`, filling in context from the previous chapter.
3. Save the translated output to `translated/` (e.g. `ch001.md`).
4. Update the relevant `glossary/` YAML files with any new entries.
5. Log uncertain terms in `notes/unresolved-terms.md`.
