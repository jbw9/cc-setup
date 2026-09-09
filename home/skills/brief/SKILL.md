---
name: brief
description: Generate a self-contained handoff for a human teammate taking a workstream — what to build, which files are theirs, the frozen contracts, and what not to touch.
disable-model-invocation: true
argument-hint: "[workstream id] [who]"
---

Write a handoff a teammate can act on without reading `PLAN.md` and without interrupting you. Include the branch and the commit they should start from, and tell them to pull before they begin and again before they merge: this repo is checkpointed every few minutes, so what they cloned goes stale faster than they will expect. Output it as a single block they can paste into Slack or a branch description.

The partition in `PLAN.md` already solves the human problem too: two engineers editing the same file race exactly the way two agents do. A workstream is a delegation unit whether the owner is `builder` or a person.

## Before writing

1. Confirm the workstream's `owner:` is a person, not `builder`. If it still says `builder`, change it in `PLAN.md` first — otherwise `/fanout` will dispatch an agent onto their files while they work.
2. Confirm the contracts they depend on exist **as files on disk**. Never hand someone a described interface; they will invent a different one, exactly as an agent would.
3. Check their `owns:` globs overlap nothing currently in flight.

## The brief

```markdown
**WS<id> — <name>** · owner: @<them>

**Build:** <what it does, 2-3 sentences, in terms of behavior not implementation>

**Your files** (nobody else touches these):
  <glob>
  <glob>

**Do not touch:** everything else — especially <the contract files>. If one of them
is wrong, message me; don't fix it. Others are coding against it right now.

**Code against:**
  `<path>` — <the type/interface, quoted inline so they don't have to go find it>

**Already decided** (don't relitigate, ask if it blocks you):
  <the 2-4 entries from DECISIONS.md that constrain this workstream>

**Done when:** `<command>` passes.

**Stack:** <language, framework, package manager> · Run: `<cmd>` · Test: `<cmd>`

**Getting it back to me:** branch `ws<id>-<slug>`, push when `done-when` passes.
Don't merge to main — I'm handling integration.

**Out of scope:** <what they should not build, so they don't gold-plate>
```

## Rules

- Self-contained. Every question they'd have to ask you is a minute off the clock for both of you.
- Quote the contract inline. A path alone means they open it, misread it, or guess.
- `Already decided` prevents the most expensive interruption there is — a teammate reopening a settled choice an hour in.
- Say what's out of scope. It is the highest-value line in the brief.
- If they'll drive their own Claude Code on this, tell them to work on their own branch or worktree. Two agents in one working tree collide the same way two builders do, and neither one knows it.

After writing the brief, update `PLAN.md`: set the workstream's `owner:` and mark it `in-progress` in `## Status`.
