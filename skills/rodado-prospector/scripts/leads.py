#!/usr/bin/env python3
"""Lead list for Rodado: brands that look like our customers, found by the prospector.
Collect and track only; nothing is sent from here.

Commands:
  add <lead.json>                 add a proposed lead (refuses duplicates and do-not-contact)
  list [status]                   proposed | approved | contacted | replied | won | lost | rejected | expired | all
  show <id>
  approve <id> [<id> ...]         Pedro wants to contact them
  reject <id> [<id> ...] [--reason R]
  mark <id> <status> [--note N]   contacted | replied | won | lost | not_fit  (Pedro updates as he works them)
  dnc add <email-or-domain> | dnc list
  stats                           pipeline counts
  export                          CSV of all leads to stdout
  expire                          proposed leads older than 3 days -> expired

Data: $CONTENT_DATA/leads/{leads.json, dnc.txt, log.csv}
"""
import csv
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Santo_Domingo")
if not os.environ.get("CONTENT_DATA"):
    sys.exit("CONTENT_DATA is not set (the data folder, e.g. /opt/data/rodado). Tell Pedro.")
DIR = Path(os.environ["CONTENT_DATA"]) / "leads"
LEADS, SETTINGS, DNC, LOG = DIR / "leads.json", DIR / "settings.json", DIR / "dnc.txt", DIR / "log.csv"
DEFAULTS = {"proposed_ttl_days": 3}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.I)


def now():
    return dt.datetime.now(TZ)


def die(msg):
    raise SystemExit(msg)


def settings():
    DIR.mkdir(parents=True, exist_ok=True)
    if not SETTINGS.exists():
        SETTINGS.write_text(json.dumps(DEFAULTS, indent=2))
    return {**DEFAULTS, **json.loads(SETTINGS.read_text())}


def load():
    return json.loads(LEADS.read_text()) if LEADS.exists() else []


def save(leads):
    DIR.mkdir(parents=True, exist_ok=True)
    tmp = LEADS.with_suffix(".tmp")
    tmp.write_text(json.dumps(leads, indent=2, ensure_ascii=False))
    tmp.replace(LEADS)


def log(row):
    new = not LOG.exists()
    with LOG.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["time", "id", "event", "step", "email", "detail"])
        if new:
            w.writeheader()
        w.writerow({"time": now().isoformat(timespec="seconds"), **row})


def dnc():
    return {l.strip().lower() for l in DNC.read_text().splitlines() if l.strip()} if DNC.exists() else set()


def blocked(email):
    e = email.lower()
    d = dnc()
    return e in d or e.split("@")[-1] in d


def get(leads, lid):
    for l in leads:
        if l["id"] == lid:
            return l
    die(f"No lead {lid}.")


def cmd_add(args):
    lead = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    for k in ("company", "why"):
        if not lead.get(k):
            die(f"Missing field: {k}")
    email = (lead.get("email") or "").strip().lower()
    if email and not EMAIL_RE.match(email):
        die(f"Not a valid email: {email}")
    if email and not lead.get("email_source"):
        die("An email needs its email_source (the URL where it's published).")
    if email and blocked(email):
        die(f"{email} is on the do-not-contact list.")
    leads = load()
    domain = email.split("@")[-1] if email else None
    generic = {"gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com", "live.com"}
    for l in leads:
        le = l.get("email") or ""
        if (email and le == email) or (domain and domain not in generic and le.split("@")[-1] == domain) \
                or l["company"].strip().lower() == lead["company"].strip().lower():
            die(f"Duplicate of {l['id']} ({l['company']}, {l['status']}).")
    lid = "L%03d" % (max([int(l["id"][1:]) for l in leads] or [0]) + 1)
    lead.update(id=lid, email=email or None, status="proposed", added=now().isoformat(timespec="seconds"), history=[])
    leads.append(lead)
    save(leads)
    log({"id": lid, "event": "proposed", "step": "", "email": email, "detail": lead["company"]})
    print(f"{lid} · {lead['company']} · {email or 'no email (DM)'} · proposed")


def cmd_list(args):
    st = args[0] if args else "all"
    rows = [l for l in load() if st == "all" or l["status"] == st]
    if not rows:
        print(f"No leads ({st}).")
    for l in rows:
        print(f"{l['id']} · {l['company']} · {l.get('email') or l.get('instagram') or '-'} · {l['status']}")


def cmd_show(args):
    print(json.dumps(get(load(), args[0]), indent=2, ensure_ascii=False))


def cmd_approve(args):
    leads = load()
    for lid in args:
        l = get(leads, lid)
        if l["status"] != "proposed":
            print(f"{lid} is {l['status']}, skipped.")
            continue
        l.update(status="approved", approved=now().isoformat(timespec="seconds"))
        log({"id": lid, "event": "approved", "step": "", "email": l.get("email"), "detail": ""})
        print(f"{lid} approved · {l['company']}")
    save(leads)


def cmd_reject(args):
    reason = args[args.index("--reason") + 1] if "--reason" in args else ""
    ids = [a for a in args if re.match(r"^L\d+$", a)]
    leads = load()
    for lid in ids:
        l = get(leads, lid)
        l.update(status="rejected", reason=reason)
        log({"id": lid, "event": "rejected", "step": "", "email": l.get("email"), "detail": reason})
        print(f"{lid} rejected")
    save(leads)


def cmd_mark(args):
    lid, status = args[0], args[1]
    if status not in ("contacted", "replied", "won", "lost", "not_fit"):
        die("Status must be contacted | replied | won | lost | not_fit.")
    note = args[args.index("--note") + 1] if "--note" in args else ""
    leads = load()
    l = get(leads, lid)
    l.setdefault("history", []).append({"time": now().isoformat(timespec="seconds"), "status": status, "note": note})
    l["status"] = status
    if status in ("lost", "not_fit") and l.get("email") and "no contactar" in note.lower():
        with DNC.open("a") as f:
            f.write(l["email"] + "\n")
    save(leads)
    log({"id": lid, "event": status, "step": "", "email": l.get("email"), "detail": note})
    print(f"{lid} · {l['company']} · {status}")


def cmd_export(_):
    w = csv.writer(sys.stdout)
    cols = ["id", "status", "company", "category", "city", "contact_name", "role", "email", "email_source",
            "instagram", "website", "why", "source", "added"]
    w.writerow(cols)
    for l in load():
        w.writerow([l.get(c, "") or "" for c in cols])


def cmd_dnc(args):
    if args and args[0] == "add":
        DIR.mkdir(parents=True, exist_ok=True)
        with DNC.open("a") as f:
            f.write(args[1].strip().lower() + "\n")
        print(f"Added {args[1]} to do-not-contact.")
    else:
        print("\n".join(sorted(dnc())) or "Empty.")


def cmd_stats(_):
    by = {}
    for l in load():
        by[l["status"]] = by.get(l["status"], 0) + 1
    print("Pipeline: " + " · ".join(f"{k} {v}" for k, v in sorted(by.items())) if by else "Pipeline: empty")


def cmd_expire(_):
    s = settings()
    leads = load()
    cut = now() - dt.timedelta(days=s["proposed_ttl_days"])
    n = 0
    for l in leads:
        if l["status"] == "proposed" and dt.datetime.fromisoformat(l["added"]) < cut:
            l["status"] = "expired"
            n += 1
    save(leads)
    print(f"{n} proposed lead(s) expired.")


if __name__ == "__main__":
    cmds = {"add": cmd_add, "list": cmd_list, "show": cmd_show, "approve": cmd_approve, "reject": cmd_reject,
            "mark": cmd_mark, "dnc": cmd_dnc, "stats": cmd_stats, "export": cmd_export, "expire": cmd_expire}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
