#!/usr/bin/env python3
"""Render a Claude Code setup as one static page, and summarise it in the README.

  python3 site/build.py           what this repo installs (home/) -> site/index.html + README block
  python3 site/build.py --live    this machine's ~/.claude        -> site/live.html (git-ignored)

Reads only; never writes to the config. Live MCP servers show name and command
only: their env and headers can hold secrets. The output carries no timestamp,
so an unchanged setup rebuilds byte-identical and CI commits nothing.
"""
import glob, html, json, os, re, shutil, subprocess, sys, tempfile

HOME = os.path.expanduser("~")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = "--live" in sys.argv
CDIR = os.environ.get("CLAUDE_CONFIG_DIR", f"{HOME}/.claude") if LIVE else f"{REPO}/home"
OUT = f"{REPO}/site/{'live' if LIVE else 'index'}.html"
README = f"{REPO}/README.md"
e = html.escape


def load(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default


def short(path):
    return path.replace(REPO + "/", "").replace(HOME, "~")


# ---- skills ---------------------------------------------------------------
def frontmatter(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return {}
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    out, lines, i = {}, m.group(1).splitlines(), 0
    while i < len(lines):
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", lines[i])
        i += 1
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        # Block scalars (>-, |) and plain values that wrap onto indented lines.
        if val in ("", ">", ">-", "|", "|-") or (i < len(lines) and lines[i].startswith("  ")):
            parts = [] if val in ("", ">", ">-", "|", "|-") else [val]
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                parts.append(lines[i].strip())
                i += 1
            val = " ".join(p for p in parts if p)
        out[key] = val.strip("'\"")
    return out


def skills_in(root):
    found = []
    for f in sorted(glob.glob(f"{root}/*/SKILL.md")):
        fm = frontmatter(f)
        found.append({"name": fm.get("name") or os.path.basename(os.path.dirname(f)),
                      "desc": fm.get("description", ""),
                      "path": short(os.path.dirname(f))})
    return found


groups = []
ours = {os.path.basename(os.path.dirname(f)) for f in glob.glob(f"{REPO}/home/skills/*/SKILL.md")}
mine, aws, other = [], [], []
for s in skills_in(f"{CDIR}/skills"):
    n = s["name"]
    if n in ours:
        mine.append(s)
    elif n.startswith("aws-") or "aws" in n or n == "amazon-bedrock" or "cloudwatch" in n:
        aws.append(s)
    else:
        other.append(s)
where = short(CDIR) + "/skills"
groups.append(("From cc-setup", where, mine))
if other:
    groups.append(("Other", where, other))
if aws:
    groups.append(("AWS", where + " — the AWS skill pack", aws))

synced = []
for d in glob.glob(f"{CDIR}/skills/synced/*/"):
    synced += skills_in(d)
if synced:
    groups.append(("Synced from claude.ai", "~/.claude/skills/synced", sorted(synced, key=lambda s: s["name"])))

settings = load(f"{CDIR}/settings.json", {})
installed = load(f"{CDIR}/plugins/installed_plugins.json", {}).get("plugins", {})
plugins = []
for pid, on in (settings.get("enabledPlugins") or {}).items():
    inst = (installed.get(pid) or [{}])[0]
    path = inst.get("installPath", "")
    sk = skills_in(f"{path}/skills") if path else []
    plugins.append({"id": pid, "on": on, "version": inst.get("version", ""), "skills": sk})
    if sk:
        groups.append((f"Plugin · {pid.split('@')[0]}", short(path), sk))

# ---- status line, rendered live --------------------------------------------
def xterm(n):
    if n < 16:
        base = ["000000", "cd3131", "0dbc79", "e5e510", "2472c8", "bc3fbc", "11a8cd", "e5e5e5",
                "666666", "f14c4c", "23d18b", "f5f543", "3b8eea", "d670d6", "29b8db", "ffffff"]
        return "#" + base[n]
    if n < 232:
        n -= 16
        lv = [0, 95, 135, 175, 215, 255]
        return "#%02x%02x%02x" % (lv[n // 36], lv[n // 6 % 6], lv[n % 6])
    g = 8 + (n - 232) * 10
    return "#%02x%02x%02x" % (g, g, g)


BASIC = {30: 0, 31: 1, 32: 2, 33: 3, 34: 4, 35: 5, 36: 6, 37: 7, 90: 8}


def ansi_to_html(s):
    out, style = [], {}
    for chunk in re.split(r"(\x1b\[[0-9;]*m)", s):
        m = re.fullmatch(r"\x1b\[([0-9;]*)m", chunk)
        if not m:
            if chunk:
                css = ";".join(f"{k}:{v}" for k, v in style.items())
                out.append(f'<span style="{css}">{e(chunk)}</span>' if css else e(chunk))
            continue
        codes = [int(c) for c in m.group(1).split(";") if c] or [0]
        i = 0
        while i < len(codes):
            c = codes[i]
            if c == 0:
                style = {}
            elif c == 1:
                style["font-weight"] = "700"
            elif c == 38 and i + 2 < len(codes) and codes[i + 1] == 5:
                style["color"] = xterm(codes[i + 2]); i += 2
            elif c in BASIC:
                style["color"] = xterm(BASIC[c])
            i += 1
    return "".join(out)


def sample_repo(root):
    """A throwaway repo on `main` with a fixed uncommitted diff, so the +/- segment
    reads the same on every machine and in CI rather than echoing this checkout."""
    def git(*a):
        subprocess.run(["git", "-C", root, "-c", "user.name=x", "-c", "user.email=x@x", *a],
                       capture_output=True, check=True)
    os.makedirs(root)
    git("init", "-q", "-b", "main")
    open(f"{root}/app.py", "w").write("".join(f"line {i}\n" for i in range(20)))
    git("add", "."); git("commit", "-qm", "init")
    open(f"{root}/app.py", "w").write("".join(f"line {i}\n" for i in range(3, 20)) + "new\n" * 12)


def statusline_samples():
    script = f"{CDIR}/statusline.py"
    if not os.path.exists(script):
        return []
    tmpdir = tempfile.mkdtemp()
    proj, tmp = f"{tmpdir}/my-project", f"{tmpdir}/transcript.jsonl"
    rows = []
    try:
        sample_repo(proj)
        # A fake transcript per sample, so the context meter shows its colour ramp.
        for pct, effort, cost in ((4, "high", 0.42), (22, "xhigh", 3.18), (39, "max", 11.07)):
            with open(tmp, "w") as f:
                f.write(json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": pct * 10000}}}) + "\n")
            data = {"workspace": {"current_dir": proj},
                    "model": {"display_name": "Opus 5.5"}, "effort": {"level": effort},
                    "cost": {"total_cost_usd": cost}, "transcript_path": tmp}
            r = subprocess.run(["python3", script], input=json.dumps(data), capture_output=True,
                               text=True, timeout=5, env={**os.environ, "CC_CONTEXT_LIMIT": "1000000"})
            rows.append(ansi_to_html(r.stdout))
    except Exception:
        pass
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return rows


# ---- CLAUDE.md as markdown --------------------------------------------------
def inline(t):
    t = e(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return t


def markdown(text):
    out, para, items = [], [], []

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>"); para.clear()
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); items.clear()

    for line in text.splitlines():
        if not line.strip():
            flush(); continue
        h = re.match(r"^(#{1,3})\s+(.*)", line)
        if h:
            flush(); lvl = len(h.group(1)) + 1
            out.append(f"<h{lvl}>{inline(h.group(2))}</h{lvl}>"); continue
        b = re.match(r"^\s*[-*]\s+(.*)", line)
        if b:
            if para:
                flush()
            items.append(b.group(1)); continue
        if items:
            items[-1] += " " + line.strip()
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out)


claude_md = ""
try:
    claude_md = open(f"{CDIR}/CLAUDE.md").read()
except Exception:
    pass

# ---- settings ---------------------------------------------------------------
perm = settings.get("permissions") or {}
facts = [
    ("Model", settings.get("model", "default")),
    ("Effort", settings.get("effortLevel", "default")),
    ("Permission mode", perm.get("defaultMode", "default")),
    ("Auto-compact", f"at {settings['autoCompactWindow']:,} tokens" if settings.get("autoCompactWindow") else
     ("on" if settings.get("autoCompactEnabled", True) else "off")),
    ("Interface", settings.get("tui", "default")),
    ("Notifications", settings.get("preferredNotifChannel", "default")),
    ("Always thinking", "on" if settings.get("alwaysThinkingEnabled") else "off"),
    # install.sh injects statusLine with this machine's path, so home/ has none.
    ("Status line", short((settings.get("statusLine") or {}).get("command", "none")) if LIVE else "statusline.py"),
]

hooks = []
for event, blocks in (settings.get("hooks") or {}).items():
    for b in blocks:
        for h in b.get("hooks", []):
            hooks.append((event, b.get("matcher", "*"), short(h.get("command", ""))))

mcp = []
for name, v in ((load(f"{HOME}/.claude.json", {}) if LIVE else {}).get("mcpServers") or {}).items():
    mcp.append((name, v.get("type", "stdio"), v.get("command") or v.get("url") or ""))

agents = sorted(os.path.basename(f)[:-3] for f in glob.glob(f"{CDIR}/agents/*.md"))

# ---- page -------------------------------------------------------------------
def card(title, sub, body, cls=""):
    sub_html = f'<div class="sub">{e(sub)}</div>' if sub else ""
    return f'<section class="card {cls}"><div class="card-h"><h3>{e(title)}</h3>{sub_html}</div>{body}</section>'


def rows(pairs):
    return '<dl class="rows">' + "".join(f"<dt>{e(k)}</dt><dd><code>{e(str(v))}</code></dd>" for k, v in pairs) + "</dl>"


def mono_list(items, empty):
    if not items:
        return f'<p class="empty">{e(empty)}</p>'
    return '<ul class="mono-list">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


skill_total = sum(len(g[2]) for g in groups)
skill_html = []
for title, where, items in groups:
    cards = "".join(
        f'<details class="skill" data-q="{e((s["name"] + " " + s["desc"]).lower())}">'
        f'<summary><span class="sk-name">{e(s["name"])}</span>'
        f'<span class="sk-desc">{e(s["desc"]) or "<em>no description</em>"}</span></summary>'
        f'<div class="sk-full"><p>{e(s["desc"])}</p><code>{e(s["path"])}</code></div></details>'
        for s in items)
    skill_html.append(
        f'<div class="group"><div class="group-h"><span class="eyebrow">{e(title)}</span>'
        f'<span class="count tnum">{len(items)}</span><span class="where">{e(where)}</span></div>'
        f'<div class="skills">{cards}</div></div>')

status_rows = statusline_samples()
status_html = "".join(f'<div class="term-line">{r}</div>' for r in status_rows) or '<p class="empty">no status line</p>'

chips = [f'{settings.get("model", "default")}', f'effort {settings.get("effortLevel", "default")}',
         f'{perm.get("defaultMode", "default")} mode', f"{skill_total} skills", f"{len(plugins)} plugins",
         f"{len(mcp)} MCP servers"][: 6 if LIVE else 5]

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claude Code Setup</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --cream:#fafaf8; --white:#ffffff; --surface:#f9f9f7; --low:#f4f4f2; --container:#eeeeec; --dim:#dadad8;
  --ink:#1a1a2e; --on:#1a1c1b; --variant:#404945; --slate:#6b7280; --faint:#9aa0a6;
  --green:#1f5c4d; --mint:#e8f5e9; --mint-line:#cfe6d4;
  --amber:#8a6416; --amber-s:#fdf6e3; --amber-l:#e2c77e;
  --clay:#8e3320; --clay-s:#fbede9; --clay-l:#e0b3a5;
  --line:#e7e5e0; --line-strong:#d6d3cc; --night:#1a1a2e;
  --shadow:0 1px 2px rgba(26,26,46,.04);
  --sans:'Inter',ui-sans-serif,system-ui,sans-serif; --mono:'JetBrains Mono',ui-monospace,monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  color-scheme:dark;
  --cream:#121317; --white:#1b1d23; --surface:#17191e; --low:#1f2128; --container:#262932; --dim:#30343e;
  --ink:#ececf1; --on:#e3e3e6; --variant:#b7bcc4; --slate:#9aa1ad; --faint:#6e7581;
  --green:#6cc28a; --mint:#16302a; --mint-line:#2c5446;
  --amber:#e2c77e; --amber-s:#2b2414; --amber-l:#6b5520;
  --clay:#f0a58e; --clay-s:#331f1a; --clay-l:#7a4436;
  --line:#2b2e37; --line-strong:#3a3e4a; --night:#0c0d10; --shadow:0 1px 2px rgba(0,0,0,.3);
}} }}
* {{ box-sizing:border-box; border-color:var(--line); }}
html {{ font-family:var(--sans); -webkit-font-smoothing:antialiased; }}
body {{ margin:0; background:var(--cream); color:var(--ink);
  background-image:radial-gradient(var(--dim) 1px, transparent 1px); background-size:24px 24px; background-position:-1px -1px; }}
.wrap {{ max-width:1080px; margin:0 auto; padding:56px 24px 96px; }}
code, .mono {{ font-family:var(--mono); }}
.tnum {{ font-variant-numeric:tabular-nums; }}
.eyebrow {{ font-family:var(--mono); font-size:10.5px; text-transform:uppercase; letter-spacing:.09em; color:var(--faint); }}
header h1 {{ font-size:30px; line-height:1.18; letter-spacing:-.02em; font-weight:600; margin:10px 0 6px; }}
header p {{ color:var(--variant); margin:0 0 18px; font-size:14px; }}
.chips {{ display:flex; flex-wrap:wrap; gap:6px; }}
.chip {{ font-family:var(--mono); font-size:11px; padding:4px 9px; border:1px solid var(--line); border-radius:6px; background:var(--white); color:var(--variant); }}
.chip.on {{ color:var(--green); background:var(--mint); border-color:var(--mint-line); }}
nav {{ position:sticky; top:0; z-index:5; display:flex; gap:4px; padding:10px 0; margin:28px 0 8px;
  background:color-mix(in srgb, var(--cream) 88%, transparent); backdrop-filter:blur(6px); border-bottom:1px solid var(--line); overflow-x:auto; }}
nav a {{ font-size:13px; font-weight:500; color:var(--slate); text-decoration:none; padding:6px 10px; border-radius:8px; white-space:nowrap;
  transition:background-color .15s ease, color .15s ease; }}
nav a:hover {{ background:var(--low); color:var(--ink); }}
h2 {{ font-size:20px; line-height:1.3; letter-spacing:-.01em; font-weight:600; margin:48px 0 4px; scroll-margin-top:64px; }}
.lede {{ color:var(--slate); font-size:13.5px; margin:0 0 16px; }}
.grid {{ display:grid; gap:12px; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); }}
.card {{ background:var(--white); border:1px solid var(--line); border-radius:14px; padding:16px 18px;
  transition:border-color .15s ease, box-shadow .15s ease; min-width:0; }}
.card:hover {{ border-color:var(--line-strong); box-shadow:var(--shadow); }}
.card-h {{ margin-bottom:12px; }}
.card h3 {{ font-size:15px; font-weight:600; letter-spacing:-.01em; margin:0; }}
.card .sub {{ font-family:var(--mono); font-size:11.5px; color:var(--faint); margin-top:3px; overflow-wrap:anywhere; }}
.rows {{ display:grid; grid-template-columns:auto 1fr; gap:0; margin:0; font-size:13px; }}
.rows dt, .rows dd {{ padding:7px 0; border-top:1px solid var(--line); margin:0; }}
.rows dt {{ color:var(--slate); padding-right:16px; }}
.rows dd {{ text-align:right; overflow-wrap:anywhere; }}
.rows dd code, .mono-list code {{ font-size:12px; color:var(--on); }}
.rows dt:first-of-type, .rows dt:first-of-type + dd {{ border-top:0; }}
.mono-list {{ list-style:none; margin:0; padding:0; }}
.mono-list li {{ font-family:var(--mono); font-size:12px; padding:7px 0; border-top:1px solid var(--line); color:var(--on); overflow-wrap:anywhere; }}
.mono-list li:first-child {{ border-top:0; }}
.tag {{ font-family:var(--mono); font-size:10px; letter-spacing:.04em; padding:2px 6px; border-radius:6px; border:1px solid; margin-right:8px; }}
.tag.deny {{ color:var(--clay); background:var(--clay-s); border-color:var(--clay-l); }}
.tag.ev {{ color:var(--amber); background:var(--amber-s); border-color:var(--amber-l); }}
.tag.off {{ color:var(--slate); background:var(--low); border-color:var(--line-strong); }}
.dim {{ color:var(--faint); }}
.empty {{ color:var(--faint); font-size:13px; margin:0; }}
.term {{ background:var(--night); border-radius:14px; padding:18px 20px; overflow-x:auto; }}
.term-line {{ font-family:var(--mono); font-size:12.5px; white-space:pre; color:#d4d4d4; line-height:2; }}
.prompt {{ background:var(--white); border:1px solid var(--line); border-radius:14px; padding:8px 28px 20px; font-size:14px; line-height:1.65; color:var(--on); }}
.prompt h2 {{ font-size:13px; margin:22px 0 6px; font-family:var(--mono); text-transform:uppercase; letter-spacing:.09em; color:var(--faint); font-weight:500; }}
.prompt h2:first-child {{ display:none; }}
.prompt h3 {{ font-size:15px; font-weight:600; margin:22px 0 6px; padding-top:16px; border-top:1px solid var(--line); }}
.prompt h3:first-of-type {{ border-top:0; padding-top:4px; }}
.prompt ul {{ margin:0; padding-left:18px; }}
.prompt li {{ margin:4px 0; }}
.prompt li::marker {{ color:var(--faint); }}
.prompt code {{ font-size:12.5px; background:var(--container); padding:1px 5px; border-radius:5px; }}
.prompt-meta {{ font-family:var(--mono); font-size:11.5px; color:var(--faint); margin-top:10px; }}
.search {{ width:100%; font:inherit; font-size:14px; padding:10px 14px; border:1px solid var(--line); border-radius:12px; background:var(--white); color:var(--ink); margin-bottom:8px; outline:none;
  transition:border-color .15s ease; }}
.search:focus {{ border-color:var(--green); }}
.group {{ margin-top:22px; }}
.group-h {{ display:flex; align-items:baseline; gap:10px; margin-bottom:10px; flex-wrap:wrap; }}
.count {{ font-family:var(--mono); font-size:10.5px; color:var(--green); background:var(--mint); border:1px solid var(--mint-line); padding:1px 7px; border-radius:999px; }}
.where {{ font-family:var(--mono); font-size:11px; color:var(--faint); overflow-wrap:anywhere; }}
.skills {{ display:grid; gap:8px; grid-template-columns:repeat(auto-fill, minmax(300px, 1fr)); align-items:start; }}
.skill {{ background:var(--white); border:1px solid var(--line); border-radius:12px; transition:border-color .15s ease, box-shadow .15s ease; min-width:0; }}
.skill:hover {{ border-color:var(--line-strong); box-shadow:var(--shadow); }}
.skill[open] {{ grid-column:1 / -1; border-color:var(--line-strong); }}
.skill summary {{ list-style:none; cursor:pointer; padding:12px 14px; display:block; }}
.skill summary::-webkit-details-marker {{ display:none; }}
.sk-name {{ display:block; font-family:var(--mono); font-size:12.5px; font-weight:600; color:var(--ink); }}
.sk-desc {{ display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; font-size:12.5px; line-height:1.55; color:var(--variant); margin-top:4px; }}
.skill[open] .sk-desc {{ display:none; }}
.sk-full {{ padding:0 14px 14px; font-size:13px; line-height:1.6; color:var(--variant); animation:arrive .32s cubic-bezier(.22,1,.36,1); }}
.sk-full p {{ margin:4px 0 10px; }}
.sk-full code {{ font-size:11px; color:var(--faint); overflow-wrap:anywhere; }}
.hidden {{ display:none !important; }}
footer {{ margin-top:64px; font-family:var(--mono); font-size:11px; color:var(--faint); }}
@keyframes arrive {{ from {{ opacity:0; transform:translateY(-6px) scale(.97); }} to {{ opacity:1; transform:none; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration:.01ms !important; transition-duration:.01ms !important; }} }}
@media (max-width:640px) {{ .wrap {{ padding:32px 16px 64px; }} .grid, .skills {{ grid-template-columns:1fr; }} .prompt {{ padding:4px 18px 16px; }} }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="eyebrow">{"~/.claude · live" if LIVE else "jbw9/cc-setup"}</div>
  <h1>Claude Code setup</h1>
  <p>{"What every session on this machine starts with" if LIVE else "What <code>install.sh</code> puts in <code>~/.claude</code>"}: the status line, the instructions, the settings and the skills.</p>
  <div class="chips">{''.join(f'<span class="chip{" on" if i == 0 else ""}">{e(c)}</span>' for i, c in enumerate(chips))}</div>
</header>
<nav><a href="#statusline">Status line</a><a href="#prompt">System prompt</a><a href="#settings">Settings</a><a href="#skills">Skills</a></nav>

<h2 id="statusline">Status line</h2>
<p class="lede">Under the prompt. Rendered by running <code>statusline.py</code> on sample sessions; context fades green → red as it nears 40%.</p>
<div class="term">{status_html}</div>

<h2 id="prompt">System prompt</h2>
<p class="lede">Your global <code>CLAUDE.md</code>, added to every session in every project.</p>
<div class="prompt">{markdown(claude_md) if claude_md else '<p class="empty">no CLAUDE.md</p>'}</div>
<div class="prompt-meta">{e(short(CDIR))}/CLAUDE.md · {len(claude_md.splitlines())} lines</div>

<h2 id="settings">Settings</h2>
<p class="lede"><code>{e(short(CDIR))}/settings.json</code>{", plus MCP servers from <code>~/.claude.json</code>" if LIVE else ", merged onto the machine's own"}.</p>
<div class="grid">
{card("Defaults", "settings.json", rows(facts))}
{card("Blocked", f"permissions.deny · {len(perm.get('deny', []))} rules", mono_list([f'<span class="tag deny">deny</span>{e(r)}' for r in perm.get("deny", [])], "nothing blocked"))}
{card("Allowed without asking", f"permissions.allow · {len(perm.get('allow', []))} rules", mono_list([e(r) for r in perm.get("allow", [])], "none — auto mode decides"))}
{card("Hooks", f"{len(hooks)} configured", mono_list([f'<span class="tag ev">{e(ev)}</span>{e(cmd)}' for ev, m, cmd in hooks], "no hooks"))}
{card("Plugins", "enabledPlugins", mono_list([(f'{e(p["id"].split("@")[0])} <span class="dim">{e(p["version"])}</span>' if p["on"] else f'<span class="tag off">off</span>{e(p["id"])}') for p in plugins], "no plugins"))}
{card("MCP servers", "~/.claude.json · name and command only", mono_list([f'{e(n)} <span class="dim">{e(t)} · {e(c)}</span>' for n, t, c in mcp], "none configured locally")) if LIVE else ""}
{card("Agents", short(CDIR) + "/agents", mono_list([e(a) for a in agents], "no custom agents")) if LIVE else ""}
</div>

<h2 id="skills">Skills</h2>
<p class="lede"><span class="tnum">{skill_total}</span> skills Claude can load on demand. Click one for its full description.</p>
<input class="search" id="q" type="search" placeholder="Filter skills…" autocomplete="off">
{''.join(skill_html)}

<footer>generated by site/build.py{" --live" if LIVE else " from home/"}</footer>
</div>
<script>
const q = document.getElementById('q');
q.addEventListener('input', () => {{
  const v = q.value.trim().toLowerCase();
  document.querySelectorAll('.group').forEach(g => {{
    let shown = 0;
    g.querySelectorAll('.skill').forEach(s => {{
      const hit = !v || s.dataset.q.includes(v);
      s.classList.toggle('hidden', !hit); shown += hit;
    }});
    g.classList.toggle('hidden', !shown);
    g.querySelector('.count').textContent = shown;
  }});
}});
</script>
</body>
</html>
"""
open(OUT, "w").write(page)
print(f"wrote {short(OUT)} · {skill_total} skills · {len(status_rows)} status lines")

# ---- README block -----------------------------------------------------------
# GitHub strips scripts, styles and iframes from a README, so the page can't be
# embedded; the README gets the same facts as markdown, between these markers.
if not LIVE and os.path.exists(README):
    md = ["| Setting | Value |", "|---|---|"] + [f"| {k} | `{v}` |" for k, v in facts]
    md += ["", f"**Blocked** ({len(perm.get('deny', []))} rules): " + ", ".join(f"`{r}`" for r in perm.get("deny", [])), ""]
    md += ["| Skill | What it does |", "|---|---|"]
    for _, _, items in groups:
        for s in items:
            d = s["desc"].replace("|", "\\|")
            md.append(f"| `{s['name']}` | {d[:157] + '…' if len(d) > 160 else d} |")
    block = "<!-- setup:start — generated by site/build.py, edit home/ instead -->\n" + "\n".join(md) + "\n<!-- setup:end -->"
    text = open(README).read()
    new = re.sub(r"<!-- setup:start.*?<!-- setup:end -->", lambda _: block, text, flags=re.S)
    if new != text:
        open(README, "w").write(new)
        print("updated README.md")
