# AGENTS.md · Rodado Creativo

Read this first. It applies to any agent working in this repo (Hermes, Claude, others).

## What this is
Rodado Creativo (roda.do) makes AI-produced vertical video ads for Instagram and Facebook for mid-size Dominican brands.
This repo holds the website, design files, the content system and the agent setup.

## Map
| Path | What | Agents may edit? |
| --- | --- | --- |
| `content/strategy-full.md`, `content/strategy.md` | Strategy (source of truth) | Only with Pedro's approval |
| `content/voice.md` | Voice and copy rules | Propose changes in a retro |
| `content/templates/` | One template per post format | Propose changes in a retro |
| `content/ideas/bank.csv` | W41 idea history (live bank: Hermes, `rodado-strategist`) | No |
| `content/calendar/<week>/` | The week's posts (`post.md`), `selection.md`, `audit.md`, `retro.md` | Yes |
| `content/metrics/log.csv` | One row per published post (git-ignored) | Publisher only |
| `content/prospects/` | Target brands (git-ignored) | Yes (research) |
| `skills/` | How each recurring job is done (agentskills format) | Propose changes in a retro or as a new skill for Pedro to review |
| `index.html`, `css/`, `js/`, `assets/`, `privacy.html` | Live website | No |
| `design/`, `ads/`, `offer/`, `projects/` | Design files, ad creatives, client work | No, unless a card says so |

## Rules
- Audience-facing copy is Spanish (neutral Dominican). Everything else is English.
- Never publish, spend money or message anyone. Prepare files; Pedro approves.
- Never commit. Pedro reviews `git diff` and commits.
- Client brands only with their logo replaced; category ideas use invented brands.

## How the system improves
## Roles (skills)

| Skill | Role | Does |
| --- | --- | --- |
| `rodado-strategist` | Strategist | Daily idea pitch on WhatsApp, idea bank, Sunday plan, creates the week's cards |
| `rodado-copywriter` | Copywriter | Writes one post (hook, structure, CTA, caption) in any of the 6 formats |
| `rodado-designer` | Designer | Renders approved carousels and statics to PNG |
| `rodado-copy`, `rodado-audit`, `rodado-retro` | — | Repo-based weekly flow (copy all 7, audit, retro) |

Next roles: editor (Reels), publisher, analyst.

Every week starts with a **retro** (skill `rodado-retro`): compare what agents drafted with what Pedro changed and with the metrics, then edit the skills, templates or `voice.md` so next week's first draft is closer. Those edits go to Pedro for review; once he commits them, they're the new rules.
