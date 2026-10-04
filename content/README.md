# Content · Rodado Creativo

System for producing 7 Instagram posts a week (@rodado.creativo), fast and consistent.
Everything starts from a template, everything lives in a folder, nothing is invented on the day.

> Note: this repo is public and published at roda.do. `prospects/` and `metrics/` are in `.gitignore`.
> Language: file names, structure and instructions are in English. Audience-facing copy (hooks, captions, slides, CTAs) is in Spanish.

## Structure

```
content/
  strategy-full.md        Full strategy (imported from the doc)
  strategy.md             Operating summary: audience, goal, pillars, formats, cadence, decisions
  voice.md                How we sound: tone, words, CTAs, copy rules
  instagram-profile.md    Bio, highlights and pinned posts
  publishing.md           How to schedule the week in Meta Business Suite
  templates/              One template per format + caption + post brief
  ideas/bank.csv          W41 idea history (the live bank is in Hermes, skill rodado-strategist)
  calendar/YYYY-Wnn/      One folder per week, one subfolder per post
  metrics/log.csv         One row per published post (private)
  prospects/              Target brands for outbound (private)
  scripts/new-week.sh     Creates the week's folders from the templates
```

## Weekly ritual

| When | What | Time |
| --- | --- | --- |
| Friday | Fill `metrics/log.csv` with the week that's ending | 15 min |
| Daily, 9:00 | Answer Hermes' idea pitches on WhatsApp until 3 are approved | 5 min |
| Sunday, 17:00 | Approve next week's 7 (Hermes picks from the bank) | 5 min |
| Sunday–Monday | Approve the 7 briefs in Kanban (Review column) | 20 min |
| Monday | Batch-produce Tuesday to Sunday (Pencil + video) | 3–4 h |
| Monday | Schedule everything in Meta Business Suite (`publishing.md`) | 30 min |
| Daily | Reply to comments and DMs; 10+ outbound messages | 30 min |

Agents (Hermes, Claude) can run ideas, copy and audit with the skills in `../skills/`; you review and commit.

## File names

`calendar/2026-W41/01-mon-reel-storyboard/` → `post.md` (brief + copy), `final/` (what gets uploaded), `sources/` (working files).
Final files: `2026-10-05-reel-storyboard-guaraguao.mp4`, `2026-10-06-carousel-01.png` … `-08.png`.

## Rules that save time

1. One post = one idea = one hook. If it needs two ideas, it's two posts.
2. Reuse before creating: every client project yields 3 posts (storyboard to ad, 3 cuts, one lesson).
3. Real clients only with their logo replaced by an invented look-alike. Never their real brand without permission.
4. Fixed format per day (see `strategy.md`) so results compare week to week.
5. Change one variable at a time and note it in `log.csv` (`test` column).
