# Rodado Creativo

Repo for roda.do: the website, the design files, the content system and the agents that run it.
Names and docs are in English; audience-facing copy (site, ads, posts) is in Spanish.

## Layout

| Path | What |
| --- | --- |
| `index.html`, `privacy.html`, `css/`, `js/`, `assets/` | The website (static, no build) |
| `privacidad.html` | Redirect to `privacy.html` (old URL used in Meta's message templates; keep it) |
| `design/` | Pencil files (`rodado.pen`, `templates/storyboards.pen`) and their images |
| `ads/` | Rodado's own ad creatives (statics, videos, LATAM set) |
| `offer/` | Offer PDF |
| `content/` | Content system: strategy, voice, templates, idea bank, weekly calendar |
| `.hermes/` | Hermes agents: compose, profiles, skills, theme, scripts |
| `projects/` | Client work (git-ignored; the repo is public) |
| `_downloads/` | Local downloads, not committed |

## Website

```
python3 -m http.server 8080      # from the repo root, then open http://localhost:8080
```

Published with GitHub Pages at roda.do (`CNAME`).

Frequent changes:
- WhatsApp number and prefilled message: top of `js/main.js` (`WA_NUMBER`, `WA_TEXT`).
- Price and copy: directly in `index.html`.

## Content and agents

See `content/README.md` for the weekly content system and `.hermes/README.md` to run the agents.
