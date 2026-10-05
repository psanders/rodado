#!/usr/bin/env python3
"""Rodado publisher: queue approved posts and publish them to Instagram at their time.

Commands:
  publish.py queue <post folder> [--at "YYYY-MM-DD HH:MM"] [--title T]   prepare files + caption, add to queue
  publish.py list                                                         show the queue
  publish.py cancel <id>                                                  take a post off the queue
  publish.py run-due                                                      publish what's due (cron, every 10 min)
  publish.py check                                                        verify token, account and public URL

Times are Santo Domingo time. Instagram has no API scheduling, so `run-due` publishes at the time.
run-due prints only when something happened (empty output = silent cron).

Env: IG_ACCESS_TOKEN (Instagram Login token with instagram_business_content_publish; seeds the token file),
     PUBLIC_MEDIA_BASE (URL of the public file server, e.g. https://files.example.com),
     PUBLIC_MEDIA_DIR (folder it serves; default $HERMES_HOME/public), IG_API_VERSION (default v23.0).
Files: $HERMES_HOME/rodado/publish/{queue.json, token.json}; public copies in $PUBLIC_MEDIA_DIR/rodado/<random>/ while publishing
`queue` needs Pillow (PNG -> JPEG; Instagram accepts JPEG only). Everything else is stdlib.
"""
import datetime as dt
import json
import os
import re
import secrets
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Santo_Domingo")
HOME = Path(os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes"))
BASE = HOME / "rodado" / "publish"
QUEUE = BASE / "queue.json"
TOKEN = BASE / "token.json"
PUBLIC = Path(os.environ.get("PUBLIC_MEDIA_DIR") or HOME / "public") / "rodado"   # served at PUBLIC_MEDIA_BASE
API = os.environ.get("IG_API_BASE", "https://graph.instagram.com") + "/" + os.environ.get("IG_API_VERSION", "v23.0")
VIDEO = {".mp4", ".mov"}


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def now():
    return dt.datetime.now(TZ)


# ---------- queue storage ----------

def load_queue():
    return json.loads(QUEUE.read_text()) if QUEUE.exists() else []


def save_queue(q):
    BASE.mkdir(parents=True, exist_ok=True)
    tmp = QUEUE.with_suffix(".tmp")
    tmp.write_text(json.dumps(q, indent=2, ensure_ascii=False))
    tmp.replace(QUEUE)


# ---------- post folder -> media + caption ----------

def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.split("#")[0].strip().strip('"').strip("'")
    return out


def caption_of(text):
    m = re.search(r"## Caption[^\n]*\n+```[^\n]*\n(.*?)\n```", text, re.S)
    if not m:
        die("No caption found: post.md needs a '## Caption' section with a ``` block.")
    cap = m.group(1).strip()
    if len(cap) > 2200:
        die(f"Caption is {len(cap)} characters; Instagram allows 2200.")
    return cap


def media_of(folder, fmt):
    final = folder / "final"
    if not final.is_dir():
        die(f"No final/ folder in {folder}")
    files = sorted(p for p in final.iterdir() if p.is_file())
    if fmt.startswith("reel"):
        vids = [p for p in files if p.suffix.lower() in VIDEO]
        if not vids:
            die("Reel: no .mp4 in final/.")
        return [max(vids, key=lambda p: p.stat().st_mtime)]
    slides = {}
    for p in files:
        if p.name.endswith("-poster.png") or p.suffix.lower() not in {".png", ".jpg", ".jpeg"} | VIDEO:
            continue
        m = re.search(r"-(\d{2})\.(png|jpe?g|mp4|mov)$", p.name, re.I)
        key = int(m.group(1)) if m else 1
        if key not in slides or p.suffix.lower() in VIDEO:   # a clip wins over a still for the same slide
            slides[key] = p
    if not slides:
        die("No slides (PNG/JPG/MP4) in final/.")
    items = [slides[k] for k in sorted(slides)]
    if len(items) > 10:
        die("Instagram carousels allow at most 10 items.")
    return items


def to_jpeg(p, out_dir):
    if p.suffix.lower() in VIDEO or p.suffix.lower() in {".jpg", ".jpeg"}:
        dest = out_dir / p.name
        shutil.copy2(p, dest)
        return dest
    from PIL import Image
    dest = out_dir / (p.stem + ".jpg")
    Image.open(p).convert("RGB").save(dest, "JPEG", quality=92, optimize=True)
    return dest


def cmd_queue(args):
    folder = Path(args[0]).resolve()
    post = (folder / "post.md").read_text(encoding="utf-8")
    fm = frontmatter(post)
    fmt = fm.get("format", "")
    if "--at" in args:
        when = dt.datetime.strptime(args[args.index("--at") + 1], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    else:
        if not fm.get("date"):
            die("post.md has no date; pass --at 'YYYY-MM-DD HH:MM'.")
        when = dt.datetime.strptime(f"{fm['date']} {fm.get('time') or '12:00'}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    if when < now():
        die(f"{when:%Y-%m-%d %H:%M} is in the past.")
    title = args[args.index("--title") + 1] if "--title" in args else (re.search(r"^# (.+)$", post, re.M) or [None, folder.name])[1]
    cap = caption_of(post)
    items = media_of(folder, fmt)
    pid = when.strftime("%m%d-%H%M-") + secrets.token_hex(2)
    out = BASE / "ready" / pid
    out.mkdir(parents=True, exist_ok=True)
    ready = [str(to_jpeg(p, out)) for p in items]
    kind = "reel" if fmt.startswith("reel") else ("carousel" if len(ready) > 1 else ("video" if Path(ready[0]).suffix in VIDEO else "image"))
    q = load_queue()
    for old in [e for e in q if e["folder"] == str(folder) and e["status"] == "scheduled"]:
        shutil.rmtree(BASE / "ready" / old["id"], ignore_errors=True)
    q = [e for e in q if not (e["folder"] == str(folder) and e["status"] == "scheduled")]
    q.append({"id": pid, "title": title, "folder": str(folder), "format": fmt, "kind": kind, "at": when.isoformat(),
              "files": ready, "caption": cap, "status": "scheduled", "warned": False})
    save_queue(q)
    print(f"Scheduled {when:%a %d %b %H:%M} · {title} · {kind}, {len(ready)} file(s) · id {pid}")


def cmd_list(_):
    q = load_queue()
    rows = [e for e in q if e["status"] in ("scheduled", "failed")] or []
    if not rows:
        print("Nothing scheduled.")
    for e in sorted(rows, key=lambda e: e["at"]):
        at = dt.datetime.fromisoformat(e["at"])
        print(f"{e['id']} · {at:%a %d %b %H:%M} · {e['title']} · {e['kind']} · {e['status']}")


def cmd_cancel(args):
    q = load_queue()
    hit = [e for e in q if e["id"] == args[0] and e["status"] == "scheduled"]
    if not hit:
        die(f"No scheduled post with id {args[0]}.")
    hit[0]["status"] = "cancelled"
    save_queue(q)
    print(f"Cancelled {hit[0]['title']}.")


# ---------- Instagram API ----------

def token():
    if TOKEN.exists():
        t = json.loads(TOKEN.read_text())
    else:
        env = os.environ.get("IG_ACCESS_TOKEN") or die("IG_ACCESS_TOKEN is not set.")
        t = {"token": env, "refreshed": now().isoformat()}
        BASE.mkdir(parents=True, exist_ok=True)
        TOKEN.write_text(json.dumps(t))
        os.chmod(TOKEN, 0o600)
    age = now() - dt.datetime.fromisoformat(t["refreshed"])
    if age > dt.timedelta(days=7):      # long-lived tokens last 60 days; refresh weekly
        try:
            r = call("GET", "https://graph.instagram.com/refresh_access_token",
                     {"grant_type": "ig_refresh_token", "access_token": t["token"]}, raw=True)
            t = {"token": r["access_token"], "refreshed": now().isoformat()}
            TOKEN.write_text(json.dumps(t))
        except SystemExit:
            pass                         # keep the old one; check will report if it's dead
    return t["token"]


def call(method, url, params, raw=False):
    if not raw:
        params = dict(params, access_token=token())
    data = None
    if method == "GET":
        url = url + "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            body = json.loads(body).get("error", {}).get("message", body)
        except Exception:
            pass
        die(f"Instagram API {e.code}: {body[:600]}")


def ig_id():
    return call("GET", f"{API}/me", {"fields": "user_id,username"})["user_id"]


def wait_ready(cid, label):
    for _ in range(90):                  # up to ~15 min for videos
        st = call("GET", f"{API}/{cid}", {"fields": "status_code"}).get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            die(f"Instagram could not process {label} ({st}).")
        time.sleep(10)
    die(f"Timed out waiting for Instagram to process {label}.")


def publish(e, uid):
    base = os.environ.get("PUBLIC_MEDIA_BASE") or die("PUBLIC_MEDIA_BASE is not set.")
    slot = secrets.token_urlsafe(18)
    pub = PUBLIC / slot
    pub.mkdir(parents=True, exist_ok=True)
    try:
        urls = []
        for f in e["files"]:
            shutil.copy2(f, pub / Path(f).name)
            urls.append((f"{base.rstrip('/')}/rodado/{slot}/{urllib.parse.quote(Path(f).name)}", Path(f).suffix.lower() in VIDEO))
        if e["kind"] == "reel":
            cid = call("POST", f"{API}/{uid}/media", {"media_type": "REELS", "video_url": urls[0][0],
                                                    "caption": e["caption"], "share_to_feed": "true"})["id"]
            wait_ready(cid, "the reel")
        elif e["kind"] == "carousel":
            kids = []
            for i, (u, is_vid) in enumerate(urls, 1):
                p = {"is_carousel_item": "true", **({"media_type": "VIDEO", "video_url": u} if is_vid else {"image_url": u})}
                k = call("POST", f"{API}/{uid}/media", p)["id"]
                wait_ready(k, f"slide {i}")
                kids.append(k)
            cid = call("POST", f"{API}/{uid}/media", {"media_type": "CAROUSEL", "children": ",".join(kids),
                                                    "caption": e["caption"]})["id"]
            wait_ready(cid, "the carousel")
        else:
            u, is_vid = urls[0]
            p = {"media_type": "REELS", "video_url": u} if is_vid else {"image_url": u}
            cid = call("POST", f"{API}/{uid}/media", dict(p, caption=e["caption"]))["id"]
            wait_ready(cid, "the post")
        mid = call("POST", f"{API}/{uid}/media_publish", {"creation_id": cid})["id"]
        link = call("GET", f"{API}/{mid}", {"fields": "permalink"}).get("permalink", "")
        return mid, link
    finally:
        shutil.rmtree(pub, ignore_errors=True)


def cmd_run_due(_):
    lock = BASE / ".lock"
    BASE.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL)
        os.close(fd)
    except FileExistsError:
        if time.time() - lock.stat().st_mtime < 3600:
            return
        lock.unlink()
        return cmd_run_due(_)
    try:
        q = load_queue()
        out, uid = [], None
        for e in sorted(q, key=lambda e: e["at"]):
            if e["status"] != "scheduled":
                continue
            at = dt.datetime.fromisoformat(e["at"])
            if not e.get("warned") and now() >= at - dt.timedelta(hours=1) and now() < at:
                out.append(f"In 1 hour ({at:%H:%M}): {e['title']} · id {e['id']}. Reply 'cancel {e['id']}' to stop it.")
                e["warned"] = True
            if now() >= at:
                try:
                    uid = uid or ig_id()
                    mid, link = publish(e, uid)
                    e.update(status="published", media_id=mid, permalink=link, published_at=now().isoformat())
                    shutil.rmtree(BASE / "ready" / e["id"], ignore_errors=True)
                    out.append(f"Published: {e['title']} · {link}")
                except SystemExit as err:
                    e.update(status="failed", error=str(err.code if isinstance(err.code, str) else err))
                    out.append(f"FAILED to publish {e['title']} (id {e['id']}): {e['error']}")
            save_queue(q)
        if out:
            print("\n".join(out))
    finally:
        lock.unlink(missing_ok=True)


def cmd_check(_):
    me = call("GET", f"{API}/me", {"fields": "user_id,username"})
    print(f"Token OK · @{me.get('username')} · id {me.get('user_id')}")
    base = os.environ.get("PUBLIC_MEDIA_BASE") or die("PUBLIC_MEDIA_BASE is not set.")
    probe = PUBLIC / "check"
    probe.mkdir(parents=True, exist_ok=True)
    (probe / "ok.txt").write_text("ok")
    try:
        with urllib.request.urlopen(f"{base.rstrip('/')}/rodado/check/ok.txt", timeout=20) as r:
            print(f"Public URL OK · {base}" if r.read().strip() == b"ok" else "Public URL answered but with the wrong content")
    except Exception as err:
        print(f"Public URL NOT reachable ({base}): {err}")
    finally:
        shutil.rmtree(probe, ignore_errors=True)


if __name__ == "__main__":
    cmds = {"queue": cmd_queue, "list": cmd_list, "cancel": cmd_cancel, "run-due": cmd_run_due, "check": cmd_check}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
