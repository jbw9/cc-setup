#!/usr/bin/env bash
# Undo install.sh: remove what it added, restore what it replaced.
set -euo pipefail
CDIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MANIFEST="$CDIR/.restore-manifest"
[ -f "$MANIFEST" ] || { echo "no manifest at $MANIFEST — nothing to undo"; exit 0; }
BACKUP="$(ls -d "$CDIR"/.pre-restore-backup-* 2>/dev/null | tail -1 || true)"

while read -r action path; do
  [ -n "${path:-}" ] || continue
  case "$action" in
    ADDED)    rm -rf "$path"; echo "  removed $path" ;;
    REPLACED) rel="${path#$CDIR/}"
              if [ -n "$BACKUP" ] && [ -e "$BACKUP/$rel" ]; then
                rm -rf "$path"; cp -R "$BACKUP/$rel" "$path"; echo "  restored $path"
              else echo "  !! no backup for $path — left as is"; fi ;;
  esac
done < "$MANIFEST"
rm -f "$MANIFEST"
echo "done. backup kept at: ${BACKUP:-none}"
