#!/usr/bin/env bash
# Run this BEFORE you hand the laptop back.
# Signs out, undoes the install, and removes the session transcripts/history
# this account left on a machine that isn't yours.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CDIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

read -r -p "Sign out of Claude and wipe local session data in $CDIR? [y/N] " a
[ "$a" = y ] || [ "$a" = Y ] || { echo "aborted"; exit 0; }

command -v claude >/dev/null 2>&1 && claude logout 2>/dev/null || true
bash "$SRC/uninstall.sh" || true

rm -rf "$CDIR"/projects "$CDIR"/sessions "$CDIR"/history.jsonl \
       "$CDIR"/file-history "$CDIR"/shell-snapshots "$CDIR"/paste-cache \
       "$CDIR"/plans "$CDIR"/todos "$CDIR"/.pre-restore-backup-* 2>/dev/null || true

echo "signed out; transcripts, history and the restored config are gone."
echo "note: ~/.claude.json still holds an account id — delete it if this laptop"
echo "      had no Claude Code install before you arrived:  rm ~/.claude.json"
