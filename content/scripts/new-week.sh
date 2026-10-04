#!/usr/bin/env bash
# Creates calendar/<YYYY-Wnn>/ with 7 post folders from the templates.
# Usage: content/scripts/new-week.sh 2026-W42
set -euo pipefail
WEEK="${1:?Usage: new-week.sh YYYY-Wnn}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/calendar/$WEEK"
if [ -d "$DEST" ]; then echo "Already exists: $DEST"; exit 1; fi
python3 - "$WEEK" "$ROOT" <<'PY'
import sys, datetime, pathlib, re
week, root = sys.argv[1], pathlib.Path(sys.argv[2])
y, w = map(int, week.split("-W"))
monday = datetime.date.fromisocalendar(y, w, 1)
slots = [  # fixed weekly slots (see strategy.md)
  ("mon","reel-storyboard","proof"),
  ("tue","carousel-framework","strategy"),
  ("wed","reel-category","category"),
  ("thu","carousel-faq","trust"),
  ("fri","reel-storyboard","proof"),
  ("sat","static-quote","open"),
  ("sun","reel-cta","offer"),
]
base = (root/"templates/post.md").read_text()
dest = root/"calendar"/week
rows = []
for i,(day,fmt,pillar) in enumerate(slots):
    date = monday + datetime.timedelta(days=i)
    d = dest/f"{i+1:02d}-{day}-{fmt}"
    (d/"final").mkdir(parents=True); (d/"sources").mkdir()
    t = base.replace("YYYY-MM-DD", date.isoformat())
    t = re.sub(r"^day: .*$", f"day: {day}", t, flags=re.M)
    t = re.sub(r"^format: \S+", f"format: {fmt}", t, flags=re.M)
    t = re.sub(r"^pillar: \S+", f"pillar: {pillar}", t, flags=re.M)
    t += f"\n\nFormat template: ../../../templates/{fmt}.md\n"
    (d/"post.md").write_text(t)
    rows.append(f"| {day} {date.isoformat()} | {fmt} | {pillar} | | idea |")
(dest/"week.md").write_text(
  f"# Week {week} ({monday.isoformat()} to {(monday+datetime.timedelta(days=6)).isoformat()})\n\n"
  "| Day | Format | Pillar | Hook | Status |\n| --- | --- | --- | --- | --- |\n" + "\n".join(rows) + "\n")
print(dest)
PY
