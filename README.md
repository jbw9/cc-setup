# cc-setup

My Claude Code setup: a status line, a few skills, and sensible defaults.
Installs in about a second on any machine and comes back off cleanly.

```sh
curl -fsSL https://github.com/jbw9/cc-setup/archive/refs/heads/main.tar.gz | tar xz -C ~ \
  && ~/cc-setup-main/install.sh
```

or, for a working tree:

```sh
git clone --depth 1 https://github.com/jbw9/cc-setup ~/cc-setup && ~/cc-setup/install.sh
```

Then quit and relaunch Claude Code (the status line loads at startup) and check
`/status` shows model `opus`, effort `high`.

## What it installs

| | |
|---|---|
| `home/statusline.py` | the status line under the prompt |
| `home/skills/` | `eli5`, `recap`, `karpathy-guidelines`, `frontend-design` |
| `home/CLAUDE.md` | short working-style and code rules |
| `home/settings.json` | opus · high effort · auto mode · 400k compact window · deny rules for `sudo`, `~/.ssh`, `~/.aws`, keychain, gcloud, gnupg, kube |

Flags: `--no-statusline`.

## The status line

```
cc-setup   |   main   |   +42 -7   |   Opus   |   high   |   context 12% used   |   $1.84
```

Directory, branch, uncommitted lines added/removed against `HEAD`, model, effort,
context used, and session cost. The context figure fades from green to red as it
approaches 40%. It assumes a 1M window; set `CC_CONTEXT_LIMIT=200000` for the
200k one. Each segment fails on its own, so a missing git repo never blanks the line.

## Safety on a borrowed machine

`install.sh` never destroys anything. Anything it overwrites is copied to
`~/.claude/.pre-restore-backup-<ts>/` and recorded in `~/.claude/.restore-manifest`.
`settings.json` is merged onto the existing one, not replaced.

- `./uninstall.sh` puts the machine back exactly as it was
- `./cleanup.sh` signs out, uninstalls, and wipes the transcripts and history
  your session left behind

Run `install.sh` once. A second run backs up the first run's files, so
`uninstall.sh` would then restore this setup instead of the original.

`permissions.defaultMode` is `auto`, so Claude edits files and runs commands
without asking. Change it to `acceptEdits` in `home/settings.json` if you'd
rather be asked.

## Keeping it current

`./export.sh` copies the live status line and skills back into this repo. Then commit.

## Credits

`skills/karpathy-guidelines` is vendored from
[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) (MIT).
`skills/frontend-design` is vendored from the official Claude plugin marketplace.
