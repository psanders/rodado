# Compose spec (JSON)

```json
{
  "name": "2026-10-13-carousel-framework-2-segundos",
  "theme": "paper",
  "max_seconds": 12,
  "slides": [ { "layout": "cover", "media": "../../library/A012.mp4", "title": "...", "kicker": "..." } ]
}
```

- `name`: file prefix. One slide → `<name>.png`; carousels → `<name>-01.png …`.
- `theme`: default for all slides; any slide can override. `ink` (dark), `paper` (cream), `sand` (warm beige), `red` (brand red).
- `media`: a path (or a list, for `compare`) relative to the spec file. Images: png/jpg/webp. Videos: mp4/mov/webm.
- A slide with a video becomes `<stem>.mp4` (1080 × 1350, H.264, no sound, length = the clip, capped by `max_seconds`) plus `<stem>-poster.png` to review. Instagram accepts mixed photo/video carousels.
- `focus` (0–1, optional): where to crop media vertically. 0 = keep the top, 0.5 = center, 1 = keep the bottom.

## Layouts

| layout | media | fields | good for |
| --- | --- | --- | --- |
| `quote` | – | `text`, `attribution`? | static one-liner, classic |
| `statement` | – | `text`, `highlight`? (words drawn in red), `label`? | static one-liner, poster-size type; 3–8 words |
| `number` | – | `number` ("2 s", "US$299", "7"), `text`, `label`? | one striking figure |
| `quote-media` | 1 | `text`, `attribution`? | one-liner over a photo or clip |
| `media` | 1 | `caption`?, `label`? | the picture/clip is the point (show the work) |
| `cover` | 0–1 | `title`, `kicker`?, `subtitle`? | first carousel slide; with media it's full-bleed |
| `point` | – | `title`, `body`?, `label`? | one idea, text only |
| `point-media` | 1 | `title`, `body`?, `label`?, `media_height`? (default 660) | one idea with its example on top |
| `compare` | 2 | `title`?, `labels` (default ["Antes","Después"]) | before/after, A/B directions |
| `list` | – | `title`, `items` (3–5) | summary |
| `cta` | 0–1 | `title`, `button`?, `note`? | last slide; with media it's full-bleed |

The renderer adds the slide counter (01/08), the bottom rule and the roda.do wordmark. Old specs with `"type"` instead of `"layout"` still work.

## Limits that keep slides readable
- Titles ~12 words, bodies ~30 words, list items ~10 words, statements 3–8 words.
- Carousels 4–10 slides. Video clips 3–15 s.
- Spanish accents and ¿¡ are fine; emoji and arrows are not (not in the font).
- Text auto-shrinks; if it gets small, the text is too long for that layout.
