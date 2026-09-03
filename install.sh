#!/usr/bin/env bash
# Restore Jonathan's Claude Code setup on a machine that isn't his.
# Non-destructive: everything it overwrites is backed up, and uninstall.sh puts it back.
#
#   ./install.sh                 core setup (~2s)
#   ./install.sh --with-stitch   + the Stitch/shadcn/Remotion design skills
#   ./install.sh --with-gstack   + gstack (clones ~1GB, needs bun, takes minutes)
#   ./install.sh --no-statusline skip the python status line

set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CDIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$CDIR/.pre-restore-backup-$STAMP"
MANIFEST="$CDIR/.restore-manifest"

WITH_STITCH=0; WITH_GSTACK=0; STATUSLINE=1
for a in "$@"; do case "$a" in
  --with-stitch) WITH_STITCH=1 ;;
  --with-gstack) WITH_GSTACK=1 ;;
  --no-statusline) STATUSLINE=0 ;;
  -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
  *) echo "unknown flag: $a" >&2; exit 1 ;;
esac; done

say() { printf '  %s\n' "$*"; }
mkdir -p "$CDIR/skills" "$BACKUP"
: > "$MANIFEST"

# back up a path before we touch it, and remember what we did
stash() {  # stash <path>
  [ -e "$1" ] || { echo "ADDED $1" >> "$MANIFEST"; return; }
  mkdir -p "$BACKUP/$(dirname "${1#$CDIR/}")"
  cp -R "$1" "$BACKUP/${1#$CDIR/}"
  echo "REPLACED $1" >> "$MANIFEST"
}

echo "==> restoring into $CDIR"

# ---- CLAUDE.md -------------------------------------------------------------
stash "$CDIR/CLAUDE.md"
cp "$SRC/home/CLAUDE.md" "$CDIR/CLAUDE.md"
say "CLAUDE.md"

# ---- settings.json (merged onto whatever is already there) -----------------
stash "$CDIR/settings.json"
MINE="$BACKUP/.mine.json"
cp "$SRC/home/settings.json" "$MINE"

HAVE_PY=0; command -v python3 >/dev/null 2>&1 && HAVE_PY=1
[ "$HAVE_PY" = 1 ] || STATUSLINE=0

if [ "$STATUSLINE" = 1 ]; then
  python3 - "$MINE" "$CDIR" <<'PYX'
import json,sys
p=sys.argv[1]; d=json.load(open(p))
d["statusLine"]={"type":"command","command":f"python3 {sys.argv[2]}/statusline.py"}
json.dump(d,open(p,"w"),indent=2)
PYX
fi

if [ "$HAVE_PY" = 1 ] && [ -s "$CDIR/settings.json" ]; then
  python3 - "$CDIR/settings.json" "$MINE" <<'PYX'
import json,sys
try: old=json.load(open(sys.argv[1]))
except Exception: old={}
new=json.load(open(sys.argv[2]))
def merge(a,b):
    for k,v in b.items():
        if isinstance(v,dict) and isinstance(a.get(k),dict): merge(a[k],v)
        elif isinstance(v,list) and isinstance(a.get(k),list): a[k]=list(dict.fromkeys(a[k]+v))
        else: a[k]=v
    return a
json.dump(merge(old,new),open(sys.argv[1],"w"),indent=2)
PYX
  say "settings.json (merged onto existing)"
else
  cp "$MINE" "$CDIR/settings.json"; say "settings.json"
fi

# ---- status line -----------------------------------------------------------
if [ "$STATUSLINE" = 1 ] && command -v python3 >/dev/null 2>&1; then
  stash "$CDIR/statusline.py"
  cp "$SRC/home/statusline.py" "$CDIR/statusline.py"; chmod +x "$CDIR/statusline.py"
  say "statusline.py"
fi

# ---- skills ----------------------------------------------------------------
for d in "$SRC/home/skills"/*/; do
  n="$(basename "$d")"; stash "$CDIR/skills/$n"; rm -rf "$CDIR/skills/$n"
  cp -R "$d" "$CDIR/skills/$n"; say "skill: $n"
done

if [ "$WITH_STITCH" = 1 ]; then
  for d in "$SRC/optional/agents-skills"/*/; do
    n="$(basename "$d")"; stash "$CDIR/skills/$n"; rm -rf "$CDIR/skills/$n"
    cp -R "$d" "$CDIR/skills/$n"; say "skill: $n"
  done
fi

# ---- plugins ---------------------------------------------------------------
if command -v claude >/dev/null 2>&1; then
  claude plugin marketplace add anthropics/claude-plugins-official >/dev/null 2>&1 || true
  claude plugin install frontend-design@claude-plugins-official >/dev/null 2>&1 || true
  say "plugin: frontend-design (best effort)"
fi

# ---- gstack (big; opt in) --------------------------------------------------
if [ "$WITH_GSTACK" = 1 ]; then
  echo "==> gstack (this takes a few minutes)"
  if [ -d "$CDIR/skills/gstack/.git" ]; then
    git -C "$CDIR/skills/gstack" pull --ff-only || true
  else
    echo "ADDED $CDIR/skills/gstack" >> "$MANIFEST"
    git clone --depth 1 https://github.com/garrytan/gstack.git "$CDIR/skills/gstack"
  fi
  if command -v bun >/dev/null 2>&1; then (cd "$CDIR/skills/gstack" && bun install)
  else say "bun not installed — skipping gstack deps (skills that shell out will fail)"; fi
fi

rm -f "$BACKUP/.mine.json"; rmdir "$BACKUP" 2>/dev/null || true
cat <<EOF

done. next:
  1. claude            # then /login if not signed in
  2. /status           # confirm model=opus, skills loaded
  3. edit $CDIR/CLAUDE.md — fill in the FILL IN sections
  4. cp $SRC/templates/PROJECT_CLAUDE.md <project>/CLAUDE.md

undo everything:  $SRC/uninstall.sh
leaving the machine:  $SRC/cleanup.sh
EOF
