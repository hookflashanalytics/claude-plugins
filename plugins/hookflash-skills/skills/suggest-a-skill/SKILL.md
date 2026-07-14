---
name: suggest-a-skill
description: Suggest a new Hookflash skill (or promote a personal skill you've built) — checks the idea against the certified skill list, makes sure a working skill file plus screenshot evidence exists (drafting the skill with you and sending you off to test it if not), then files a review-ready suggestion in the Suggest-a-skill backlog in Notion. Use when the user runs /suggest-a-skill, asks to suggest/propose/submit a skill idea, says "can we get a skill that…" or "I wish Claude could…" about a repeatable team job, wants a personal skill certified for the whole team, or comes back with test screenshots for a skill drafted in an earlier chat.
---

# Suggest a skill

File a **review-ready** skill suggestion into the **Suggest a skill** database in the
Notion AI Ops hub. Review-ready means two things exist before anything is filed:

1. **A working skill file** — the complete `SKILL.md`, drafted here if it doesn't exist yet.
2. **Screenshot evidence of it working** — the submitter shows you screenshot(s) of the
   skill producing its real output. **No screenshot, no submission — no exceptions.**

Two pathways get there:

- **Path A — the skill already exists** (a personal skill they've been using):
  collect the skill file + screenshots, verify, file.
- **Path B — no skill yet** (usually they want to suggest something off freeform work
  they've just done): draft the skill with them, then **stop and send them off to test
  it in a fresh chat**. They come back with screenshots → Path A.

## Prerequisites (read first)

- **Notion connector required** to file the row. If this session has no Notion tools,
  skip to **No-Notion fallback** below — never claim a row was created when it wasn't.
- Target: the **Suggest a skill** database in the AI Ops hub —
  page `https://app.notion.com/p/5d84a8b44163453ca18757436d917950`,
  data source `collection://0cccdf72-2485-4ab7-8efe-2ef3c9dc8fd7`.

## Step 1 — Route

Ask (or infer from context): **does this already exist as a personal skill — a written
procedure they've actually run?**

- **Yes, and they can share the skill file** → Path A.
- **No — or "sort of, but it's in my head"** → Path B. A remembered habit is not a
  skill file; draft it properly.

## Step 2 — Overlap check (both paths, before any drafting)

Compare the idea against the certified skills already installed from this plugin (the
hookflash-skills names and descriptions available in this session).

- **Overlap or a tweak of an existing skill** → name the existing skill and explain the
  house rule: preference tweaks stay personal; improvements belong to the canonical skill.
  Offer to reframe the suggestion as "Improve <existing-skill>: …". If they still want a
  new skill filed, continue — the reviewer decides; you only set expectations.
- **No overlap** → proceed.

## Path B — Draft the skill, then dispatch to test (NO filing this session)

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

Iterate until the user says the draft matches how the job should work. Then:

1. **Help them save it as a personal skill** in their client (Cowork/claude.ai: add it
   as a personal skill/capability in settings; Claude Code: `~/.claude/skills/<name>/SKILL.md`).
   If they can't install skills, the test still works: paste the drafted procedure at
   the top of a fresh chat.
2. **Dispatch them, verbatim:** "Open a **new chat**, run the skill on a real job,
   screenshot the result — the output itself must be visible — then come back and run
   /suggest-a-skill again with the screenshot(s) and the skill file."
3. **STOP. Do not create the Notion row in this session.** The fresh-chat test is the
   point: it proves the skill works without this conversation's context propping it up.

## Path A — Evidence gate, then file

### A1 — Collect the two artifacts

- **The skill file:** have them paste or upload the `SKILL.md`. If it doesn't meet the
  house conventions above, tidy it with them (content unchanged, structure fixed).
- **The screenshot(s):** at least one, attached in this chat, showing the skill
  **producing its real output** — the deliverable visible on screen, from a chat that
  isn't this one. Screenshots of past runs are fine.

### A2 — Verify the evidence (the gate)

Inspect the screenshot(s) yourself. They must show the skill's actual output — a deck,
a workbook, an analysis, a filed result — consistent with what the skill claims to do.
Not acceptable: a description of what happened, a promise to test later, a screenshot
showing only a prompt with no output, or output that doesn't match the skill.

**If the evidence is missing or insufficient: do not file.** Say exactly what's needed
and route them through Path B's dispatch step. No exceptions — the reviewer will not
certify without evidence, so filing without it only queues a rejection.

### A3 — Gather the one-liners

From context or a quick ask: **Skill idea** (short working name), **What it should do**
(one sentence), **Current manual process** (one line — how the job was done before the
skill), **Proof** (one line saying what the screenshots show).

### A4 — Confirm, then file

Show the user the final package — the four one-liners, the skill file, and your reading
of the evidence — and get an explicit go-ahead. Then create **one** new page in the data
source above.

**Properties are one-liners** (the table view is a scannable queue; full detail goes in
the page body):

- `Skill idea` (title) — the working name.
- `What should it do` — one sentence.
- `Current manual process` — one line.
- `Proof / example output` — one line, e.g. "Screenshots of a real run — see Evidence in the page".
- `Status` = `Suggested` — never any other value.
- `Submitted by` — the current Notion user, if your connector can set a person property;
  if it can't, skip it.

**Page body** (Notion markdown), in this order:

```
# What it should do
<full description: inputs → what Claude does → deliverable>

# Current manual process
<numbered steps, as the user described them>

# Evidence
<your attestation: what each screenshot shows, when it was sighted, and that the
output matches the skill's claim. Then this line, verbatim:>
**Submitter: paste the screenshot(s) below this line — the reviewer will not
certify without the images present in this section.**
<plus links to any real outputs that live at a shareable URL>

# Proposed skill file
<the complete SKILL.md in a fenced ```markdown code block>
```

If there are supporting files, add each under its own heading (`# Proposed file:` plus
the filename in backticks) in its own fenced code block. In body prose and headings,
always wrap filenames like `SKILL.md` in backticks — Notion auto-links bare filenames
ending in `.md` into broken URLs.

### A5 — Verify and hand over (REQUIRED)

Fetch the created row back. Confirm the title, `Status = Suggested`, and that the body
contains the Evidence section and the proposed skill file's code block intact. Then give
the user the row's URL with the **final railroaded step**: *"Open the row and paste your
screenshot(s) into the Evidence section now — the submission isn't complete until the
images are in."* (Your Notion connector cannot upload image files, so this one drag-and-
drop is theirs.) Set expectations: suggestions are reviewed weekly; they'll hear back on
the row itself.

## No-Notion fallback

Apply the same gate: no screenshot sighted, no submission — route through Path B if
needed. Once evidence is verified, output the full package — one-liners, Evidence
attestation, and the skill file — as a tidy copy-paste block, link the AI Ops hub
(`https://app.notion.com/p/399568ace9cf810ebb0af09f3305b7b9`), and tell the user to add
it as a new row in **Suggest a skill** (one-liners in the fields, everything else in the
page body, screenshots pasted into Evidence) — and to enable the Notion connector so
this is automatic next time.

## Guardrails

- **The gate is absolute:** never file a row without having sighted screenshot evidence
  of the skill working in this chat. "I'll add proof later" → Path B dispatch, not a row.
- Evidence means the output is visible. A prompt with no result, a mock-up, or a verbal
  description is not evidence.
- One row per suggestion. Never edit or delete existing rows; never touch the Skill
  catalog database.
- Never set `Status` to anything but `Suggested` — Reviewing/Approved/Rejected are the
  reviewer's moves.
- The drafted skill file is a **proposal**: tell the user the reviewer may edit it
  before certifying. Don't promise approval, a delivery date, or anything beyond
  "reviewed weekly".
- Never pad a draft with invented steps, tools, or checks the user didn't describe —
  a short honest draft beats a plausible-looking fabrication.
- If the "suggestion" is really a bug report about an existing certified skill, don't
  file a near-duplicate skill idea — tell them to flag it to AI Ops against that skill.
