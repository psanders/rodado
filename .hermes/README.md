# .hermes

How Rodado's agents run: Hermes Agent + Kanban in Docker, model provider Anthropic.
It lives inside the repo, so cloning the repo is the whole setup. (Hermes also treats `./.hermes/` as a project folder, e.g. for project plugins and plans.)

```
rodado/
  index.html, css/, js/, assets/   website (roda.do)
  content/                         what the agents work on: strategy, templates, calendar, ideas
  projects/                        client work (not in git)
  design/, ads/, offer/            Pencil files, ad creatives, offer PDF
  .hermes/                         how the agents run (this folder)
    compose.yaml                   Hermes container; mounts the repo at /workspace/rodado
    .env.example → .env            dashboard login + ANTHROPIC_API_KEY (.env is never committed)
    profiles/                      one folder per agent: SOUL.md (role) + description.txt; _shared.md applies to all
    skills/                        procedures the agents follow (agentskills format, also work in Claude)
    themes/                        dashboard branding
    scripts/setup.sh               applies profiles, skills, theme, model, board (safe to re-run)
    scripts/week.sh                creates one week's card chain
    data/                          Hermes runtime state (not in git; back it up)
```

## Start (on any machine with Docker)

```bash
git clone <rodado repo> && cd rodado/.hermes
cp .env.example .env            # dashboard login + ANTHROPIC_API_KEY
openssl rand -hex 32            # paste into HERMES_DASHBOARD_BASIC_AUTH_SECRET
docker compose up -d
docker compose exec hermes bash /workspace/rodado/.hermes/scripts/setup.sh
```

Dashboard: http://localhost:9119. On a server it's bound to localhost: use Tailscale or `ssh -L 9119:localhost:9119 user@server`.

## Run a week

```bash
docker compose exec hermes bash /workspace/rodado/.hermes/scripts/week.sh 2026-W42
```

| Card | Skill | Ends in |
| --- | --- | --- |
| Retro (previous week) | rodado-retro | **Review**: you approve the rule changes it made (`retro.md` + diff) |
| Ideas | rodado-ideation | **Review**: you approve the 7 ideas (`selection.md`) |
| Briefs & copy | rodado-copy | Done |
| Audit | rodado-audit | **Review**: you approve copy + `audit.md` |

All four run on the `rodado` profile. Agents only write files in the repo; review with `git diff`, commit yourself.

## Profiles

| Profile | Job | Access | Never |
| --- | --- | --- | --- |
| `rodado` | Ideas, briefs, copy, audit, weekly report, prospect research | Repo only | Spend money, publish, message anyone |
| `rodado-studio` | Carousels, statics, Reels, image/video generation | Generation keys (later, with a spending cap) | Change strategy or copy, publish |
| `rodado-publisher` | Schedule approved posts, pull Instagram metrics | Meta token (later) | Write or edit content |

## How it knows the repo and gets better

- Every session starts in `/workspace/rodado` (`terminal.cwd`), so Hermes loads `AGENTS.md` from the repo root: the map of what's where and what agents may edit.
- Skills live in `.hermes/skills/` (git). Hermes' background curator never edits them; changes happen in the weekly retro, which compares the agents' drafts with your edits and the metrics, edits the skill/template/voice files, and asks for review. You commit what you accept.
- In the dashboard chat, pick the `rodado` profile (or use the default one, which gets the same instructions).

## Growing it

- **Change how an agent behaves:** edit `profiles/<name>/SOUL.md` or a skill, then re-run `setup.sh`.
- **New agent:** add `profiles/<name>/` with `SOUL.md` and `description.txt`, re-run `setup.sh`.
- **New procedure:** add `skills/<name>/SKILL.md`. Every profile sees it.
- **Different model:** `RODADO_MODEL=<model> setup.sh`.
- **Another project on the same server:** its own `.hermes/` with a different `HERMES_PORT` in `.env`.

Conventions: folder and file names, frontmatter keys, CSV columns and values are in English. Audience-facing copy (hooks, captions, slides) stays in Spanish.
