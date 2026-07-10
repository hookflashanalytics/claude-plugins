# Hookflash claude-plugins

The single source of truth for Hookflash's certified Claude skills. Merging to `main` **is** deployment: clients registered against this marketplace auto-update at startup and roughly hourly during sessions.

## Layout

```
.claude-plugin/marketplace.json      catalog of plugins in this repo
plugins/
  hookflash-skills/                  auto-installed org-wide (Cowork + Claude Code)
    .claude-plugin/plugin.json
    .mcp.json                        wires up the Tether MCP connector
    skills/<skill-name>/SKILL.md     one folder per certified skill
  hookflash-dev/                     platform-dev skills, NOT auto-installed
    skills/
```

Versioning is commit-based on purpose (no `version` fields): every merge to `main` is a release.

## Governance (the short version)

Full rationale lives in the AI Ops docs (`docs/adr/0003-skill-governance.md` in the AI Ops folder).

- Anyone may build **personal skills** for themselves, unreviewed. This repo holds only **certified** skills.
- Connor (AI Ops) is the sole approver. A submission is accepted when:
  1. **It demonstrably works** — the PR/suggestion includes at least one real output from actual use (a link to the deck it made, the analysis it produced).
  2. **It's a genuinely new use case** — not a formatting or preference tweak of an existing skill. Tweaks are rejected to personal skills; if the same tweak is requested repeatedly, fold it into the canonical skill as an option instead.
- One certified skill per shared job (the "canonical skill" rule). Improve the existing skill via PR rather than adding a near-duplicate.

## Adding or changing a skill

1. Branch, add `plugins/hookflash-skills/skills/<kebab-name>/SKILL.md` (frontmatter: `name`, `description` — the description drives triggering, so write it as "Use when the user asks to …").
2. Include proof it works in the PR description.
3. On merge: add a row to the Skill catalog in Notion (AI Ops hub) with a copy-paste example prompt, and re-upload the skill bundle to claude.ai org settings if web-chat users need it (see `docs/runbooks/skill-release.md` in the AI Ops folder).

## Quality doctrine

Skills that produce artifacts (decks, workbooks, documents) must include a verify step in their procedure — render/inspect the output before handing it over — and should keep golden examples alongside the skill. If the model keeps making the same mistake, move that check into the server (Tether/Tapa) as a hard gate rather than prompting around it.
