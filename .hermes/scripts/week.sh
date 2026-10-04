#!/usr/bin/env bash
# Creates one week's card chain on the rodado board:
#   Retro (previous week) → Ideas → Briefs & copy → Audit
#   docker compose exec hermes bash /workspace/rodado/.hermes/scripts/week.sh 2026-W42
set -euo pipefail
WEEK="${1:?Usage: week.sh YYYY-Wnn}"
WS="${RODADO_WS:-/workspace/rodado}"
# Find a Python that has PyYAML (Hermes' own venv first). The `hermes` command may be a
# shell wrapper, so its shebang is not a reliable way to find Python.
find_py () {
  local c
  for c in "$(head -1 "$(command -v hermes)" | sed 's/^#!//')" \
           /opt/hermes/.venv/bin/python /opt/hermes/venv/bin/python /opt/venv/bin/python \
           "$(dirname "$(readlink -f "$(command -v hermes)")")/python" python3 python; do
    [ -n "$c" ] && command -v "$c" >/dev/null 2>&1 || continue
    "$c" -c 'import yaml, json' >/dev/null 2>&1 && { echo "$c"; return; }
  done
  echo "No Python with PyYAML found inside the container" >&2; exit 1
}
PY="$(find_py)"
PREV="$("$PY" -c "import datetime,sys; y,w=map(int,'$WEEK'.split('-W')); d=datetime.date.fromisocalendar(y,w,1)-datetime.timedelta(days=7); i=d.isocalendar(); print(f'{i[0]}-W{i[1]:02d}')")"

card () {  # title skill parent body
  local args=(--board rodado create "$1" --assignee rodado --skill "$2" --workspace "dir:$WS"
              --idempotency-key "rodado-$WEEK-$2" --max-runtime 30m --body "$4" --json)
  [ -n "$3" ] && args+=(--parent "$3")
  hermes kanban "${args[@]}" | "$PY" -c 'import sys,json;print(json.load(sys.stdin)["id"])'
}
t0=$(card "Retro $PREV" rodado-retro "" \
  "Retro of week $PREV. Learn from Pedro's edits in content/calendar/$PREV/ and the metrics; improve skills, templates or voice.md. Write content/calendar/$PREV/retro.md.")
t1=$(card "Ideas $WEEK" rodado-ideation "$t0" \
  "Week $WEEK. Add new ideas to content/ideas/bank.csv and pick the week's 7 (one per slot in strategy.md). Write content/calendar/$WEEK/selection.md.")
t2=$(card "Briefs & copy $WEEK" rodado-copy "$t1" \
  "Week $WEEK. If missing, run content/scripts/new-week.sh $WEEK. Fill the 7 post.md files with the approved selection in content/calendar/$WEEK/selection.md.")
t3=$(card "Audit $WEEK" rodado-audit "$t2" \
  "Week $WEEK. Audit content/calendar/$WEEK/*/post.md against the checklist and write content/calendar/$WEEK/audit.md.")
echo "Chain $WEEK: $t0 → $t1 → $t2 → $t3"
hermes kanban --board rodado list
