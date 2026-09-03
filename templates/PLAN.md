# <project>

## Goal
<The demoable thing at the deadline, one paragraph. Concrete enough to be a
command or a click-path, not an aspiration.>

## Constraints
Deadline:     <when>
Judged on:    <working demo / code quality / how you reason out loud>
Out of scope: <auth, persistence, deploy, responsive, tests — name what is NOT built>

## Stack
<language / framework / package manager>
Run: `<cmd>` · Test: `<cmd>` · Build: `<cmd>`

## Contracts
<Types, interfaces, API shapes, schema — and the file each one lives in.
Written as real code on disk BEFORE any fan-out. Frozen once builders start:
a builder that hits a bad contract reports it, it does not renegotiate it.>

`src/types.ts`
```ts
export type Item = { id: string; ... }
```

## Workstreams
### WS1 <name>
owner:      builder | me | @<teammate>
owns:       src/api/**, src/db/schema.ts      <- exclusive; no glob appears twice
depends:    Contracts §<x>
blocked-by: —
done-when:  `<command>` passes

### WS2 <name>
owner:      builder
owns:       src/ui/**
depends:    Contracts §<x>
blocked-by: —
done-when:  `<command>` passes

## Integration
<What only the main thread does: wiring, anything crossing workstreams.>

## Status
Updated: <date> · Branch: <branch>

WS1 <name> — not-started
WS2 <name> — not-started

Next:    <the single next action>
Gotchas: <stubs, hardcoded values, skipped tests — what a fresh session would get wrong>
