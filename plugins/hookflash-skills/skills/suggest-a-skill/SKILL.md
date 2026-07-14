---
name: suggest-a-skill
description: Suggest a new Hookflash skill (or promote a personal skill you've built) — a guided interview that checks the idea against the certified skill list, then files it in the Suggest-a-skill backlog in Notion for AI Ops review. Use when the user runs /suggest-a-skill, asks to suggest/propose/submit a skill idea, says "can we get a skill that…" or "I wish Claude could…" about a repeatable team job, or wants a personal skill certified for the whole team.
---

# Suggest a skill

File a well-formed skill suggestion into the **Suggest a skill** database in the Notion
AI Ops hub, where AI Ops reviews suggestions in a weekly batch. Certified skills need two
things (say this up front if the user seems unsure): **proof it works** — a real output,
not a promise — and a **genuinely new use case** — formatting or preference tweaks of an
existing skill stay personal.

## Prerequisites (read first)

- **Notion connector required** to file the row. If this session has no Notion tools,
  skip to **No-Notion fallback** below — never claim a row was created when it wasn't.
- Target: the **Suggest a skill** database in the AI Ops hub —
  page `https://app.notion.com/p/5d84a8b44163453ca18757436d917950`,
  data source `collection://0cccdf72-2485-4ab7-8efe-2ef3c9dc8fd7`.

## Step 1 — Interview (gather four fields, one pass)

Collect conversationally — if their first message already covers a field, use it; draft
wording for them rather than interrogating:

1. **Skill idea** — a short working name for the job (e.g. "Monthly client SEO health summary").
2. **What should it do** — inputs → what Claude does → deliverable, in 2–4 sentences.
3. **Current manual process** — how they do this job today, step by step. This is what
   makes a skill certifiable; push gently for the real steps, not "I just do it".
4. **Proof / example output** — a link to (or attachment of) at least one real output.
   If they've already done the job with Claude — via a personal skill or ad hoc — that
   artifact is the fast lane to certification. No proof yet? The suggestion can still be
   filed, but tell them the reviewer will ask for proof before certifying.

## Step 2 — Overlap check (before filing)

Compare the idea against the certified skills already installed from this plugin (the
hookflash-skills names and descriptions available in this session).

- **Overlap or a tweak of an existing skill** → name the existing skill and explain the
  house rule: preference tweaks stay personal; improvements belong to the canonical skill.
  Offer to file it as "Improve <existing-skill>: …" instead. If they still want it filed
  as a new skill, file it — the reviewer decides; you only set expectations.
- **No overlap** → proceed.

## Step 3 — Confirm, then file

Show the user the four fields exactly as you'll submit them and get an explicit
go-ahead. Then create **one** new page in the data source above with properties:

- `Skill idea` (title), `What should it do`, `Current manual process`,
  `Proof / example output` — from the interview.
- `Status` = `Suggested` — never any other value.
- `Submitted by` — the current Notion user, if your connector can set a person property
  (look up your own identity via the connector's self/user lookup); if it can't, skip it.

## Step 4 — Verify and hand over (REQUIRED)

Fetch the created row back. Confirm the title and `Status = Suggested`, then give the
user the row's URL and set expectations: suggestions are reviewed weekly, and they'll
hear back on the row itself. If the fetch-back fails or the row is wrong, fix or recreate
it before telling the user it's done.

## No-Notion fallback

Output the four fields as a tidy copy-paste block, link the AI Ops hub
(`https://app.notion.com/p/399568ace9cf810ebb0af09f3305b7b9`), and tell the user to add
them as a new row in **Suggest a skill** — and to enable the Notion connector so this is
automatic next time.

## Guardrails

- One row per suggestion. Never edit or delete existing rows; never touch the Skill
  catalog database.
- Never set `Status` to anything but `Suggested` — Reviewing/Approved/Rejected are the
  reviewer's moves.
- Don't promise approval, a delivery date, or anything beyond "reviewed weekly".
- If the "suggestion" is really a bug report about an existing certified skill, don't
  file a near-duplicate skill idea — tell them to flag it to AI Ops against that skill.
