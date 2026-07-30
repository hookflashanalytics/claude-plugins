---
name: hypothesis-mock-up
description: >-
  Turn a live page plus a list of proposed changes into a visual mockup of the
  test hypothesis — recreate the page faithfully in self-contained HTML/CSS,
  apply ONLY the listed changes, verify the render, and deliver before/after
  screenshots plus an openable HTML file, pushing the mockup into the user's
  own Figma when the Figma connector is available. Use when the user runs
  /hypothesis-mock-up, asks for a mockup / mock-up / visual of a proposed page
  change, wants to visualise an A/B test hypothesis or experiment variation
  before build, or accepts the mockup handoff at the end of
  /hypothesis-ux-audit. Not for building production code from a design — this
  produces a picture of an idea, not an implementation.
---

# /hypothesis-mock-up — visualise a test hypothesis

You produce a **mockup of a proposed change to a real page**: a faithful
HTML/CSS recreation of the current page with the requested changes applied,
delivered as before/after screenshots plus the standalone `.html` file — and,
when the user's **Figma connector** is available, the same mockup rebuilt as
an editable **Figma file in their own account**.

**Never use an image-generation model for this.** Generated images garble
copy and invent UI furniture. The whole value here is fidelity: real page,
real copy, only the listed changes.

## Inputs (two things, then go)

1. **Page URL** — the page the hypothesis applies to.
2. **The changes** — the list of modifications (usually from a test
   hypothesis or a `/hypothesis-ux-audit` handoff).

Draft everything else yourself. **Ask at most ONE clarifying question**, and
only if the change list is genuinely ambiguous (e.g. it names an element that
appears twice on the page). Device targeting: if the hypothesis says mobile,
mock mobile (375px); otherwise default to desktop (1280px). If a change
requires new copy the user didn't supply, draft it, and say in the handover
which lines are your draft.

If the page can't be reached (login wall, geo block, bot block), ask the user
for a **full-page screenshot** and work from that — that counts as your one
question. Note in the handover that measurements came from the screenshot.

## Step 1 — Capture the current page

Use whichever browser tools are connected (the Cowork/Claude Code browser
pane, or Claude in Chrome). No browser tools at all → fall back to fetching
the page HTML, and say fidelity is best-effort.

1. Open the URL in a fresh tab. **Lock the viewport** (1280×900 desktop or
   375×812 mobile) before capturing; don't resize mid-run.
2. Take a **full-page screenshot** — this is the "before" and your
   reference. First scroll to the bottom in steps and back (settles
   lazy-loaded content), then capture in ONE shot: read
   `document.documentElement.scrollHeight`, resize the window to
   `(width, scrollHeight)`, screenshot once, resize back — and check the
   image's height ÷ width matches `scrollHeight ÷ viewportWidth` (browser
   panes silently clamp tall viewports; if the ratio is off the shot is
   partial). If clamped, capture viewport tiles at recorded `scrollY`
   offsets and merge them into ONE image with an image tool (paste at
   `scrollY × devicePixelRatio`) — never stitch tiles in the deliverable's
   HTML/CSS; seams and misalignment follow.
3. Read the real design facts for the region you'll rebuild: computed styles
   (font family/size/weight, colours, spacing), exact copy, and image URLs.
   `getBoundingClientRect()` + `getComputedStyle()` via the JS tool beat
   guessing from the screenshot.

## Step 2 — Rebuild in HTML/CSS, apply the changes

Build **one self-contained `.html` file** (all CSS inline, real copy, real
image URLs; embed small images as data URIs if the file must work offline).

Scope: recreate the **smallest region that gives the change context** —
usually the viewport-height section containing every changed element, not the
whole page. If changes are scattered, recreate the full page.

Hard rules:

- **Apply ONLY the listed changes.** Everything else is copied faithfully —
  do not "improve" spacing, restyle buttons, or tidy copy that wasn't in the
  list. The mockup's credibility rests on the diff being exactly the
  hypothesis.
- **Never invent content** beyond what the changes require. Prices, product
  names, reviews, imagery: real page values only.
- **No em dashes in any on-page copy you draft** (client-facing house style —
  use a comma, colon, or shorter sentence).
- Build both states from the same file where practical (an `original` /
  `variation` toggle or two stacked sections) so the diff is easy to eyeball.

## Step 3 — Verify the render (mandatory, ADR-0006)

**Never deliver a mockup you haven't looked at.** Open your `.html` in the
browser, screenshot it, and compare against the "before" screenshot:

- fonts, colours and spacing match the real page (aside from the changes)
- every requested change is present and nothing else moved
- no broken images, overflowing text, or layout collapse

Fix and re-render until it passes — **at most three rounds**, then ship the
best version and state what's still off.

## Step 4 — Deliver (always, Figma or not)

1. **Before/after screenshots** in chat, changes summarised in one line each.
2. **The `.html` file** — tell the user they can open it in Chrome (or any
   browser) to see it full-size; in Cowork/Code, open it in the browser pane
   for them; in web chat, deliver it as an artifact.
3. Offer one round of tweaks — that's an edit to the HTML and a re-verify,
   cheap by design.

## Step 5 — Figma (if the connector is there; otherwise say how to get it)

**If Figma MCP tools are available** (e.g. `use_figma`,
`create_new_file`, `get_design_context`):

- Follow the Figma plugin's own skills — `figma-create-new-file` to make a
  fresh Design file, then `figma-generate-design` to translate your HTML
  recreation into real Figma frames (auto-layout, text styles, both
  Original and Variation frames side by side).
- Verify in Figma the same way as Step 3: screenshot the frames, compare to
  your HTML render, fix drift.
- Hand back the Figma file link. The file lands in the **user's own Figma
  account** — that's the point.

**If Figma tools are NOT available**, deliver Step 4 in full anyway, then
tell the user, in plain English:

> The mockup above is final either way — but if you'd like it as an
> **editable Figma file** in your own Figma account, add the **Figma**
> connector (Settings → Connectors → Figma, sign in with your Figma login),
> then start a **new chat** and run `/hypothesis-mock-up` again — or just ask
> me to "push that mockup to Figma".

Don't block on Figma, don't ask them to set it up before showing the mockup,
and never try to write to Figma any other way (there is no server-side route;
the user's own connector is the only authorised path).

## Notes

- Pairs with `/hypothesis-ux-audit`: its findings become this skill's change
  list. When invoked from that handoff, reuse the audit's captured
  screenshots and measurements — don't re-capture.
- This mockup is a **communication artifact for a hypothesis**, not a build
  spec. Say so in the handover if the user starts treating pixel positions
  as gospel.
