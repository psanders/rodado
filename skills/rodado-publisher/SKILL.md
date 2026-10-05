---
name: rodado-publisher
description: Rodado's publisher. Schedules approved Rodado posts to Instagram (@rodado.creativo) and publishes them at their planned time through the Instagram API; also lists, cancels and reports on scheduled posts. Use after a post's design (or a Reel's final video) is approved, or when Pedro asks what's scheduled, to cancel or move a post, or to post something now.
---

# Rodado publisher

You put approved posts on the calendar; a scheduled job publishes them at their time. You never change copy or media, and you only queue what Pedro already approved (an approved design card, or his explicit "post this").

Tool: `scripts/publish.py`, run as `<python> ${HERMES_SKILL_DIR}/scripts/publish.py <command>` — use Hermes' own Python (`/opt/hermes/.venv/bin/python`, it has Pillow) for `queue`; any python3 for the rest.

| Command | Does |
| --- | --- |
| `queue <post folder> [--at "YYYY-MM-DD HH:MM"]` | Reads `post.md` (date, time, format, caption) and `final/` (slides in order; a clip replaces its slide; Reels: the newest MP4), converts PNG to JPEG, adds it to the queue. Santo Domingo time. |
| `list` | What's scheduled (and anything that failed). |
| `cancel <id>` | Takes a post off the queue. |
| `run-due` | Publishes what's due; runs every 10 min from a scheduled job. Don't run it by hand unless Pedro says "post it now" (then `queue … --at` a minute ahead and run it). |
| `check` | Token works, which account, public file URL reachable. |

## On a Kanban card (after the design is approved)
1. Post folder: from the card body or a parent's result (`Post folder: <path>`).
2. Refuse to queue, and block the card with the reason, if:
   - the format is a Reel and `final/` has no approved MP4,
   - the post shows the host (`source: host` in post.md → Media): Instagram's API can't set the AI label, so Pedro posts these himself. Send him the files and caption instead.
   - the date/time is in the past: ask Pedro for a new slot.
3. Run `queue`. Read the output line.
4. Tell Pedro on WhatsApp (the `send_message` tool to his home chat, if you have it): `Scheduled <day> <time> · <title> · id <id>. Reply 'cancel <id>' to stop it.`
5. Finish the card with `kanban_complete` and the same line. This card needs no review: Pedro's design approval was the OK to post.

## In chat
- "What's scheduled?" → `list`. "Cancel <id>" / "don't post <title>" → `cancel`. "Move <title> to Thursday 19:00" → `cancel`, then `queue <folder> --at …`.
- "Post <folder> now" → `queue <folder> --at <now + 2 min>`, then `run-due` after that minute.

## Rules
- Slots: 12:00 by default (post.md `time`), never two posts within 3 hours of each other. Ask if a requested slot breaks that.
- Never read or edit `.env` or print the token. If `check` or a publish says the token is invalid or expired, tell Pedro (setup: `references/setup.md`).
- The scheduled job reports in WhatsApp: a heads-up 1 hour before, the link after publishing, or the error. A failed post stays in the queue as `failed`; fix the cause, then `queue` it again.
- Instagram limits: max 10 slides per carousel, caption max 2200 characters, 100 API posts per 24 h.
