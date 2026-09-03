# Timed-build runbook

Target: usable in **under 5 minutes** on a machine you've never touched.

## Before the day
- [ ] Ask, in writing, whether Claude Code and a personal login on their laptop
      is acceptable, and what happens to code pushed from their machine.
- [ ] Dry-run the clone + install on a second machine or a fresh user account.
- [ ] Put a copy on a USB stick. Guest wifi blocks things.
- [ ] Know your login path — browser OAuth needs a browser on *their* machine.

## Setup (~1 min)

Recon first, because on a machine that isn't yours the config belongs to someone
else — and a managed policy silently outranks anything you set:

    ls "/Library/Application Support/ClaudeCode/managed-settings.json"
    cat ~/.claude/settings.json

Then install. Needs no git and no GitHub account:

    claude --version || curl -fsSL https://claude.ai/install.sh | bash
    curl -fsSL https://github.com/jbw9/cc-setup/archive/refs/heads/main.tar.gz \
      | tar xz -C ~ && ~/cc-setup-main/install.sh
    claude                      # /login if the account isn't yours
    /status                     # model opus, effort high, Setting sources

Install **before** launching Claude. A SessionStart hook only fires at session
start, so a session that's already running won't have it.

If `/status` shows `Enterprise managed settings (file)`, a policy is overriding
you — `claude doctor` lists what got dropped. The likely casualties are Opus
(`availableModels`), auto mode (`permissions.defaultMode`), and hooks
(`disableAllHooks`). If Opus is locked out, set `model: sonnet` in
`~/.claude/agents/builder.md`; the rest of the design is unaffected.

## The build

    /kickoff <one line on what you're building>

Answer its questions properly — this is the highest-return five minutes of the
session. It writes `PLAN.md`, the contract files, and `DECISIONS.md`.

    /fanout                     # up to 3 parallel builders, then verify
    /handoff                    # checkpoint before anything long or risky
    /fanout                     # next round

Keep `/decide` in reach. Every time you or Claude picks something with a real
alternative, log it in the moment — you will not reconstruct it at hour three.

## Pairing and delegation

When another engineer joins:

    /brief WS2 @alice

They get a self-contained handoff: what to build, which globs are theirs, the
contracts quoted inline, what's already decided, and their `done-when`. Set the
workstream's `owner:` first — `/fanout` refuses to dispatch an agent onto a
human-owned workstream, and that check is the thing standing between you and two
writers in one file.

If they'll run their own Claude Code, put them on a separate branch or worktree.
Two agents in one working tree collide exactly like two builders, and neither
knows it.

**What to hand off:** the workstream with the cleanest contract boundary and the
least coupling to what you're doing live. Keep integration yourself.

## Last 15 minutes

    /defend

Reads `PLAN.md`, `DECISIONS.md` and the diff, then interrogates you the way a
sharp reviewer will. It flags decisions visible in the code that never made it
into `DECISIONS.md` — those are the ones you'll get asked about with no answer
ready.

## Before you hand the laptop back

    ~/cc-setup-main/cleanup.sh  # logout + undo + wipe transcripts
    rm -rf ~/cc-setup-main

## If something goes wrong
- No network → USB copy, or paste `home/CLAUDE.md` into the project root by hand.
  That alone gets you most of the value.
- `python3` missing → `./install.sh --no-statusline` (the hook also no-ops
  silently without python3; the workflow still works, it just stops surviving
  compactions).
- Login loops → run `claude` in a plain terminal, not the IDE extension.
- Existing `~/.claude` on their machine → install.sh merges and backs up;
  `uninstall.sh` restores it exactly.
- Fan-out produced a merge mess → the partition was wrong. Re-run `/kickoff` on
  the remaining work with fewer, larger workstreams.

## Deliberately not included
| Thing | Why |
|---|---|
| gstack | Browser-QA/ship/deploy tooling, 1.2 GB and a `bun install` you won't use in a timed build. |
| MCP servers | All project-scoped, each needs its own auth. Add per-project with `claude mcp add` only if the task needs one. |
| Session history, transcripts | Belongs on your machine, not theirs. |
| Stack defaults | On purpose. `/kickoff` asks; assuming wrong costs more than asking. |
