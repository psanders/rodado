# Reel spec (JSON)

```json
{
  "name": "2026-10-14-reel-category-snack",
  "clips": [
    {"file": "../../../library/A008.mp4", "in": 0, "out": 4.5, "text": "Así venderíamos un snack dominicano", "pos": "top"},
    {"file": "../../../library/A009.mp4", "in": 0.5, "out": 5, "text": "en 15 segundos. Sin rodaje.", "pos": "bottom", "style": "caption"}
  ],
  "end_card": {"title": "¿Lo probamos con tu producto?", "button": "Escribe ANUNCIO por WhatsApp", "note": "US$299 · 30, 20 y 15 s", "seconds": 2.5, "theme": "ink"},
  "music": null,
  "music_volume": 0.25,
  "cover": {"clip": 0, "at": 1.0, "title": "Así venderíamos un snack dominicano en 15 s"}
}
```

| Field | Meaning |
| --- | --- |
| `clips[].file` | Clip path, relative to the spec file (or absolute). Any aspect ratio; cropped to fill 1080 × 1920. |
| `clips[].in` / `out` | Seconds to keep from that clip. |
| `clips[].text` | On-screen line (Spanish, exactly from the copy). Empty = no text. |
| `clips[].pos` | `top`, `center` or `bottom` (inside the safe area). |
| `clips[].style` | `title` (big serif, default; ≤ 7 words) or `caption` (Inter on a dark pill; longer lines). |
| `clips[].audio` | `false` to mute that clip (silence is used instead). |
| `end_card` | Brand card at the end: `title`, `button`, `note`, `seconds`, `theme` (`ink` or `paper`). Omit for none. |
| `music`, `music_volume` | Optional bed under everything (looped, faded out), mixed under the clips' own sound. |
| `cover` | Frame for the Reel cover: which clip (0-based), at which second of the kept part, optional `title`. |

Output: `<name>.mp4` (H.264, AAC 48 kHz, 30 fps, -14 LUFS, faststart) and `<name>-cover.jpg`.
