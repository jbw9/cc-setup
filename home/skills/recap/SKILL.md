---
name: recap
description: Summarize everything done in the session so far as a concise high-level recap, then update the project's documentation md files (CLAUDE.md today, others as they appear) to reflect what changed.
trigger: /recap
---

# /recap

Two jobs, in order: **(1)** give a concise high-level recap of the session, then
**(2)** update the relevant project docs so they reflect what changed.

## Usage

```
/recap                # recap the session + update docs
/recap --no-docs      # recap only, do not touch any md files
```

## Step 1 — Recap the session

Use the `/eli5` style: high-level, skimmable, structured. Cover:

- **Done** — what was actually changed/built/decided this session (bulleted).
- **Why** — the goal behind it, in a line or two.
- **State** — where things stand now: what's finished, what's pending, any
  open questions or follow-ups.

Keep it tight. Lists and short lines over paragraphs. This is a map of the
session, not a transcript.

## Step 2 — Update the docs

Reflect the session's real changes into the project's documentation.

1. **Find the doc files.** Start with `CLAUDE.md`. Also check for and include,
   if present: `AGENTS.md`, `README.md`, and any other `*.md` the repo treats as
   living docs (e.g. files `CLAUDE.md` references with `@`). Today this repo has
   `CLAUDE.md` — this list will grow, so **discover, don't hardcode**.
2. **Update only what actually changed.** New/changed behavior, invariants,
   commands, file locations, gotchas, or "upcoming tasks" status. Match the
   existing voice and section structure of each file — surgical edits, not
   rewrites.
3. **Don't invent.** If nothing in the session warrants a doc change, say so and
   change nothing rather than padding.
4. **Show what you touched.** After editing, list each file and the one-line
   reason it changed.

## Rules

- Recap first, then docs — the recap is what you're distilling into the docs.
- Never fabricate progress. If a step failed or was skipped, recap it as such.
- Respect `--no-docs`: recap and stop.
- Don't duplicate a fact the code/git history already records; docs capture the
  *why* and the non-obvious, per this repo's memory conventions.
