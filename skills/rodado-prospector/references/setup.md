# Setup (once)

Collect-only: no email account or extra keys needed.

1. Copy the skill to the server (git pull + copy into `data/skills/rodado-prospector`).
2. Schedule the morning research from the WhatsApp chat, so your replies stay in context:
   > Create a scheduled job, delivered to this chat, with attach_to_session on: "Leads research", Mon–Fri 8:00, skill rodado-prospector, prompt "Run the morning research."
3. Data lives in `$CONTENT_DATA/leads/` (`leads.json`, `log.csv`, `dnc.txt`). `leads.py export` gives a CSV for a spreadsheet.

Later (not built yet): sending emails and follow-ups. Options discussed: a Gmail app password with the script sending via SMTP/IMAP, or a Google OAuth client with workspace-mcp.
