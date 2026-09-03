# cc-setup

My Claude Code environment: a plan-first, fan-out build workflow that travels.
Clone it on any machine and be working in under a minute.

```sh
curl -fsSL https://github.com/jbw9/cc-setup/archive/refs/heads/main.tar.gz | tar xz -C ~ \
  && ~/cc-setup-main/install.sh
```

No git, no GitHub account, no credentials — it's a public tarball. Use this on a
machine that isn't yours. If you'd rather have a working tree:

```sh
git clone --depth 1 https://github.com/jbw9/cc-setup ~/cc-setup && ~/cc-setup/install.sh
```

(Cloning a public repo is anonymous too — GitHub auth is only for private repos
and for pushing.)

Then `claude`, `/login`, `/kickoff`. See **[RUNBOOK.md](RUNBOOK.md)** for the
timed-build checklist, and **[ARCHITECTURE.md](ARCHITECTURE.md)** for why any of
this is shaped the way it is.

## The workflow

```
/kickoff  →  /fanout  →  /defend
```

| | |
|---|---|
| `/kickoff` | Interrogates the request until nothing material is ambiguous, then writes `PLAN.md`: frozen contracts, workstreams with disjoint file ownership, and a `done-when` command each. Writes the contracts as real files. |
| `/fanout` | Dispatches up to 3 parallel `builder` agents on non-overlapping globs, fans in, runs `verifier`, harvests decisions. |
| `/brief` | Hands a workstream to a human teammate instead of an agent. |
| `/decide` | Logs a choice to `DECISIONS.md` the moment it's made — with the option it beat. |
| `/handoff` | Checkpoints state into `PLAN.md` so it survives a compaction. |
| `/defend` | Rehearses the "why this over that" questions before you present. |

The one idea underneath all of it: **parallel agents cannot coordinate**, so
anything two of them would touch is written first, as a file, by the main thread.
After that they can't collide.

## What it installs

| | |
|---|---|
| `home/CLAUDE.md` | working style and the parallelism rules — no stack assumptions |
| `home/settings.json` | opus · high effort · auto mode · 400k compact window · dev-command allowlist · deny rules for `sudo`, `~/.ssh`, `~/.aws`, keychain |
| `home/agents/` | `builder` (one workstream, own files only) · `verifier` (checks, short verdict) |
| `home/skills/` | the six workflow skills, plus graphify, visual-plan, apple-design, eli5, recap, karpathy-guidelines |
| `home/hooks/inject-plan.sh` | `SessionStart` hook — re-injects `PLAN.md` state after a compaction |
| `home/statusline.py` | dir · model · context% · 5h usage% · cost · diff · branch |
| plugin | `frontend-design` from the official marketplace (best effort) |

Flags: `--with-stitch` (Stitch/shadcn/Remotion/design-md skills),
`--no-statusline`.

The workflow skills are all `disable-model-invocation: true`, so their
descriptions stay out of context entirely — they cost nothing until you type them.

## Safety on a borrowed machine

`install.sh` never destroys anything. Existing `CLAUDE.md`, `settings.json`,
same-named skills, agents and hooks are copied to
`~/.claude/.pre-restore-backup-<ts>/` and recorded in `~/.claude/.restore-manifest`.
`settings.json` is *merged* onto theirs, not replaced.

- `./uninstall.sh` — restore the machine to exactly how you found it
- `./cleanup.sh` — logout + uninstall + wipe the transcripts and history your
  session left behind

`permissions.defaultMode` is `auto`: Claude edits files and runs commands without
prompting. That's the point on your own machine; on someone else's, decide
deliberately. Change it to `acceptEdits` in `home/settings.json` if you'd rather
be asked.

## Keeping it current

`./export.sh` pulls your live config back into this repo. Then commit.

## Credits

`skills/karpathy-guidelines` is vendored from
[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) (MIT).
