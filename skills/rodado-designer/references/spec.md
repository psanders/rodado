# Render spec (JSON)

```json
{
  "name": "2026-10-08-carousel-faq-jefe",   // file name prefix: YYYY-MM-DD-<format>-<topic>
  "theme": "paper",                          // "ink" (dark) or "paper" (light); can be overridden per slide
  "slides": [ { "type": "...", ... } ]
}
```

## Slide types
| type | fields | use |
| --- | --- | --- |
| `quote` | `text`, `attribution`? | static-quote. Max ~15 words. |
| `cover` | `title`, `kicker`?, `subtitle`? | first carousel slide; shows "Desliza" |
| `point` | `title`, `body`?, `label`? | one idea or one FAQ question per slide; `label` like "Pregunta 2" or "Señal 1" |
| `list` | `title`, `items` (3–4 strings) | summary slide |
| `cta` | `title`, `button`?, `note`? | last slide; `button` like "Escribe ANUNCIO por WhatsApp", `note` for offer facts |

Any slide can set `"theme": "ink"` or `"paper"` (e.g. a dark CTA at the end of a light carousel).

## Limits that keep slides readable
- Titles: up to ~12 words. Bodies: up to ~30 words. List items: up to ~10 words each.
- Carousels: 4–8 slides. The renderer numbers them (01/08) and adds the roda.do wordmark.
- Spanish accents and ¿¡ are fine; emoji and arrows are not (not in the font).
