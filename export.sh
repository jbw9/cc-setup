#!/usr/bin/env bash
# Re-export the live config on MY machine back into this repo. Then commit.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CDIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS="graphify apple-design visual-plan eli5 recap"

cp "$CDIR/statusline.py" "$SRC/home/statusline.py"
for s in $SKILLS; do
  [ -d "$CDIR/skills/$s" ] || continue
  rm -rf "$SRC/home/skills/$s"; cp -RL "$CDIR/skills/$s" "$SRC/home/skills/$s"
done
[ -d "$HOME/.agents/skills" ] && { rm -rf "$SRC/optional/agents-skills"; cp -RL "$HOME/.agents/skills" "$SRC/optional/agents-skills"; }
find "$SRC" -name .DS_Store -delete
echo "exported. NOTE: home/CLAUDE.md and home/settings.json are hand-maintained"
echo "portable versions — diff them against $CDIR yourself:"
echo "  diff $SRC/home/CLAUDE.md $CDIR/CLAUDE.md"
