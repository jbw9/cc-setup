# <project>

The authoritative plan is PLAN.md. Read it before doing anything.

<!-- That first line is load-bearing: subagents inherit CLAUDE.md but not the
     conversation, so this file plus PLAN.md is all a builder will ever know. -->

## Stack
- Language / runtime:
- Framework:
- Package manager:        <!-- state it; stops agents guessing npm vs pnpm vs bun -->
- Run:        `<command>`
- Test:       `<command>`
- Lint/build: `<command>`

## Conventions
- Keep it in <N> files until it works; refactor after.
- No new dependencies without asking.
- Tests only for <the parts that matter>. Don't scaffold a suite.

## Parallel work
- Write only inside your workstream's `owns:` globs.
- Contracts in PLAN.md are frozen. Report problems with one; don't fix it.
- Don't edit PLAN.md or DECISIONS.md — the main thread owns both.

## Decisions
Non-obvious choices go in DECISIONS.md as they're made, with the option they beat.
