# Setup (once)

## 1. Instagram token (Meta)
1. developers.facebook.com → My Apps → Create app → use case **"Manage messaging & content on Instagram"** (Instagram API with Instagram Login). App type Business. It can stay in development mode: it only posts to your own account.
2. In the app: Instagram → **API setup with Instagram login** → *Generate access tokens* → **Add account** → log in as @rodado.creativo (a professional account) and allow the permissions, including `instagram_business_content_publish`.
3. Copy the generated token (long-lived, 60 days; the publisher refreshes it weekly by itself).
4. Server: add `IG_ACCESS_TOKEN=<token>` to `/opt/hermes/.env`.
(Meta renames these screens often; the parts that matter are "Instagram API with Instagram Login" and the content-publish permission.)

## 2. Public file server
Instagram downloads each image/video from a public URL when publishing.
1. DNS: an A record `media.roda.do` → the server's IP.
2. Check ports 80/443 are free on the server: `ss -ltnp | grep -E ':(80|443) '` (no output = free). If something already serves them, add `media.roda.do` to that proxy instead (root: `/opt/hermes/data/rodado/publish/public`).
3. `/opt/hermes/.env`: `MEDIA_DOMAIN=media.roda.do` and `PUBLIC_MEDIA_BASE=https://media.roda.do`.
4. `docker compose --profile publish up -d` (starts the `media` service from compose.yaml next to Hermes).

## 3. Check and schedule the job
```bash
cd /opt/hermes
docker compose up -d --force-recreate        # picks up the new .env values
docker compose exec -u hermes hermes python3 /opt/data/skills/rodado-publisher/scripts/publish.py check
# expected: "Token OK · @rodado.creativo …" and "Public URL OK · https://media.roda.do"
mkdir -p data/scripts && cat > data/scripts/rodado-publish-due.sh <<'SH'
#!/bin/bash
exec python3 /opt/data/skills/rodado-publisher/scripts/publish.py run-due
SH
chown -R 10000:10000 data/scripts
docker compose exec -u hermes hermes hermes cron create --name "Rodado publisher" --script rodado-publish-due.sh --no-agent --deliver whatsapp "*/10 * * * *"
```
The job is silent unless something happens (heads-up, published link, or an error).
