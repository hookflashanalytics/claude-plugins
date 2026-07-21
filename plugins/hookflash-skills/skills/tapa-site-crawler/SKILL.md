---
name: tapa-site-crawler
description: Crawl a website with Tapa's Site Crawler via the Tether MCP — a one-off crawl of up to 10,000 pages returning the full crawl CSV as a download link in chat. Use when the user runs /tapa-site-crawler, asks to crawl a site, or needs a fresh crawl file (e.g. as input for the redirect mapper, cannibalisation detector or internal link audit).
---

# Tapa Site Crawler

Crawl a site and hand back the **crawl CSV** (URLs with status codes, titles, on-page
fields and a `page_category` per page — Homepage / PDP / PLP / Article / Service / About /
Contact / Other). The deliverable is the file — this tool has no chart visualisation. The
CSV is also the natural input for `/tapa-cannibalisation-detector`, `/tapa-redirect-mapper`
and `/tapa-internal-link-audit`.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_sc_*` tools are limited to a small allow-list of
  test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_sc_*` tools are missing, the user is not on
    the allow-list: explain that Tapa skills are still in testing and access is limited to a small
    test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_sc_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tools under the Tether MCP: `tapa_sc_options`, `tapa_sc_run`, `tapa_sc_result`.
- **Works in normal claude.ai chat.** One-off crawls only — crawl *schedules* are managed in
  the Tapa UI and are deliberately not available here.

## Step 1 — Gather the inputs (ASK if the URL or CMS is missing; never guess)

- **Site URL (REQUIRED)** → `url`, the full URL including `https://`. If the user named a
  brand but not a URL, confirm the exact domain rather than guessing it.
- **Site CMS (ASK if not provided)** → `cms`. The CMS sharpens each page's `page_category`
  using that platform's URL conventions (e.g. Squarespace `/shop/p/…` is a product page,
  Shopify `/blogs/…` is an article), and it feeds the crawl dashboard's page-type
  breakdown. If the user hasn't said which platform the site runs on, ask — offer:
  Shopify, WordPress (incl. WooCommerce), Magento / Adobe Commerce, BigCommerce,
  Salesforce Commerce Cloud, Wix, Squarespace, Webflow, Drupal, or Custom / Unknown.
  If they don't know or it's custom, omit `cms` — the crawl still categorises pages with
  the generic rules. Never guess the CMS yourself, and never block a crawl on this
  question if the user has already said they don't know.
- **Page cap (OPTIONAL)** → `max_pages`. Defaults to 500; cap 10,000 (see `tapa_sc_options`).
  Only ask if the user's intent is unclear (e.g. a very large site where 500 pages won't cut
  it) — otherwise use the default silently.

## Step 2 — Run and poll

Call `tapa_sc_run` (with `cms` when the user named a platform). Crawls take minutes on
real sites:

- If it returns `answer_status: "pending"` with a `job_id`, tell the user it's crawling
  (progress reports pages crawled so far) and poll `tapa_sc_result` with that `job_id` until
  it finishes. Never abandon a pending job or start a duplicate crawl.

The finished output includes a **`download_url`** — the crawl CSV.

## Step 3 — Deliver the CSV

Put the `download_url` as a **plain clickable link in your reply** and mention it expires.
No visualisation for this tool — a one-line description of what the CSV holds is enough.
If the user wanted the crawl as input to another Tapa tool, offer to run that tool next
(the CSV can be staged straight into it).

## Guardrails

- Crawl only sites the user/client owns or manages — decline requests to crawl arbitrary
  third-party sites at scale.
- Never fabricate crawl contents; if the user asks what was found, read the CSV rather than
  guessing.
