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

## Step 1 — Capture

Use whichever browser tools are connected (Cowork/Claude Code browser pane,
or Claude in Chrome).

1. Fresh tab, navigate, dismiss/decline any consent banner (most
   privacy-preserving option), confirm the page loaded properly.
2. **Desktop pass:** lock viewport to 1280×900, full-page screenshot.
3. **Mobile pass:** resize to 375×812, reload, full-page screenshot. Both
   passes always — half the findings only exist on one of them.
4. While live, record each candidate problem element's
   `getBoundingClientRect()` box (per viewport) — you need real coordinates
   for the highlights, not eyeballed ones.

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

## Step 3 — Build the annotated pages (the page IS the deliverable)

Build **one self-contained `.html` file per viewport** (desktop and mobile).
Each file is the user's page, annotated — not a report *about* the page:

- **The full-page screenshot IS the page body.** Embed it as a data URI in
  an `<img>` with `display:block; width:100%`, wrapped in a
  `position:relative` div. **Never put the screenshot inside a fixed-size
  panel, card, or frame** — no borders, no padding, no max-height, no white
  letterboxing around it. If any background is visible beside or below the
  screenshot, the layout is wrong: the image alone defines the page height.
- **Highlight boxes are positioned in percentages** of the screenshot's
  natural dimensions (`left = x/imgWidth*100%`, same for top/width/height),
  so they stay glued to their elements at any window size. Draw them from
  the recorded `getBoundingClientRect()` values — never eyeballed. Border
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
link, screenshot it, and check: no white gutters or empty panels around the
screenshot; every numbered box sits on the element its finding describes (a
mislabelled highlight is worse than none); tooltips appear on hover and on
tap and don't clip at the edges. Fix and republish until right (at most
three rounds).

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
