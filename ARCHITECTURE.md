# Architecture

Why this setup is shaped the way it is. Written in the same format `/decide`
produces, so it doubles as a worked example of a `DECISIONS.md`.

## The constraint everything follows from

Subagents do not share context. A dispatched agent gets its task message, the
`CLAUDE.md` files, and a git status snapshot — **not** the conversation, not the
files the main thread has read, and not each other's work. They also cannot talk
to each other while running.

So parallelism is only safe if two things hold before anyone is dispatched:

1. **Disjoint file ownership.** Two builders writing one file race, and neither
   can see it happen.
2. **Frozen, materialized interfaces.** Agents coding against a *described*
   interface each invent a different one. Agents coding against a *file* agree by
   construction.

`PLAN.md` exists to encode exactly those two things. Everything else is plumbing.

---

## D1 · Plan file on disk, not in conversation
Chose:    `PLAN.md` at the repo root, authoritative over conversation memory.
Over:     Keeping the plan in context and re-describing it in each dispatch prompt.
Because:  Subagents can't see the conversation, so a plan that lives only in
          context is unreachable to the agents that need it. Restating it per
          dispatch introduces drift — each paraphrase is a slightly different spec.
Costs us: A stale `PLAN.md` silently misleads every agent. `/handoff` exists to
          force it back in sync, and it's on the human to run it.

## D2 · Contracts written as real files before fan-out
Chose:    Main thread writes shared types/interfaces/schema to disk first.
Over:     Letting the first builder define them and having others follow.
Because:  "Others follow" requires seeing the first builder's output, which is
          exactly what parallel agents cannot do. Serializing to get that ordering
          gives up the parallelism the whole design is for.
Costs us: Front-loaded design time before any code lands, and contracts get
          frozen while still partly guesses. Mitigated by builders reporting
          contract problems upward instead of fixing them locally.

## D3 · Opus builders, capped at 3
Chose:    `model: inherit` on `builder`, hard cap of 3 concurrent.
Over:     Sonnet builders at 5+ concurrent — cheaper, faster per agent.
Because:  Chosen deliberately for code quality per agent over throughput. Three
          Opus agents on a 5-hour usage limit is the point where wall-clock gains
          flatten and limit risk becomes real.
Costs us: Burns the usage limit materially faster. On a long day, `model: sonnet`
          in `agents/builder.md` is a one-line change.

## D4 · `SessionStart` hook instead of a bigger context window
Chose:    Keep `autoCompactWindow` at 400k; re-inject `PLAN.md` state via a
          `SessionStart` hook matching `startup|resume|compact`.
Over:     Raising the window toward 1M to avoid compaction entirely.
Because:  Every request re-sends the whole conversation, so a 900k context makes
          every late-session turn slow and expensive. Hooks matching the `compact`
          source re-run *after* compaction and their output joins the fresh
          context — which turns a compaction from a memory-loss event into a
          reload. Fan-out already keeps the main thread far under 400k, so the
          cap rarely fires at all.
Costs us: State is only as good as the last `/handoff`. Anything not written down
          is genuinely gone.

## D5 · Verifier agent runs the checks
Chose:    A separate read-only `verifier` runs build/typecheck/tests.
Over:     Running them in the main thread.
Because:  Context economy. A test run printing 3,000 lines lands in the verifier's
          context; the main thread gets a five-line verdict. This is the single
          largest source of context bloat in a long build.
Costs us: An extra dispatch round-trip, and the main thread can't grep raw output
          without re-running.

## D6 · The workstream is the delegation unit for humans too
Chose:    An `owner:` field — `builder`, `me`, or `@name` — and `/brief` to hand a
          workstream to a person.
Over:     A separate process for human collaborators.
Because:  Two engineers editing one file race exactly the way two agents do, and
          a teammate needs the frozen contract more than an agent does — otherwise
          they interrupt you to ask. The partition already solves it; it only
          needed a name for who executes.
Costs us: Nothing structural. `/fanout` must check `owner:` before dispatching, or
          it will send an agent into a human's files mid-edit.

## D7 · Karpathy guidelines split, not adopted whole
Chose:    §1 into `/kickoff`, §2–3 into `builder`, §4 into `verifier`; intact copy
          kept for manual review passes.
Over:     Loading the skill globally as written.
Because:  Its own header says it biases toward caution over speed, and §1's "if
          something is unclear, stop and ask" is actively wrong for an unsupervised
          builder mid-fan-out — it would stall the round. The restraint rules
          (§2–3) are most valuable exactly where nobody is watching.
Costs us: A vendored fork can drift from upstream. Pinned by date and provenance
          comment.

## D8 · Skills, all manual-invoke
Chose:    `disable-model-invocation: true` on every workflow skill.
Over:     Letting Claude auto-invoke them when it judges them relevant.
Because:  With that flag the description stays out of context entirely — the
          skills cost nothing until typed. These are also ritual steps with an
          order that matters; auto-invocation would fire them at the wrong time.
Costs us: You have to remember they exist. `CLAUDE.md` names the sequence.

---

## Known weaknesses

- **Partition quality is the whole ballgame.** A bad workstream split produces
  merge pain that costs more than the parallelism saved. When in doubt, fewer,
  larger workstreams.
- **`PLAN.md` drift** is the most likely failure mode in practice.
- **No cross-agent progress visibility.** A builder heading the wrong way runs to
  completion before anyone finds out.
- **Contracts frozen too early** produce a round of rework. This is a real cost,
  accepted knowingly in exchange for safe parallelism.
