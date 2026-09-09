---
name: pair
description: Prepare for someone sitting down to pair with you mid-build — land what's in flight, quiesce the agents, and produce a 60-second walkthrough plus candidate tasks to pair on.
disable-model-invocation: true
argument-hint: "[who is joining, optional]"
---

First, make sure they can actually see your work: commit anything outstanding and, if they are on their own clone rather than a worktree here, push. The `wip:` checkpoints keep this close to true on their own, but "close to true" is not what you want at the moment someone starts reading your code. Tell them the branch and the last commit.

Someone is about to sit down and work with you for a fixed slot. This is not `/brief` — they aren't taking a workstream away, they're going to ask what you've built, why, and where you're headed, then work on something with you.

Run this **before** they arrive, not when they're already sitting there.

## 1. Quiesce

- Land whatever is in flight. Do **not** start a new `/fanout` round.
- Run `/handoff` so `STATUS.md` is current and true.
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
- Keep `STATUS.md` open. Answering "where are you" from a live artifact beats answering from memory — and it beats scrolling this conversation, which is the failure mode that file exists to prevent.

**Keep it true without being asked.** During a pairing slot, rewrite `STATUS.md` — at minimum the `Now` / `Next` lines — whenever any of these happen:

- a task is finished, started, or handed to one of you
- something becomes blocked, or unblocks
- `./demo.sh` changes colour
- you agree to cut something

Say one line when you do it (`board updated — NOW: x`), never a paragraph. The cost is a few seconds; the thing it buys is that neither of you ever has to reconstruct state from memory in front of someone evaluating you.

**Delegating during the slot.** Two of you and one repo is the same race as two builders. Split by file, not by feature:

- **They take a slice you name by path**, exactly like a workstream — `owns:` globs, a `done-when` command, contracts frozen. If it is more than a few minutes of work, `/brief` it properly rather than describing it out loud.
- **You keep integration and anything crossing files.** Same rule as `/fanout`: integration is never delegated.
- **Never both in one file.** If you both need it, it is a contract — you write it, in front of them, before either of you moves.
- **At most one agent running, and only one you are actively steering.** A background `/fanout` round during a pairing slot means neither of you owns what lands.

Add a row to the board for anything they take, with `owner:` set to their name. A task that is not on the board is a task one of you will drop.

## 5. After

- `/decide` anything that came out of the session.
- `/handoff` before resuming — the plan has probably moved.
- Then resume `/fanout`. Re-check the clock in `## Time` first; the slot cost you real minutes and the tier list may need cutting from the bottom.
