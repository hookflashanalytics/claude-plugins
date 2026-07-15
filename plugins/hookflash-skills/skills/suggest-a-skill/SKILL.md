---
name: suggest-a-skill
description: Suggest a new Hookflash skill (or promote a personal skill you've built) — checks the idea against the certified skill list, drafts the complete skill file with you if it doesn't exist yet, and files a review-ready suggestion in the Suggest-a-skill backlog in Notion. Use when the user runs /suggest-a-skill, asks to suggest/propose/submit a skill idea, says "can we get a skill that…" or "I wish Claude could…" about a repeatable team job, or wants a personal skill certified for the whole team.
---

# Suggest a skill

File a **review-ready** skill suggestion into the **Suggest a skill** database in the
Notion AI Ops hub. Review-ready means the reviewer opens the row and finds a finished
draft — the complete proposed `SKILL.md`, written here while you have the submitter's
full context — not a wish they'd have to interpret.

Testing is the submitter's responsibility, not a gate: review checks for duplicates and
fit, so a skill that doesn't work as intended comes back on the submitter. Encourage
testing before submission; never block on it.

## Prerequisites (read first)

- **Notion connector required** to file the row. If this session has no Notion tools,
  skip to **No-Notion fallback** below — never claim a row was created when it wasn't.
- Target: the **Suggest a skill** database in the AI Ops hub —
  page `https://app.notion.com/p/5d84a8b44163453ca18757436d917950`,
  data source `collection://0cccdf72-2485-4ab7-8efe-2ef3c9dc8fd7`.

## Step 1 — Route, and gather the one-liners

Ask (or infer from context): **does this already exist as a personal skill — a written
procedure they've actually run?**

- **Yes** → have them paste or upload the `SKILL.md`. If it doesn't meet the house
  conventions in Step 3, tidy it with them (content unchanged, structure fixed), then
  skip to Step 4.
- **No** (usually they're suggesting off freeform work they've just done) → you'll
  draft it in Step 3.

Along the way, collect the one-liners — from context or a quick ask, never an
interrogation: **Skill idea** (short working name), **What it should do** (one
sentence), **Current manual process** (one line — how the job is done today), and
**Proof / example output** (a link to a real output if one exists; optional, but tell
them it's the fast lane at review).

## Step 2 — Overlap check (before drafting)

Compare the idea against the certified skills already installed from this plugin (the
hookflash-skills names and descriptions available in this session).

- **Overlap or a tweak of an existing skill** → name the existing skill and explain the
  house rule: preference tweaks stay personal; improvements belong to the canonical skill.
  Offer to reframe the suggestion as "Improve <existing-skill>: …". If they still want a
  new skill filed, continue — the reviewer decides; you only set expectations.
- **No overlap** → proceed.

## Step 3 — Draft the complete skill file (when none exists)

Write the full `SKILL.md` now, with the user, grounding every step in the work they
actually did (ideally the freeform job from this very chat) — never invent procedure to
fill space. House conventions the draft must follow:

- **Frontmatter:** `name` in kebab-case; `description` that opens with what the skill
  does, then "Use when the user runs /<name>, …" — the description drives triggering,
  so include the phrasings a colleague would actually type.
- **Structure:** short intro; numbered steps; required inputs marked
  "REQUIRED — ask if missing; never guess"; a **verify step** if the skill produces an
  artifact (render/inspect the output before handing it over); a **Guardrails** section.
- **Grounding:** name the real tools/connectors each step uses only if the user actually
  used them — otherwise describe the step plainly and leave tooling to the reviewer.

Iterate until the user says the draft matches how the job should work. If the skill
needs supporting files (reference docs, examples), draft those too. Offer to help them
save the draft as a personal skill (Cowork/claude.ai: add it as a personal
skill/capability in settings; Claude Code: `~/.claude/skills/<name>/SKILL.md`) — that's
how they can test it in a fresh chat before or after submitting.

## Step 4 — The note, then confirm and file

Show the user the final package — the four one-liners and the skill file — together
with this note, verbatim:

> **Note: Please test this skill before submission. We review skills in Notion to
> prevent duplicates, but ensuring they work as intended is the submitter's
> responsibility.**

If they'd rather test first, help them set up (Step 3's personal-skill install) and
stop — they can run /suggest-a-skill again when ready. On an explicit go-ahead, create
**one** new page in the data source above.

**Properties are one-liners** (the table view is a scannable queue; full detail goes in
the page body):

- `Skill idea` (title) — the working name.
- `What should it do` — one sentence.
- `Current manual process` — one line.
- `Proof / example output` — the link itself, or one line saying where proof lives
  (leave empty if there is none).
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
<links to real outputs, and whether the submitter has tested the skill; "none yet" is
an honest and acceptable answer>

# Proposed skill file
<the complete SKILL.md in a fenced ```markdown code block>
```

If there are supporting files, add each under its own heading (`# Proposed file:` plus
the filename in backticks) in its own fenced code block. In body prose and headings,
always wrap filenames like `SKILL.md` in backticks — Notion auto-links bare filenames
ending in `.md` into broken URLs.

## Step 5 — Verify and hand over (REQUIRED)

Fetch the created row back. Confirm the title, `Status = Suggested`, and that the body
contains the proposed skill file's code block intact. Then give the user the row's URL
and set expectations: suggestions are reviewed weekly, and they'll hear back on the row
itself. If the fetch-back fails or the row is wrong, fix or recreate it before telling
the user it's done.

## No-Notion fallback

Output the full package — the four one-liners plus the drafted skill file — as a tidy
copy-paste block (include the Step 4 note), link the AI Ops hub
(`https://app.notion.com/p/399568ace9cf810ebb0af09f3305b7b9`), and tell the user to add
it as a new row in **Suggest a skill** (one-liners in the fields, everything else in the
page body) — and to enable the Notion connector so this is automatic next time.

## Guardrails

- One row per suggestion. Never edit or delete existing rows; never touch the Skill
  catalog database.
- Never set `Status` to anything but `Suggested` — Reviewing/Approved/Rejected are the
  reviewer's moves.
- Always show the Step 4 note before filing — never submit on the user's behalf without
  it and their explicit go-ahead.
- Be honest in the Proof section: never imply the skill was tested when it wasn't.
- The drafted skill file is a **proposal**: tell the user the reviewer may edit it
  before certifying. Don't promise approval, a delivery date, or anything beyond
  "reviewed weekly".
- Never pad a draft with invented steps, tools, or checks the user didn't describe —
  a short honest draft beats a plausible-looking fabrication.
- If the "suggestion" is really a bug report about an existing certified skill, don't
  file a near-duplicate skill idea — tell them to flag it to AI Ops against that skill.
