---
name: scale
description: Produce the production-at-larger-scale answer from what was actually built — what breaks first, at what volume, and what replaces it. Reads DECISIONS.md and the code.
disable-model-invocation: true
---

Write `SCALE.md` at the repo root: how this same problem gets solved in production, at a scale this build deliberately ignored.

This is the question that follows every demo of a timed build, and it is graded like a systems-design interview. The advantage you have is that you wrote the ingredients down as you went — every `At scale:` line in `DECISIONS.md` is one piece of this answer, recorded when the tradeoff was fresh rather than reconstructed under questioning.

## 1. Reconstruct

Read `DECISIONS.md` — especially the `At scale:` and `Costs us:` lines — then `PLAN.md`, then the code that actually shipped. Where a decision has no `At scale:` line, work it out now and backfill the entry.

## 2. Write it

```markdown
# Scaling this

## What breaks first
<ordered list. Each: the component, the volume where it stops working, and the
 symptom you'd see. Ordered by which one you'd hit soonest, not which is most
 interesting.>

## The production shape
<what replaces each broken piece, and why that specific replacement. One
 paragraph per piece, tied to the break it fixes.>

## What survives
<the parts that were right at any scale. Say why — this is where the design
 judgment shows, and it is shorter and more convincing than the rewrite list.>

## Cost shape
<what dominates the bill at 1000×, and the one change with the largest effect
 on it.>

## What I'd measure
<the metrics that tell you which break is coming before it arrives.>

## What I'd do first with another week
<one thing. The honest one.>
```

## Rules

- **Every claim traces to this build.** "We'd add a queue" is worthless; "the transform is synchronous inside the request handler, so past roughly N concurrent uploads the p99 is the transform time — that moves to a worker behind a queue" is an answer.
- **Name volumes.** Requests/sec, rows, GB/day, concurrent users. A break with no number attached is a guess wearing a suit.
- **Ordering beats architecture.** Knowing what fails first is the signal. A beautiful diagram with the bottlenecks in the wrong order reads worse than a plain list in the right one.
- **Don't design what you can't explain in three minutes.** Every box you draw is a box you can be asked about.
- **Keep what you got right.** A scale story that rewrites everything implies the original had no judgment in it.
- Where the honest answer is "I don't know where this breaks, I'd measure it," write that. It is a better answer than a fabricated number and it is the one an experienced engineer actually gives.
