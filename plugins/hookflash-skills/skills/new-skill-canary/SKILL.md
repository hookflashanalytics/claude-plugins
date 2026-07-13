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

> 🐤 new-skill canary — **v3**, updated 2026-07-13 ~12:55 UTC. If you see v3 in Cowork WITHOUT having reinstalled anything, Anthropic's marketplace mirror auto-refreshed a healthy registration — merge-to-main reaches Cowork automatically. ✅

Interpretation for the maintainer:
- **v3 banner** = the claude.ai-side plugin snapshot refreshed on its own after this
  commit was merged — Cowork auto-update is confirmed end-to-end; merge = deploy.
- **v2 banner** = still serving the snapshot taken at the 2026-07-13 marketplace
  re-registration — the server refresh hasn't run yet (note how long it's been) or
  Cowork snapshots don't auto-refresh at all (if it persists >48h, update the
  release runbook: each merge needs a manual re-publish for Cowork).
- **Skill not found** = the registration is stale/diverged — remove the marketplace
  registration itself (not just the plugin) in Cowork → Customize → Plugins, re-add
  `hookflashanalytics/claude-plugins`, reinstall. (This was needed once after the
  2026-07-10 history rewrite, which bricked Anthropic's server-side mirror.)
- Once the test is done, retire this folder in a PR (see `docs/runbooks/skill-release.md`).
