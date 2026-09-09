# How I work

## Build workflow
`/kickoff` → spine → `/fanout` → `/defend`. Plan, prove it end to end, partition,
dispatch, verify, log why.

- `PLAN.md` at the repo root is authoritative. Where it and the conversation
  disagree, re-read it and fix it — don't trust recall.
- **Build the spine before the breadth.** The thinnest path through every layer,
  serial, before any fan-out. Contracts derived from running code aren't guesses,
  and from that point on there is always something demoable.
- `demo.sh` is the product's heartbeat. It runs at every fan-in. A green
  typecheck with a broken demo path is the worst state to be in, because it
  looks fine.
- `DECISIONS.md` records every non-obvious choice **as it is made**, with the
  option it beat, the cost accepted, and where it breaks at scale. `/decide`.
- Checkpoint with `/handoff` before a long fan-out or anything risky.
- `/pair` before someone joins, `/scale` for the production story, `/defend`
  before presenting.

## Parallel work
Two agents editing one file race, and neither can see the other.

- Shared things are **contracts**: write them as real files, in the main thread,
  before dispatching anyone. Never hand out a described interface.
- Every workstream owns a disjoint set of globs. If two need the same file, that
  file is a contract, not a workstream.
- Contracts are frozen during a round. A builder that hits a bad one reports it;
  I change it here.
- Max 3 concurrent builders (they inherit Opus). Watch the 5h usage meter.
- Never dispatch an agent onto a workstream a human owns. `/brief` instead.

## Code I have to defend
Agents produce more code than I can absorb, and unread code cannot be explained
later — by then it's too late to learn it.

- **Read back what every builder wrote** at fan-in. Files touched, choices made,
  anything that diverges from the plan. Ten lines is enough; skipping it isn't.
- Anything surprising in that diff becomes a `/decide` entry immediately.
- Never present code nobody has read. Under questioning the difference between
  "I built this" and "an agent built this" is obvious within two follow-ups.

## Working style
- Act when you have enough to act. Don't re-ask what I've answered or re-litigate
  a settled decision.
- Make routine calls yourself. Ask when two readings produce materially different
  builds — during planning, not mid-build.
- Finish the whole task. If part is blocked, do the rest and say what you skipped.
- Report failures with the real output. Never claim a check passed that you didn't
  run. A truthful failure costs less than a false pass.
- On a clock: cut from the bottom of the tier list, mechanically, and say what
  got cut. Never quietly ship less than was planned.

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
- No `git push` unless I ask (`CC_CHECKPOINT_PUSH=1` is me asking, standing).
- Committing is different, and there are two kinds:
  - **Green commits.** After every green fan-in round, when `PLAN.md` has a
    `## Time` block. These are the rollback points that make the next round safe
    to attempt. `/fanout` makes them; write a real message naming the workstreams.
  - **`wip:` checkpoints.** The `Stop` hook commits the tree every ~10 minutes so
    that anyone pulling this repo is working on current files. It is automatic —
    don't make them by hand, don't clean them up mid-build, and don't treat one
    as evidence anything passed. Rollback points are
    `git log --grep='^wip:' --invert-grep`.
- A checkpoint appearing in the middle of your work is expected, not a conflict.
  If one committed something it shouldn't have, say so — don't rewrite history
  during a timed build.
