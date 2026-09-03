---
name: decide
description: Log an architecture decision to DECISIONS.md at the moment it is made, including the option rejected and the cost accepted.
disable-model-invocation: true
argument-hint: "[what was decided, or blank to capture the decision just made]"---

Append one entry to `DECISIONS.md` at the repo root. Create the file if it doesn't exist.

Write it now, not later. At the end of a build nobody remembers why SQLite beat Postgres at minute 40 — and if an agent made the call, it was never in your head to begin with.

## Entry format

```markdown
## D<n> · <the decision, as a short noun phrase>
When:     <HH:MM> · By: me | claude | @<name>
Chose:    <what we're doing>
Over:     <the strongest alternative that was actually on the table>
Because:  <the reason, in terms of this project's constraints — not general principle>
Costs us: <what this breaks, when it stops working, what you'd do with another week>
```

## Rules

- **`Over:` is not optional.** "Why this over that" is the question you'll be asked; an entry without a rejected alternative doesn't answer it. If nothing was seriously considered, that's the honest entry: `Over: nothing — first thing that worked, under time pressure.`
- **`Costs us:` is the follow-up question**, every time. Fill it in even when the cost is "nothing at this scale."
- **`Because:` must cite a real constraint** — the deadline, the data size, the demo path, a stated requirement. "Best practice" and "industry standard" are not reasons and will not survive one follow-up.
- Write it in your own voice. You have to say this out loud later.
- Log the ones that were *close*. A decision with no real alternative is not worth an entry; a decision you'd defend differently on a different day is the whole point.

## What counts

Storage and schema shape · framework or library with a real alternative · sync vs async · where state lives · what got stubbed or faked and why · what was cut for time · anything a builder agent reported under `Decisions:`.

Not: formatting, naming, or anything with one obvious answer.

If invoked with no argument, look at what just happened — the last few turns, the diff — find the decision in it, and confirm the entry with the user before writing. Never invent a rationale they didn't have.
