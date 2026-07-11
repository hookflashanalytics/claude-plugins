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

> 🐤 new-skill canary — **v1**, added 2026-07-11. If you can read this in Cowork, a brand-new skill reached your client via marketplace auto-update. ✅

Interpretation for the maintainer:
- This skill folder did **not** exist at the last install/restart. If it triggers in
  Cowork after a restart, auto-update pulls *new* skills from the marketplace with no
  uninstall/reinstall needed.
- The date in the banner is the day the skill was added — use it to confirm which
  commit your Cowork client has synced to.
- Once the test is done, retire this folder in a PR (see `docs/runbooks/skill-release.md`).
