---
name: rodado-copy
description: Fills the week's 7 post.md files for Rodado (hook, structure, CTA, caption, assets) from the approved selection and the templates.
---

# Weekly briefs and copy

## Read first
- `content/calendar/<week>/selection.md` (approved ideas). If it doesn't exist, stop and say so (on a Kanban board: `kanban_block`).
- `content/voice.md`, `content/templates/caption.md` and each format's template in `content/templates/`.
- Quality reference: `content/calendar/2026-W41/*/post.md`.

## Do
1. If the week's folders don't exist, run `bash content/scripts/new-week.sh <week>`.
2. For each of the 7 `post.md`, follow the `rodado-content` skill for that post's format (it holds the brand rules, the format templates and the checklist).
3. Update the Hook column in `week.md` and mark the 7 ideas in `bank.csv` as `status=used` with `used_in=<week>`.
4. Change `status: idea` to `status: production` in each post.md.

## Finish
Report back (on a Kanban board: `kanban_complete`) with a summary: the 7 hooks, one per line.
