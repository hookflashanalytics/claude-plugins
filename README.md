# Hookflash claude-plugins

The single source of truth for Hookflash's **certified** Claude skills. **A merged version-bump PR is the deployment**: Cowork's marketplace sync fires on it, and Claude Code clients registered against this marketplace pick it up at app startup.

## Three shelves

| Shelf | Repo | Who has it |
|---|---|---|
| **Certified** | this repo (`hookflash` marketplace) | everyone |
| **Staging** | [`claude-plugins-staging`](https://github.com/hookflashanalytics/claude-plugins-staging) (`hookflash-staging`) | nominated testers, on request |
| **Dev** | `claude-plugins-dev` (private) | AI Ops only |

A skill proves itself in staging on real client work, then graduates here (ADR-0009). Two
invariants hold that together:

- **The certified and staging skill sets are disjoint.** Skills are namespaced by plugin, so
  the same name in both marketplaces appears twice with near-identical descriptions and makes
  the slash command ambiguous. Promoting means adding here *and* removing there.
- **Only this repo ships `.mcp.json`.** Plugin MCP servers are registered per plugin, so a
  second Tether config in staging would mean a second OAuth grant per tester and every Tether
  tool loaded twice (against the ADR-0002 budget). Staging borrows Tether from this plugin —
  which is why **testers keep this plugin installed** rather than disabling it, and why this
  plugin is a prerequisite for staging even when a tester wants none of the skills in it.

## Layout

```
.claude-plugin/marketplace.json      catalog of plugins in this repo
plugins/
  hookflash-skills/                  installed org-wide (Cowork + Claude Code)
    .claude-plugin/plugin.json
    .mcp.json                        wires up the Tether MCP connector — the only copy,
                                     shared by the staging plugin too; never duplicate it
    skills/<skill-name>/SKILL.md     one folder per certified skill
```

Maintainer/dev skills live in the **private** `claude-plugins-dev` marketplace (registered
only by AI Ops), not here — this repo is public, so everything in it is world-readable and
installable by anyone who adds the marketplace.

**Versioning:** every release bumps the plugin `version` in `.claude-plugin/marketplace.json` (the per-plugin entry) **and** the plugin's own `plugin.json`, kept in lockstep — no exceptions. Cowork's marketplace sync only fires on a merged PR whose manifest version changed; a content-only merge deploys nowhere.

⚠ **Never rewrite history on this repo** — no force-push, no rebase of pushed commits. Rewritten history silently and permanently breaks auto-update for every installed client *and* for Anthropic's server-side marketplace mirror that feeds Cowork; the only recovery is per-user re-registration of the marketplace. Fix mistakes in forward commits. If a secret lands on main, rotate it and remove it in a forward commit — treat it as an incident, not a history scrub.

## Governance (the short version)

Full rationale lives in the AI Ops docs (`docs/adr/0003-skill-governance.md` in the AI Ops folder).

- Anyone may build **personal skills** for themselves, unreviewed. This repo holds only **certified** skills.
- Connor (AI Ops) is the sole approver. A submission is accepted when:
  1. **It demonstrably works** — the PR/suggestion includes at least one real output from actual use (a link to the deck it made, the analysis it produced).
  2. **It's a genuinely new use case** — not a formatting or preference tweak of an existing skill. Tweaks are rejected to personal skills; if the same tweak is requested repeatedly, fold it into the canonical skill as an option instead.
- One certified skill per shared job (the "canonical skill" rule). Improve the existing skill via PR rather than adding a near-duplicate.

## Adding or changing a skill

**New skills start in `claude-plugins-staging`, not here.** Land it there, have a nominated
tester use it on real client work, then promote with the steps below. Only fixes to already
certified skills go straight to this repo.

1. Branch, add `plugins/hookflash-skills/skills/<kebab-name>/SKILL.md` (frontmatter: `name`, `description` — the description drives triggering, so write it as "Use when the user asks to …").
2. Include proof it works in the PR description — the real output from the staging test, not a promise.
3. Bump the plugin `version` in `.claude-plugin/marketplace.json` and the plugin's `plugin.json` in lockstep (see Versioning above) — without this, the merge deploys nothing.
4. On merge: **remove the skill folder from `claude-plugins-staging`** (version-bumped PR there) so it is never in both, flip its Skill catalog row in Notion from *Staging* to *Live* with a copy-paste example prompt, and re-upload the skill bundle to claude.ai org settings if web-chat users need it (see `docs/runbooks/skill-release.md` in the AI Ops folder).

## Quality doctrine

Skills that produce artifacts (decks, workbooks, documents) must include a verify step in their procedure — render/inspect the output before handing it over — and should keep golden examples alongside the skill. If the model keeps making the same mistake, move that check into the server (Tether/Tapa) as a hard gate rather than prompting around it.
