#!/usr/bin/env bash
# Install this setup into a self-contained config dir that inherits NOTHING from
# the machine's existing Claude Code — no settings, no CLAUDE.md, no skills, no
# agents, no plugins, no account, no transcripts. `~/.claude` is never touched,
# so there is nothing to back up and nothing to restore.
#
#   ./isolate.sh [workdir]        default: ~/cc-build
#
# Writes <workdir>/.cc (the whole config) and <workdir>/claude-iso (the launcher
# you use instead of `claude`). Tear down with: rm -rf <workdir>
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="${1:-$HOME/cc-build}"
CDIR="$WORK/.cc"

say()  { printf '  %s\n' "$*"; }
warn() { printf '  !! %s\n' "$*" >&2; }

mkdir -p "$WORK"
WORK="$(cd "$WORK" && pwd)"; CDIR="$WORK/.cc"

echo "==> isolating into $CDIR"

# ---- 1. what this machine would have leaked in --------------------------------
# Env vars beat settings files, so an ANTHROPIC_BASE_URL or CLAUDE_CODE_USE_BEDROCK
# left in someone's .zshrc silently repoints the whole session. The launcher below
# strips them; report them here so the choice is visible rather than magic.
LEAKED="$(env | grep -E '^(ANTHROPIC_|CLAUDE_)[A-Z0-9_]*=' | cut -d= -f1 \
          | grep -v '^CLAUDE_CONFIG_DIR$' | sort || true)"
if [ -n "$LEAKED" ]; then
  warn "env vars found and stripped by the launcher:"
  printf '     %s\n' $LEAKED
fi

[ -e "$HOME/.claude" ] && say "existing ~/.claude present — untouched" || say "no existing ~/.claude"

# CLAUDE.md and CLAUDE.local.md load from every ancestor directory. That walk is
# not scoped by CLAUDE_CONFIG_DIR and cannot be turned off, so the only fix is to
# build somewhere with no ancestor memory files.
d="$WORK"
while [ "$d" != "/" ]; do
  for f in "$d/CLAUDE.md" "$d/CLAUDE.local.md"; do
    [ "$d" = "$WORK" ] && continue
    [ -e "$f" ] && warn "ancestor memory file WILL load: $f"
  done
  d="$(dirname "$d")"
done

# Managed settings outrank everything, including this. Nothing can escape them.
for M in "/Library/Application Support/ClaudeCode/managed-settings.json" \
         "/etc/claude-code/managed-settings.json"; do
  [ -f "$M" ] && warn "managed policy PRESENT: $M — outranks this setup; run 'claude doctor'"
done

# ---- 2. install into the isolated dir ----------------------------------------
CLAUDE_CONFIG_DIR="$CDIR" "$SRC/install.sh" "${@:2}" | sed -n '/^==>/,/^done\./p' \
  | grep -v '^done\.' | sed 's/^/  /'

# ---- 3. the launcher ---------------------------------------------------------
# A subshell is the wrong tool here: an interactive shell re-sources the machine
# owner's rc files and re-exports whatever we just unset. A launcher scrubs on
# every invocation instead, so isolation cannot decay.
cat > "$WORK/claude-iso" <<LAUNCHER
#!/usr/bin/env bash
# Launch Claude Code with this machine's Claude config and env fully out of scope.
for v in \$(env | grep -E '^(ANTHROPIC_|CLAUDE_)[A-Z0-9_]*=' | cut -d= -f1); do
  unset "\$v"
done
export CLAUDE_CONFIG_DIR="$CDIR"
exec claude "\$@"
LAUNCHER
chmod +x "$WORK/claude-iso"
say "launcher: $WORK/claude-iso"

# ---- 4. teardown -------------------------------------------------------------
# `rm -rf` handles the config, transcripts and account id, all of which live in
# the dir. The OAuth credential does not: on macOS it lands in the login keychain,
# which no directory scoping reaches. So log out first, through the launcher, so
# the logout runs against this config and not the machine owner's.
cat > "$WORK/teardown.sh" <<TEARDOWN
#!/usr/bin/env bash
# Run before handing the laptop back.
# The brace group matters: this script deletes the directory it lives in, and
# bash reads scripts incrementally. Grouping forces the whole body to be parsed
# before the first command runs, so the rm can't pull the file out from under it.
set -euo pipefail
{
  "$WORK/claude-iso" auth logout || echo "!! logout failed — sign out manually before leaving"
  cd /
  rm -rf "$WORK"
  echo "gone. this machine's own Claude Code config was never modified."
}
TEARDOWN
chmod +x "$WORK/teardown.sh"
say "teardown: $WORK/teardown.sh"

cat <<EOF

done. everything lives in $WORK — nothing else on this machine was modified.

  cd $WORK
  ./claude-iso            # instead of \`claude\`; /login is scoped to this dir
                          # CC_CHECKPOINT_PUSH=1 ./claude-iso  if someone pairing
                          # has their own clone and needs your commits pushed
  /status                 # confirm model=opus, effort=high, no managed policy
  /kickoff <what you're building>

before you hand the laptop back:
  $WORK/teardown.sh       # scoped logout, then deletes everything above
EOF
