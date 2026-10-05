---
name: rodado-copywriter
description: Creates a ready-to-produce Instagram post for Rodado Creativo (roda.do) in any of its 6 formats (reel-storyboard, carousel-framework, reel-category, carousel-faq, static-quote, reel-cta). Use when asked to write, draft or plan a Rodado post, hook, carousel, Reel script or caption.
---

# Rodado copywriter: one post, any format

Produces one complete post brief (hook, structure, CTA, caption, assets, checklist) that a designer or a rendering step can build without asking questions. Audience-facing copy is always in Spanish; notes for the team are in English.

## Data folder
Everything this skill reads and writes lives under `$CONTENT_DATA` (set in the environment, e.g. `/opt/data/rodado`). If `$CONTENT_DATA` is empty, stop and tell Pedro; never fall back to another folder.

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
5. Plan the **Media** (the atoms the producer makes and the designer composes). Statics: optional, one image or clip for a quote over media. Carousels: 1–3 atoms (a clip for the cover or the "show the work" slide, an image per example). Describe each in one concrete sentence: what we see, not how it feels. Prefer moments a manager recognizes (product being poured, a before/after, a DR setting). Never real brands; client products only as "source: client". The host (Rodado's AI avatar) is "source: host"; if she speaks, write her exact line in Spanish (≤ 2.5 words per second) right in the Media item.
6. Self-check against the checklist at the end of `references/brand.md`. Fix anything that fails before answering.

## Output
Save the filled post as `post.md` in the post folder:
- If the request or card gives a post folder, use it (create it if needed).
- Else, with the rodado repo as workspace: `content/calendar/<YYYY-Wnn>/<NN>-<day>-<format>/post.md`.
- Else: `$CONTENT_DATA/posts/<YYYY-Wnn or today's date>/<NN>-<day>-<format>/post.md`.

Then reply (in a chat) or finish the card (on a Kanban board, ask for review) with:
1. The post folder path, on its own line, as `Post folder: <path>`. The designer reads the post from there.
2. The chosen hook and the CTA, one line each.
3. One line: what the human must provide or decide (e.g. "need the Cacao Mae frames with the logo replaced"), or "Nothing needed."

If Pedro asks for changes, edit `post.md` in place and finish again the same way.


## Approval gate (Kanban)
Pedro approves every card's output before the next step starts. So on a Kanban card you **never** finish with `kanban_complete`:
- Use `kanban_request_review` with your summary (if your Hermes has it).
- If it doesn't exist, use `kanban_block` with the reason `Waiting for Pedro's review: <summary>`.
Pedro approving (moving the card to Done) is what starts the next card. The only exception is the producer's "No media needed", which completes directly.

## Never
- Use a real brand without "logo replaced"; category concepts always use an invented brand.
- Promise results ("viral", "más ventas garantizadas") or change offer facts.
- Publish, schedule or message anyone. This skill only writes the brief.
