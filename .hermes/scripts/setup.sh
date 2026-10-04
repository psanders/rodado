#!/usr/bin/env bash
# Configures Hermes for this repo. Safe to re-run after editing profiles/, skills/ or themes/.
#   docker compose exec hermes bash /workspace/rodado/.hermes/scripts/setup.sh
set -euo pipefail
WS="${RODADO_WS:-/workspace/rodado}"
H="$WS/.hermes"
MODEL="${RODADO_MODEL:-claude-sonnet-5}"
PY="$(head -1 "$(command -v hermes)" | sed 's/^#!//')"; [ -x "$PY" ] || PY=python3

set_cfg () {  # config.yaml: Anthropic provider + model, skills from .hermes/skills, start in the repo
  "$PY" - "$1" "$MODEL" "$H/skills" "$WS" <<'PYEOF'
import sys, yaml, pathlib
p = pathlib.Path(sys.argv[1]); c = (yaml.safe_load(p.read_text()) if p.exists() else {}) or {}
m = c.get("model") if isinstance(c.get("model"), dict) else {}
m.update({"provider": "anthropic", "default": sys.argv[2]}); c["model"] = m
c.setdefault("skills", {})["external_dirs"] = [sys.argv[3]]
c.setdefault("terminal", {})["cwd"] = sys.argv[4]   # sessions start in the repo, so AGENTS.md loads
p.write_text(yaml.safe_dump(c, sort_keys=False, allow_unicode=True))
PYEOF
}

hermes config set kanban.auto_decompose false >/dev/null
hermes config set dashboard.theme rodado >/dev/null
HOME_DIR="$(dirname "$(hermes config path)")"
set_cfg "$HOME_DIR/config.yaml"

SHARED="$(sed "s#{{WS}}#$WS#g" "$H/profiles/_shared.md")"
for dir in "$H"/profiles/*/; do
  name="$(basename "$dir")"
  desc="$(cat "$dir/description.txt" 2>/dev/null || echo "$name")"
  if [ ! -d "$HOME_DIR/profiles/$name" ]; then
    hermes profile create "$name" --clone --description "$desc" >/dev/null && echo "profile created: $name"
  fi
  cfg="$(hermes -p "$name" config path)"
  set_cfg "$cfg"
  printf '%s\n\n%s\n' "$SHARED" "$(cat "$dir/SOUL.md")" > "$(dirname "$cfg")/SOUL.md"
done

# The default profile (what the dashboard chat uses unless you switch) gets the same instructions as rodado
printf '%s\n\n%s\n' "$SHARED" "$(cat "$H/profiles/rodado/SOUL.md")" > "$HOME_DIR/SOUL.md"

# Let agents read git history (the retro compares drafts with Pedro's edits)
command -v git >/dev/null && git config --global --add safe.directory "$WS" 2>/dev/null || true

hermes kanban init >/dev/null 2>&1 || true
[ -d "$HOME_DIR/kanban/boards/rodado" ] || \
  hermes kanban boards create rodado --name "Rodado" --description "Rodado Creativo content" >/dev/null
hermes kanban boards switch rodado >/dev/null
PROFILES="$(for d in "$H"/profiles/*/; do printf "%s " "$(basename "$d")"; done)"
echo "Done: profiles [ $PROFILES], model $MODEL (Anthropic), theme rodado, board rodado."
