# Hookflash claude-plugins

The single source of truth for Hookflash's Claude skills. **A merged version-bump PR is the deployment**: Cowork's marketplace sync fires on it, and Claude Code clients registered against this marketplace pick it up at app startup.

## Which plugin do I install?

One marketplace (`hookflash`), two plugins:

| Plugin | Install it? | What's in it |
|---|---|---|
| **`hookflash-skills`** | **Yes — everyone.** Required. | Certified skills, plus the Tether connection every Hookflash skill needs |
| **`hookflash-skills-staging`** | **Only if AI Ops asked you to.** | Skills in testing — unproven, may break or change without notice |

Staging is visible in the marketplace on purpose. There's no technical gate, just the
convention that you don't install it uninvited. Install it anyway and a skill misbehaves,
that's the deal you took — but do tell Connor rather than working around it.

**`hookflash-skills-staging` requires `hookflash-skills`.** It ships no connector of its own
(see below), so alone its skills can't reach Tether. Add it *alongside*, never instead of.

## The staging channel (ADR-0009)

New skills land in `plugins/hookflash-skills-staging/`, get used on real client work by a
nominated tester, and graduate to `plugins/hookflash-skills/` once there's a real output to
point at (ADR-0003's proof-of-work gate). Two invariants:

- **A skill is in exactly one plugin, never both.** Skills are namespaced by plugin, so the same
  name in both would appear twice with near-identical descriptions and make the slash command
  ambiguous. Because both plugins live in this one repo, promotion is a single `git mv` in a
  single PR — atomic, so the two can't drift apart.
- **Only `hookflash-skills` ships `.mcp.json`.** Plugin MCP servers are registered per plugin
  (`plugin:hookflash-skills:tether`), so a second Tether config in the staging plugin would mean
  a second OAuth grant per tester and every Tether tool registered twice, against the ADR-0002
  tool budget. The staging plugin ships skills only and borrows Tether from the certified plugin;
  MCP tools resolve session-wide regardless of which plugin contributed them.

**Versions are per plugin**, so bumping staging doesn't churn anyone running only
`hookflash-skills` — staging can move fast.

## Layout

```
.claude-plugin/marketplace.json      both plugins listed here, each with its own version
plugins/
  hookflash-skills/                  installed org-wide (Cowork + Claude Code)
    .claude-plugin/plugin.json
    .mcp.json                        wires up the Tether MCP connector — the ONLY copy in this
                                     repo, shared by the staging plugin; never duplicate it
    skills/<skill-name>/SKILL.md     one folder per certified skill
  hookflash-skills-staging/          testers only
    .claude-plugin/plugin.json
    skills/<skill-name>/SKILL.md     one folder per skill under test
                                     (no .mcp.json here — deliberate, see above)
```

Maintainer/dev skills live in the **private** `claude-plugins-dev` marketplace (registered
only by AI Ops), not here — this repo is public, so everything in it is world-readable and
installable by anyone who adds the marketplace. That applies to staging skills too: **never
commit secrets or client identifiers, not even to a skill that's "only in testing."**

**Versioning:** every release bumps the `version` of the plugin you touched, in `.claude-plugin/marketplace.json` (that plugin's entry) **and** in its own `plugin.json`, kept in lockstep — no exceptions. Cowork's marketplace sync only fires on a merged PR whose manifest version changed; a content-only merge deploys nowhere.

⚠ **Never rewrite history on this repo** — no force-push, no rebase of pushed commits. Rewritten history silently and permanently breaks auto-update for every installed client *and* for Anthropic's server-side marketplace mirror that feeds Cowork; the only recovery is per-user re-registration of the marketplace. Fix mistakes in forward commits. If a secret lands on main, rotate it and remove it in a forward commit — treat it as an incident, not a history scrub.

## Governance (the short version)

Full rationale lives in the AI Ops docs (`docs/adr/0003-skill-governance.md` in the AI Ops folder).

- Anyone may build **personal skills** for themselves, unreviewed. This repo holds **certified** skills and skills **in testing**, in separate plugins.
- Connor (AI Ops) is the sole approver of certification. A submission is accepted when:
  1. **It demonstrably works** — the PR/suggestion includes at least one real output from actual use (a link to the deck it made, the analysis it produced).
  2. **It's a genuinely new use case** — not a formatting or preference tweak of an existing skill. Tweaks are rejected to personal skills; if the same tweak is requested repeatedly, fold it into the canonical skill as an option instead.
- One certified skill per shared job (the "canonical skill" rule). Improve the existing skill via PR rather than adding a near-duplicate.

## Adding a new skill

**New skills go into the staging plugin, not the certified one.**

1. Branch, add `plugins/hookflash-skills-staging/skills/<kebab-name>/SKILL.md` (frontmatter: `name`, `description` — the description drives triggering, so write it as "Use when the user asks to …").
2. Bump `hookflash-skills-staging`'s version in `marketplace.json` and its `plugin.json`, in lockstep. PR → merge.
3. Add a Skill catalog row in Notion with status **Staging**, then tell the nominated tester to install the plugin.

## Promoting a skill to certified

1. Confirm there's a real output from actual use to point at (ADR-0003).
2. One PR, one `git mv`:
   ```bash
   git mv plugins/hookflash-skills-staging/skills/<name> plugins/hookflash-skills/skills/<name>
   ```
   This is why both plugins share a repo — the move is atomic, so the skill can never be in both.
3. Confirm the skill has a **verify step** if it produces an artifact (ADR-0006).
4. Bump **both** plugins' versions (certified gained a skill, staging lost one), each in lockstep with its `plugin.json`.
5. Include the proof in the PR description. On merge: flip the Skill catalog row from *Staging* to *Live* with a copy-paste example prompt, and re-upload the bundle to claude.ai org settings if web-chat users need it (see `docs/runbooks/skill-release.md` in the AI Ops folder).

## Quality doctrine

Skills that produce artifacts (decks, workbooks, documents) must include a verify step in their procedure — render/inspect the output before handing it over — and should keep golden examples alongside the skill. If the model keeps making the same mistake, move that check into the server (Tether/Tapa) as a hard gate rather than prompting around it.
