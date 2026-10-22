#!/usr/bin/env bash
# Restore Jonathan's Claude Code setup on a machine that isn't his.
# Non-destructive: everything it overwrites is backed up, and uninstall.sh puts it back.
#
#   ./install.sh                 everything (~1s)
#   ./install.sh --no-statusline skip the python status line

set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CDIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$CDIR/.pre-restore-backup-$STAMP"
MANIFEST="$CDIR/.restore-manifest"

STATUSLINE=1
for a in "$@"; do case "$a" in
  --no-statusline) STATUSLINE=0 ;;
  -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
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

# Paths are injected here, not stored in home/settings.json, so they point at
# this machine's config dir.
if [ "$HAVE_PY" = 1 ]; then
  python3 - "$MINE" "$CDIR" "$STATUSLINE" <<'PYX'
import json, sys
p, cdir, statusline = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
d = json.load(open(p))
if statusline:
    d["statusLine"] = {"type": "command", "command": f"python3 {cdir}/statusline.py"}
json.dump(d, open(p, "w"), indent=2)
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
        elif isinstance(v,list) and isinstance(a.get(k),list):
            merged=list(a[k])
            for item in v:
                if item not in merged: merged.append(item)
            a[k]=merged
        else: a[k]=v
    return a
json.dump(merge(old,new),open(sys.argv[1],"w"),indent=2)
PYX
  say "settings.json (merged onto existing)"
else
  cp "$MINE" "$CDIR/settings.json"; say "settings.json"
fi

# ---- status line -----------------------------------------------------------
if [ "$STATUSLINE" = 1 ]; then
  stash "$CDIR/statusline.py"
  cp "$SRC/home/statusline.py" "$CDIR/statusline.py"; chmod +x "$CDIR/statusline.py"
  say "statusline.py"
fi

# ---- skills ----------------------------------------------------------------
for d in "$SRC/home/skills"/*/; do
  n="$(basename "$d")"; stash "$CDIR/skills/$n"; rm -rf "$CDIR/skills/$n"
  cp -R "$d" "$CDIR/skills/$n"; say "skill: $n"
done

rm -f "$BACKUP/.mine.json"; rmdir "$BACKUP" 2>/dev/null || true
cat <<EOF

done. next:
  1. quit and relaunch claude   # the status line loads at startup
  2. /status                    # confirm model=opus, effort=high

undo everything:      $SRC/uninstall.sh
leaving the machine:  $SRC/cleanup.sh
EOF
