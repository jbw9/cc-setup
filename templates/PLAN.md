# <project>

## Goal
<The demoable thing at the deadline, one paragraph. Concrete enough to be a
command or a click-path, not an aspiration.>

## Time
Started: <HH:MM> · Deadline: <HH:MM> · Freeze: <deadline − 45m>
Fixed points: <e.g. pairing 13:00, present 16:00>

## Constraints
Judged on:    <working demo / code quality / how you reason out loud>
Out of scope: <auth, persistence, deploy, responsive, tests — name what is NOT built>

## Stack
<language / framework / package manager>
Run: `<cmd>` · Test: `<cmd>` · Build: `<cmd>`

## Demo path
<The exact sequence you will run in front of an audience — materialized as
`demo.sh` at the repo root, exiting non-zero when the path is broken.>
1. <step>
2. <step>
Last green: <round or time>

## Contracts
<Types, interfaces, API shapes, schema — and the file each one lives in.
Provisional until Round 0 lands; derived from the running spine and frozen after.
A builder that hits a bad contract reports it, it does not renegotiate it.>

`src/types.ts`
```ts
export type Item = { id: string; ... }
```

## Workstreams
### WS1 <name>
tier:       MUST | SHOULD | CUT               <- cut from the bottom at freeze
owner:      builder | builder-fast | me | @<teammate>
owns:       src/api/**, src/db/schema.ts      <- exclusive; no glob appears twice
depends:    Contracts §<x>
blocked-by: —
done-when:  `<command>` passes

### WS2 <name>
tier:       MUST
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
