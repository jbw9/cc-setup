---
name: decide
description: Log an architecture decision to DECISIONS.md at the moment it is made, including the option rejected, the cost accepted, and where it breaks at scale.
disable-model-invocation: false
argument-hint: "[what was decided, or blank to capture the decision just made]"
---

Append one entry to `DECISIONS.md` at the repo root. Create the file if it doesn't exist.

Write it now, not later. At the end of a build nobody remembers why SQLite beat Postgres at minute 40 — and if an agent made the call, it was never in your head to begin with.

## Entry format

```markdown
## D<n> · <the decision, as a short noun phrase>
When:     <HH:MM> · By: me | claude | @<name>
Chose:    <what we're doing>
Over:     <the strongest alternative that was actually on the table>
Because:  <the reason, in terms of this project's constraints — not general principle>
Costs us: <what this breaks, what you'd do with another week>
At scale: <what breaks first, at roughly what volume, and what replaces it>
```

## Rules

- **`Over:` is not optional.** "Why this over that" is the question you'll be asked; an entry without a rejected alternative doesn't answer it. If nothing was seriously considered, that's the honest entry: `Over: nothing — first thing that worked, under time pressure.`
- **`Costs us:` is the follow-up question**, every time. Fill it in even when the cost is "nothing at this scale."
- **`At scale:` is the second follow-up**, and the one people improvise badly. Name a volume — requests/sec, rows, concurrent users, GB/day — and what you would replace this with past it. Written one line at a time as you go, these compose into the production-design answer for free; reconstructed at the end, they're guesses. `/scale` reads them.
- **`Because:` must cite a real constraint** — the deadline, the data size, the demo path, a stated requirement. "Best practice" and "industry standard" are not reasons and will not survive one follow-up.
- Write it in your own voice. You have to say this out loud later.
- Log the ones that were *close*. A decision with no real alternative isn't worth an entry; one you'd defend differently on a different day is the whole point.

## What counts

Storage and schema shape · framework or library with a real alternative · sync vs async · where state lives · what got stubbed or faked and why · what was cut for time · anything a builder agent reported under `Decisions:` · anything that came out of a pairing session, attributed to whoever raised it.

Not: formatting, naming, or anything with one obvious answer.

If invoked with no argument, look at what just happened — the last few turns, the diff — find the decision in it, and confirm the entry with the user before writing. Never invent a rationale they didn't have.
