---
name: handoff
description: Rewrite STATUS.md — the engineer's live dashboard of what is happening now, what is left, and what has bitten us. Run at every fan-in, before anything risky, and whenever the answer to "where are we" has changed.
disable-model-invocation: false
---

Rewrite `STATUS.md` at the repo root from what is actually true right now. Create it if it does not exist.

`STATUS.md` exists for **one reader: the engineer running this build.** Its only job is that they can answer "what is happening, what is left, and what went wrong" in ten seconds without reading the conversation, scrolling this session, or reconstructing anything from memory. Every rule below follows from that.

**You are the only writer.** Builders never edit this file — they run in parallel and would race each other in it. Their `Decisions:` and `Blocked:` lines come back at fan-in and *you* write them here. If you are tempted to tell a builder to update status, you are about to create the exact collision `/fanout` check #4 prevents.

## Check reality first

Never copy the old file forward. Before writing:

- `git status` and `git log --oneline -5` — what actually landed
- `./demo.sh` — the demo state is a fact, not a memory
- the last verifier verdict
- `## Time` in `PLAN.md` — recompute minutes to freeze

## The shape

Five sections, always in this order, always all present. Overwrite the file; never append.

```markdown
# Status — <project>

Updated: <HH:MM> · Branch: <branch> · Demo: **green** @ <HH:MM> | **BROKEN** — <what>
Clock: <Xh>m elapsed · freeze <HH:MM> (**<N>m left**) · deadline <HH:MM>

---

## Now

**<the one thing being worked on this minute>** — <who>, <which round>.
<one line of context: what is blocked, what is running, or "nothing blocked">

Next: <the single next action after this one>

---

## Todo

<current round name and window>

- [x] <done — checked as it completes>
- [ ] <not done>

At risk if the clock slips: <what gets cut first, from the bottom of the tier list>

---

## State

| WS | name | tier | owner | state | where it stands |
|----|------|------|-------|-------|-----------------|

<one row per workstream in PLAN.md, always, including done ones>
<any numbers worth seeing at a glance>

---

## Gotchas

Things a fresh reader — or you at the deadline — would get wrong:

- **<the stub, the hardcoded value, the swap made under quota>**

---

## Problems log

Real blockers and things that cost real minutes. Not a diary.

| Time | What bit us | Cost | Resolution |
|------|-------------|------|------------|
```

## Rules per section

**Now** — names exactly one thing. If you cannot name a single one, that is the finding: say so rather than listing three. This is the section the engineer reads first and most often.

**Todo** — the current round's checklist, checked off as items complete. Not the whole build; the round. `At risk` is mechanical — read the bottom of the tier list, do not relitigate it.

**State** — one row per workstream in `PLAN.md`, **always, including `done` ones**. A row disappearing is indistinguishable from a workstream being forgotten. `state` is one of exactly five words: `not-started` · `in-progress` · `done` · `blocked` · `cut`. Anything needing a sentence goes in the last column.

**Gotchas** — what someone would get wrong acting on this repo without the conversation. The temporary hack, the hardcoded value, the model swapped under quota, the test that is skipped. This is the highest-value section at hour four.

**Problems log** — append-only, and the one exception to overwriting. A row earns its place if it **blocked something or cost more than ~5 minutes**: a builder hitting a bad contract, an API throttling, a test that would not stabilize, a calibration that had to be redone. Not "renamed a file". A log that becomes a diary stops being read, which costs more than not having one.

## When to rewrite it

- **Every fan-in**, without being asked — this is where builder reports become durable
- Before anything risky, and before a `/pair` slot
- Whenever `Now` stops being true: something starts, finishes, blocks, unblocks
- When `./demo.sh` changes colour
- When something gets cut

Say one line when you do it (`status: NOW is x`), never a paragraph.

## Keep PLAN.md and STATUS.md apart

`PLAN.md` is the **plan** — goal, contracts, workstreams, tiers, the demo path. It is stable and re-read in full; it should barely move after Round 0.

`STATUS.md` is **live state** and churns every few minutes.

Mixing them is what makes both unreadable. If `PLAN.md` still has a `## Status` block, replace its body with a pointer to `STATUS.md` and keep the state here. Update `## Contracts` in `PLAN.md` if a contract changed — that is plan, not status.

Then say in one line what you checkpointed.
