# Setup (once)

## 1. Instagram token (Meta)
1. developers.facebook.com → My Apps → Create app → use case **"Manage messaging & content on Instagram"** (Instagram API with Instagram Login). App type Business. It can stay in development mode: it only posts to your own account.
2. In the app: Instagram → **API setup with Instagram login** → *Generate access tokens* → **Add account** → log in as @rodado.creativo (a professional account) and allow the permissions, including `instagram_business_content_publish`.
3. Copy the generated token (long-lived, 60 days; the publisher refreshes it weekly by itself).
4. Server: add `IG_ACCESS_TOKEN=<token>` to `/opt/hermes/.env`.
(Meta renames these screens often; the parts that matter are "Instagram API with Instagram Login" and the content-publish permission.)

## 2. Public file server
Instagram downloads each image/video from a public URL when publishing. Hermes' compose has a generic `media` service (Caddy) that serves `/opt/hermes/data/public` over HTTPS; the publisher puts files in `data/public/rodado/<random>/` only while publishing.
1. Pick a hostname you control and add a DNS A record for it → the server's IP.
2. Check ports 80/443 are free: `ss -ltnp | grep -E ':(80|443) '` (no output = free). If another proxy already uses them, point that hostname at `/opt/hermes/data/public` there instead.
3. `/opt/hermes/.env`: `MEDIA_DOMAIN=<hostname>` and `PUBLIC_MEDIA_BASE=https://<hostname>`.
4. `mkdir -p data/public && chown 10000:10000 data/public && docker compose --profile media up -d`

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
