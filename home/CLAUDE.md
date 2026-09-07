# How I work

## Build workflow
`/kickoff` → `/fanout` → `/defend`. Plan, partition, dispatch, verify, log why.

- `PLAN.md` at the repo root is authoritative. Where it and the conversation
  disagree, re-read it and fix it — don't trust recall.
- `DECISIONS.md` records every non-obvious choice **as it is made**, with the
  option it beat and the cost accepted. `/decide`.
- Checkpoint with `/handoff` before a long fan-out or anything risky.

## Parallel work
Two agents editing one file race, and neither can see the other.

- Shared things are **contracts**: write them as real files, in the main thread,
  before dispatching anyone. Never hand out a described interface.
- Every workstream owns a disjoint set of globs. If two need the same file, that
  file is a contract, not a workstream.
- Contracts are frozen during a round. A builder that hits a bad one reports it;
  I change it here.
- Max 3 concurrent builders (they inherit Opus).
- Never dispatch an agent onto a workstream a human owns. `/brief` instead.

## Working style
- Act when you have enough to act. Don't re-ask what I've answered or re-litigate
  a settled decision.
- Make routine calls yourself. Ask when two readings produce materially different
  builds — during planning, not mid-build.
- Finish the whole task. If part is blocked, do the rest and say what you skipped.
- Report failures with the real output. Never claim a check passed that you didn't
  run. A truthful failure costs less than a false pass.

## Code
- Match the surrounding file's conventions over any general rule.
- Minimum code that solves the problem. No speculative abstractions, no
  configurability nobody asked for, no error handling for impossible cases.
- Surgical edits: don't improve adjacent code, don't refactor what isn't broken.
  Clean up only what your own change orphaned.
- Comments explain why, never what, and only when non-obvious.

## Don't
- No stack assumptions — every project declares its own in `PLAN.md`.
- No README, CHANGELOG, or docs unless asked.
- No new dependencies without asking.
- No `git commit` or `git push` unless I ask.
