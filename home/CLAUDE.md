# Global preferences

<!-- This file is loaded into EVERY session. It is the single highest-leverage
     thing in this repo. Keep it short and specific — vague preferences are
     ignored, concrete rules are followed. -->

## How to work
- Act when you have enough to act. Don't re-ask what I've already answered.
- Make routine judgment calls yourself; ask only when two readings lead to
  materially different work.
- Finish the whole task. If part is blocked, do the rest and say what you skipped.
- Report failures plainly with the actual output. Never claim something passes
  that you didn't run.

## Code style
<!-- FILL IN: your real defaults. Examples to replace, not keep verbatim. -->
- Match the surrounding file's conventions over any general style rule.
- No comments explaining what the code does; only why, and only when non-obvious.
- No defensive try/except around things that shouldn't fail.

## Stack defaults
<!-- FILL IN: what you reach for when unspecified, so I don't have to say it. -->
- Frontend:
- Backend:
- DB:
- Tests:
- Package manager:

## Don't
- Don't add README/CHANGELOG/docs unless asked.
- Don't add a test framework to a project that has none without asking.
- Don't `git commit` or `git push` unless I ask.

## Skills
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) — any input to knowledge graph. Trigger: `/graphify`
  When I type `/graphify`, invoke the Skill tool with `skill: "graphify"` before anything else.
