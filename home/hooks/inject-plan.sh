#!/usr/bin/env bash
# SessionStart hook. Re-injects the live plan state into a fresh or compacted context.
#
# Fires on startup, resume, and — the one that matters — `compact`. After an
# auto-compact the conversation is a summary, but this runs again and puts the
# current Status block back in front of the model. State lives on disk, so a
# compaction stops being a memory loss event.
#
# Silent no-op when there is no PLAN.md. Never fails the session.

set -u
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
PLAN="$DIR/PLAN.md"
DECISIONS="$DIR/DECISIONS.md"

[ -r "$PLAN" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

python3 - "$PLAN" "$DECISIONS" "$DIR" <<'PY' 2>/dev/null || exit 0
import json, os, subprocess, sys

plan_path, dec_path, dir_ = sys.argv[1], sys.argv[2], sys.argv[3]

def section(text, name):
    """Return the body of '## <name>' up to the next '## ' heading."""
    out, grab = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if grab:
                break
            grab = line[3:].strip().lower().startswith(name)
            continue
        if grab:
            out.append(line)
    return "\n".join(out).strip()

try:
    plan = open(plan_path, encoding="utf-8", errors="replace").read()
except OSError:
    sys.exit(0)

parts = [f"# Live plan state (re-injected from {os.path.basename(plan_path)})"]

status = section(plan, "status")
parts.append("## Status\n" + status if status else
             "PLAN.md has no ## Status block yet. Run /handoff to write one.")

contracts = section(plan, "contracts")
if contracts:
    head = contracts.splitlines()[:25]
    parts.append("## Contracts (frozen — do not change without saying so)\n" + "\n".join(head))

if os.path.exists(dec_path):
    try:
        n = sum(1 for l in open(dec_path, encoding="utf-8", errors="replace")
                if l.startswith("## D"))
        parts.append(f"{n} decision(s) logged in DECISIONS.md. "
                     "Log new ones with /decide as they are made.")
    except OSError:
        pass

try:
    branch = subprocess.run(["git", "-C", dir_, "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True, timeout=5)
    if branch.returncode == 0 and branch.stdout.strip():
        parts.append(f"Branch: {branch.stdout.strip()}")
except Exception:
    pass

parts.append("PLAN.md is authoritative. Where it and the conversation disagree, "
             "re-read PLAN.md and fix it rather than trusting recall.")

print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "\n\n".join(parts),
}}))
PY
