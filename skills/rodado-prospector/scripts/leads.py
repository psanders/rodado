#!/usr/bin/env python3
"""Lead ledger for Rodado's outbound email: who we found, who Pedro approved, what was sent,
what's due next, and the hard daily limits. The agent finds leads and sends through Gmail;
this script decides WHAT may be sent and WHEN, and keeps the record.

Commands (all output is plain text or JSON for the agent):
  add <lead.json>                  add a proposed lead (refuses duplicates and do-not-contact)
  list [status]                    proposed | approved | active | replied | stopped | all
  show <id>
  approve <id> [<id> ...]          Pedro said yes
  reject <id> [<id> ...] [--reason R]
  due                              JSON: what may be sent in THIS run (follow-ups first, then new), within limits
  sent <id> --step N --thread T [--message M]   record a send right after it went out
  fail <id> --step N --reason R    record a failed send (not counted)
  stop <id> --reason replied|bounced|unsubscribed|not_interested|manual [--note N]
  active                           JSON: leads waiting for an answer (for the reply check)
  dnc add <email-or-domain> | dnc list
  stats                            today's sends vs limits, pipeline counts
  expire                           drop proposed leads older than 3 days

Data: $CONTENT_DATA/leads/{leads.json, settings.json, dnc.txt, log.csv}
Limits (settings.json, created with defaults): max 15 emails/day, max 5 new/day, max 5 per run,
follow-ups on day 3 and day 8 after the first email, Mon-Fri 08:30-17:30 Santo Domingo time.
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
DEFAULTS = {"max_per_day": 15, "max_new_per_day": 5, "max_per_run": 5, "followup_days": [3, 8],
            "send_days": [0, 1, 2, 3, 4], "send_start": "08:30", "send_end": "17:30", "proposed_ttl_days": 3}
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


def sends_today():
    if not LOG.exists():
        return 0, 0
    today = now().date().isoformat()
    total = new = 0
    with LOG.open() as f:
        for r in csv.DictReader(f):
            if r["event"] == "sent" and r["time"].startswith(today):
                total += 1
                new += r["step"] == "0"
    return total, new


def in_window(s):
    n = now()
    hhmm = n.strftime("%H:%M")
    return n.weekday() in s["send_days"] and s["send_start"] <= hhmm <= s["send_end"]


# ---------- commands ----------

def cmd_add(args):
    lead = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    for k in ("company", "email", "email_source", "why", "first_email", "followups"):
        if not lead.get(k):
            die(f"Missing field: {k}")
    email = lead["email"].strip().lower()
    if not EMAIL_RE.match(email):
        die(f"Not a valid email: {email}")
    if blocked(email):
        die(f"{email} is on the do-not-contact list.")
    leads = load()
    domain = email.split("@")[-1]
    generic = {"gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com", "live.com"}
    for l in leads:
        if l["email"] == email or (domain not in generic and l["email"].split("@")[-1] == domain) \
                or l["company"].strip().lower() == lead["company"].strip().lower():
            die(f"Duplicate of {l['id']} ({l['company']}, {l['status']}).")
    s = settings()
    if len(lead["followups"]) < len(s["followup_days"]):
        die(f"Need {len(s['followup_days'])} follow-up texts.")
    lid = "L%03d" % (max([int(l["id"][1:]) for l in leads] or [0]) + 1)
    lead.update(id=lid, email=email, status="proposed", added=now().isoformat(timespec="seconds"),
                steps=[], next_step=0, next_due=None, thread_id=None)
    leads.append(lead)
    save(leads)
    log({"id": lid, "event": "proposed", "step": "", "email": email, "detail": lead["company"]})
    print(f"{lid} · {lead['company']} · {email} · proposed")


def cmd_list(args):
    st = args[0] if args else "all"
    rows = [l for l in load() if st == "all" or l["status"] == st]
    if not rows:
        print(f"No leads ({st}).")
    for l in rows:
        nd = f" · next: step {l['next_step']} on {l['next_due'][:10]}" if l.get("next_due") and l["status"] in ("approved", "active") else ""
        print(f"{l['id']} · {l['company']} · {l['email']} · {l['status']}{nd}")


def cmd_show(args):
    print(json.dumps(get(load(), args[0]), indent=2, ensure_ascii=False))


def cmd_approve(args):
    leads = load()
    for lid in args:
        l = get(leads, lid)
        if l["status"] != "proposed":
            print(f"{lid} is {l['status']}, skipped.")
            continue
        l.update(status="approved", approved=now().isoformat(timespec="seconds"), next_step=0,
                 next_due=now().isoformat(timespec="seconds"))
        log({"id": lid, "event": "approved", "step": "", "email": l["email"], "detail": ""})
        print(f"{lid} approved · first email goes out in the next send window")
    save(leads)


def cmd_reject(args):
    reason = args[args.index("--reason") + 1] if "--reason" in args else ""
    ids = [a for a in args if re.match(r"^L\d+$", a)]
    leads = load()
    for lid in ids:
        l = get(leads, lid)
        l.update(status="rejected", reason=reason)
        log({"id": lid, "event": "rejected", "step": "", "email": l["email"], "detail": reason})
        print(f"{lid} rejected")
    save(leads)


def cmd_due(_):
    s = settings()
    out = {"window_open": in_window(s), "items": []}
    if not out["window_open"]:
        out["note"] = f"Outside the send window ({s['send_start']}-{s['send_end']} Mon-Fri). Send nothing."
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    total, new = sends_today()
    room = min(s["max_per_day"] - total, s["max_per_run"])
    new_room = s["max_new_per_day"] - new
    n = now()
    leads = load()
    follow = [l for l in leads if l["status"] == "active" and l.get("next_due") and dt.datetime.fromisoformat(l["next_due"]) <= n]
    first = [l for l in leads if l["status"] == "approved"]
    follow.sort(key=lambda l: l["next_due"])
    first.sort(key=lambda l: l.get("approved", ""))
    for l in follow:
        if room <= 0:
            break
        if blocked(l["email"]):
            continue
        k = l["next_step"]
        out["items"].append({"id": l["id"], "step": k, "kind": "follow-up", "to": l["email"], "company": l["company"],
                             "thread_id": l["thread_id"], "in_reply_to": l["steps"][-1].get("message_id") if l["steps"] else None,
                             "subject": "Re: " + l["first_email"]["subject"], "body": l["followups"][k - 1]})
        room -= 1
    for l in first:
        if room <= 0 or new_room <= 0:
            break
        if blocked(l["email"]):
            continue
        out["items"].append({"id": l["id"], "step": 0, "kind": "first", "to": l["email"], "company": l["company"],
                             "subject": l["first_email"]["subject"], "body": l["first_email"]["body"]})
        room -= 1
        new_room -= 1
    out["limits"] = {"sent_today": total, "max_per_day": s["max_per_day"], "new_today": new,
                     "max_new_per_day": s["max_new_per_day"], "this_run": len(out["items"])}
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_sent(args):
    lid = args[0]
    step = int(args[args.index("--step") + 1])
    thread = args[args.index("--thread") + 1] if "--thread" in args else None
    msg = args[args.index("--message") + 1] if "--message" in args else None
    s = settings()
    total, new = sends_today()
    if total >= s["max_per_day"] or (step == 0 and new >= s["max_new_per_day"]):
        print("WARNING: this send was over today's limit. Stop sending for today and tell Pedro.")
    leads = load()
    l = get(leads, lid)
    if step != l["next_step"]:
        die(f"{lid}: expected step {l['next_step']}, got {step}.")
    l["steps"].append({"step": step, "sent": now().isoformat(timespec="seconds"), "message_id": msg})
    if step == 0:
        l["thread_id"] = thread
        l["first_sent"] = now().isoformat(timespec="seconds")
    l["status"] = "active"
    days = s["followup_days"]
    if step < len(days):
        first = dt.datetime.fromisoformat(l["first_sent"])
        due = (first + dt.timedelta(days=days[step])).replace(hour=9, minute=0, second=0)
        while due.weekday() not in s["send_days"]:
            due += dt.timedelta(days=1)
        l["next_step"], l["next_due"] = step + 1, due.isoformat(timespec="seconds")
    else:
        l["next_step"], l["next_due"] = None, None
        l["status"] = "finished"            # sequence done, no reply
    save(leads)
    log({"id": lid, "event": "sent", "step": str(step), "email": l["email"], "detail": thread or ""})
    nd = f"next: step {l['next_step']} on {l['next_due'][:10]}" if l["next_due"] else "sequence finished"
    print(f"{lid} · step {step} recorded · {nd}")


def cmd_fail(args):
    lid = args[0]
    step = args[args.index("--step") + 1]
    reason = args[args.index("--reason") + 1] if "--reason" in args else ""
    l = get(load(), lid)
    log({"id": lid, "event": "failed", "step": step, "email": l["email"], "detail": reason})
    print(f"{lid} · failure logged (not counted against the limit)")


def cmd_stop(args):
    lid = args[0]
    reason = args[args.index("--reason") + 1]
    note = args[args.index("--note") + 1] if "--note" in args else ""
    leads = load()
    l = get(leads, lid)
    l.update(status="replied" if reason == "replied" else "stopped", stop_reason=reason, note=note,
             next_step=None, next_due=None, stopped=now().isoformat(timespec="seconds"))
    if reason in ("unsubscribed", "not_interested", "bounced"):
        with DNC.open("a") as f:
            f.write(l["email"] + "\n")
    save(leads)
    log({"id": lid, "event": "stopped", "step": "", "email": l["email"], "detail": f"{reason} {note}".strip()})
    print(f"{lid} · {l['status']} ({reason})")


def cmd_active(_):
    rows = [{"id": l["id"], "company": l["company"], "email": l["email"], "thread_id": l["thread_id"],
             "first_sent": l.get("first_sent"), "steps_sent": len(l["steps"])}
            for l in load() if l["status"] in ("active", "finished")]
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cmd_dnc(args):
    if args and args[0] == "add":
        DIR.mkdir(parents=True, exist_ok=True)
        with DNC.open("a") as f:
            f.write(args[1].strip().lower() + "\n")
        print(f"Added {args[1]} to do-not-contact.")
    else:
        print("\n".join(sorted(dnc())) or "Empty.")


def cmd_stats(_):
    s = settings()
    total, new = sends_today()
    by = {}
    for l in load():
        by[l["status"]] = by.get(l["status"], 0) + 1
    print(f"Today: {total}/{s['max_per_day']} emails · {new}/{s['max_new_per_day']} new · window {'open' if in_window(s) else 'closed'}")
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
            "due": cmd_due, "sent": cmd_sent, "fail": cmd_fail, "stop": cmd_stop, "active": cmd_active,
            "dnc": cmd_dnc, "stats": cmd_stats, "expire": cmd_expire}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
