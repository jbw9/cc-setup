# claude-setup

My Claude Code environment, portable. Clone it on any machine and be working in
under a minute.

```sh
git clone --depth 1 https://github.com/<you>/claude-setup ~/claude-setup
~/claude-setup/install.sh
```

Then `claude`, `/login`, and go. Read **[RUNBOOK.md](RUNBOOK.md)** before an
interview — it's the ordered checklist, including how to clean up afterwards.

## What it installs

| | |
|---|---|
| `home/CLAUDE.md` | global preferences, loaded into every session |
| `home/settings.json` | opus · high effort · auto mode · 400k compact window · deny-rules for `sudo`, `~/.ssh`, `~/.aws`, keychain |
| `home/statusline.py` | dir · model · context% · 5h usage% · cost · diff · branch |
| `home/skills/` | graphify, visual-plan, apple-design, eli5, recap |
| plugin | `frontend-design` from the official marketplace (best effort) |

Flags: `--with-stitch` (Stitch/shadcn/Remotion/design-md skills),
`--with-gstack` (clones gstack, needs `bun`, takes minutes),
`--no-statusline`.

## Safety on a borrowed machine

`install.sh` never destroys anything. Existing `CLAUDE.md`, `settings.json` and
same-named skills are copied to `~/.claude/.pre-restore-backup-<ts>/` and
recorded in `~/.claude/.restore-manifest`. `settings.json` is *merged* onto
theirs, not replaced.

- `./uninstall.sh` — restore the machine to exactly how you found it
- `./cleanup.sh` — logout + uninstall + wipe the transcripts and history your
  session left behind

Note `permissions.defaultMode` is `auto`, which lets Claude edit files and run
commands without prompting. That's the point on your own machine; on someone
else's, decide deliberately. Change it to `acceptEdits` in
`home/settings.json` if you'd rather be asked about shell commands.

## Keeping it current

Run `./export.sh` on your own machine to pull your live config back into this
repo, then commit.
