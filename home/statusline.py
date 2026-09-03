#!/usr/bin/env python3
"""Claude Code status line (single line, branch right-aligned).

  <dir>  ·  <model>  ·  context <n>% used  ·  5h <n>%  ·  $<cost>  ·  +add -del ......... ⎇ <branch>*

Segments are individually guarded — a failure in one never blanks the line.
The 5-hour usage % divides your rolling token total by CC_5H_TOKEN_BUDGET
(env override; default 200M) since Anthropic doesn't expose the plan limit.
"""
import sys, os, json, glob, subprocess, time, shutil
from datetime import datetime

# ---- config ---------------------------------------------------------------
# 5h usage budget in *cost-weighted* units (input*1 + cache_creation*1.25 +
# cache_read*0.1 + output*5). Calibrated so the local estimate matched the
# claude.ai usage page (1.73M units -> 16% => ~10.8M budget). This is an
# approximation of Anthropic's meter, not the real limit — the settings/usage
# page is authoritative.
BUDGET_5H = int(os.environ.get("CC_5H_TOKEN_BUDGET", "10800000"))  # tune to your plan

# ---- ANSI helpers ---------------------------------------------------------
def c(code, s):
    return f"\033[{code}m{s}\033[0m"

BOLD, CYAN, BLUE, MAG, GREEN, YELL, RED, GREY = "1", "36", "34", "35", "32", "33", "31", "90"
ORANGE = "38;5;208"
SEP_PLAIN = "   |   "
SEP = c(GREY, SEP_PLAIN)

def meter_color(pct, warn=70, bad=90):
    return GREEN if pct < warn else (ORANGE if pct < bad else RED)

def term_width():
    col = os.environ.get("COLUMNS")
    if col and col.isdigit():
        return int(col)
    try:
        return shutil.get_terminal_size((120, 24)).columns
    except Exception:
        return 120

# ---- input ----------------------------------------------------------------
try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

cwd        = data.get("workspace", {}).get("current_dir") or data.get("cwd") or os.getcwd()
transcript = data.get("transcript_path", "")
model_name = data.get("model", {}).get("display_name", "")
cost       = data.get("cost", {}) or {}

left = []          # list of (plain, colored) tuples, in display order
branch_seg = None  # (plain, colored) right-aligned

# ---- dir ------------------------------------------------------------------
try:
    d = os.path.basename(cwd.rstrip("/")) or cwd
    left.append((d, c(BOLD, d)))
except Exception:
    pass

# ---- model ----------------------------------------------------------------
if model_name:
    left.append((model_name, c(CYAN, model_name)))

# ---- provider -------------------------------------------------------------
provider = "bedrock" if os.environ.get("CLAUDE_CODE_USE_BEDROCK") else "subscription"
prov_color = ORANGE if provider == "bedrock" else BLUE
left.append((provider, c(prov_color, provider)))

# ---- context used ---------------------------------------------------------
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
    used = None
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
        break
    if used is None:
        return None
    # Context window. This account runs Opus 4.8 on the 1M window (matches
    # /context). Override with CC_CONTEXT_LIMIT if a project uses 200k.
    limit = int(os.environ.get("CC_CONTEXT_LIMIT", "1000000"))
    return min(100, round(used * 100 / limit))

ctx = context_pct_used()
if ctx is not None:
    left.append((f"context {ctx}% used", c(meter_color(ctx), f"context {ctx}% used")))

# ---- 5h rolling usage % (account-wide), cached 60s ------------------------
def rolling_5h_tokens():
    cache = "/tmp/cc_statusline_5h.json"
    now = time.time()
    try:
        st = json.load(open(cache))
        if now - st.get("t", 0) < 60:
            return st.get("v")
    except Exception:
        pass
    cutoff = now - 5 * 3600
    total = 0
    for path in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
        try:
            if os.path.getmtime(path) < cutoff:
                continue
        except OSError:
            continue
        try:
            with open(path, "rb") as f:
                if os.path.getsize(path) > 2_000_000:
                    f.seek(-2_000_000, os.SEEK_END)
                    f.readline()
                lines = f.read().decode("utf-8", "replace").splitlines()
        except Exception:
            continue
        for line in lines:
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") != "assistant":
                continue
            ts = o.get("timestamp")
            if ts:
                try:
                    if datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() < cutoff:
                        continue
                except Exception:
                    pass
            u = o.get("message", {}).get("usage", {})
            total += (u.get("input_tokens", 0) * 1.0
                      + u.get("cache_creation_input_tokens", 0) * 1.25
                      + u.get("cache_read_input_tokens", 0) * 0.1
                      + u.get("output_tokens", 0) * 5.0)
    try:
        json.dump({"t": now, "v": total}, open(cache, "w"))
    except Exception:
        pass
    return total

# Reset countdown for Anthropic's *fixed* 5h block (anchored to the exact
# first message of the block, +5h) — not the sliding token window above.
def reset_remaining():
    cache = "/tmp/cc_statusline_reset.json"
    now = time.time()
    try:
        st = json.load(open(cache))
        if now - st.get("t", 0) < 60:
            return st.get("v")
    except Exception:
        pass
    SESSION = 5 * 3600
    lookback = now - 11 * 3600  # far enough back to find the true block start
    tss = []
    for path in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
        try:
            if os.path.getmtime(path) < lookback:
                continue
        except OSError:
            continue
        try:
            with open(path, "rb") as f:
                if os.path.getsize(path) > 2_000_000:
                    f.seek(-2_000_000, os.SEEK_END)
                    f.readline()
                lines = f.read().decode("utf-8", "replace").splitlines()
        except Exception:
            continue
        for line in lines:
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") != "assistant":
                continue
            ts = o.get("timestamp")
            if not ts:
                continue
            try:
                e = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except Exception:
                continue
            if e >= lookback:
                tss.append(e)
    remaining = None
    if tss:
        tss.sort()
        block_end = None
        prev = None
        for e in tss:
            if block_end is None or e >= block_end or (e - prev) >= SESSION:
                block_end = e + SESSION  # exact first-message anchor
            prev = e
        if block_end and block_end > now:
            remaining = int(block_end - now)
    try:
        json.dump({"t": now, "v": remaining}, open(cache, "w"))
    except Exception:
        pass
    return remaining

def fmt_remaining(secs):
    h, m = secs // 3600, (secs % 3600) // 60
    return f"{h}h {m:02d}m" if h else f"{m}m"

try:
    tok = rolling_5h_tokens()
    if tok:
        pct = min(100, round(tok * 100 / BUDGET_5H))
        rem = reset_remaining()
        label = f"{fmt_remaining(rem)} {pct}%" if rem is not None else f"5h {pct}%"
        left.append((label, c(meter_color(pct), label)))
except Exception:
    pass

# ---- session cost ---------------------------------------------------------
try:
    usd = cost.get("total_cost_usd")
    if usd is not None:
        left.append((f"${usd:.2f}", c(GREEN, f"${usd:.2f}")))
except Exception:
    pass

# ---- lines changed --------------------------------------------------------
try:
    add = cost.get("total_lines_added", 0)
    rem = cost.get("total_lines_removed", 0)
    if add or rem:
        plain = f"+{add} -{rem}"
        left.append((plain, c(GREEN, f"+{add}") + " " + c(RED, f"-{rem}")))
except Exception:
    pass

# ---- git branch + dirty (right-aligned) -----------------------------------
def git(*args):
    return subprocess.run(["git", "-C", cwd, *args],
                          capture_output=True, text=True, timeout=1).stdout.strip()
try:
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch:
        dirty = "*" if git("status", "--porcelain") else ""
        plain = f"⎇ {branch}{dirty}"
        branch_seg = (plain, c(MAG, f"⎇ {branch}") + c(YELL, dirty))
except Exception:
    pass

# ---- assemble with right alignment ----------------------------------------
left_plain   = SEP_PLAIN.join(p for p, _ in left)
left_colored = SEP.join(cc for _, cc in left)

if branch_seg:
    bp, bc = branch_seg
    gap = term_width() - len(left_plain) - len(bp)
    out = left_colored + (" " * gap if gap >= 2 else SEP_PLAIN) + bc
else:
    out = left_colored

sys.stdout.write(out)
