#!/usr/bin/env bash
# Re-export the live config on MY machine back into this repo. Then commit.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CDIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS="graphify apple-design visual-plan eli5 recap"
MINE="kickoff fanout handoff brief decide defend karpathy-guidelines"

cp "$CDIR/statusline.py" "$SRC/home/statusline.py"
for f in "$CDIR"/agents/*.md;  do [ -e "$f" ] && cp "$f" "$SRC/home/agents/";  done
for f in "$CDIR"/hooks/*.sh;   do [ -e "$f" ] && cp "$f" "$SRC/home/hooks/";   done
for s in $SKILLS $MINE; do
  [ -d "$CDIR/skills/$s" ] || continue
  rm -rf "$SRC/home/skills/$s"; cp -RL "$CDIR/skills/$s" "$SRC/home/skills/$s"
done
[ -d "$HOME/.agents/skills" ] && { rm -rf "$SRC/optional/agents-skills"; cp -RL "$HOME/.agents/skills" "$SRC/optional/agents-skills"; }
find "$SRC" -name .DS_Store -delete
echo "exported. NOTE: home/CLAUDE.md and home/settings.json are hand-maintained"
echo "portable versions — diff them against $CDIR yourself:"
echo "  diff $SRC/home/CLAUDE.md $CDIR/CLAUDE.md"
echo "  diff $SRC/home/settings.json $CDIR/settings.json"
