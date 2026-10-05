#!/usr/bin/env python3
"""Design one Rodado slide with the pen.dev CLI, export it to PNG, and log the cost.

Usage:
    python pen_design.py --brief brief.md --out <dir> --name <stem> [--media img.png ...] [--est 1.50] [--dry-run]

- brief.md: the full design brief (text, layout intent, brand tokens). Sent as the prompt.
- --media: approved images to place (attached to the prompt). Repeatable. Video is not supported by Pen.
- Writes <dir>/<stem>.pen (editable in Pencil) and <dir>/<stem>.png, plus <stem>-usage.json.
- Shares the producer's ledger and monthly cap (spend.csv): refuses (exit 3) if the cap would be passed.

Env: PEN_CLI_KEY (pen.dev auth), PEN_AGENT_API_KEY (Anthropic key for Pen's design agent; Hermes strips ANTHROPIC_API_KEY from scripts), PEN_BIN (optional path to `pen`),
     RODADO_MONTHLY_CAP (default 100), RODADO_LEDGER (default $HERMES_HOME/rodado/library/spend.csv).
"""
import csv
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def ledger():
    if os.environ.get("RODADO_LEDGER"):
        return Path(os.environ["RODADO_LEDGER"])
    home = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
    return Path(home) / "rodado" / "library" / "spend.csv"


def month_spend(p):
    m = dt.date.today().strftime("%Y-%m")
    if not p.exists():
        return 0.0
    with p.open() as f:
        return sum(float(r["usd"]) for r in csv.DictReader(f) if r["date"].startswith(m))


def log(p, row):
    new = not p.exists()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "name", "endpoint", "usd", "request_id", "note"])
        if new:
            w.writeheader()
        w.writerow(row)


def pen_bin():
    for c in (os.environ.get("PEN_BIN"), shutil.which("pen"),
              str(Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser() / "tools/pen/node_modules/.bin/pen")):
        if c and Path(c).exists():
            return c
    die("pen CLI not found. Install: npm i --prefix $HERMES_HOME/tools/pen @pen.dev/cli (Node >= 22.19).")


def find_cost(obj):
    """Best-effort: the usage JSON's total cost in USD."""
    if isinstance(obj, dict):
        for k in ("total_cost_usd", "cost_usd", "totalCostUsd", "costUsd", "total_cost", "cost"):
            if isinstance(obj.get(k), (int, float)):
                return float(obj[k])
        for v in obj.values():
            c = find_cost(v)
            if c is not None:
                return c
    return None


def main():
    if "--brief" not in sys.argv or "--out" not in sys.argv or "--name" not in sys.argv:
        die(__doc__)
    brief = Path(arg("--brief")).read_text(encoding="utf-8")
    out = Path(arg("--out"))
    name = arg("--name")
    est = float(arg("--est", "1.50"))
    media = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--media"]
    for m in media:
        if not Path(m).exists():
            die(f"media not found: {m}")
        if Path(m).suffix.lower() in {".mp4", ".mov", ".webm"}:
            die("Pen can't place video: use render.py for slides with clips.")
    cap = float(os.environ.get("RODADO_MONTHLY_CAP", "100"))
    led = ledger()
    spent = month_spend(led)
    if spent + est > cap:
        die(f"Refused: month spend US${spent:.2f} + Pen run ≈US${est:.2f} would pass the cap US${cap:.2f}. Ask Pedro.", 3)
    if "--dry-run" in sys.argv:
        print(f"dry-run ok · pen · cost≈US${est:.2f} month≈US${spent:.2f}/{cap:.0f}")
        return
    out.mkdir(parents=True, exist_ok=True)
    pen_file, png, usage = out / f"{name}.pen", out / f"{name}.png", out / f"{name}-usage.json"
    cmd = [pen_bin(), "--out", str(pen_file), "--prompt", brief, "--export", str(png),
           "--export-type", "png", "--export-scale", "1", "--usage", str(usage), "--max-failed-calls", "8"]
    if arg("--model"):
        cmd += ["--model", arg("--model")]
    for m in media:
        cmd += ["--prompt-file", m]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1500)
    cost = None
    if usage.exists():
        try:
            cost = find_cost(json.loads(usage.read_text()))
        except Exception:
            pass
    cost = est if cost is None else cost
    log(led, {"date": dt.date.today().isoformat(), "name": name, "endpoint": "pen.dev",
              "usd": f"{cost:.4f}", "request_id": "", "note": "pen design"})
    if r.returncode != 0 or not png.exists():
        die(f"pen failed (exit {r.returncode}).\n{(r.stderr or r.stdout)[-1500:]}")
    try:
        from PIL import Image
        im = Image.open(png)
        if im.size != (1080, 1350):
            sc = max(1080 / im.width, 1350 / im.height)
            im = im.convert("RGB").resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
            l, t = (im.width - 1080) // 2, (im.height - 1350) // 2
            im.crop((l, t, l + 1080, t + 1350)).save(png)
            print(f"note: export was not 1080x1350; scaled and center-cropped")
    except ImportError:
        pass
    print(pen_file)
    print(png)
    print(f"cost≈US${cost:.2f} month≈US${spent + cost:.2f}/{cap:.0f}")


if __name__ == "__main__":
    main()
