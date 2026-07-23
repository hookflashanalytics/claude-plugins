---
name: qa-datalayer
description: QA a site's ecommerce dataLayer / GA4 events by driving a connected Chrome browser, walking the funnel, capturing each event's real push straight from the browser, and building an .xlsx report (one row per event) with verbatim JSON, the source it was found in, a tight screenshot of the element interacted with, and a bulleted pass/fail. Use when the user runs /qa-datalayer, asks to QA / test / verify a dataLayer, GA4 ecommerce events, GTM tracking, or a web pixel's pushes, or wants to check events like view_item, add_to_cart, begin_checkout fire with the right params.
---

# QA dataLayer

Drive the user's connected Chrome, walk an ecommerce funnel, capture each event's push, and hand back an `.xlsx`: one row per event with verbatim JSON, where it was found (top frame vs web pixel), a tight screenshot of the element that triggered it, and a bulleted verdict. Requires the Claude-in-Chrome browser tools.

**Platform-agnostic.** This works on any site (GTM, GA4/gtag, Tealium, Adobe, custom, or Shopify). The workflow (walk the funnel, capture the push, screenshot the trigger, judge coverage, verify) is the same everywhere; only the capture mechanism differs by stack. Do NOT assume Shopify: run the discovery step first (below) to learn how THIS site emits events. Shopify is called out separately only because its sandboxed web pixel is the most tedious case, treat that section as a per-platform add-on, not the default.

**Scope: the dataLayer / push layer only.** This skill QAs the data the site pushes into its `dataLayer` (or equivalent JS layer), typically after the dataLayer is implemented but BEFORE the GTM/GA4 tags that forward it are built. So there are usually no GA4 or vendor network beacons to read yet, and QAing network requests is out of scope. The source of truth is always the JS push captured in the browser, never a network request.

## Gather inputs first (use AskUserQuestion)

1. **Test URL** - page/store to start from (staging/preview is fine; any theme/preview params must survive redirects).
2. **Web pixel?** - "Are events sent via a web pixel (e.g. a Shopify custom pixel)? If so, where does it run and what is its ID?" The ID is in the DevTools Console / pixel helper. This tells you which events will live in a sandboxed iframe (see "Web-pixel events" below).
3. **dataLayer guide** - ask the user to paste their expected-coverage spec (which params should be populated vs null per event). If none, QA against the standard GA4 expectations in [REFERENCE.md](REFERENCE.md).
4. **Which events** - default to the standard set; skip `purchase` unless asked (never complete a real payment).

## Golden rules

- **Never complete a purchase.** Stop at the payment step. Pause and ask before anything irreversible, account, or payment related. Never enter real personal or payment data into checkout forms.
- **The JSON column is pulled from the browser, never rewritten.** Dump the captured object verbatim with `json.dumps(obj, indent=2)`: no truncation, no added comments. It must be byte-for-byte what fired.
- **No em dashes or en dashes anywhere in the report text.** Use commas, parentheses, or hyphens. (`build_report.py` also strips them from prose cells as a safety net.)
- **Do not screenshot any debug overlay or pixel helper.** Those are dev tools that will not exist on most sites and are irrelevant. Hide them (see below). Screenshots must show the real page and, for interactions, a tight crop of the element interacted with.
- **Output filename must be tiny.** The session output directory is already ~200 characters; a long descriptive filename blows past the Windows 259-char path limit and the workbook will not open. See "Output filename".

## Workflow

1. Open a **fresh tab**, navigate to the test URL, confirm you are on the right page (params/theme intact). Note: preview/theme params are often consumed into a session cookie and stripped from the visible URL, that is fine as long as the right theme/pixel is active (check e.g. `window.Shopify.theme.id`).
2. **Lock the viewport.** Call `resize_window` to **1280 x 900** before capturing anything. This makes the site content fill the frame (no empty gutter on full-page shots), keeps screenshot pixels ~1:1 with CSS pixels (so `getBoundingClientRect()` values can be used directly as crop regions with no scaling factor), and makes coordinates reproducible. Do not resize again mid-run.
3. **Hide dev overlays** so they never leak into a screenshot, e.g. Shopify's web-pixels helper: `document.getElementById('web-pixels-helper-sandbox-container')?.style.setProperty('display','none')`. Re-hide after each navigation.
4. **Identify how this site emits events** (do not assume). Quick probe for: `window.dataLayer` (GTM/GA4), `window.gtag`, Tealium `window.utag`, Adobe `window._satellite` / `window.digitalData`, a Shopify bus (`Shopify.analytics`), or a custom module (scan `Object.keys(window)`). See REFERENCE "Identify how the site emits events". Whichever it is, that JS push is the source of truth for the QA.
5. Install the capture hook (`scripts/capture_hook.js`) via `javascript_tool`. It wraps every common emitter it finds (`dataLayer.push`, `gtag`, Tealium `utag`, `Shopify.analytics.publish`, and any `window.tracking.*`-style builder) and installs a `pagehide` sessionStorage carry. **Re-install after every navigation** (page load wipes it). Reset with `window.__dlqa = []` before each event you trigger.
6. Walk the funnel, capturing after each trigger: PLP load (`view_item_list`) -> click a product (`select_item`) -> PDP (`view_item`, + change variant/kit to re-fire) -> add to cart from PDP **and** from the mini-bag/drawer, including any upsell/bundle add (`add_to_cart`) -> open cart/mini-bag (`view_cart`) -> remove from **both** cart page and mini-bag, testing **every** remove control incl. quantity-decrement AND the trash/remove button AND any add-on remove (`remove_from_cart`) -> checkout (`begin_checkout`) -> shipping (`add_shipping_info`) -> payment (`add_payment_info`, **stop before paying**).
7. For each event record: `source` (Top frame / Web pixel / Not fired); the push (see below); a **tight location screenshot** (see "Location screenshots"); a tight bulleted verdict judged against the dataLayer guide (see "Writing the verdict").
8. Build the report: write `events.json` (schema in REFERENCE) and run `python scripts/build_report.py events.json <screenshots_dir> <out.xlsx>`.
9. **Verify**: reopen the workbook, confirm every row has push text + a readable screenshot and nothing clips.

### Output filename (hard rule)

The output `.xlsx` name must be **short and generic: at most ~12 characters before `.xlsx`, with no client/theme/description in it** (e.g. `CB_QA.xlsx`, `dl_qa.xlsx`). Never a long descriptive name like `CurrentBody_IE_dataLayer_QA.xlsx`. Put the descriptive title (client, theme, date) inside the workbook, on the sheet/tab name or a header row, not in the filename. After saving, assert `len(full_windows_path) < 259` and shorten further if not.

## Where the event lives (set the Source column)

After triggering, read `window.__dlqa`. If the push is there, `source = "Top frame"`. If nothing appears, do not conclude "missing" yet: the event may fire in a **sandboxed / cross-origin iframe** (Shopify custom pixels and the whole Shopify checkout work this way), QA it the sandbox way (platform playbook below) and set `source = "Web pixel"`. Only if it fires nowhere, `source = "Not fired"` (a finding).

## Capturing pushes reliably

- **Hook whatever bus THIS site uses, not just `dataLayer`.** Do not assume. Sites emit through GTM (`dataLayer.push`), GA4 direct (`gtag`), Tealium (`utag`), Adobe (`_satellite` / `digitalData`), a vendor pub/sub bus (e.g. `Shopify.analytics.publish`), or a bespoke `window.tracking`-style builder. `capture_hook.js` wraps all of these that it finds. If `window.dataLayer` and `window.__dlqa` are both empty after a known event, run the discovery probe (REFERENCE) to find the emitter this site uses, then hook that.
- **Click-then-navigate events** (e.g. `select_item`, which fires just before the PDP loads) are lost because the page unloads. Capture them with the `pagehide` sessionStorage carry: the hook writes `window.__dlqa` to `sessionStorage.__dlqa_carry` on unload; read and parse it on the next page.
- **Load-only events** (e.g. `view_item_list`) fire once at document load, before any hook can be injected. Do NOT give up and mark them `warn` without exhausting the re-fire path below, they are almost always capturable. Work through these in order and stop at the first that yields a payload (see REFERENCE "Re-firing a load-only builder event" for the exact snippets):
  1. **Re-invoke the theme builder** (most reliable). With the hook installed, call the builder that produced it (e.g. `window.tracking.collectionViewed`). If it throws `... reading 'map'/'forEach'` you passed the wrong shape: read the builder's `.toString()` in-page and return ONLY the parameter's first property access (a short safe token like `products` or `items`), then re-call with the theme's own product data in that exact shape (`{ <prop>: <productObjects> }`). Get the product objects from a page JSON blob, a `window.*` product array, or `window.(ShopifyAnalytics.)meta.products`. Also try the raw array, `{products:arr}`, `{items:arr}`, `{collection:{products:arr}}`.
  2. **Trigger a real re-render** if the builder arg cannot be reconstructed: use the collection's own sort / filter / pagination / "load more" / currency toggle, which re-fires the builder client-side with the hook alive.
  3. **Only if 1 and 2 both fail**, record `push: null` with a `push_note` explaining it fires pre-hook, set `source` from the pixel subscription (it is still wired), infer the item shape from sibling events (select_item/view_item), verdict `warn`, and recommend confirming in GA4 DebugView. This is the last resort, not the default.
- **Output-filter escaping.** The browser tool blanks any result that looks like a cookie/query string (contains `?`, `=`, `&`). When returning captured JSON, escape those so the payload survives, this stays valid JSON and decodes back byte-for-byte:
  `JSON.stringify(x).replace(/\?/g,'\\u003f').replace(/=/g,'\\u003d').replace(/&/g,'\\u0026').replace(/%/g,'\\u0025')`
  `capture_hook.js` exposes this as `window.__dump(obj)`.

## Platform playbook: sandboxed web pixels (Shopify, and similar)

Applies ONLY when events fire inside a sandboxed iframe (Shopify custom pixels, the whole Shopify checkout, and a few other tag-sandbox setups). Skip this entirely on ordinary GTM/GA4/Tealium/Adobe sites, there the top-frame hook already has everything.

You cannot read a sandboxed iframe's runtime memory (the `sandbox` attribute forces an opaque origin, so `contentWindow` throws SecurityError, and its network/dataLayer are invisible to the top frame). Read the pixel's **source** instead, which is usually served from the **site's own origin**:

1. Find the pixel iframe (e.g. name contains `web-pixel-sandbox-CUSTOM-<id>`), take its `src`, and `fetch(src, {credentials:"include"}).then(r=>r.text())` from the top frame. Store in `window.__pixelSrc`.
2. Locate the event's push builder in that source and read exactly which params it sets and how (this is authoritative for coverage). Checkout events map from Shopify events: `checkout_started` -> begin_checkout, `checkout_address_info_submitted` -> add_shipping_info, `payment_info_submitted` -> add_payment_info. See [REFERENCE.md](REFERENCE.md) for the output-filter workaround when the raw minified code gets blocked.
3. Build the `push` object for the report:
   - If you can obtain the **runtime values**, use them.
   - If you cannot (the usual case for a sandbox), reproduce the **object shape from the source** and set every value you cannot read to the string `"(Can't read values in web pixel)"`. Keep the real param **keys** so coverage is still reviewable.
4. Judge coverage from the code (e.g. a param hardcoded to `null` in the builder means it is not implemented, regardless of cart state). Annotate hardcoded values, e.g. `"null (hardcoded in pixel source)"`.

## Writing the verdict (Pass / Fail column)

Keep this column tight and skimmable, it is read at a glance:

- **One short bullet per real finding.** Lead with a single "All expected parameters present" line when coverage is complete, then list only the problems.
- **Only flag what is actually wrong or risky.** Do not narrate non-issues: params that are legitimately null pre-cart, standard GA4 params that are absent but not in the spec, or item-schema differences between events that are just null/absent fields. Call out a cross-event difference only when it is a genuine inconsistency (e.g. a value typed as a string in one event and a boolean in another).
- **Say what is wrong in plain language**, e.g. "Value is set to the whole cart total, not the item being added" rather than a paragraph about `final_line_price`.
- `build_report.py` renders a blank line between bullets automatically, so keep each finding as its own bullet, never one congealed block of prose.

Example (add_to_cart), this is the whole cell:

- All expected parameters present
- Value is incorrectly set to the value of the cart, not to the item being added
- from_mini_bag and from_upsell are strings instead of booleans, which differs from view_item_list

## Location screenshots (show the trigger)

One tight, readable screenshot per event. Never embed a whole-page shot for an interaction, and never centre on a debug/pixel-helper panel.

**Interaction events** (`add_to_cart`, `remove_from_cart`, `select_item`, variant/kit change, mini-bag `+`): crop to the control itself, like a zoomed product-card or button close-up (think: just the "Add to basket" button, or just the mini-bag line with its qty stepper and trash icon).
1. Get the control's box: `const r = el.getBoundingClientRect()`.
2. Pad it so context is visible but the control dominates: ~12px each side; for a small icon button (< 60px) expand to include its row/label, aiming for a crop ~240-420px wide.
3. `el.scrollIntoView({block:'center'})`, then `computer` `zoom` with `region:[x-pad, y-pad, x+w+pad, y+h+pad]` and `save_to_disk:true`. Use that saved crop as `location_image`. Do NOT also pass `location_bbox` (the crop is already tight).
4. If nothing meaningful is visible after the click (AJAX with no visual change), capture the control in its pre-click state instead.

**Page-load events** (`view_item_list`, `view_item`, `begin_checkout`): one screenshot of the page, trimmed to the content column, not the raw window. With the viewport locked to 1280 the gutter is already minimal; if a gutter remains, `zoom` to `[0, 0, contentWidth, viewportHeight]` where `contentWidth = document.querySelector('main, #MainContent, [role=main]')?.getBoundingClientRect().right || window.innerWidth`. Prefer the buy-box / relevant section over a tall full-page dump.

Because screenshots at the locked 1280 viewport are ~1:1 with CSS pixels, `getBoundingClientRect()` values can be used directly as `zoom` regions with no scaling factor. Save every crop into the screenshots directory you pass to `build_report.py`. `build_report.py` scales every image to fit inside the screenshot column (narrower than the column), so shots never overhang into the Pass/Fail column and each row is sized to its image.

See [REFERENCE.md](REFERENCE.md) for the events.json schema, the standard GA4 coverage table, capture snippets, the pixel-source fetch technique, and the sandbox caveat.
