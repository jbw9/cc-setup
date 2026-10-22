# cc-setup

A portable Claude Code setup: a status line, a few skills, a short global
`CLAUDE.md` and `settings.json`, plus the scripts that install and reverse them.

## Working on this repo

- `home/` mirrors `~/.claude/`. Adding a skill means a new
  `home/skills/<name>/SKILL.md` and nothing else; `install.sh` globs the directory.
- `home/settings.json` must not contain absolute paths. `install.sh` injects the
  `statusLine` command at install time with the real config dir.
- After changing any script: `bash -n` it, then install into a throwaway
  `CLAUDE_CONFIG_DIR` seeded with a conflicting `CLAUDE.md`, `settings.json`,
  `statusline.py` and a same-named skill, and confirm `uninstall.sh` restores
  all of them exactly. That round trip is the test suite.
- `export.sh` pulls the live status line and skills back in. `home/CLAUDE.md`
  and `home/settings.json` are hand-maintained; diff them rather than overwriting.
