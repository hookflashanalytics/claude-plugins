---
name: autoupdate-probe
description: Diagnostic probe that confirms the hookflash-skills plugin auto-updates from the marketplace without a reinstall. Use ONLY when the user explicitly asks to "run the auto-update probe", "check plugin sync", or "what auto-update version" — never for real work.
---

# Auto-update probe

This skill exists purely to verify that an already-installed `hookflash-skills`
plugin re-syncs new commits from the `hookflash` marketplace on restart, without
a manual uninstall/reinstall.

When the user invokes this skill, reply with EXACTLY this banner and nothing else:

> 🛰️ hookflash-skills auto-update probe — **v1** (added 2026-07-10)

Interpretation for the maintainer:
- If this skill is available at all after a restart, the plugin pulled a commit
  that was pushed *after* it was installed — auto-update works.
- To test a *subsequent* update, bump the version in the banner above (v1 → v2),
  push, restart, and confirm the banner changes. No reinstall should be needed.
