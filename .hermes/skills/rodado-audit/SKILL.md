---
name: rodado-audit
description: Audits the week's Rodado posts against the brand, voice and quality checklist, fixes small issues and leaves a report for human review.
---

# Weekly audit

Check each `content/calendar/<week>/*/post.md` against this checklist:

| # | Rule |
| --- | --- |
| 1 | Format and pillar match the day's slot in `strategy.md` |
| 2 | One hook, understandable without sound, no banned words from `voice.md` |
| 3 | Speaks to a marketing manager at a mid-size brand (not agencies, not founders without budget) |
| 4 | One CTA from `voice.md`; Thursday and Sunday use ANUNCIO on WhatsApp |
| 5 | Caption: first line under 125 characters, signature and 3–5 hashtags |
| 6 | No real client brand without "logo replaced"; category ideas use invented brands |
| 7 | Offer facts are right: US$299, 3 durations (30/20/15 s), 7 business days, 2 revision rounds, 100% guarantee |
| 8 | Asset list complete, file names correct |
| 9 | Spanish spelling and accents |

## Do
- Fix small things directly (accents, caption length, hashtags, file names).
- Don't rewrite hooks or ideas: if something major fails, note it.
- Write `content/calendar/<week>/audit.md`: a table `| Post | Result (ok / fixed / review) | Note |` and, at the end, "For Pedro:" with at most 3 decisions he needs to make.

## Finish
`kanban_request_review` with the summary: how many ok, fixed and for review.
