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

**Expect three rounds. Two is the floor.** A single round means you assumed rather than asked. This is the highest-leverage phase in the build: a wrong assumption here costs a whole fan-out round to unwind, a question costs thirty seconds. Bias toward asking.

A long project description is **not** the same as answers. Someone can describe a product vividly and still have settled none of the six areas below. Only compress to one gap-filling round when the user hands you a **written brief or plan file** that already names the deadline, the stack, and what is out of scope — a conversation is not that.

Cover, in roughly this order:

1. **Done means what?** The demoable thing at the deadline. Concrete enough to be a command or a click-path.
2. **Stack.** Language, framework, package manager, how to run, how to test. Never assume — this setup carries no stack defaults on purpose.
3. **Explicitly out of scope.** The most valuable answer in the room. Auth, persistence, deploy, responsive, tests — name what is *not* being built.
4. **Given vs. built.** Existing repo, API keys, seed data, design mocks?
5. **How it's judged.** Working demo, code quality, or how you think out loud — this changes what to spend minutes on.
6. **The clock.** Start time, deadline, and any fixed interruptions. Everything downstream is scheduled against these.

State assumptions out loud rather than picking silently. If two readings lead to materially different builds, ask. If a simpler approach exists, say so before planning the complex one.

**The stop test.** Do not leave Phase 1 silently. Walk the six areas and mark each *answered by them* or *assumed by me*, then say the assumed ones out loud in one short block:

```
Answered: done-means, clock, stack
Assuming: no auth · seed data is fine · single user · desktop only
Any of these wrong changes the partition — correct me now or I plan against them.
```

Anything in that list that would change the partition if wrong is a question you still owe. Ask it instead of stopping. Getting this wrong is not recoverable by working harder later: the partition, the contracts, and every builder dispatch all inherit it.

Two specific things to force into the open, because they are the ones that quietly wreck a timed build:

- **The demo's narrative.** Not "a dashboard" — the literal click-path or command sequence you will run in front of someone, in order. If they cannot say it as steps, the scope is not settled yet and no amount of planning fixes that.
- **The one thing that must not be missing.** If everything else got cut, what single capability makes this still worth presenting? That answer sets the top of the tier list, and it is often not what they described first.

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
2. **If the build has a UI, freeze a design contract too.** This is the contract people forget, and its absence is invisible until fan-in: builders cannot see each other, so three of them independently reach for the same default gray scale and the result looks like three apps stapled together — or worse, like nothing, which at a company that cares about design reads as machine-generated on sight.

   Write the tokens as a real file (`globals.css` in a Tailwind project, whatever the stack's equivalent is), semantic names only — surface, raised, border, ink, muted, one accent, plus a named color per domain state. Ten minutes, and it belongs in `## Contracts` beside `types.ts`.

   Then put one line in every UI builder's dispatch: **use only these tokens — no raw palette classes, no hex literals.** A builder that hardcodes `gray-500` has not broken a rule anyone wrote down unless you write it down.

3. Update `## Contracts` in `PLAN.md` with each contract's path. They are frozen from here.
4. Run `/handoff` to write the first `STATUS.md` — Round 0 landed, `demo.sh` green, every workstream a row.
5. Only then `/fanout` for `owner: builder` workstreams, `/brief` for the human ones.

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
Live state is in `STATUS.md` (rewritten by `/handoff`).
```

`PLAN.md` is the **plan** and should barely move after Round 0. Live state — what is happening now, what is left, what has bitten you — lives in `STATUS.md`, because a stable reference and a file that churns every few minutes cannot be the same document without both becoming unreadable.

## Rules

- No feature code before Phase 4, and none in Phase 4 beyond the spine.
- `PLAN.md` outranks anything said in conversation. If they disagree, fix `PLAN.md`.
- Keep it short enough to re-read in full. Every builder reads it, every round.
- If the clock is tight enough that Round 0 doesn't fit, the scope is too big. Cut scope, not the spine.
