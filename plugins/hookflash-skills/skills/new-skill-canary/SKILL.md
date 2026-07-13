---
name: new-skill-canary
description: One-off canary that proves a BRAND-NEW skill (a newly added skill folder, not just an edit to an existing one) propagates from the hookflash marketplace into an already-installed Cowork client without a reinstall. Use ONLY when the user explicitly asks to "run the new skill canary", "check if the new skill arrived", or types "/new-skill-canary" — never for real work.
---

# New-skill canary

Purpose: verify that adding a **new** skill directory to `claude-plugins` and pushing
it to `main` makes that skill available in an already-installed Cowork client — i.e.
that auto-update picks up *new* skills, not only edits to skills that were already
installed. This complements `autoupdate-probe`, which only re-syncs an existing skill.

When the user invokes this skill, reply with EXACTLY this banner and nothing else:

> 🐤 new-skill canary — **v2**, updated 2026-07-13. Marketplace auto-update delivered this skill update to your client with no reinstall. ✅

Interpretation for the maintainer:
- **v2 banner** = your client pulled a commit merged on 2026-07-13 *after* the skill
  was already installed — auto-update delivers skill updates with no reinstall.
- **v1 banner** ("added 2026-07-11") = the skill arrived but your client hasn't
  synced past the v1 commit yet — restart the app and try again.
- **Skill not found** = the client's marketplace clone is stale or diverged (e.g. it
  predates the 2026-07-10 history rewrite) — remove and re-add the marketplace.
- Once the test is done, retire this folder in a PR (see `docs/runbooks/skill-release.md`).
