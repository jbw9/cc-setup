---
name: defend
description: Rehearse the architecture questions before a review or presentation. Reads PLAN.md, DECISIONS.md and the diff, then interrogates the weakest choices.
disable-model-invocation: true
---

Prepare the user to defend this build. Run this with 15 minutes left, not at the end.

## 1. Reconstruct

Read `PLAN.md`, `DECISIONS.md`, and `git diff --stat` plus the diff of the most substantial files. Find decisions visible in the code that never made it into `DECISIONS.md` — those are the dangerous ones, because they'll get asked about and the user has no answer ready.

## 2. Give them the map

Six lines, no more: what the system does, its main pieces, how data flows through it, where it would break first.

## 3. Interrogate

Ask the questions a sharp reviewer asks. Real ones, in `AskUserQuestion` rounds — make them answer, don't hand them a script:

- "Why <choice> and not <the alternative in DECISIONS.md>?"
- "What happens at 100× the data?"
- "What did you cut, and what would you do first with another day?"
- "Walk me through what happens when <the demo path> runs."
- "What's the weakest part of this?"
- "This is stubbed — was that deliberate?"

When an answer is thin, say so plainly and give them a better one built from what's actually in the repo. Don't accept an answer you know the code contradicts — that's the whole value of doing this now instead of live.

## 4. Hand back

```
STRONG:  <decisions with a clear rationale — lead with these>
THIN:    <decisions with a weak or missing why — rehearse these>
EXPOSED: <what's in the code but not in DECISIONS.md — they will find it>
CUT:     <what was descoped, and the one-line reason>
```

Then the single question most likely to be asked, and the answer in their own words.

Honesty rule: if something was chosen because an agent picked it and it worked, the answer is "it was the default and I didn't have a reason to fight it" — not a rationalization invented now. Reviewers can tell the difference, and a candid answer beats a reverse-engineered one.
