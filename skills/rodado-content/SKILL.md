---
name: rodado-content
description: Creates a ready-to-produce Instagram post for Rodado Creativo (roda.do) in any of its 6 formats (reel-storyboard, carousel-framework, reel-category, carousel-faq, static-quote, reel-cta). Use when asked to write, draft or plan a Rodado post, hook, carousel, Reel script or caption.
---

# Rodado content: one post, any format

Produces one complete post brief (hook, structure, CTA, caption, assets, checklist) that a designer or a rendering step can build without asking questions. Audience-facing copy is always in Spanish; notes for the team are in English.

## Inputs
- **Format** (required): one of the 6 below. If the user gives only a topic, pick the format from the table and say why.
- **Topic or idea** (required): e.g. "why ads fatigue", "Dominican coffee", a client project.
- **Date / day** (optional): if given, check the format matches the day's slot.
- **Assets available** (optional): client project, existing ad, frames. Never invent client work.

## Formats
| Format | Pillar | Day slot | Read |
| --- | --- | --- | --- |
| `reel-storyboard` | proof | Mon, Fri | `references/formats/reel-storyboard.md` |
| `carousel-framework` | strategy (or trust) | Tue | `references/formats/carousel-framework.md` |
| `reel-category` | category | Wed | `references/formats/reel-category.md` |
| `carousel-faq` | trust | Thu | `references/formats/carousel-faq.md` |
| `static-quote` | open | Sat | `references/formats/static-quote.md` |
| `reel-cta` | offer | Sun | `references/formats/reel-cta.md` |

## Steps
1. Read `references/brand.md` (audience, offer facts, voice, CTAs, visual rules). Always.
2. Read only the reference file for the chosen format.
3. Write 3 hook options in Spanish, then pick the strongest and say why in one line (English). A hook must work in 2 seconds, without sound, for a marketing manager at a mid-size Dominican brand.
4. Fill `assets/post-template.md` exactly: frontmatter, hook, structure (timings for Reels, slide-by-slide for carousels), one CTA, full caption, asset list, checklist.
5. Self-check against the checklist at the end of `references/brand.md`. Fix anything that fails before answering.

## Output
- Return the filled post as one markdown block, ready to save as `post.md`.
- If you have a workspace with the rodado repo, save it to `content/calendar/<YYYY-Wnn>/<NN>-<day>-<format>/post.md` (create folders as needed); otherwise just return it.
- End with one line: what the human must provide or decide (e.g. "need the Cacao Mae frames with the logo replaced").

## Never
- Use a real brand without "logo replaced"; category concepts always use an invented brand.
- Promise results ("viral", "más ventas garantizadas") or change offer facts.
- Publish, schedule or message anyone. This skill only writes the brief.
