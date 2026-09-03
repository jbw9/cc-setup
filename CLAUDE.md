# cc-setup

A portable Claude Code environment: config, agents, skills and one hook, plus
the scripts that install and reverse them.

## Installing it

One command, documented at the top of README.md:

```sh
curl -fsSL https://github.com/jbw9/cc-setup/archive/refs/heads/main.tar.gz | tar xz -C ~ \
  && ~/cc-setup-main/install.sh
```

Then the user must **quit and relaunch Claude Code** — a `SessionStart` hook
cannot apply to a session already running. Say so explicitly; setup is not done
until they restart.

Never hand-copy files into `~/.claude` instead. `install.sh` writes a backup and
a `.restore-manifest` that `uninstall.sh` reads to restore the machine exactly.
Bypassing it means the install can no longer be reversed — which matters,
because this often runs on a machine that isn't the user's.

## Working on this repo

- `home/` mirrors `~/.claude/`. Adding a skill means a new `home/skills/<name>/SKILL.md`
  and nothing else — `install.sh` globs the directory.
- Adding an agent means a new `home/agents/<name>.md`. Same, it's globbed.
- `home/settings.json` must not contain absolute paths. `install.sh` injects the
  `statusLine` and hook commands at install time with the real config dir.
- `argument-hint` values must be quoted. `[a] [b]` is invalid YAML and the
  frontmatter silently fails to parse.
- After changing any script: `bash -n` it, then install into a throwaway
  `CLAUDE_CONFIG_DIR` seeded with a conflicting `CLAUDE.md`, `settings.json`,
  a same-named skill and a pre-existing `SessionStart` hook, and confirm
  `uninstall.sh` restores all four exactly. That round trip is the test suite.
- `export.sh` pulls the live config back in. `home/CLAUDE.md` and
  `home/settings.json` are hand-maintained; diff them rather than overwriting.

`ARCHITECTURE.md` explains why the workflow is shaped this way. Read it before
changing the agent or skill contracts — the disjoint-file-ownership rule is
load-bearing, not stylistic.
