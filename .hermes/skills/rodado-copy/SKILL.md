---
name: rodado-copy
description: Fills the week's 7 post.md files for Rodado (hook, structure, CTA, caption, assets) from the approved selection and the templates.
---

# Weekly briefs and copy

## Read first
- `content/calendar/<week>/selection.md` (approved ideas). If it doesn't exist, block the card with `kanban_block` and explain.
- `content/voice.md`, `content/templates/caption.md` and each format's template in `content/templates/`.
- Quality reference: `content/calendar/2026-W41/*/post.md`.

## Do
1. If the week's folders don't exist, run `bash content/scripts/new-week.sh <week>`.
2. For each of the 7 `post.md`: fill `idea_id`, title, hook, structure (following the format template: timings or slides), one CTA from voice.md, the full caption with signature and hashtags, and the asset list with file names `YYYY-MM-DD-<format>-<topic>`. All audience-facing text in Spanish.
3. Reels: hook readable in 2 s without sound. Carousels: max 30 words per slide. Caption: first line under 125 characters.
4. Update the Hook column in `week.md` and mark the 7 ideas in `bank.csv` as `status=used` with `used_in=<week>`.
5. Change `status: idea` to `status: production` in each post.md.

## Finish
`kanban_complete` with a summary: the 7 hooks, one per line.
