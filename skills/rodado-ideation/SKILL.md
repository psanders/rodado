---
name: rodado-ideation
description: Proposes and selects the week's 7 Instagram content ideas for Rodado, using the strategy, the idea bank and the metrics in the repo.
---

# Weekly ideation

Input: the week (e.g. `2026-W42`), from the request or the card. You work inside the rodado repo.

## Read first
1. `content/strategy.md` (audience, pillars, fixed slot per day)
2. `content/voice.md`
3. `content/ideas/bank.csv` (don't repeat ideas with `status=used`)
4. `content/metrics/log.csv` if it has rows: which pillar and format won on qualified chats first, then saves + shares

## Do
1. Append 5–10 new ideas to `bank.csv` (next id: I0NN), each with pillar, format, hook (in Spanish), source and score 1–3.
   Valid sources: project, production, objection, question, ad-library, metrics. Category ideas always use invented brands, never real ones.
   Pillars: proof, strategy, category, trust, offer, open. Formats: reel-storyboard, carousel-framework, reel-category, carousel-faq, static-quote, reel-cta.
2. Pick 7 ideas for the week, one per slot: mon proof, tue strategy, wed category, thu trust, fri proof, sat open, sun offer. Prefer score 3 and what won in the metrics.
3. Write the selection to `content/calendar/<week>/selection.md` (create the folder if needed):
   `| Day | Idea | Pillar | Format | Hook | Why |`
4. Don't change `status` in `bank.csv`; that happens after Pedro approves.

## Finish
Ask Pedro to review (on a Kanban board: `kanban_request_review`) with a 3-line summary: how many new ideas, the selection in one line, and the week's bet (which variable is being tested).
