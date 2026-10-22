#!/usr/bin/env python3
"""Claude Code status line.

  <dir> | <branch> | +<added> -<removed> | <model> | <effort> | context <n>% used | $<cost>

Each segment is guarded on its own: a failure in one never blanks the whole line.
"""
import sys, os, json, subprocess

# ---- ANSI -----------------------------------------------------------------
def c(code, s):
    return f"\033[{code}m{s}\033[0m"

BOLD, CYAN, GREEN, GREY, RED = "1", "36", "32", "90", "31"
ORANGE = "38;5;208"
BLUE, MAGENTA, YELLOW, PINK = "38;5;75", "38;5;177", "38;5;221", "38;5;205"
EFFORT_COLOR = {"low": "38;5;117", "medium": YELLOW, "high": ORANGE,
                "xhigh": "38;5;203", "max": PINK}
SEP = c(GREY, "   |   ")

# 256-colour ramp, bright green -> yellow -> red.
RAMP = [46, 82, 118, 154, 190, 226, 220, 214, 208, 202, 196]

def meter_color(pct, red_at=40):
    i = min(len(RAMP) - 1, pct * (len(RAMP) - 1) // red_at)
    return f"38;5;{RAMP[i]}"

# ---- input ----------------------------------------------------------------
try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

cwd        = data.get("workspace", {}).get("current_dir") or data.get("cwd") or os.getcwd()
transcript = data.get("transcript_path", "")
model_name = data.get("model", {}).get("display_name", "")

segments = []

# ---- dir ------------------------------------------------------------------
try:
    segments.append(c(f"{BOLD};{BLUE}", os.path.basename(cwd.rstrip("/")) or cwd))
except Exception:
    pass

# ---- git: branch, uncommitted +/- -----------------------------------------
def git(*a):
    return subprocess.run(["git", "-C", cwd, *a], capture_output=True,
                          text=True, timeout=1).stdout.strip()

try:
    # --show-current is empty on a detached HEAD; fall back to the short sha.
    branch = git("branch", "--show-current") or git("rev-parse", "--short", "HEAD")
    if branch:
        segments.append(c(MAGENTA, branch))
        # Tracked changes vs HEAD, staged or not; untracked files don't count.
        added = removed = 0
        for line in git("diff", "HEAD", "--numstat").splitlines():
            a, r, _ = line.split("\t", 2)
            if a != "-":  # binary files report "-"
                added, removed = added + int(a), removed + int(r)
        segments.append(c(GREEN, f"+{added}") + " " + c(RED, f"-{removed}"))
except Exception:
    pass

# ---- model ----------------------------------------------------------------
if model_name:
    # Absent on models without effort support; CLAUDE_EFFORT is the same value.
    effort = (data.get("effort") or {}).get("level") or os.environ.get("CLAUDE_EFFORT", "")
    segments.append(c(CYAN, model_name))
    if effort:
        segments.append(c(EFFORT_COLOR.get(effort, GREY), effort))

# ---- context used ---------------------------------------------------------
# The last assistant turn's usage is the whole context: input + both cache
# counters. Sidechains are subagents and don't sit in this window.
def context_pct_used():
    if not transcript or not os.path.exists(transcript):
        return None
    try:
        size = os.path.getsize(transcript)
        with open(transcript, "rb") as f:
            if size > 600_000:
                f.seek(-600_000, os.SEEK_END)
                f.readline()
            tail = f.read().decode("utf-8", "replace").splitlines()
    except Exception:
        return None
    for line in reversed(tail):
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get("type") != "assistant" or o.get("isSidechain"):
            continue
        u = o.get("message", {}).get("usage")
        if not u:
            continue
        used = (u.get("input_tokens", 0)
                + u.get("cache_creation_input_tokens", 0)
                + u.get("cache_read_input_tokens", 0))
        # Override with CC_CONTEXT_LIMIT if a project runs the 200k window.
        limit = int(os.environ.get("CC_CONTEXT_LIMIT", "1000000"))
        return min(100, round(used * 100 / limit))
    return None

try:
    ctx = context_pct_used()
    if ctx is not None:
        segments.append(c(meter_color(ctx), f"context {ctx}% used"))
except Exception:
    pass

# ---- session cost ---------------------------------------------------------
try:
    cost = (data.get("cost") or {}).get("total_cost_usd")
    if cost is not None:
        segments.append(c("38;5;180", f"${cost:.2f}"))
except Exception:
    pass

sys.stdout.write(SEP.join(segments))
