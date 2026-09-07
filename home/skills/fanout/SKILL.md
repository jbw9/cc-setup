---
name: fanout
description: Dispatch parallel builders for the ready workstreams in PLAN.md, then verify, read back what landed, and update status. Use after kickoff has frozen the contracts.
disable-model-invocation: true
argument-hint: "[workstream ids, or blank for all ready]"
---

Dispatch builders for the workstreams named in `$ARGUMENTS`, or every ready workstream if none given.

## Check before dispatching — all five

1. **`PLAN.md` exists** at the repo root with a `## Workstreams` section. If not, run `/kickoff` instead.
2. **Round 0 landed.** `./demo.sh` exists and passes. Fanning out before the spine runs means freezing contracts that are still guesses — that is the failure this setup is shaped to avoid. If there is no spine yet, go back to `/kickoff` Phase 4.
3. **Contracts are on disk.** Every file named in `## Contracts` exists and holds real types derived from the spine. If any is missing, write it now, in this thread, before dispatching.
4. **No shared files.** Compare the `owns:` globs of the workstreams you're about to dispatch. Any overlap — even one path matching two globs — means separate rounds, not together.
5. **At most 3 concurrent.** Builders inherit Opus. Beyond three the wall-clock gain flattens and the 5-hour limit gets real. If the usage meter is past two thirds, drop to two, or set `model: sonnet` in `agents/builder.md` for mechanical workstreams.

**Dispatch only `owner: builder` workstreams.** One owned by `me` or a teammate is off limits — sending an agent into a human's files while they work is the same race, and they can't see it coming. Use `/brief`.

Skip anything whose `blocked-by` isn't satisfied. Next round.

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
2. Dispatch one `verifier` for the whole tree — not per workstream. Short verdict back, raw output stays out of this context.
3. **Run `./demo.sh`.** A green typecheck with a broken demo path is the worst state to be in, because it looks fine. If the demo broke, that is the only thing that matters this round — fix it before anything else and say so plainly.
4. **Read back what actually landed.** For each builder, read its diff and give the user at most ten lines: the files it wrote, the choices it made, and anything that differs from what the plan implied. This is not optional and not a formality — it is the only point where agent-written code enters a human's head. Code nobody has read cannot be explained later, and by then it is too late to learn it.
5. Update `## Status` in `PLAN.md`. Real state only. Update `Last green` under `## Demo path`.
6. **Harvest the `Decisions:` lines** from every builder report into `DECISIONS.md` (see `/decide`). This is the only moment they exist — each was made in a context that is now gone, and unrecorded they become choices in the codebase nobody can explain. Fill in `Costs us:` and `At scale:` yourself; the builder won't have.
7. **Commit if the tree is green.** `git add -A && git commit` with a message naming the workstreams that landed. On a timed build this is not bookkeeping: it is the rollback point that makes the next round safe to attempt, and the log doubles as a record of the order things were built in.
8. Handle the fallout **in the main thread**:
   - **BLOCKED on a contract** → decide the change yourself, edit the contract file, note it in `PLAN.md`, re-dispatch affected workstreams. Never let a builder renegotiate a contract.
   - **FAIL** → read the verifier's evidence. Small and inside one workstream: re-dispatch that builder with the error. Crosses workstreams: fix it here.
   - **Integration work** is always yours.
9. Report to the user: what landed, what failed, what's next, and time remaining against `## Time`. Then stop — don't auto-start the next round.

If a builder reports a pass the verifier contradicts, believe the verifier. If the verifier passes and `demo.sh` doesn't, believe `demo.sh`.

## After the freeze time

Past `Freeze:` in `## Time`, stop dispatching builders. What remains is integration, demo rehearsal, reading anything still unread, and backfilling `DECISIONS.md`. A workstream that isn't done by then is a `CUT` — say so out loud and move it, rather than gambling the demo on it.
