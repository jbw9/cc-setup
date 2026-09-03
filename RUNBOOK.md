# Interview-day runbook

Target: usable in **under 5 minutes** on a machine you've never touched.

## Before the day
- [ ] Ask the interviewer, in writing, whether using Claude Code and signing
      into a personal account on their laptop is OK. Ask what happens to code
      you push from their machine.
- [ ] Push this repo to GitHub (public, or public gist — a private repo means a
      `gh auth login` you don't have time for).
- [ ] Dry-run the whole thing on a second machine or a fresh user account.
- [ ] Put a copy on a USB stick. Guest wifi blocks things.
- [ ] Know your login path: browser OAuth needs a browser on *their* machine.

## On the day (in order)

    # 1. is claude even installed? (~60s if not)
    claude --version || curl -fsSL https://claude.ai/install.sh | bash

    # 2. setup (~10s)
    git clone --depth 1 https://github.com/<you>/claude-setup ~/claude-setup
    ~/claude-setup/install.sh

    # 3. sign in
    claude            # then /login

    # 4. verify before you start building
    /status           # model opus, effort high
    /context          # global CLAUDE.md is loaded

    # 5. seed the project
    cp ~/claude-setup/templates/PROJECT_CLAUDE.md ./CLAUDE.md
    # spend 2 minutes filling it in. This is the highest-return 2 minutes.

## Before you hand the laptop back

    ~/claude-setup/cleanup.sh     # logout + undo + wipe transcripts
    rm -rf ~/claude-setup

## If something goes wrong
- No network / clone blocked → USB copy, or paste `home/CLAUDE.md` into the
  project root by hand. That alone gets you 80% of the value.
- `python3` missing → `./install.sh --no-statusline`.
- Login loops → run `claude` in a plain terminal, not the IDE extension.
- Their laptop has an existing `~/.claude` → install.sh merges and backs up;
  `uninstall.sh` restores it exactly.

## What is deliberately NOT restored
| Thing | Why |
|---|---|
| gstack (1.2 GB, bun deps) | minutes to install, and it's browser-QA/ship/deploy tooling you won't use in a 3-hour build. `--with-gstack` if you must. |
| MCP servers (playwright, supabase, github, stitch) | all were project-scoped, and each needs its own auth. Add per-project with `claude mcp add` only if the task needs one. |
| Session history, transcripts, memory | belongs to your machine, not theirs. |
| Chrome extension / browser tooling | requires installing an extension in their Chrome. Ask first. |
