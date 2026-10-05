#!/usr/bin/env python3
"""Run one fal.ai generation with a hard budget check, and save the results.

Usage:
    python fal.py <endpoint> <input.json> --out <dir> --name <A0NN> [--est USD] [--dry-run]

- <input.json> is the model input. Any string value "@/path/to/file" is sent as a data URI
  (use it for local reference images/audio). Remote https URLs pass through unchanged.
- Cost is estimated from references/models.md prices (built into PRICES below) or --est.
  The call is refused (exit 3) if this month's spend + estimate would pass the cap.
- Every call is logged to <ledger> (default $HERMES_HOME/rodado/library/spend.csv).
- Saves <name>.<ext> (and <name>-2.<ext> … for several outputs) plus <name>.json (full response).
  Prints one line per saved file, then "cost≈US$x.xx month≈US$y.yy/cap".

Env: FAL_KEY (required), RODADO_MONTHLY_CAP (default 100), RODADO_MAX_CALL (default 10),
     RODADO_LEDGER (default $HERMES_HOME/rodado/library/spend.csv).
Stdlib only.
"""
import base64
import csv
import datetime as dt
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

QUEUE = os.environ.get("FAL_QUEUE_URL", "https://queue.fal.run")

# USD. "image" = per image; "sec" = per output second by resolution.
PRICES = {
    "bytedance/seedream/v5/pro/text-to-image": {"image": 0.0675},
    "bytedance/seedream/v5/pro/edit": {"image": 0.0675},
    "fal-ai/bytedance/seedream/v5/lite/text-to-image": {"image": 0.035},
    "fal-ai/bytedance/seedream/v5/lite/edit": {"image": 0.035},
    "bytedance/seedance-2.5/text-to-video": {"sec": {"480p": 0.2205, "720p": 0.473, "1080p": 1.164}},
    "bytedance/seedance-2.5/image-to-video": {"sec": {"480p": 0.2205, "720p": 0.473, "1080p": 1.164}},
    "bytedance/seedance-2.5/reference-to-video": {"sec": {"480p": 0.1323, "720p": 0.2838, "1080p": 0.70}},
    "bytedance/seedance-2.5/draft/complete": {"sec": {"1080p": 1.164}},
}


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def estimate(endpoint, inp, override):
    if override is not None:
        return float(override)
    p = PRICES.get(endpoint)
    if not p:
        die(f"No price known for {endpoint}: pass --est <USD> (check fal.ai pricing).")
    if "image" in p:
        return p["image"] * int(inp.get("num_images", 1) or 1)
    res = inp.get("resolution", "720p")
    if endpoint.endswith("draft/complete"):
        res = "1080p"
    dur = inp.get("duration", "auto")
    if dur in (None, "auto"):
        die("Set an explicit duration (seconds) so the cost is known; 'auto' can run to 30 s.")
    rate = p["sec"].get(res) or max(p["sec"].values())
    est = rate * float(dur)
    if inp.get("draft"):
        est = p["sec"].get("480p", rate) * float(dur)   # drafts are previews; conservative
    return est


def ledger_path():
    if os.environ.get("RODADO_LEDGER"):
        return Path(os.environ["RODADO_LEDGER"])
    home = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
    return Path(home) / "rodado" / "library" / "spend.csv"


def month_spend(path):
    month = dt.date.today().strftime("%Y-%m")
    if not path.exists():
        return 0.0
    with path.open() as f:
        return sum(float(r["usd"]) for r in csv.DictReader(f) if r["date"].startswith(month))


def log(path, row):
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "name", "endpoint", "usd", "request_id", "note"])
        if new:
            w.writeheader()
        w.writerow(row)


def inline_files(v):
    if isinstance(v, str) and v.startswith("@") and len(v) > 1:
        p = Path(v[1:]).expanduser()
        if not p.exists():
            die(f"Reference file not found: {p}")
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    if isinstance(v, list):
        return [inline_files(x) for x in v]
    if isinstance(v, dict):
        return {k: inline_files(x) for k, x in v.items()}
    return v


def http(method, url, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Key {key}", "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        die(f"fal {method} {url} -> HTTP {e.code}: {e.read().decode(errors='replace')[:800]}")


def media_urls(obj):
    """All file URLs in a fal response, in order (images[], video, audio, …)."""
    out = []
    if isinstance(obj, dict):
        if isinstance(obj.get("url"), str) and obj["url"].startswith("http"):
            out.append((obj["url"], obj.get("content_type") or ""))
        for k, v in obj.items():
            if k != "url":
                out += media_urls(v)
    elif isinstance(obj, list):
        for v in obj:
            out += media_urls(v)
    return out


def ext_for(url, ctype):
    e = Path(url.split("?")[0]).suffix.lower()
    if e in {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".webm", ".mp3", ".wav", ".m4a"}:
        return e
    return mimetypes.guess_extension((ctype or "").split(";")[0]) or ".bin"


def main(argv):
    if len(argv) < 3 or "--out" not in argv or "--name" not in argv:
        die(__doc__)
    endpoint, inp_path = argv[1], Path(argv[2])
    out = Path(argv[argv.index("--out") + 1])
    name = argv[argv.index("--name") + 1]
    est_override = argv[argv.index("--est") + 1] if "--est" in argv else None
    dry = "--dry-run" in argv

    inp = json.loads(inp_path.read_text(encoding="utf-8"))
    est = estimate(endpoint, inp, est_override)
    cap = float(os.environ.get("RODADO_MONTHLY_CAP", "100"))
    max_call = float(os.environ.get("RODADO_MAX_CALL", "10"))
    led = ledger_path()
    spent = month_spend(led)
    if est > max_call:
        die(f"Refused: this call ≈US${est:.2f}, above the per-call limit US${max_call:.2f}. Ask Pedro first.", 3)
    if spent + est > cap:
        die(f"Refused: month spend US${spent:.2f} + this call ≈US${est:.2f} would pass the cap US${cap:.2f}. Ask Pedro.", 3)
    if dry:
        print(f"dry-run ok · {endpoint} · cost≈US${est:.2f} month≈US${spent:.2f}/{cap:.0f}")
        return

    key = os.environ.get("FAL_KEY") or die("FAL_KEY is not set.")
    sub = http("POST", f"{QUEUE}/{endpoint}", key, inline_files(inp))
    rid = sub.get("request_id", "")
    status_url = sub.get("status_url") or f"{QUEUE}/{endpoint}/requests/{rid}/status"
    resp_url = sub.get("response_url") or f"{QUEUE}/{endpoint}/requests/{rid}"
    log(led, {"date": dt.date.today().isoformat(), "name": name, "endpoint": endpoint,
              "usd": f"{est:.4f}", "request_id": rid, "note": "submitted"})
    t0 = time.time()
    while True:
        st = http("GET", status_url, key).get("status")
        if st == "COMPLETED":
            break
        if st not in ("IN_QUEUE", "IN_PROGRESS"):
            die(f"fal status {st} for {rid}")
        if time.time() - t0 > 1800:
            die(f"Timed out waiting for {rid}; check it later on fal.ai.")
        time.sleep(5)
    res = http("GET", resp_url, key)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.json").write_text(json.dumps({"endpoint": endpoint, "request_id": rid, "input": inp,
                                                 "estimate_usd": est, "response": res}, indent=2))
    files = media_urls(res)
    if not files:
        print(f"No files in response (see {out / (name + '.json')}).")
    for i, (url, ctype) in enumerate(files, 1):
        dest = out / f"{name}{'' if i == 1 else f'-{i}'}{ext_for(url, ctype)}"
        urllib.request.urlretrieve(url, dest)
        print(dest)
    if res.get("draft_id"):
        print(f"draft_id {res['draft_id']}")
    print(f"cost≈US${est:.2f} month≈US${spent + est:.2f}/{cap:.0f}")


if __name__ == "__main__":
    main(sys.argv)
