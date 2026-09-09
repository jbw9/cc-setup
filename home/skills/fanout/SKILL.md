---
name: fanout
description: Dispatch parallel builders for the ready workstreams in PLAN.md, then verify, read back what landed, and update status. Use after kickoff has frozen the contracts.
disable-model-invocation: false
argument-hint: "[workstream ids, or blank for all ready]"
---

Dispatch builders for the workstreams named in `$ARGUMENTS`, or every ready workstream if none given.

## Starting a round without being asked

You may start the next round yourself once the previous one is fully closed out. "Closed out" means all of: the verifier passed, `./demo.sh` is green, **you have read back every builder's diff to the user**, `DECISIONS.md` and `STATUS.md` are current, and the tree is committed. Chaining rounds while any of that is outstanding is the one thing this skill exists to prevent — unread code piles up at agent speed and by the deadline the user is presenting work nobody has read.

Say which workstreams you are dispatching and why, in one line, before you do it. The user can always stop you; they cannot un-read a round they never saw.

**Never self-invoke when** any of these is true — say what you would do and wait:

- the previous round left a FAIL, a BLOCKED, or an unresolved contract change
- `./demo.sh` is red
- you are past `Freeze:` in `## Time`
- the round would dispatch a workstream whose tier is `CUT`, or one owned by a human
- the user is mid-conversation about something else, or has just asked a question

## Check before dispatching — all five

1. **`PLAN.md` exists** at the repo root with a `## Workstreams` section. If not, run `/kickoff` instead.
2. **Round 0 landed.** `./demo.sh` exists and passes. Fanning out before the spine runs means freezing contracts that are still guesses — that is the failure this setup is shaped to avoid. If there is no spine yet, go back to `/kickoff` Phase 4.
3. **Contracts are on disk.** Every file named in `## Contracts` exists and holds real types derived from the spine. If any is missing, write it now, in this thread, before dispatching.
4. **No shared files.** Compare the `owns:` globs of the workstreams you're about to dispatch. Any overlap — even one path matching two globs — means separate rounds, not together.
5. **At most 3 concurrent** — and two is often better than three. The third workstream is usually the one with the muddiest boundary, and it pays you back as integration work, which is serial and yours. Fewer, larger, cleaner-edged workstreams beat more of them.

## Which builder

- `builder` (Opus) — novel logic, anything where the plan leaves a judgment call, the workstream you'd struggle to specify precisely.
- `builder-fast` (Sonnet) — mechanical breadth against a frozen contract: CRUD, wiring, rendering a known shape, boilerplate. Materially faster wall-clock, and the contract is doing the thinking.

Route by how well-specified the workstream is, not by how important it is. A `MUST`-tier workstream that is completely pinned down by its contract is a `builder-fast` job. If `/usage` is past two thirds with a third of the clock left, route everything you can to `builder-fast`.

**`builder-fast` is the default.** Reach for `builder` only when you can name the judgment call the plan leaves open — an algorithm to choose, a schema shape to design, a tradeoff nobody has settled. If you can't name it in one line, the workstream is mechanical and the contract is doing the thinking: route it fast. On a timed build the default is what runs when you don't have time to deliberate, so it should be the cheap one.

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

**For any workstream that renders UI, append these lines verbatim.** They are constraints, not taste, and they have to travel in the dispatch: a builder cannot see the other builders' output, so "make it look consistent" is unactionable while "use these tokens" is checkable.

```
Use only the design tokens in <path>. No raw palette classes (gray-500, etc.),
no hex literals outside that file.
Avoid the tells: no ALL-CAPS letter-spaced eyebrow labels; no metadata strings
joined with " · "; not every element on the same border-radius; one accent
colour, used sparingly. Vary weight and size for hierarchy instead.
Write real empty, loading and error states — never a bare spinner or blank div.
```

Two of those — the uppercase eyebrow and the middle-dot join — are the fastest visual giveaways that a screen was generated rather than designed, and they are exactly what a builder reaches for when the plan says "show the metadata".

**While the round runs, the user is not idle.** This is the window for reading the *previous* round's diff, writing the `/decide` entries that got skipped, and rehearsing `./demo.sh`. Say so when you dispatch — the serial work is the build's real ceiling, and this is the only time it overlaps with anything.

## Fan in

1. Collect the reports. For each: PASS, FAIL, or BLOCKED.
2. Dispatch one `verifier` for the whole tree — not per workstream. Short verdict back, raw output stays out of this context.
3. **Run `./demo.sh`.** A green typecheck with a broken demo path is the worst state to be in, because it looks fine. If the demo broke, that is the only thing that matters this round — fix it before anything else and say so plainly.
4. **Read back what actually landed, and stop here.** For each builder, read its diff and give the user at most ten lines: the files it wrote, the choices it made, and anything that differs from what the plan implied. This is not optional and not a formality — it is the only point where agent-written code enters a human's head. Code nobody has read cannot be explained later, and by then it is too late to learn it.

   **This is the pause in the loop.** Whatever else is automatic, the round does not continue past the read-back until the user has actually seen it. If they have not responded to it, do not start the next round — a round they did not read is a round they cannot defend, and rounds land faster than anyone reads.
5. **Run `/handoff`** to rewrite `STATUS.md`. Real state only. Roll every builder's `Blocked:` line and anything that cost real minutes into the problems log — this is the only moment those are recoverable. Update `Last green` under `## Demo path` in `PLAN.md`.
6. **Harvest the `Decisions:` lines** from every builder report into `DECISIONS.md` (see `/decide`). This is the only moment they exist — each was made in a context that is now gone, and unrecorded they become choices in the codebase nobody can explain. Fill in `Costs us:` and `At scale:` yourself; the builder won't have.
7. **Commit if the tree is green.** `git add -A && git commit`. On a timed build this is not bookkeeping: it is the rollback point that makes the next round safe to attempt, and the log doubles as a record of the order things were built in. The `wip:` checkpoints the Stop hook has been making in between are not rollback points — nothing was verified when they were taken. This commit is the one that means something, so give it a real message.

   **Write it the way a developer on this project would.** Conventional-commit prefix, imperative subject under ~70 chars, describing the *change to the product* — never the orchestration that produced it:

   ```
   feat: rank transcripts by risk severity and surface the daily brief

   - triage rules score each transcript, capped per kind
   - dashboard reads the ranked queue from the brief API
   ```

   Prefix by what landed: `feat:` new capability · `fix:` bug · `test:` tests only · `refactor:` no behaviour change · `chore:` deps, config, scaffolding · `docs:` docs only. Mixed rounds take the prefix of the dominant change, or split into two commits when the parts are genuinely unrelated.

   Never name workstream IDs, rounds, builders, agents, or models in the message. `WS7`, `Round 2b`, and `Sonnet rewrite` mean nothing to anyone reading this repo later and everything to someone asking who wrote it. The body says what changed and why, in the voice of someone who made the change themselves — because you are the one who will have to explain it.
8. Handle the fallout **in the main thread**:
   - **BLOCKED on a contract** → decide the change yourself, edit the contract file, note it in `PLAN.md`, re-dispatch affected workstreams. Never let a builder renegotiate a contract.
   - **FAIL** → read the verifier's evidence. Small and inside one workstream: re-dispatch that builder with the error. Crosses workstreams: fix it here.
   - **Integration work** is always yours.
9. Report to the user: what landed, what failed, what's next, and time remaining against `## Time`. If the round closed out cleanly and none of the never-self-invoke conditions apply, you may name the next round and start it; otherwise stop and wait.

If a builder reports a pass the verifier contradicts, believe the verifier. If the verifier passes and `demo.sh` doesn't, believe `demo.sh`.

## After the freeze time

Past `Freeze:` in `## Time`, stop dispatching builders. What remains is integration, demo rehearsal, reading anything still unread, and backfilling `DECISIONS.md`. A workstream that isn't done by then is a `CUT` — say so out loud and move it, rather than gambling the demo on it.
