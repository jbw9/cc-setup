---
name: defend
description: Rehearse the architecture questions before a review or presentation, and build a presentable architecture page. Reads PLAN.md, DECISIONS.md and the diff, interrogates the weakest choices, then generates ARCHITECTURE.html.
disable-model-invocation: true
---

Prepare the user to defend this build. Run this with 30 minutes left, not at the end.

Two outputs: the rehearsal (steps 1–4), and `ARCHITECTURE.html` (step 5) — a
self-contained page they can present from in a system-design round. Do the
rehearsal first. The page is only good if the interrogation has already found the
thin spots, and the user's own answers are what make the prose sound like them.

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

## 5. Build ARCHITECTURE.html

Write `ARCHITECTURE.html` at the repo root — one file the user can open by
double-clicking and present from. It answers the three questions a system-design
round actually asks: **what did you build, why this way, and how would you scale it.**

**Non-negotiable constraints:**

- **Self-contained.** Inline `<style>`, inline `<svg>`. No CDN scripts, no external
  fonts, no network of any kind. Interview wifi fails; a page that needs it fails
  with it. Verify: zero `http://` or `https://` in the file.
- **Diagrams as hand-written inline SVG.** Do not reach for a diagramming library —
  it is one more thing to load and one more thing to break. A `viewBox`, some
  `<rect>`s, `<text>` and arrow `<marker>`s is all this needs.
- **Legible on a projector.** Body text 16px+, diagram labels 11px+, real contrast.
  Assume a washed-out room and a reader at the back.
- **No horizontal scroll** at 1280px or at phone width.

**The shape that works** — adapt it, don't follow it blindly:

1. **The central design choice.** Lead with the one idea the whole system turns on,
   as a claim in a single sentence, then a diagram of it, then why the obvious
   alternative is worse. If the build has no such idea, say what it has instead —
   do not manufacture one.
2. **How the system is put together.** The pieces, and how data moves between them.
   One diagram. Follow it with why the split is that way.
3. **Data model**, if the project has one worth showing.
4. **Choices, and what they beat.** One card per real fork, each with: what was
   chosen, what it beat, the cost accepted, where it breaks at scale. This section
   is `DECISIONS.md` rendered for an audience — pull from it, don't reinvent it.
5. **What I know is weak.** The honest list. Severity-tagged.
6. **Taking this to production.** A diagram of the scaled shape, then the things
   that break in the order they break, then what you'd build next.
7. **The demo path**, as a table of what each step proves.

**Write the prose in the user's voice, from their answers in step 3.** This is the
whole reason the rehearsal comes first. A page that argues a position the user
cannot defend out loud is worse than no page.

**The honesty rules from the rehearsal apply to the page, in writing.** If two
results came out wrong, the page says so and says why that was accepted. If
something was chosen because it was the default, the page does not invent a
rationale for it. A reviewer who finds a weakness the page already named reads it as
rigor; one who finds a weakness the page papered over stops trusting the rest.

**Then look at it.** Open it in a browser, screenshot it, and actually read the
screenshots. SVG diagrams go wrong in ways that are invisible in source: arrows that
stop short of their box, labels clipped by a neighbouring shape, text overflowing its
container. Check the console is clean and that nothing scrolls sideways. Fix what you
find before handing it over — the user is going to project this.

## Honesty rule

If something was chosen because an agent picked it and it worked, the answer is "it was the default and I didn't have a reason to fight it" — not a rationalization invented now. Reviewers can tell the difference, and a candid answer beats a reverse-engineered one. This holds for the page as much as for the rehearsal.
