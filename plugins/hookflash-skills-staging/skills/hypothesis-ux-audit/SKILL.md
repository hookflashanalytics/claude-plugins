---
name: hypothesis-ux-audit
description: >-
  Audit a live page against UX / CRO best practice and hand back two web-page
  links (desktop view + mobile view) showing the user's own page full-bleed
  with the problem areas highlighted — hover or tap a numbered box to see the
  finding, severity and recommended change — then an offer to turn chosen
  fixes into a mockup via /hypothesis-mock-up. Use when the user runs /hypothesis-ux-audit, asks for a
  UX audit / CRO audit / heuristic review of a page, asks "what's wrong with
  this page" or "why isn't this page converting", or wants test-hypothesis
  ideas for a specific URL. Input is just a URL (or a screenshot if the page
  is gated). Not for site-wide technical SEO or page-speed audits — those are
  the Tapa crawler and speed-audit skills.
---

# /hypothesis-ux-audit — show the page its problems

You audit **one page** against UX / CRO best practice and hand back a tight
findings list plus **two links — desktop and mobile — to the page itself
with the problem areas highlighted**: the full-page screenshot rendered
full-bleed as a web page, where hovering or tapping a numbered box reveals
the finding, its severity and the recommended change. Every finding is a
candidate test hypothesis; the skill ends by offering to mock the fixes up.

**Only flag what you can see.** Every finding must point at observable
evidence on the captured page — no boilerplate findings, no guesses about
analytics you haven't seen, no padding the list to look thorough. Five real
findings beat fifteen generic ones.

## Inputs

1. **Page URL** — that's it. Optional extras if offered: the page's goal or
   KPI (e.g. "PDP, add-to-basket"), and device focus.

**Ask at most ONE clarifying question.** If the page's purpose isn't obvious
and no goal was given, that's the one question worth asking, since severity
depends on it. If the page can't be reached (login/geo/bot wall), ask for a
full-page screenshot instead and audit that (skip the live-measurement parts
below).

## Step 1 — Capture (one seamless image per viewport, exact coordinates)

Use whichever browser tools are connected (Cowork/Claude Code browser pane,
or Claude in Chrome). Run this whole procedure twice: **desktop at 1280
wide, then mobile at 375 wide.** Both always — half the findings only exist
on one of them.

1. Fresh tab, navigate, dismiss/decline any consent banner (most
   privacy-preserving option), confirm the page loaded properly.
2. **Settle the page before measuring anything:** scroll to the bottom in
   viewport-sized steps (triggers lazy-loaded images and modules), wait for
   the network to go quiet, scroll back to top. Element positions recorded
   before lazy-load settles are wrong by the height of everything that
   loaded in — this is the #1 cause of misplaced highlights.
3. **Capture in ONE shot, not tiles.** Read
   `document.documentElement.scrollHeight`, then resize the window to
   `(width, scrollHeight)` and take a single screenshot — the whole page in
   one seamless image, no stitching. Then resize back. Only if the tool
   refuses a viewport that tall, fall back to tiling — and then the tiles
   MUST be merged into one image before the HTML is built (see Step 3);
   when tiling: disable smooth scrolling, hide `position:fixed`/`sticky`
   elements after the first tile (or they repeat in every tile), scroll,
   and record the **actual** `window.scrollY` after each scroll — never
   assume it landed where you asked.
4. **Record coordinates in document space, in the same settled state:** for
   each candidate problem element,
   `getBoundingClientRect()` + `window.scrollY`, alongside the
   `scrollHeight` and viewport width they were measured at. These three
   numbers must come from the same page state as the screenshot — remeasure
   if anything reflowed. Never eyeball coordinates from the screenshot.

## Step 2 — Audit

Judge the page against this checklist, in the context of its goal. For each
finding record: **what** (one plain sentence), **where** (element + which
viewport), **why it matters** (tie to the page goal), **severity**
(High / Medium / Low), and **the recommended change** written as a concrete,
mockable edit ("move X above Y", "rewrite headline to lead with Z").

- **Value proposition** — can a first-time visitor tell what this is and why
  it's worth it within the first screen? Is the headline about the user or
  about the company?
- **Primary CTA** — one obvious next step? Visible without scrolling on both
  viewports? Does its label say what happens next? Do secondary actions
  compete with it?
- **Visual hierarchy** — does the layout order match the importance order?
  Dead zones, banner blindness traps, or walls of equal-weight elements?
- **Trust** — social proof, reviews, guarantees, delivery/returns clarity
  near the point of decision; anything that looks broken or placeholder-ish
  (trust killers).
- **Friction** — forms asking more than they need, hidden costs appearing
  late, dead ends, steps that could be removed.
- **Content scannability** — heading structure, paragraph length, jargon;
  can the page be skimmed in 10 seconds?
- **Mobile specifics** — tap-target size/spacing, sticky elements eating the
  viewport, content order after reflow, thumb reach for the primary CTA.
- **Accessibility basics** (observable ones) — text contrast, text embedded
  in images, focus/affordance of interactive elements, alt text where
  inspectable.

Severity is about the **page goal**: a Low-contrast footnote is Low; a
primary CTA below the fold on mobile is High.

**Never claim something is absent without asking the DOM.** Before writing
any finding of the form "there is no X" or "nothing here does Y" (no H1, no
CTA, nothing clickable in the hero, no reviews), run the query that would
find it — `document.querySelector('h1')`,
`heroEl.querySelectorAll('a,button,[role=button]')`, and so on. If the
element exists but is weak, the finding is "too small / too faint / too
buried", stated with its measured size or contrast — not "missing". One
finding disproved by a one-line DOM query costs the whole audit its
credibility.

## Step 3 — Build the annotated pages (the page IS the deliverable)

Build **one self-contained `.html` file per viewport** (desktop and mobile).
Each file is the user's page, annotated — not a report *about* the page:

- **Exactly ONE `<img>` per file, and it IS the page body.** Embed the
  full-page screenshot as a data URI in an `<img>` with
  `display:block; width:100%`, wrapped in a `position:relative` div. If
  capture had to tile, merge the tiles into a single image FIRST (offscreen
  `<canvas>` drawn at the recorded scrollY offsets, exported once) — never
  stack multiple `<img>` tiles with aspect-ratio boxes or negative-margin
  crops in the deliverable; that is where seams and drift come from.
- **The desktop file fills the whole browser width.** No `max-width`, no
  centring, no visible page background beside the screenshot at any window
  size — the image scales with the window. (Only the mobile file is a
  centred phone-width column, per below.)
- **Highlight boxes are positioned in percentages of the document CSS
  size** you recorded at capture: `left = x / viewportWidth * 100%`,
  `top = (rect.top + scrollY) / scrollHeight * 100%`, same for
  width/height. Because both the boxes and the image scale together,
  device-pixel-ratio and window size drop out — but ONLY if all numbers
  came from the same settled page state. Never eyeball coordinates. Border
  colour by severity (red/amber/yellow), a small severity-coloured number
  badge on the corner, nothing that obscures the content being criticised.
- **The finding lives in a tooltip, not a legend.** On hover (desktop) and
  tap (mobile — hover doesn't exist on touch), the box shows: number,
  severity, the finding in one sentence, and the recommended change. Flip
  the tooltip's side when the box is near a viewport edge so it never
  clips. Tap again or tap elsewhere to dismiss.
- The only furniture allowed: a **slim fixed header bar** — page URL, audit
  date, severity key, and a "hover or tap a highlight" hint. No prose
  sections, no findings list on the page; detail lives in the tooltips and
  the chat report.
- The **mobile file** renders the 375px capture at its natural CSS width,
  centred on a plain dark background, so it reads as a phone view on any
  screen. Same tooltips, tap-driven.

**Deliver as two links.** Publish each file as a web page and hand back one
link for desktop and one for mobile (in Claude Code / Cowork, the Artifact
tool; in web chat, two artifacts). Published pages block external requests,
which is why the screenshot must be a data URI. If publishing isn't
available in the session, fall back to sending the two `.html` files and
opening the desktop one in the browser pane.

**Verify the published links, not just the files (ADR-0006):** open each
link and check, in order:

1. **Full-bleed:** at a wide window (~1900px) the desktop screenshot spans
   edge to edge — no gutters beside it, no gaps or repeated
   headers/banners inside it (stitching artefacts).
2. **Every box, individually:** zoom into each numbered box and confirm the
   element its finding describes sits inside it. If boxes are all offset
   the same way, the total-height or scrollY numbers are stale — remeasure
   and rebuild; do not nudge boxes by hand to compensate. A mislabelled
   highlight is worse than none.
3. **Tooltips:** appear on hover and on tap, don't clip at the edges.

Fix and republish until right (at most three rounds).

## Step 4 — Report

In chat, alongside the two links:

- Findings table: `# | Severity | Finding | Recommended change`, ordered by
  severity, numbers matching the highlight boxes.
- One-paragraph overall read of the page against its goal.
- **No em dashes in the report or annotation text** (client-facing house
  style — commas, colons, or shorter sentences).

## Step 5 — Offer the mockup handoff

End with one question: **"Want any of these actioned into a mockup?"** —
let the user pick finding numbers. If they do, run `/hypothesis-mock-up`
with the same URL and the chosen recommendations as the change list, and
pass along the screenshots and element measurements you already captured so
it doesn't re-capture.

## Notes

- Page speed, Core Web Vitals and technical SEO are out of scope — point the
  user at `/tapa-page-speed-audit`, `/tapa-full-site-speed-audit` or the
  crawler skills instead of duplicating them here.
- If the user gives several URLs, audit them one at a time (one annotated
  page each) rather than blending findings.
