---
name: handoff
description: Rewrite STATUS.md — the engineer's live dashboard of what is happening now, what is left, and what has bitten us. Run at every fan-in, before anything risky, and whenever the answer to "where are we" has changed.
disable-model-invocation: false
---

Rewrite `STATUS.md` at the repo root from what is actually true right now. Create it if it does not exist.

`STATUS.md` exists for **one reader: the human engineer running this build.** Its only
job is that they can answer "what is happening, what is left, and what went wrong"
in ten seconds without reading the conversation, scrolling this session, or
reconstructing anything from memory. Every rule below follows from that.

**You are the only writer.** Builders never edit this file — they run in parallel and would race each other in it. Their `Decisions:` and `Blocked:` lines come back at fan-in and *you* write them here. If you are tempted to tell a builder to update status, you are about to create the exact collision `/fanout` check #4 prevents.

## Write it for a human, not for an agent

This is the rule most often broken, and breaking it makes the file useless at
hour four — which is exactly when it matters most.

- **Never refer to a workstream by its ID alone.** "WS5 landed" tells the reader
  nothing. Name the thing: "the printable coaching report is done." IDs may appear
  in the state table as a lookup column, never as the way a sentence identifies work.
- **Write sentences, not fragments.** "Editor round-trip verified end to end" is a
  note to yourself from an hour ago that you will not decode. "You can edit the
  action items, save, reload, and the edits are still there" survives.
- **Expand jargon on first use, or drop it.** Tier names, internal shorthand, and
  library names that only make sense with the code open all need a clause of
  context. If a sentence only parses for someone who just read the diff, rewrite it.
- **Explain what the project does**, briefly, near the top. The reader may have been
  away for two hours, or may be presenting this to someone else in ten minutes.
- **Say why, not just what.** "Switched to the built-in SQLite" is a fact.
  "Switched to the built-in SQLite because the other one crashed the process" is
  usable.

Length is not the enemy — density of unexplained references is. A status file that
takes two minutes to read and leaves the reader oriented beats a terse one that
leaves them reconstructing.

## Check reality first

Never copy the old file forward. Before writing:

- `git status` and `git log --oneline -5` — what actually landed
- `./demo.sh` — the demo state is a fact, not a memory
- the last verifier verdict
- `## Time` in `PLAN.md` — recompute minutes to freeze

## The shape

Seven sections, always in this order, always all present. Overwrite the file; never append.

```markdown
# Status — <project>

**Updated <HH:MM> · branch <branch> · <tree state> · demo <green|BROKEN> at <HH:MM>**
**Clock: started <HH:MM>, <N>h in. Freeze <HH:MM> (~<N>m left). Deadline <HH:MM>.**

---

## Where the project is right now

**<the one thing being worked on this minute, in a full sentence>**
<what is blocked, what is running, or plainly "nothing is blocked">

<a short paragraph a returning reader can act on: what works end to end today>

**The single next thing to do:** <one action>

---

## What the app actually does

<3–6 numbered steps describing the real flow through the system, in plain language.
Someone who has never seen the code should be able to follow it. Name the one design
choice most likely to be questioned, and say why it was made.>

---

## What is done, and what is left

**Done — <category>:**
- <named features, not IDs>

**Left:**
- [ ] **<label>:** <what it is, how long, and whether it is worth doing>

**If time runs short**, <what gets cut first, and what is not at risk>

---

## <Domain-specific table — the numbers worth seeing at a glance>

<Whatever this project's "am I winning" number is: the queue, the pass rate, the
benchmark. Include it if it exists; skip the section if it genuinely does not.>

---

## Things that will trip you up

<Was "Gotchas". Each entry is a full sentence explaining the trap AND the
consequence of hitting it. Bold the trap, then explain.>

---

## What went wrong along the way

| Time | What happened | Lost | How it was fixed |
|------|---------------|------|------------------|
```

A state table with one row per workstream is still worth keeping when a build has
more than three or four of them — put it under "What is done", with the
human-readable name first and the ID last, as a lookup column. When there are only
a handful, prose is better.

## Rules per section

**Where the project is right now** — names exactly one thing. If you cannot name a single one, that is the finding: say so rather than listing three. This is the section the engineer reads first and most often. The paragraph under it is what makes the file survivable after a long break.

**What the app actually does** — the section that makes this file readable by someone other than you, including you-in-two-hours. Rewrite it only when the system's shape actually changes; it is the most stable section in the file.

**What is done, and what is left** — named features, checked off as they complete. `If time runs short` is mechanical — read the bottom of the tier list, do not relitigate it.

**Things that will trip you up** — what someone would get wrong acting on this repo without the conversation. The temporary hack, the hardcoded value, the model swapped under quota, the test that is skipped. This is the highest-value section at hour four, and the one where terseness costs the most: say what breaks, not just what is unusual.

**What went wrong along the way** — append-only, and the one exception to overwriting. A row earns its place if it **blocked something or cost more than ~5 minutes**: a builder hitting a bad contract, an API throttling, a test that would not stabilize, a calibration that had to be redone. Not "renamed a file". A log that becomes a diary stops being read, which costs more than not having one. These rows are also the war stories worth being able to tell in a review.

## When to rewrite it

- **Every fan-in**, without being asked — this is where builder reports become durable
- Before anything risky, and before a `/pair` slot
- Whenever the current focus stops being true: something starts, finishes, blocks, unblocks
- When `./demo.sh` changes colour
- When something gets cut

Say one line when you do it (`status: now working on x`), never a paragraph.

## Keep PLAN.md and STATUS.md apart

`PLAN.md` is the **plan** — goal, contracts, workstreams, tiers, the demo path. It is stable and re-read in full; it should barely move after Round 0.

`STATUS.md` is **live state** and churns every few minutes.

Mixing them is what makes both unreadable. If `PLAN.md` still has a `## Status` block, replace its body with a pointer to `STATUS.md` and keep the state here. Update `## Contracts` in `PLAN.md` if a contract changed — that is plan, not status.

Then say in one line what you checkpointed.
