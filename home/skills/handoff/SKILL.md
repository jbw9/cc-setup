---
name: handoff
description: Checkpoint the current state into PLAN.md's Status block so it survives a compaction or a lost session. Run before a long fan-out or any risky step.
disable-model-invocation: true
---

Rewrite the `## Status` block in `PLAN.md` from what is actually true right now.

Check reality first — `git status`, the files that changed, the last verifier verdict. Do not copy the old status forward.

```markdown
## Status
Updated: <date> · Branch: <branch>

WS1 <name> — done      · verified by `<cmd>`
WS2 <name> — in-progress · <what's left, one line>
WS3 <name> — blocked   · <on what>

Next: <the single next action>
Gotchas: <anything a fresh session would get wrong — a workaround, a stubbed thing, a lie in the code>
```

Write it for a reader with no memory of this conversation, because after a compaction that is exactly who reads it. The `Gotchas` line is the one that saves the most time: the temporary hack, the hardcoded value, the test that's skipped.

Keep it under ~20 lines. Update `## Contracts` too if any contract changed. Then say in one line what you checkpointed.
