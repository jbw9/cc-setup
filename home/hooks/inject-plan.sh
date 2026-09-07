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
import datetime, json, os, re, subprocess, sys

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

# Clock. `## Time` carries `Started: HH:MM · Deadline: HH:MM · Freeze: HH:MM`.
# On a timed build this is the first thing that should re-enter a fresh context:
# a plan with no sense of how much clock is left will happily start work that
# cannot land.
time_block = section(plan, "time")
if time_block:
    def at(label):
        m = re.search(rf"{label}:\s*(\d{{1,2}}):(\d{{2}})", time_block)
        if not m:
            return None
        now = datetime.datetime.now()
        try:
            return now.replace(hour=int(m.group(1)), minute=int(m.group(2)),
                               second=0, microsecond=0)
        except ValueError:
            return None

    now = datetime.datetime.now()
    clock = [f"Now: {now:%H:%M}"]
    started, deadline, freeze = at("Started"), at("Deadline"), at("Freeze")
    if started and now >= started:
        el = int((now - started).total_seconds() // 60)
        clock.append(f"Elapsed: {el // 60}h{el % 60:02d}m")
    for label, when in (("Freeze", freeze), ("Deadline", deadline)):
        if when:
            left = int((when - now).total_seconds() // 60)
            clock.append(f"{label} {when:%H:%M} "
                         + (f"(in {left // 60}h{left % 60:02d}m)" if left > 0
                            else "(PASSED)"))
    parts.append("## Clock\n" + " · ".join(clock) + "\n" + time_block)
    if freeze and now >= freeze:
        parts.append("Past the freeze time: no new workstreams. Integration, "
                     "demo rehearsal, and unlogged decisions only. Anything "
                     "unfinished is a CUT — say so rather than gambling the demo.")

status = section(plan, "status")
parts.append("## Status\n" + status if status else
             "PLAN.md has no ## Status block yet. Run /handoff to write one.")

# The demo path is the one thing whose breakage is invisible to typecheck and
# fatal at the deadline.
demo = section(plan, "demo path")
if demo:
    parts.append("## Demo path (must stay green — run ./demo.sh)\n" + demo)
elif os.path.exists(os.path.join(dir_, "demo.sh")):
    parts.append("demo.sh exists but PLAN.md has no ## Demo path section.")

contracts = section(plan, "contracts")
if contracts:
    head = contracts.splitlines()[:25]
    parts.append("## Contracts (frozen — do not change without saying so)\n" + "\n".join(head))

if os.path.exists(dec_path):
    try:
        text = open(dec_path, encoding="utf-8", errors="replace").read()
        n = sum(1 for l in text.splitlines() if l.startswith("## D"))
        missing = n - len(re.findall(r"^At scale:", text, re.M))
        note = (f"{n} decision(s) logged in DECISIONS.md. "
                "Log new ones with /decide as they are made.")
        if missing > 0:
            note += (f" {missing} lack{'s' if missing == 1 else ''} an "
                     "`At scale:` line — backfill before /scale, while the "
                     "reasoning is still recoverable.")
        parts.append(note)
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
