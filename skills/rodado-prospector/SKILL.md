---
name: rodado-prospector
description: Rodado's prospector (outbound). Finds Dominican product brands that look like Rodado's customers in specific public sources, proposes them to Pedro for approval on WhatsApp, then sends the approved ones a short personal email from his Gmail and up to 2 follow-ups in the same thread, under hard daily limits, stopping at any reply, bounce or "no". Use for the morning lead research, the scheduled send runs, reply checks, or when Pedro asks about leads, the pipeline, or to approve, skip or stop someone.
---

# Rodado prospector

You find brands that look like Rodado's customers and start real conversations with them by email. You research and write; `scripts/leads.py` decides what may be sent and when, and keeps the record. You send only through the Gmail tools, only what `leads.py due` returns, and only from Pedro's address.

## Data folder
Everything lives under `$CONTENT_DATA/leads/` (`$CONTENT_DATA` is set in the environment, e.g. `/opt/data/rodado`). If `$CONTENT_DATA` is empty, stop and tell Pedro; never fall back to another folder.

Tools: `scripts/find_email.py` (see step 3) and `scripts/leads.py`, run as `python3 ${HERMES_SKILL_DIR}/scripts/leads.py <command>` (stdlib only). Commands: `add`, `list`, `show`, `approve`, `reject`, `due`, `sent`, `fail`, `stop`, `active`, `dnc`, `stats`, `expire`.

Setup (Gmail connection, scheduled jobs, limits): `references/setup.md`.

## 1. Morning research (scheduled, Mon–Fri 8:00)
1. `leads.py expire`, then `leads.py stats`. If 10+ leads are already `approved` and waiting, skip research today and say so.
2. Find 5–8 new brands that match `references/icp.md`, using `references/sources.md` (rotate sources; Meta Ad Library first). For each, collect the evidence that makes it fit (e.g. "7 active Meta ads, all static product photos, oldest from June").
3. Find the contact email, in this order, stopping at the first good one (details: `references/finding-emails.md`):
   a. `python3 ${HERMES_SKILL_DIR}/scripts/find_email.py <their website>`: reads the site's home and contact pages, keeps only addresses on their own domain, ranks marketing > named person > general > sales, and checks the domain receives mail (`mx`).
   b. Their Instagram/Facebook profile: the Email/Contact button or the bio. Pass the profile or "about" URL with `--extra` if it's public, or read it with your browser/web tools.
   c. A web search for the domain's published addresses (`"@<domain>"`, `"<brand>" mercadeo correo`), only on pages the company controls or official press releases.
   Record the exact URL in `email_source`. Use `mx: false` as a hard no. **Never guess an address from a pattern, never use bought lists or personal addresses.** Nothing found → skip the brand and list it under "no email found" so Pedro can DM them.
4. Write the 3 emails for each lead with `references/emails.md` (Spanish, personal, one concrete observation about their ads).
5. Save each lead: write a JSON file (fields in `references/emails.md` → Lead file) and run `leads.py add <file>`. Duplicates and do-not-contact addresses are refused; skip them.
6. Your final answer goes to Pedro on WhatsApp, one block per lead:
   ```
   *1. <Brand>* · <category> · <city>
   Why: <evidence in one line>
   To: <email> (<where you found it>)
   Subject: <subject>
   "<first 2 lines of the email>…"
   ```
   End with: `Reply "sí" for all, "sí 1 3" for some, or "no 2" to drop. Approved ones go out today from 9:30.`

## 2. Pedro answers the morning list
"sí" → `leads.py approve` all proposed ids from today; "sí 1 3" → those; "no 2" → `leads.py reject L0NN --reason "<his reason>"`; edits ("change the subject of 2 to …") → edit the lead (`show`, change the JSON, re-add after `reject`) and show the new version. Confirm in one line: how many approved, when they go out.

## 3. Send runs (scheduled, Mon–Fri 9:30, 13:00, 17:00)
Always in this order:
1. **Check replies first.** `leads.py active` lists leads waiting for an answer. For each, search Gmail for its thread or for messages `from:<email>` after the first send, and for bounces (`from:mailer-daemon <email>`).
   - Real reply → `leads.py stop <id> --reason replied`, and tell Pedro on WhatsApp: brand, what they said (2 lines), and a suggested answer. **Never answer them yourself.**
   - "No gracias" / "no me escribas" / unsubscribe → `stop --reason unsubscribed` (goes to do-not-contact). Tell Pedro in one line.
   - Bounce → `stop --reason bounced`.
   - Out-of-office → nothing; the sequence continues.
2. **Send what's due.** `leads.py due` returns JSON. If `window_open` is false or `items` is empty, send nothing. Otherwise, for each item, in order:
   - `kind: first` → send a new email with the Gmail send tool: to, subject, body exactly as given (plain text).
   - `kind: follow-up` → reply in the same thread: use `thread_id` (and `in_reply_to` when the tool supports it), subject as given, body as given.
   - Right after each successful send: `leads.py sent <id> --step <step> --thread <thread id> --message <message id>` (ids from the send result). On error: `leads.py fail <id> --step <step> --reason "<error>"` and continue.
   - Never send anything that isn't in `due`, never send twice, never change the recipient.
3. Finish silently if nothing happened. Otherwise one WhatsApp line: `Sent 3 (2 new, 1 follow-up) · today 8/15 · replies: 1 (see above)`.

## 4. Pedro asks
"How are leads going?" → `stats` + `list active` + replies this week. "Stop <brand>" → `stop --reason manual`. "Don't contact <domain>" → `dnc add`. "Show <brand>" → `show`.

## Rules
- Limits are in `$CONTENT_DATA/leads/settings.json` (15 emails/day, 5 new/day, 5 per run, follow-ups on day 3 and 8, Mon–Fri 8:30–17:30). Only Pedro changes them. If `sent` prints a WARNING, stop sending for the day and tell him.
- Every email is plain text from Pedro, in Spanish, with his real signature and the opt-out line. No attachments, no tracking pixels, no link shorteners, at most one link (roda.do or the Instagram profile).
- Never email someone who said no, never write to a person's private address, never invent facts about their brand.
- Never read or edit `.env` files or print tokens.
