# Timed-build runbook

Target: usable in **under 5 minutes** on a machine you've never touched.

## Before the day
- [ ] Ask, in writing, whether Claude Code and a personal login on their laptop
      is acceptable, and what happens to code pushed from their machine.
- [ ] Ask what's already on the machine: runtimes, package managers, editor, and
      whether there's a package cache. On a borrowed machine a cold
      `install` on guest wifi is dead clock — know which stacks are warm before
      you pick one.
- [ ] Dry-run the clone + install on a second machine or a fresh user account.
- [ ] Print or copy `templates/KICKOFF_NOTES.md`. You fill it in *during* the
      briefing — that window costs no build clock, and `/kickoff <notes file>`
      reads it instead of interrogating you at minute five.
- [ ] Put a copy on a USB stick. Guest wifi blocks things.
- [ ] Know your login path — browser OAuth needs a browser on *their* machine.

## Setup (~1 min)

Recon first, because on a machine that isn't yours the config belongs to someone
else — a managed policy silently outranks anything you set, and which toolchains
are warm decides what stack is cheap to build in:

    ~/cc-setup-main/preflight.sh

Five seconds. Reports runtimes, package-manager caches and their sizes, registry
reachability, and whether managed settings are in play. **A toolchain that's
installed with a populated cache costs a minute to start; one that needs a
runtime install over guest wifi can cost thirty.** Make that a stack input
before the clock starts, not a discovery at minute five.

Then install. Needs no git and no GitHub account.

**On their machine, use the isolated install.** It puts the whole environment in
one folder, never reads or writes their `~/.claude`, and strips the `ANTHROPIC_*`
and `CLAUDE_*` variables their shell profile may be exporting — a stray
`ANTHROPIC_BASE_URL` silently repoints every request, and settings files cannot
override an env var:

    claude --version || curl -fsSL https://claude.ai/install.sh | bash
    curl -fsSL https://github.com/jbw9/cc-setup/archive/refs/heads/main.tar.gz \
      | tar xz -C ~ && ~/cc-setup-main/isolate.sh
    cd ~/cc-build
    ./claude-iso                # the launcher — NOT `claude`
    /login                      # scoped to this folder
    /status                     # model opus, effort high, Setting sources

Read what `isolate.sh` prints. It names the env vars it stripped, any ancestor
`CLAUDE.md` that will load regardless (the upward walk can't be turned off — if
one exists, build somewhere else), and any managed policy.

Use `install.sh` instead only on a machine that is yours.

Install **before** launching Claude. A SessionStart hook only fires at session
start, so a session that's already running won't have it.

If `/status` shows `Enterprise managed settings (file)`, a policy is overriding
you — `claude doctor` lists what got dropped. The likely casualties are Opus
(`availableModels`), auto mode (`permissions.defaultMode`), and hooks
(`disableAllHooks`). Opus being locked out needs no fix — `builder` is `model: inherit` and follows
the main model down; the rest of the design is unaffected.

## The build

Times below are fractions of the clock, not absolutes. The shape is what matters:
prove it end to end before going wide, and stop building well before you stop.

| When | What |
|---|---|
| **T+0** | `/kickoff notes.md` — hand it the notes you filled in during the briefing. It reads them and asks only about genuine gaps. Writes `PLAN.md` (with `## Time`), the project `CLAUDE.md`, and `DECISIONS.md`. Cap this at ~15 minutes: past that you are planning against a problem you don't understand yet, and the spine will teach you more than more planning would. |
| **T+6%** | **Round 0 — the spine.** Serial, no agents. One hardcoded input → one real transformation → one endpoint → one thing rendered. Then `demo.sh`. |
| **T+16%** | Spine green. **You are now demoable.** Contracts get derived from the code that just ran and frozen. |
| | `/fanout` — round 1. Fan in: verifier, `./demo.sh`, read back every builder's diff, harvest decisions, commit. |
| **T+50%** | `/pair` before anyone sits down with you. |
| | `/fanout` — further rounds. `/handoff` before anything long or risky. |
| **T−45m** | **Freeze.** No new workstreams. Integration, demo rehearsal, backfilling `DECISIONS.md`. Unfinished work is a `CUT` — say so. |
| **T−30m** | `/scale` → `SCALE.md`. |
| **T−15m** | `/defend`. |

**While a round runs, you are not idle.** That is the window for reading the
previous round's diff, writing the `/decide` entries you skipped, and rehearsing
`./demo.sh`. Over half of a timed build is serial work that no number of agents
touches — dispatch time is the only stretch where it overlaps with anything.

Keep `/decide` in reach the whole way. Every time you or Claude picks something
with a real alternative, log it in the moment — you will not reconstruct it at
hour three, and the `At scale:` lines are what `/scale` is built from.

Watch two numbers on the status line: **context %** and **5h usage %**. Three
Opus builders over a long build will find the usage limit. If it's past two
thirds with a third of the clock left, drop to two concurrent or put
`builder-fast` (Sonnet) for the mechanical workstreams.

### Why the spine comes first

Skipping Round 0 means freezing contracts you have only guessed at, and having
nothing runnable until the first fan-in lands. Both are worse than they sound.
A wrong contract discovered with three builders' work stacked on it costs more
than the spine did, and a build with no demoable state has nothing to fall back
to when a round goes badly. The spine costs a sixth of the clock and removes
both failure modes at once.

## The pairing session

Someone sitting down with you mid-build is not a delegation — they want to see
what you built, why, and how you work. `/pair` gets you ready:

    /pair

It lands what's in flight, runs `/handoff`, confirms `demo.sh` is green, and
gives you a six-line walkthrough plus two or three candidates to pair on.

**Have no agents running.** Three builders mid-flight makes you a spectator to
your own project at the exact moment someone is watching you own it. Land the
round first; pair on something you drive, or on one focused agent they can watch
you steer.

**Name the weak part yourself** before they find it. They will find it either way.

## Delegating a workstream

When another engineer takes work away:

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

## The last hour

    /scale     # -> SCALE.md, from the At scale: lines you've been logging
    /defend    # interrogates the weakest choices, in AskUserQuestion rounds

`/defend` reads `PLAN.md`, `DECISIONS.md` and the diff. It flags decisions
visible in the code that never made it into `DECISIONS.md` — those are the ones
you'll get asked about with no answer ready. If that list is long, the read-back
step at fan-in was being skipped.

Rehearse `./demo.sh` out loud at least once before presenting. A demo path you
have only ever seen a machine run is a demo path you have not rehearsed.

## Before you hand the laptop back

    ~/cc-build/teardown.sh      # scoped logout, then deletes the whole folder
    rm -rf ~/cc-setup-main

Do not skip the logout. Settings, skills, transcripts and the account id all
live inside `~/cc-build` and go with it — but on macOS the OAuth credential is
in the login keychain, which no directory scoping reaches. `teardown.sh` runs
the logout through the launcher so it targets your config and not theirs.

If you used the global `install.sh` instead: `~/cc-setup-main/cleanup.sh`.

## If something goes wrong
- No network → USB copy, or paste `home/CLAUDE.md` into the project root by hand.
  That alone gets you most of the value.
- Ran `claude` instead of `./claude-iso` → you were using their config, not
  yours. Quit, run the launcher, and re-check `/status`.
- `python3` missing → `./install.sh --no-statusline` (the hook also no-ops
  silently without python3; the workflow still works, it just stops surviving
  compactions).
- Login loops → run `claude` in a plain terminal, not the IDE extension.
- Existing `~/.claude` on their machine → install.sh merges and backs up;
  `uninstall.sh` restores it exactly.
- Fan-out produced a merge mess → the partition was wrong. Re-run `/kickoff` on
  the remaining work with fewer, larger workstreams.
- Usage limit hit mid-build → you are coding by hand from here. Survivable only
  if you've been reading the diffs at fan-in. Cut to the `MUST` tier and protect
  the demo path.
- `demo.sh` red and the cause isn't obvious → `git reset --hard` to the last
  green round's commit. That commit exists because `/fanout` makes it.

## Deliberately not included
| Thing | Why |
|---|---|
| gstack | Browser-QA/ship/deploy tooling, 1.2 GB and a `bun install` you won't use in a timed build. |
| MCP servers | All project-scoped, each needs its own auth. Add per-project with `claude mcp add` only if the task needs one. |
| Session history, transcripts | Belongs on your machine, not theirs. |
| Stack defaults | On purpose. `/kickoff` asks; assuming wrong costs more than asking. |
