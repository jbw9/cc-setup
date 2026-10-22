#!/usr/bin/env bash
# Re-export the live config on MY machine back into this repo. Then commit.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CDIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

cp "$CDIR/statusline.py" "$SRC/home/statusline.py"
for n in $(ls "$SRC/home/skills"); do
  [ -d "$CDIR/skills/$n" ] && { rm -rf "$SRC/home/skills/$n"; cp -RL "$CDIR/skills/$n" "$SRC/home/skills/$n"; }
done
find "$SRC" -name .DS_Store -delete
echo "exported. NOTE: home/CLAUDE.md and home/settings.json are hand-maintained"
echo "portable versions — diff them against $CDIR yourself:"
echo "  diff $SRC/home/CLAUDE.md $CDIR/CLAUDE.md"
echo "  diff $SRC/home/settings.json $CDIR/settings.json"
