#!/usr/bin/env bash
# Five-second recon of a machine you're about to build on.
#
# Answers one question: which stacks are WARM here? A toolchain that's installed
# with a populated package cache costs you a minute to start. One that needs a
# runtime install over guest wifi can cost you thirty — and on a timed build
# that decision is made before the clock starts, not at minute five.
#
#   ./preflight.sh

set -u
say() { printf '%s\n' "$*"; }
row() { printf '  %-12s %s\n' "$1" "$2"; }
have() { command -v "$1" >/dev/null 2>&1; }
ver()  { have "$1" && "$1" ${2:---version} 2>&1 | head -1 | cut -c1-40 || echo "—"; }
dirsize() { [ -d "$1" ] && du -sh "$1" 2>/dev/null | cut -f1 || echo ""; }

say "==> machine"
row "os" "$(uname -srm)"
row "disk free" "$(df -h "$HOME" 2>/dev/null | awk 'NR==2{print $4}')"
row "cores" "$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo '?')"

say ""
say "==> toolchains"
row "node"    "$(ver node)"
row "npm"     "$(ver npm)"
row "pnpm"    "$(ver pnpm)"
row "yarn"    "$(ver yarn)"
row "bun"     "$(ver bun)"
row "python3" "$(ver python3)"
row "uv"      "$(ver uv)"
row "go"      "$(ver go version)"
row "cargo"   "$(ver cargo)"
row "git"     "$(ver git)"
row "docker"  "$(ver docker)"

say ""
say "==> package caches (populated = fast install)"
for c in "$HOME/.npm:npm" "$HOME/Library/pnpm/store:pnpm" \
         "$HOME/.local/share/pnpm/store:pnpm" "$HOME/.bun/install/cache:bun" \
         "$HOME/.cache/yarn:yarn" "$HOME/.cache/uv:uv" "$HOME/.cache/pip:pip" \
         "$HOME/Library/Caches/pip:pip" "$HOME/go/pkg/mod:go" \
         "$HOME/.cargo/registry:cargo"; do
  p="${c%:*}"; n="${c##*:}"; s="$(dirsize "$p")"
  [ -n "$s" ] && row "$n" "$s  ($p)"
done

say ""
say "==> network"
if have curl; then
  t0=$(date +%s)
  if curl -fsS --max-time 8 -o /dev/null https://registry.npmjs.org/ 2>/dev/null; then
    row "npm registry" "reachable (~$(( $(date +%s) - t0 ))s)"
  else
    row "npm registry" "UNREACHABLE — proxy or blocked. Ask before you pick a stack."
  fi
else
  row "curl" "missing"
fi

say ""
say "==> claude code"
row "claude" "$(ver claude)"
MANAGED=""
for M in "/Library/Application Support/ClaudeCode/managed-settings.json" \
         "/etc/claude-code/managed-settings.json"; do
  [ -f "$M" ] && MANAGED="$M"
done
[ -n "$MANAGED" ] && row "managed" "PRESENT ($MANAGED) — a policy outranks your settings. Run 'claude doctor'." \
                  || row "managed" "none"
[ -e "$HOME/.claude/settings.json" ] && row "existing" "$HOME/.claude/settings.json — install.sh will merge + back up" \
                                    || row "existing" "clean"

say ""
say "==> read this as"
say "  A toolchain present AND its cache populated = warm. Prefer it."
say "  Everything else costs setup minutes you do not get back."
