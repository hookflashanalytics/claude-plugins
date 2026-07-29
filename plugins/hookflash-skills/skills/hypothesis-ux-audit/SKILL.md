---
name: hypothesis-ux-audit
description: >-
  Audit a live page against UX / CRO best practice and show the user their own
  page with the problem areas visually highlighted — numbered boxes drawn over
  a full-page screenshot, each keyed to a finding with severity, evidence and
  a recommendation, then an offer to turn chosen fixes into a mockup via
  /hypothesis-mock-up. Use when the user runs /hypothesis-ux-audit, asks for a
  UX audit / CRO audit / heuristic review of a page, asks "what's wrong with
  this page" or "why isn't this page converting", or wants test-hypothesis
  ideas for a specific URL. Input is just a URL (or a screenshot if the page
  is gated). Not for site-wide technical SEO or page-speed audits — those are
  the Tapa crawler and speed-audit skills.
---

# /hypothesis-ux-audit — show the page its problems

You audit **one page** against UX / CRO best practice and hand back two
things: a tight findings list, and **the page itself with the problem areas
highlighted** — numbered boxes over a full-page screenshot the user can open
in their browser. Every finding is a candidate test hypothesis; the skill
ends by offering to mock the fixes up.

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

## Step 3 — Build the annotated page

Build **one self-contained `.html` file**: the full-page screenshot embedded
as a data URI, with absolutely-positioned numbered highlight boxes drawn from
the recorded coordinates, and a findings legend (number → severity → one-line
finding) alongside or beneath. One annotated image per viewport you found
issues on. Red/amber/yellow border by severity; keep the boxes crisp, no
overlays that obscure the content being criticised.

**Verify before handover (ADR-0006):** open the file in the browser,
screenshot it, and check every numbered box actually sits on the element its
finding describes — a mislabelled highlight is worse than none. Fix and
re-render until right (at most three rounds).

Deliver: open it in the browser pane for the user (Cowork/Code), and hand
over the `.html` file so they can open it in Chrome; in web chat, deliver it
as an artifact.

## Step 4 — Report

In chat, alongside the annotated page:

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
