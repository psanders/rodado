# Setup (once)

## 1. Instagram token (Meta)
1. developers.facebook.com → My Apps → Create app → use case **"Manage messaging & content on Instagram"** (Instagram API with Instagram Login). App type Business. It can stay in development mode: it only posts to your own account.
2. In the app: Instagram → **API setup with Instagram login** → *Generate access tokens* → **Add account** → log in as @rodado.creativo (a professional account) and allow the permissions, including `instagram_business_content_publish`.
3. Copy the generated token (long-lived, 60 days; the publisher refreshes it weekly by itself).
4. Server: add `IG_ACCESS_TOKEN=<token>` to `/opt/hermes/.env`.
(Meta renames these screens often; the parts that matter are "Instagram API with Instagram Login" and the content-publish permission.)

## 2. Public file server
Instagram downloads each image/video from a public URL when publishing. Hermes' compose has a generic `media` service that serves `/opt/hermes/data/public` on port `MEDIA_PORT` (default 8088). The publisher puts files in `data/public/rodado/<random>/` only while publishing.
1. `/opt/hermes/.env`: `MEDIA_PORT=8088` (any free port) and `PUBLIC_MEDIA_BASE=http://<server IP or hostname>:8088`.
2. Open that port in the server's firewall if there is one (e.g. `ufw allow 8088/tcp`, or the DigitalOcean cloud firewall).
3. `mkdir -p data/public && chown 10000:10000 data/public && docker compose --profile media up -d`
4. `publish.py check` (step 3) confirms the URL is reachable. If Instagram later refuses plain-HTTP links, put HTTPS in front (a reverse proxy) and change only `PUBLIC_MEDIA_BASE`.

## 3. Check and schedule the job
```bash
cd /opt/hermes
docker compose up -d --force-recreate        # picks up the new .env values
docker compose exec -u hermes hermes python3 /opt/data/skills/rodado-publisher/scripts/publish.py check
# expected: "Token OK · @rodado.creativo …" and "Public URL OK · https://<hostname>"
mkdir -p data/scripts && cat > data/scripts/rodado-publish-due.sh <<'SH'
#!/bin/bash
exec python3 /opt/data/skills/rodado-publisher/scripts/publish.py run-due
SH
chown -R 10000:10000 data/scripts
docker compose exec -u hermes hermes hermes cron create --name "Rodado publisher" --script rodado-publish-due.sh --no-agent --deliver whatsapp "*/10 * * * *"
```
The job is silent unless something happens (heads-up, published link, or an error).
