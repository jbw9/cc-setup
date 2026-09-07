---
name: kickoff
description: Start a build. Interrogates the request, builds a thin end-to-end slice, derives frozen contracts from working code, then partitions into disjoint workstreams that builders can run in parallel.
disable-model-invocation: true
argument-hint: "[one line on what we're building]"
---

Do not write feature code this turn beyond the spine in Phase 4. Produce a plan good enough that parallel agents can execute it without talking to each other — and a running product before anything gets frozen.

If `$ARGUMENTS` names a file, read it first. Notes taken during a briefing are worth more than anything you'd ask.

## Phase 1 — Interrogate

Ask before you plan. Use `AskUserQuestion`, batched, up to 4 per round. Keep going while the next question would still change what gets built. Stop when it wouldn't.

If the user arrives with answers already — a brief, notes, a conversation they just had — do **one** round targeting genuine gaps only. Re-asking what they already told you is time off the clock.

Cover, in roughly this order:

1. **Done means what?** The demoable thing at the deadline. Concrete enough to be a command or a click-path.
2. **Stack.** Language, framework, package manager, how to run, how to test. Never assume — this setup carries no stack defaults on purpose.
3. **Explicitly out of scope.** The most valuable answer in the room. Auth, persistence, deploy, responsive, tests — name what is *not* being built.
4. **Given vs. built.** Existing repo, API keys, seed data, design mocks?
5. **How it's judged.** Working demo, code quality, or how you think out loud — this changes what to spend minutes on.
6. **The clock.** Start time, deadline, and any fixed interruptions. Everything downstream is scheduled against these.

State assumptions out loud rather than picking silently. If two readings lead to materially different builds, ask. If a simpler approach exists, say so before planning the complex one.

## Phase 2 — Draft the partition

Draft into the harness plan file. **Plan mode allows no other writes** — nothing lands yet. Design against the schema in Phase 6.

1. List everything that must exist.
2. Identify the **spine**: the thinnest path that touches every layer of the system. One record in, one result out, one thing on screen. That is Phase 4, and it is yours alone.
3. Pull out everything two pieces of work would both touch — shared types, API shapes, schema, config, route table. That is your `## Contracts` section. Mark them **provisional**; Phase 5 freezes them.
4. Partition the remaining breadth into workstreams with **no overlapping files**. Check glob by glob: if a path could match two workstreams, the partition is wrong.
5. If two workstreams still collide, the collision is a contract. Move it up and re-partition.
6. Give each workstream a `done-when` that is a command someone can run.
7. Tier every workstream **MUST / SHOULD / CUT**. At freeze time you cut mechanically, from the bottom, without relitigating.

Sequence honestly: a workstream needing another's output isn't parallel. Mark it `blocked-by` and run it next round.

Two to three agent workstreams per round. Set an `owner:` on each — `builder`, `me`, or `@name`. Human-owned workstreams don't count against the concurrency cap; they cost a `/brief`, not context.

## Phase 3 — Exit and land the plan

Call `ExitPlanMode`. Once approved, in this order:

1. Write `PLAN.md` to the repo root, matching the schema below. Fill in `## Time` from the clock answers.
2. Write the project `CLAUDE.md`, first line exactly:
   `The authoritative plan is PLAN.md. Read it before doing anything.`
   Then stack, run/test commands, and conventions. Subagents inherit `CLAUDE.md` but not your conversation — this file plus `PLAN.md` is all they will know.
3. Write `DECISIONS.md`, seeded with the choices already made in Phase 1 — stack, storage, what was cut for time. Every one needs the alternative it beat. See `/decide`.

Contracts are **not** written yet. That is deliberate.

## Phase 4 — Round 0: build the spine

Serial. Main thread only. **No fan-out.** Budget roughly a sixth of the total clock.

Build the thinnest path that runs end to end. One hardcoded input → one real transformation → one endpoint → one thing rendered. Fake everything you can get away with: hardcode the record, stub the store, one of each thing. It should be embarrassing and it should work.

Then write **`demo.sh`** at the repo root: the exact sequence you would run in front of an audience. Start it, hit it, show the output. Make it exit non-zero when the path is broken.

Round 0 is done when `./demo.sh` passes and you could stand up and show it. Log it: `/decide` the stack and shape choices the spine just settled.

This costs serial time and buys two things worth more than that time:

- **Contracts stop being guesses.** You are about to freeze interfaces that running code already uses.
- **You are demoable from here on.** Every round after only improves it. If the day collapses at any point past this, you still have something to present.

## Phase 5 — Freeze the contracts, then fan out

1. **Derive the contracts from the spine.** Read what Phase 4 actually wrote — the real types, the real response shapes, the real function signatures. Lift them into their own files. This is the step the whole partition rests on: a builder coding against a described interface invents a different one; a builder coding against a file agrees by construction.
2. Update `## Contracts` in `PLAN.md` with each contract's path. They are frozen from here.
3. Note in `## Status` that Round 0 landed and `demo.sh` is green.
4. Only then `/fanout` for `owner: builder` workstreams, `/brief` for the human ones.

A builder that hits a bad contract reports it upward. You change it here, in the main thread, never them.

## Phase 6 — PLAN.md schema

```markdown
# <project>

## Goal
<the demoable thing, one paragraph>

## Time
Started: <HH:MM> · Deadline: <HH:MM> · Freeze: <deadline − 45m>
Fixed points: <e.g. pairing 13:00, present 16:00>

## Constraints
Judged on: · Out of scope:

## Stack
Language/framework/package manager · Run: `cmd` · Test: `cmd` · Build: `cmd`

## Demo path
<the exact sequence you will run in front of an audience — materialized as `demo.sh`>
1. <step>
2. <step>
Last green: <round or time>

## Contracts
<types, signatures, API shapes — and the file each lives in.
 Provisional until Round 0 lands; frozen after.>

## Workstreams
### WS1 <name>
tier:       MUST | SHOULD | CUT          <- cut from the bottom at freeze
owner:      builder | me | @<teammate>   <- /fanout only dispatches `builder`
owns:       src/api/**, src/db/schema.ts <- exclusive; no glob appears twice
depends:    Contracts §A
blocked-by: —
done-when:  `pnpm test api` passes

### WS2 <name>
...

## Integration
<what only the main thread does: wiring, the parts that cross workstreams>

## Status
<one line per workstream: not-started | in-progress | done | blocked>
<this block is what gets re-injected after a compaction — keep it current and true>
```

## Rules

- No feature code before Phase 4, and none in Phase 4 beyond the spine.
- `PLAN.md` outranks anything said in conversation. If they disagree, fix `PLAN.md`.
- Keep it short enough to re-read in full. Every builder reads it, every round.
- If the clock is tight enough that Round 0 doesn't fit, the scope is too big. Cut scope, not the spine.
