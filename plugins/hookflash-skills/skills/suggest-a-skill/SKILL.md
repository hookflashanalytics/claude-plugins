---
name: suggest-a-skill
description: Suggest a new Hookflash skill (or promote a personal skill you've built) — a guided interview that checks the idea against the certified skill list, drafts the complete skill file with you, and files everything in the Suggest-a-skill backlog in Notion for AI Ops review. Use when the user runs /suggest-a-skill, asks to suggest/propose/submit a skill idea, says "can we get a skill that…" or "I wish Claude could…" about a repeatable team job, or wants a personal skill certified for the whole team.
---

# Suggest a skill

File a **review-ready** skill suggestion into the **Suggest a skill** database in the
Notion AI Ops hub. Review-ready means the reviewer opens the row and finds a finished
draft — the complete proposed `SKILL.md`, written here while you have the submitter's
full context — not a wish they'd have to interpret. Certified skills need two things
(say this up front if the user seems unsure): **proof it works** — a real output, not a
promise — and a **genuinely new use case** — formatting or preference tweaks of an
existing skill stay personal.

## Prerequisites (read first)

- **Notion connector required** to file the row. If this session has no Notion tools,
  skip to **No-Notion fallback** below — never claim a row was created when it wasn't.
- Target: the **Suggest a skill** database in the AI Ops hub —
  page `https://app.notion.com/p/5d84a8b44163453ca18757436d917950`,
  data source `collection://0cccdf72-2485-4ab7-8efe-2ef3c9dc8fd7`.

## Step 1 — Interview (gather four things, one pass)

Collect conversationally — if their first message already covers a field, use it; draft
wording for them rather than interrogating:

1. **Skill idea** — a short working name for the job (e.g. "Weekly client SEO health summary").
2. **What it should do** — inputs → what Claude does → deliverable.
3. **Current manual process** — how they do this job today, step by step. This is the
   raw material for the draft; push gently for the real steps, not "I just do it".
4. **Proof / example output** — a link to (or attachment of) at least one real output.
   If they've done the job with Claude in this very session, that output is the proof —
   link it. If the job is quick and they have no proof yet, offer to **do it together
   once, now** — you get proof and a tested procedure in one go. No proof? File anyway,
   but tell them the reviewer will ask for it before certifying.

## Step 2 — Overlap check (before drafting)

Compare the idea against the certified skills already installed from this plugin (the
hookflash-skills names and descriptions available in this session).

- **Overlap or a tweak of an existing skill** → name the existing skill and explain the
  house rule: preference tweaks stay personal; improvements belong to the canonical skill.
  Offer to file it as "Improve <existing-skill>: …" instead. If they still want it filed
  as a new skill, file it — the reviewer decides; you only set expectations.
- **No overlap** → proceed.

## Step 3 — Draft the complete SKILL.md (the heart of this skill)

Write the full proposed `SKILL.md` now, with the user, while you have their context.
Ground every step in how they actually do the job — never invent procedure to fill
space. House conventions the draft must follow:

- **Frontmatter:** `name` in kebab-case; `description` that opens with what the skill
  does, then "Use when the user runs /<name>, …" — the description drives triggering,
  so include the phrasings a colleague would actually type.
- **Structure:** short intro; numbered steps; required inputs marked
  "REQUIRED — ask if missing; never guess"; a **verify step** if the skill produces an
  artifact (render/inspect the output before handing it over); a **Guardrails** section.
- **Grounding:** name the real tools/connectors each step uses (e.g. Tether MCP tools)
  only if the user actually uses them today — otherwise describe the step plainly and
  leave tooling to the reviewer.

Iterate with the user until they say the draft matches how the job should work. If the
skill needs supporting files (reference docs, examples), draft those too.

## Step 4 — Confirm, then file

Show the user the final package — the four one-liners and the drafted SKILL.md — and get
an explicit go-ahead. Then create **one** new page in the data source above.

**Properties are one-liners** (the table view is a scannable queue; full detail goes in
the page body):

- `Skill idea` (title) — the working name.
- `What should it do` — one sentence.
- `Current manual process` — one line (e.g. "Manual pull + spreadsheet every Monday — full steps in the page").
- `Proof / example output` — the link itself, or one line saying where proof lives.
- `Status` = `Suggested` — never any other value.
- `Submitted by` — the current Notion user, if your connector can set a person property;
  if it can't, skip it.

**Page body** (Notion markdown), in this order:

```
# What it should do
<full description: inputs → what Claude does → deliverable>

# Current manual process
<numbered steps, as the user described them>

# Proof / example output
<links to real outputs; note if proof is still to come>

# Proposed SKILL.md
<the complete draft in a fenced ```markdown code block>
```

If there are supporting files, add each under its own heading
(`# Proposed <filename>`) in its own fenced code block.

## Step 5 — Verify and hand over (REQUIRED)

Fetch the created row back. Confirm the title, `Status = Suggested`, and that the body
contains the `Proposed SKILL.md` code block intact. Then give the user the row's URL and
set expectations: suggestions are reviewed weekly, and they'll hear back on the row
itself. If the fetch-back fails or the row is wrong, fix or recreate it before telling
the user it's done.

## No-Notion fallback

Output the full package — the four one-liners plus the drafted SKILL.md — as a tidy
copy-paste block, link the AI Ops hub
(`https://app.notion.com/p/399568ace9cf810ebb0af09f3305b7b9`), and tell the user to add
it as a new row in **Suggest a skill** (one-liners in the fields, everything else in the
page body) — and to enable the Notion connector so this is automatic next time.

## Guardrails

- One row per suggestion. Never edit or delete existing rows; never touch the Skill
  catalog database.
- Never set `Status` to anything but `Suggested` — Reviewing/Approved/Rejected are the
  reviewer's moves.
- The drafted SKILL.md is a **proposal**: tell the user the reviewer may edit it before
  certifying. Don't promise approval, a delivery date, or anything beyond "reviewed
  weekly".
- Never pad the draft with invented steps, tools, or checks the user didn't describe —
  a short honest draft beats a plausible-looking fabrication.
- If the "suggestion" is really a bug report about an existing certified skill, don't
  file a near-duplicate skill idea — tell them to flag it to AI Ops against that skill.
