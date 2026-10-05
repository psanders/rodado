# Setup (once)

## 1. Gmail access for Hermes (Google Workspace MCP)
Hermes sends and reads through an MCP server that runs inside the Hermes container: **workspace-mcp** (github.com/taylorwilsdon/google_workspace_mcp), limited to Gmail with send permission (`--permissions gmail:send`: read, labels, drafts, send; no delete, no settings). It can send in-thread replies (`thread_id`, `in_reply_to`).
1. Google Cloud Console → new project "Rodado Outbound" → enable **Gmail API**.
2. Google Auth Platform → Branding (app name, your email) → Audience: External, add your Gmail as a **test user** → Clients → Create client → **Desktop app**. Copy the client ID and secret.
3. `/opt/hermes/.env`: `GOOGLE_OAUTH_CLIENT_ID=…` and `GOOGLE_OAUTH_CLIENT_SECRET=…`, then `docker compose up -d --force-recreate`.
4. Register it in Hermes (Gmail only, single user):
   ```bash
   docker compose exec -it -u hermes hermes hermes mcp add gmail --command uvx --args workspace-mcp --single-user --permissions gmail:send
   docker compose exec -u hermes hermes hermes mcp test gmail
   ```
5. The first Gmail call returns a Google sign-in link. Open it, sign in with the Gmail you'll send from, allow. If the callback can't reach the container (`localhost:8000`), use an SSH tunnel from your Mac: `ssh -L 8000:localhost:8000 root@<server>` and open the link again.
6. Test from WhatsApp: "Use rodado-prospector: search my Gmail for the last email I sent and tell me its subject."
(Exact flags can change between workspace-mcp versions; `uvx workspace-mcp --help` shows the current ones.)

## 2. Scheduled jobs (from the WhatsApp chat, so replies stay in context)
> Create these scheduled jobs, delivered to this chat, with attach_to_session on:
> 1) "Leads research", Mon–Fri 8:00, skill rodado-prospector, prompt "Run the morning research."
> 2) "Leads send 9:30", Mon–Fri 9:30, skill rodado-prospector, prompt "Run a send run."
> 3) "Leads send 13:00", Mon–Fri 13:00, same skill and prompt.
> 4) "Leads send 17:00", Mon–Fri 17:00, same skill and prompt.

Send runs need the agent (they read Gmail), so they're normal jobs, not scripts. They stay silent when nothing happened.

## 3. Limits
`$CONTENT_DATA/leads/settings.json` is created on first use: 15 emails/day, 5 new/day, 5 per run, follow-ups day 3 and day 8, Mon–Fri 8:30–17:30. Raise slowly (e.g. +5/day per week) only if replies come and nothing bounces.
