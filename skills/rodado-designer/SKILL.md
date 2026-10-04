---
name: rodado-designer
description: Rodado's designer. Turns an approved Rodado post (static-quote, carousel-framework or carousel-faq) into finished on-brand PNGs at 1080 × 1350 with a bundled renderer and Rodado's fonts. Use after rodado-copywriter, or when asked to make the image, slides or carousel for a Rodado post.
---

# Rodado designer: approved post → PNG

Builds the images for the text-based formats. Reels are not covered (that's the editor, later).
You never change the copy: the words were approved by Pedro. You never publish or send the images anywhere.

| Format | Renders as |
| --- | --- |
| `static-quote` | 1 slide, type `quote` |
| `carousel-framework` | `cover` → `point` × N → `list` (summary) → `cta` |
| `carousel-faq` | `cover` → `point` per question (label "Pregunta N") → `cta` |

## Steps
1. Find the post. On a Kanban card: the post folder is in the card body or in the copywriter's result under "Parent task results" (`Post folder: <path>`). Read `<post folder>/post.md`. If there is no post.md, stop and say so (on a Kanban board: block the card); don't write copy yourself.
2. If the format is a Reel, stop and say it's not a designer job.
3. Write the spec to `<post folder>/final/spec.json`. Format and limits: `references/spec.md`. Working examples: `examples/quote.json`, `examples/carousel.json`.
   - Copy slide text exactly from the post's Structure section (Spanish). Only cut a slide's text if it doesn't fit, and say what you cut.
   - `name`: `<date or week>-<format>-<topic>` (e.g. `2026-10-13-carousel-framework-2-segundos`).
   - Theme: `paper` for carousels with a dark (`ink`) CTA slide at the end; `ink` for static-quote. Change only if the post asks for it.
4. Render with a Python that has Pillow (Hermes' own: `/opt/hermes/.venv/bin/python`; otherwise `python3`):
   ```
   <python> ${HERMES_SKILL_DIR}/scripts/render.py <post folder>/final/spec.json --out <post folder>/final
   ```
   (`${HERMES_SKILL_DIR}` is this skill's folder.) It prints one path per PNG.
5. **Look at every PNG** before finishing (open it with your vision tool). Check: nothing cut off, no boxes instead of letters, readable at phone size, no slide over ~30 words, slide order matches the post. Fix the spec and render again if needed.
6. Deliver:
   - On a Kanban card: attach each PNG with `hermes kanban attach $HERMES_KANBAN_TASK <png>`, then ask for review with: the post folder, the number of slides, and anything you cut or changed.
   - In a chat: list the PNG paths and the same notes.

If Pedro asks for changes: a copy change goes back to the copywriter (say so); a layout change you make in `spec.json` and render again.

## Notes
- Renderer: `scripts/render.py` (Pillow only, no browser, no network). Text auto-shrinks to fit; if it gets small, the text is too long for one slide.
- Fonts are bundled: `assets/fonts/InstrumentSerif-Regular.ttf`, `assets/fonts/InstrumentSerif-Italic.ttf`, `assets/fonts/Inter-Regular.ttf`, `assets/fonts/Inter-SemiBold.ttf`, `assets/fonts/JetBrainsMono-Regular.ttf`. Latin only: no emoji or arrows in slide text.
- Brand: ink #16130F, paper #F5EFE4, red #E23D2A accents; Instrument Serif titles, Inter body, JetBrains Mono labels. The renderer applies all of this; don't fight it.
- Images inside slides (frames from our ads) are not supported yet; if the post asks for one, render without it and mention it in the review note.
