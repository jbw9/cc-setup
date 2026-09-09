#!/usr/bin/env python3
"""Claude Code status line.

  <dir>   |   <model>   |   context <n>% used

Three things, because a status line you have to read is not a status line. Each
segment is guarded on its own: a failure in one never blanks the whole line.
"""
import sys, os, json

# ---- ANSI -----------------------------------------------------------------
def c(code, s):
    return f"\033[{code}m{s}\033[0m"

BOLD, CYAN, GREEN, GREY, RED = "1", "36", "32", "90", "31"
ORANGE = "38;5;208"
SEP = c(GREY, "   |   ")

def meter_color(pct, warn=70, bad=90):
    return GREEN if pct < warn else (ORANGE if pct < bad else RED)

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
    d = os.path.basename(cwd.rstrip("/")) or cwd
    segments.append(c(BOLD, d))
except Exception:
    pass

# ---- model ----------------------------------------------------------------
if model_name:
    segments.append(c(CYAN, model_name))

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

sys.stdout.write(SEP.join(segments))
