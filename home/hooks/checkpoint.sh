#!/usr/bin/env bash
# Stop hook. Commits the working tree on a clock, so nobody pulling from this
# repo is ever more than one interval behind what you have actually built.
#
# This exists for the pairing session. A teammate who cloned or pulled forty
# minutes ago is editing files that have moved under them, and neither of you
# finds out until the merge. Committing on a cadence makes "git pull" a true
# statement about the build instead of a guess.
#
# It runs on `Stop` — when the main thread finishes a turn, so never mid-edit.
# `SubagentStop` is deliberately NOT wired: during a fan-out round three
# builders are writing at once and the tree is not coherent until fan-in.
#
# Two kinds of commit live in this workflow and they are not the same thing:
#   /fanout  commits a GREEN tree at fan-in    -> the rollback points
#   this     commits `wip:` on a clock         -> so your teammate isn't stale
# List the rollback points with:  git log --grep='^wip:' --invert-grep
#
# Only runs where PLAN.md is, which is the same gate inject-plan.sh uses. That
# keeps it to repos where a build is actually underway: opening Claude Code in
# someone's work repo should not start committing to it.
#
#   CC_CHECKPOINT=0         off
#   CC_CHECKPOINT_MINS=10   minutes between checkpoints (default 10)
#   CC_CHECKPOINT_PUSH=1    also push to the branch's upstream (default: no)
#   CC_CHECKPOINT_ANY=1     checkpoint any git repo, PLAN.md or not
#
# Never fails the session: every path exits 0.
set -u

emit() {  # emit <message>  — one line to the user, then stop
  m=$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')
  printf '{"systemMessage":"%s"}\n' "$m"
  exit 0
}

INPUT="$(cat 2>/dev/null || true)"
case "$INPUT" in *'"stop_hook_active":true'*) exit 0 ;; esac

[ "${CC_CHECKPOINT:-1}" = "0" ] && exit 0
MINS="${CC_CHECKPOINT_MINS:-10}"
case "$MINS" in ''|*[!0-9]*) MINS=10 ;; esac
[ "$MINS" -eq 0 ] && exit 0

cd "${CLAUDE_PROJECT_DIR:-$PWD}" 2>/dev/null || exit 0
[ "${CC_CHECKPOINT_ANY:-0}" = "1" ] || [ -r PLAN.md ] || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
G="$(git rev-parse --git-dir 2>/dev/null)" || exit 0

# Mid-merge, mid-rebase or detached: the tree is someone else's business.
for f in MERGE_HEAD REBASE_HEAD CHERRY_PICK_HEAD REVERT_HEAD BISECT_LOG; do
  [ -e "$G/$f" ] && exit 0
done
{ [ -d "$G/rebase-merge" ] || [ -d "$G/rebase-apply" ]; } && exit 0
BRANCH="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
[ -n "$BRANCH" ] || exit 0

# Due yet? An empty repo has no last commit and is always due.
LAST="$(git log -1 --format=%ct 2>/dev/null || true)"
if [ -n "$LAST" ]; then
  [ $(( ( $(date +%s) - LAST ) / 60 )) -lt "$MINS" ] && exit 0
fi

STATUS="$(git status --porcelain 2>/dev/null || true)"
[ -n "$STATUS" ] || exit 0

# A tree this dirty means no .gitignore, not an hour of work. Committing it
# would push a few hundred megabytes of vendor directory at your teammate.
N=$(printf '%s\n' "$STATUS" | wc -l | tr -d ' ')
[ "$N" -gt 200 ] && emit "checkpoint skipped: $N changed paths, which usually means a missing .gitignore. Sort that out and the hook resumes on its own."

# git commit with no identity fails every time, silently, forever. Say so once.
[ -n "$(git config user.email 2>/dev/null || true)" ] && [ -n "$(git config user.name 2>/dev/null || true)" ] \
  || emit "checkpoint skipped: this machine has no git identity. Set one in the repo: git config user.name NAME && git config user.email EMAIL"

# Only untracked paths get filtered. Something already tracked was a deliberate
# choice; a stray .env or an unignored node_modules/ can only arrive here.
EXCL=(); SKIPPED=""
while IFS= read -r line; do
  case "$line" in '??'*) ;; *) continue ;; esac
  p="${line#\?\? }"; p="${p%\"}"; p="${p#\"}"
  case "$p" in
    .env|.env.*|*/.env|*/.env.*|*.pem|*.p12|*.pfx|*.keystore|id_rsa*|*/id_rsa*|\
    .npmrc|*/.npmrc|credentials.json|*/credentials.json|*secrets*|*.tfvars)
      EXCL+=(":(exclude)$p"); SKIPPED="$SKIPPED $p" ;;
    node_modules/|*/node_modules/|.venv/|*/.venv/|venv/|*/venv/|\
    __pycache__/|*/__pycache__/|target/|.next/|*/.next/)
      EXCL+=(":(exclude)$p"); SKIPPED="$SKIPPED $p" ;;
  esac
done <<EOF
$STATUS
EOF

git add -A -- . ${EXCL[@]+"${EXCL[@]}"} >/dev/null 2>&1 || exit 0
git diff --cached --quiet 2>/dev/null && exit 0   # everything was filtered out

FILES="$(git diff --cached --name-only 2>/dev/null || true)"
NF=$(printf '%s\n' "$FILES" | wc -l | tr -d ' ')

# --no-verify on purpose: a checkpoint that a repo's lint hook can veto is not a
# checkpoint. /fanout still runs the real checks before its green commit.
if ! git commit --quiet --no-verify \
     -m "wip: $NF file(s) in progress" -m "$FILES" >/dev/null 2>&1; then
  git reset --quiet >/dev/null 2>&1
  exit 0
fi

NOTE=""
if [ "${CC_CHECKPOINT_PUSH:-0}" = "1" ]; then
  if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    git push --quiet >/dev/null 2>&1 && NOTE=" and pushed" || NOTE=" - PUSH FAILED, your teammate is still stale"
  else
    NOTE=" - no upstream set, not pushed"
  fi
fi
[ -n "$SKIPPED" ] && NOTE="$NOTE (left out:$SKIPPED)"

emit "checkpoint: $NF file(s) committed on $BRANCH$NOTE"
