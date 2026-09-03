---
name: fanout
description: Dispatch parallel builders for the ready workstreams in PLAN.md, then verify and update status. Use after kickoff has written the contracts.
disable-model-invocation: true
argument-hint: "[workstream ids, or blank for all ready]"---

Dispatch builders for the workstreams named in `$ARGUMENTS`, or every ready workstream if none given.

## Check before dispatching — all four

1. **`PLAN.md` exists** at the repo root and has a `## Workstreams` section. If not, run `/kickoff` instead.
2. **Contracts are on disk.** Every file named in `## Contracts` exists and holds real types. If any is missing, write it now, in this thread, before dispatching. This is the step that makes parallelism safe; skipping it is how you get three incompatible implementations.
3. **No shared files.** Compare the `owns:` globs of the workstreams you're about to dispatch. Any overlap — even one path matching two globs — means you dispatch them in separate rounds, not together.
4. **At most 3 concurrent.** Builders inherit Opus. Beyond three the wall-clock gain flattens and the 5-hour limit gets real.

**Dispatch only `owner: builder` workstreams.** One owned by `me` or a teammate is off limits — sending an agent into a human's files while they work is the same race, and they can't see it coming. Use `/brief` to hand those off.

Skip anything whose `blocked-by` isn't satisfied. It goes in the next round.

## Dispatch

One `builder` agent per workstream, all in a single message so they run concurrently.

Each prompt is short and names things by path — never restate the task in prose:

```
Implement WS<id> from /abs/path/to/PLAN.md.
Read the plan, your workstream, and the ## Contracts section first.
Write only inside your owns: globs. Contracts are frozen.
Finish by running your done-when and reporting its real output.
```

The builder reads its own instructions from `PLAN.md`. Your paraphrase can only introduce drift.

## Fan in

1. Collect the reports. For each: PASS, FAIL, or BLOCKED.
2. Dispatch one `verifier` for the whole tree — not per workstream. It runs the checks and hands back a short verdict, keeping the raw output out of this context.
3. Update `## Status` in `PLAN.md`. Real state only.
4. **Harvest the `Decisions:` lines** from every builder report into `DECISIONS.md` (see `/decide`). This is the only moment they exist — each was made in a context that is now gone, and unrecorded they become choices in the codebase nobody can explain. Fill in `Costs us:` yourself; the builder won't have.
5. Handle the fallout **in the main thread**:
   - **BLOCKED on a contract** → decide the contract change yourself, edit the contract file, note it in `PLAN.md`, and re-dispatch affected workstreams. Never let a builder renegotiate a contract.
   - **FAIL** → read the verifier's evidence. Small and inside one workstream: re-dispatch that builder with the error. Crosses workstreams: fix it here.
   - **Integration work** is always yours.
6. Report to the user: what landed, what failed, what's next. Then stop — don't auto-start the next round.

If a builder reports a pass the verifier contradicts, believe the verifier.
