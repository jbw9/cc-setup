---
name: eli5
description: Explain the current session context — or whatever the user asks about — as a concise, high-level overview that shows how it fits the big picture. Not literally "like I'm 5"; just plain, skimmable, no rabbit holes.
trigger: /eli5
---

# /eli5

Give a **high-level overview**, not a deep dive. The user wants to understand
*what* something is and *how it fits the big picture* — not the underlying
mechanics, line-by-line detail, or exhaustive edge cases.

## Usage

```
/eli5                 # explain what's going on in this session right now
/eli5 <topic>         # explain that topic/file/concept/error at a high level
```

## What to produce

Answer these three, in order, and stop:

1. **What is it?** — one or two plain sentences.
2. **How does it fit?** — where it sits in the bigger system / flow / goal.
3. **What matters** — the 2–5 things worth knowing. Nothing more.

## Rules (do not skip)

- **Be concise.** No preamble, no "great question", no wrap-up paragraph.
- **Use structure aggressively** — lists, tables, a tiny flow (`A → B → C`),
  bold labels. If a table makes it clearer, use a table.
- **High level only.** Skip implementation details, config minutiae, and history
  unless the user explicitly asks. If tempted to explain *how*, ask yourself if
  they need it — usually they don't.
- **No spam.** Fewer words that land beat more words that bury.
- **Plain language.** Explain jargon the first time it appears, in a few words.
- **Analogies are fine** when they make the big picture click — keep them short.
- Match depth to the ask: a one-line question gets a few lines, not an essay.

## Scope of `/eli5` (no arg)

When run with no topic, explain **this session**: what the user is working on,
what's been done or decided, and where things stand — as a high-level map, not a
transcript. (This overlaps with `/recap`; keep it to the "what & why" overview,
leave the full done-list to `/recap`.)

## Shape to aim for

> **What it is** — <1–2 sentences.>
>
> **Big picture** — <where it fits / the flow it's part of.>
>
> **What matters**
> - <point>
> - <point>
