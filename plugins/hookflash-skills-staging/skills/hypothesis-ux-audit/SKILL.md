---
name: hypothesis-ux-audit
description: >-
  Audit a live page against UX / CRO best practice and hand back two web-page
  links (desktop view + mobile view) showing the user's own page with the
  problem areas highlighted — hover or tap a numbered box to see the finding,
  severity and recommended change — then an offer to turn chosen fixes into a
  mockup via /hypothesis-mock-up. Use when the user runs /hypothesis-ux-audit, asks for a
  UX audit / CRO audit / heuristic review of a page, asks "what's wrong with
  this page" or "why isn't this page converting", or wants test-hypothesis
  ideas for a specific URL. Input is just a URL (or a screenshot if the page
  is gated). Not for site-wide technical SEO or page-speed audits — those are
  the Tapa crawler and speed-audit skills.
---

# /hypothesis-ux-audit — show the page its problems

You audit **one page** against UX / CRO best practice and hand back a tight
findings list plus **two links — desktop and mobile — to the page itself
with the problem areas highlighted**: the full-page screenshot rendered as a
web page at true size, where hovering or tapping a numbered box reveals the
finding, its severity and the recommended change. Every finding is a
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
3. **Try a single full-page shot first:** read
   `document.documentElement.scrollHeight`, resize the window to
   `(width, scrollHeight)`, screenshot once, resize back. **Then prove it
   worked:** the saved image's height ÷ width must equal
   `scrollHeight ÷ viewportWidth` within 2%. Browser panes often silently
   clamp tall viewports — if the ratio is off, the shot is partial:
   discard it and tile-and-merge instead. Never patch a partial shot with
   CSS.
4. **Tile-and-merge** (the expected path when tall viewports are clamped).
   The merge happens in an image tool BEFORE the HTML exists — the
   deliverable never sees tiles:
   - Disable smooth scrolling; hide `position:fixed`/`sticky` elements
     after the first tile (or they repeat in every tile).
   - Scroll one viewport at a time; after each scroll read the **actual**
     `window.scrollY` (never assume it landed where you asked) and keep
     tile → scrollY pairs.
   - Screenshots come out larger than CSS pixels (devicePixelRatio,
     usually 1.5–2×). Compute `s = tileImageWidth ÷ viewportCssWidth`,
     make a canvas of `tileImageWidth × round(scrollHeight × s)`
     (Python/PIL in the session, or an offscreen canvas), and paste each
     tile at `y = round(scrollY × s)`. Exact offsets make overlaps
     invisible — no guessed percentages anywhere.
   - Run the same ratio check as step 3 on the merged file.
5. **Record coordinates in document space, in the same settled state:** for
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

- **Exactly ONE `<img>` per file** — the merged full-page screenshot from
  Step 1, embedded as a data URI, `display:block; width:100%` of its
  column, wrapped in a `position:relative` div. The deliverable never
  contains tiles: no stacked images, no aspect-ratio boxes, no
  negative-margin crops.
- **Show the image whole and never enlarged.** The `<img>` width is always
  exactly 100% of its column — never more (an oversized width like `190%`
  plus `overflow:hidden` crops the page off-screen; this class of hack is
  banned). devicePixelRatio only makes the file sharper, it is handled by
  downscaling, never by cropping.
- **The desktop screenshot sits in a centred column, ~60% of the window
  width**, on a plain dark background, and additionally never wider than
  the capture's CSS width (`width:60vw; max-width:1280px; margin:0 auto` —
  the max-width stops the image rendering bigger than the real site, which
  reads as "zoomed in"). The column holds the image alone: no card, no
  border, no padding, nothing above or below it but the header bar.
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

1. **The page looks like the real site, not a zoom or a crop:** compare
   the rendered top of the page against the live site at the same window
   size — text and elements the same visual size (not blown up), nothing
   cut off at the left or right edge, the full page top-to-bottom in one
   piece with no seams, gaps, or repeated headers/banners (merge
   artefacts). The desktop column sits centred at ~60% of the window.
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
