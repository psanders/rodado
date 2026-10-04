---
name: rodado-retro
description: Weekly retro for Rodado's content system. Learns from Pedro's edits and the metrics, then improves the skills, templates and voice rules in the repo.
---

# Weekly retro

Input: the previous week (e.g. `2026-W41`) comes in the card. Goal: next week's first drafts need fewer edits and produce more qualified WhatsApp chats.

## Gather
1. **Pedro's edits:** `git log --oneline -- content/calendar/<week>/` and `git diff <first agent commit>..HEAD -- content/calendar/<week>/` (if there are no commits yet, compare against `selection.md` and `audit.md`). Note every change Pedro made to hooks, captions, structure or CTAs, and every audit item he overruled.
2. **Results:** rows for that week in `content/metrics/log.csv`. Rank posts by qualified chats, then saves + shares. If there's no data yet, say so and skip.
3. **Friction:** blocked or failed cards on the board for that week (`hermes kanban --board rodado list`), and anything the audit flagged.

## Decide
Turn findings into at most 3 concrete rule changes. A change needs evidence: the same edit made 2+ times, or a clear metrics gap. One-offs are noted, not turned into rules.

## Change
Edit the files directly, smallest change that fixes it:
- `.hermes/skills/<skill>/SKILL.md` for how a job is done (ideation, copy, audit).
- `content/templates/<format>.md` for a format's structure.
- `content/voice.md` for words, tone or CTAs.
Never edit `strategy*.md`, `.hermes/profiles/`, or the website. If the evidence points there, recommend it instead.

## Report
Write `content/calendar/<week>/retro.md`:
- What Pedro changed (pattern, with 1–2 examples)
- What the numbers say (top and bottom post, why)
- Changes made (file, what changed, evidence)
- Recommendations for Pedro (strategy-level, max 2)

## Finish
`kanban_request_review` with a 3-line summary: the changes made and the files touched. Pedro reviews the diff and commits.
