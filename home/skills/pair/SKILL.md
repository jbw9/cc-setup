---
name: pair
description: Prepare for someone sitting down to pair with you mid-build — land what's in flight, quiesce the agents, and produce a 60-second walkthrough plus candidate tasks to pair on.
disable-model-invocation: true
argument-hint: "[who is joining, optional]"
---

Someone is about to sit down and work with you for a fixed slot. This is not `/brief` — they aren't taking a workstream away, they're going to ask what you've built, why, and where you're headed, then work on something with you.

Run this **before** they arrive, not when they're already sitting there.

## 1. Quiesce

- Land whatever is in flight. Do **not** start a new `/fanout` round.
- Run `/handoff` so `## Status` is current and true.
- Run `./demo.sh`. It must be green. This is what you open with.

**No agents running while you pair.** Three builders mid-flight makes you a spectator to your own project at the exact moment someone is evaluating whether you own it. You want to be the one typing, or the one directing a single focused agent they can watch you steer.

## 2. The walkthrough

Six lines, written to be said out loud in about a minute. Not a document — a script for talking:

```
WHAT IT DOES:  <one sentence, then run ./demo.sh>
THE SHAPE:     <N pieces, and how data moves through them>
WHERE I AM:    <what's done, what's in flight>
WHERE HEADED:  <the next two things, in order>
CLOSEST CALL:  <the one decision from DECISIONS.md most worth raising, with the
                alternative it beat — offer it before they have to dig for it>
KNOWN SOFT:    <the weakest part, named before they find it>
```

Naming the weak part yourself costs nothing and buys a great deal. They will find it regardless; finding it *with* you is a different conversation than finding it *despite* you.

## 3. Nominate what to pair on

Read `PLAN.md` and offer two or three candidates. For each, one line on why. Good ones are:

- **A real tradeoff**, not typing. Something where two approaches are defensible and thinking out loud is the point.
- **Finishable in the slot.** Roughly half of it, so there's room to talk.
- **Off the critical path.** If it goes sideways, the demo is untouched. Never pair on the thing your demo depends on.
- **Not blocked.** Watching you wait is worse than watching you struggle.

Say which one you'd pick and why. Then let them choose — they may want to see something specific, and what they steer toward is information about what they care about.

## 4. During

- Log decisions as they're made: `/decide`, attributed to whoever raised it. A suggestion they push you toward is a decision, and it belongs in the record with their name on it.
- If they propose something you disagree with, say so and give the reason from `DECISIONS.md`. Disagreeing well is the thing being observed.
- Keep `PLAN.md` open. Answering "where are you" from a live artifact beats answering from memory.

## 5. After

- `/decide` anything that came out of the session.
- `/handoff` before resuming — the plan has probably moved.
- Then resume `/fanout`. Re-check the clock in `## Time` first; the slot cost you real minutes and the tier list may need cutting from the bottom.
