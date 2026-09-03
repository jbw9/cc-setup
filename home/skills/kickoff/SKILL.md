---
name: kickoff
description: Start a build. Interrogates the request until nothing material is ambiguous, then writes PLAN.md with frozen contracts and disjoint workstreams that builders can run in parallel.
disable-model-invocation: true
argument-hint: "[one line on what we're building]"---

Do not write code this turn. Produce a plan good enough that parallel agents can execute it without talking to each other.

## Phase 1 — Interrogate (do this first, always)

Ask before you plan. Use `AskUserQuestion`, batched, up to 4 per round. At least one round; keep going while the next question would still change what gets built. Stop when it wouldn't.

Cover, in roughly this order:

1. **Done means what?** The demoable thing at the deadline. Get it concrete enough to be a command or a click-path.
2. **Stack.** Language, framework, package manager, how to run, how to test. Never assume — this setup carries no stack defaults on purpose.
3. **Explicitly out of scope.** The most valuable answer in the room. Auth, persistence, deploy, responsive, tests — name what is *not* being built.
4. **Given vs. built.** Existing repo, API keys, seed data, design mocks?
5. **How it's judged.** Working demo, code quality, or how you think out loud — this changes what to spend minutes on.

State your assumptions out loud rather than picking silently. If two readings of the request lead to materially different builds, ask — don't choose. If a simpler approach exists, say so before planning the complex one.

## Phase 2 — Draft

Draft into the harness plan file. **Plan mode allows no other writes** — `PLAN.md` cannot exist yet. Design against the schema in Phase 4.

The hard part is the partition. Work it in this order:

1. List everything that must exist.
2. Pull out everything two pieces of work would both touch — shared types, API shapes, schema, config, route table. That is your `## Contracts` section.
3. Partition the rest into workstreams with **no overlapping files**. Check glob by glob: if a path could match two workstreams, the partition is wrong.
4. If two workstreams still collide, the collision is a contract. Move it up and re-partition.
5. Give each workstream a `done-when` that is a command someone can run.

Sequence honestly: a workstream that needs another's output isn't parallel. Mark it `blocked-by` and run it in the next round.

Two to three agent workstreams per round. Builders run on Opus — more than three in flight is slow and burns the 5-hour limit.

Set an `owner:` on each. A workstream is a delegation unit regardless of who executes it: `builder` for an agent, `@name` for a teammate, `me` for work you're keeping. Human-owned workstreams don't count against the concurrency cap — they cost you a `/brief`, not context. Give a teammate the workstream with the cleanest contract boundary and the least coupling to what you're doing live; keep integration for yourself.

## Phase 3 — Exit and land the plan

Call `ExitPlanMode`. Once approved, in this order:

1. Write `PLAN.md` to the repo root, matching the schema below.
2. Write the project `CLAUDE.md`, first line exactly:
   `The authoritative plan is PLAN.md. Read it before doing anything.`
   Then stack, run/test commands, and conventions. Subagents inherit `CLAUDE.md` but not your conversation — this file plus `PLAN.md` is all they will know.
3. **Write the contracts as real files.** Types, interfaces, signatures, stubs — real code on disk, in the main thread, before any fan-out. Builders coding against a described contract will each invent a different one; builders coding against a file agree by construction.
4. Write `DECISIONS.md`, seeded with the choices already made during Phase 1 — stack, storage, what was cut for time. Every one needs the alternative it beat. See `/decide`.
5. Only then `/fanout` for `owner: builder` workstreams, `/brief` for the human ones.

## Phase 4 — PLAN.md schema

```markdown
# <project>

## Goal
<the demoable thing, one paragraph>

## Constraints
Deadline: · Judged on: · Out of scope:

## Stack
Language/framework/package manager · Run: `cmd` · Test: `cmd` · Build: `cmd`

## Contracts
<types, signatures, API shapes — and the file each lives in. Frozen once fan-out starts.>

## Workstreams
### WS1 <name>
owner:      builder | me | @<teammate>       <- who does it; /fanout only dispatches `builder`
owns:       src/api/**, src/db/schema.ts     <- exclusive; no glob appears twice
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

- No code this turn beyond the contract files in Phase 3.
- `PLAN.md` outranks anything said in conversation. If they disagree, fix `PLAN.md`.
- Keep it short enough to re-read in full. It is read by every builder, every round.
