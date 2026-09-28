---
name: qa-datalayer
description: QA a site's ecommerce dataLayer / GA4 events by driving a connected Chrome browser, walking the funnel, capturing each event's real push straight from the browser, and filling in the team's dataLayer QA checklist (.xlsx) - one block per event with Pass / Fail per parameter for "present" and "value correct", statuses rolled up on a Summary tab, and every push kept verbatim with a tight screenshot of what triggered it. Tests against a prefilled QA checklist (the DataLayer Doc Creator's "Export a QA Checklist", or the QA team's own), a dataLayer guide, or standard GA4 expectations. Use when the user runs /qa-datalayer, asks to QA / test / verify a dataLayer, GA4 ecommerce events, GTM tracking, or a web pixel's pushes, wants a QA checklist filled in from a live site, or wants to check events like view_item, add_to_cart, begin_checkout fire with the right params.
---

# QA dataLayer

Drive the user's connected Chrome, walk an ecommerce funnel, capture each event's push, and hand back the team's **dataLayer QA checklist**, filled in: one block per event tested, a row per expected parameter with **Present / fired?** and **Value correct?** set to Pass / Fail / N/A, block statuses that roll up to a Summary tab, and a **Captured pushes** tab holding each push verbatim, where it was found (top frame vs web pixel) and a tight screenshot of the element that triggered it. It is the same workbook the QA team fills in by hand and Tapa's DataLayer Doc Creator exports prefilled, so a tester can pick it up and carry on. Requires the Claude-in-Chrome browser tools.

**Platform-agnostic.** This works on any site (GTM, GA4/gtag, Tealium, Adobe, custom, or Shopify). The workflow (walk the funnel, capture the push, screenshot the trigger, judge coverage, verify) is the same everywhere; only the capture mechanism differs by stack. Do NOT assume Shopify: run the discovery step first (below) to learn how THIS site emits events. Shopify is called out separately only because its sandboxed web pixel is the most tedious case, treat that section as a per-platform add-on, not the default.

**Scope: the dataLayer / push layer only.** This skill QAs the data the site pushes into its `dataLayer` (or equivalent JS layer), typically after the dataLayer is implemented but BEFORE the GTM/GA4 tags that forward it are built. So there are usually no GA4 or vendor network beacons to read yet, and QAing network requests is out of scope. The source of truth is always the JS push captured in the browser, never a network request.

**Once the tags are built, that job belongs to `/qa-network-requests`**, which reads the outgoing hits and their payloads instead. If the user wants both, run this one first: a push that looks perfect here can still arrive at the vendor mangled by the tag mapping.

## Gather inputs first (use AskUserQuestion)

1. **Test URL** - page/store to start from (staging/preview is fine; any theme/preview params must survive redirects).
2. **Web pixel?** - "Are events sent via a web pixel (e.g. a Shopify custom pixel)? If so, where does it run and what is its ID?" The ID is in the DevTools Console / pixel helper. This tells you which events will live in a sandboxed iframe (see "Web-pixel events" below).
3. **What to test against** - in order of preference:
   - **A QA checklist `.xlsx`**: the one Tapa's DataLayer Doc Creator exports ("Export a QA Checklist"), one the QA team built, or a previous run of this skill. It already lists every event and its expected parameters. Convert it with `python scripts/checklist_to_spec.py <checklist.xlsx> spec.json`; checks already filled in come across too.
   - **The dataLayer guide** (the Doc Creator's deck, a PDF, or a pasted spec). Read each event's parameter table into the same spec shape (REFERENCE "The spec").
   - **Nothing**: QA against the standard GA4 expectations in [REFERENCE.md](REFERENCE.md).
4. **Which events** - default to the spec's events (or the standard set); skip `purchase` unless asked (never complete a real payment).

## Golden rules

- **Never complete a purchase.** Stop at the payment step. Pause and ask before anything irreversible, account, or payment related. Never enter real personal or payment data into checkout forms.
- **The push is pulled from the browser, never rewritten.** It goes onto the Captured pushes tab exactly as captured (`build_report.py` dumps it with `json.dumps(obj, indent=2)`): no truncation, no added comments, byte-for-byte what fired. Checks and "Seen" values are read from that same object by the script, never retyped by you.
- **No em dashes or en dashes anywhere in the report text.** Use commas, parentheses, or hyphens. (`build_report.py` also strips them from the prose you write as a safety net, never from values or the push.)
- **Do not screenshot any debug overlay or pixel helper.** Those are dev tools that will not exist on most sites and are irrelevant. Hide them (see below). Screenshots must show the real page and, for interactions, a tight crop of the element interacted with.
- **Output filename must be tiny.** The session output directory is already ~200 characters; a long descriptive filename blows past the Windows 259-char path limit and the workbook will not open. See "Output filename".

## Workflow

1. Open a **fresh tab**, navigate to the test URL, confirm you are on the right page (params/theme intact). Note: preview/theme params are often consumed into a session cookie and stripped from the visible URL, that is fine as long as the right theme/pixel is active (check e.g. `window.Shopify.theme.id`).
2. **Lock the viewport.** Call `resize_window` to **1280 x 900** before capturing anything. This makes the site content fill the frame (no empty gutter on full-page shots), keeps screenshot pixels ~1:1 with CSS pixels (so `getBoundingClientRect()` values can be used directly as crop regions with no scaling factor), and makes coordinates reproducible. Do not resize again mid-run.
3. **Hide dev overlays** so they never leak into a screenshot, e.g. Shopify's web-pixels helper: `document.getElementById('web-pixels-helper-sandbox-container')?.style.setProperty('display','none')`. Re-hide after each navigation.
4. **Identify how this site emits events** (do not assume). Quick probe for: `window.dataLayer` (GTM/GA4), `window.gtag`, Tealium `window.utag`, Adobe `window._satellite` / `window.digitalData`, a Shopify bus (`Shopify.analytics`), or a custom module (scan `Object.keys(window)`). See REFERENCE "Identify how the site emits events". Whichever it is, that JS push is the source of truth for the QA.
5. Install the capture hook (`scripts/capture_hook.js`) via `javascript_tool`. It wraps every common emitter it finds (`dataLayer.push`, `gtag`, Tealium `utag`, `Shopify.analytics.publish`, and any `window.tracking.*`-style builder) and installs a `pagehide` sessionStorage carry. **Re-install after every navigation** (page load wipes it). Reset with `window.__dlqa = []` before each event you trigger.
6. Walk the funnel, capturing after each trigger: PLP load (`view_item_list`) -> click a product (`select_item`) -> PDP (`view_item`, + change variant/kit to re-fire) -> add to cart from PDP **and** from the mini-bag/drawer, including any upsell/bundle add (`add_to_cart`) -> open cart/mini-bag (`view_cart`) -> remove from **both** cart page and mini-bag, testing **every** remove control incl. quantity-decrement AND the trash/remove button AND any add-on remove (`remove_from_cart`) -> checkout (`begin_checkout`) -> shipping (`add_shipping_info`) -> payment (`add_payment_info`, **stop before paying**). Cover the spec's custom events on the pages where they fire.
7. For each event record: `source` (Top frame / Web pixel / Not fired); the push (see below); `name_seen` when the event name rides beside the payload rather than in it (gtag, Tealium, `Shopify.analytics.publish`); a **tight location screenshot** (see "Location screenshots"); and what you did to trigger it.
8. Build the report: write `events.json` (schema in REFERENCE: one entry per event tested, each carrying that event's parameter rows from the spec) and run `python scripts/build_report.py events.json <screenshots_dir> <out.xlsx>`. It fills every check the push answers by itself and prints the **Value checks still yours to judge**. Judge them (see "Filling the checks"), set `value_ok` in `events.json`, and rerun until that list is empty or every remaining blank is deliberate and explained in the event's note.
9. **Verify**: reopen the workbook with `openpyxl.load_workbook(path, data_only=True)`. Every Summary row has its Params count and a status, the statuses agree with the checks you set, every block's Push link lands on a Captured pushes row with the push text and a readable screenshot, and nothing clips. Clear any `WARNING` the build printed.

### Output filename (hard rule)

The output `.xlsx` name must be **short and generic: at most ~12 characters before `.xlsx`, with no client/theme/description in it** (e.g. `CB_QA.xlsx`, `dl_qa.xlsx`). Never a long descriptive name like `CurrentBody_IE_dataLayer_QA.xlsx`. Put the descriptive title (client, batch, date) inside the workbook: `client`, `batch`, `site` and `tested` in `events.json` put it in the title bars. After saving, assert `len(full_windows_path) < 259` and shorten further if not.

## The spec: which parameters each event should carry

- **One block per event tested**, not one per event in the spec. The same event triggered from two places (add_to_cart from the PDP and from the mini-bag, remove_from_cart by stepper and by trash) is two blocks, with the place as the `variant`. Copy the spec's parameter rows into each.
- **Keep the spec's rows as they are**: its types (never "correct" a String because the value looks numeric, specs often make those Strings on purpose), its Required flags, its expected values. The tester judges the push against what the spec says.
- A spec event you triggered that fired nowhere still gets its block, `source: "Not fired"`. One you deliberately did not test (`purchase` with no authorised test order) is not a failure: keep its block with `push: null`, no `source`, and a `push_note` / note saying why. Its checks stay blank and it reads In progress.
- Params the push carries that the spec does not list: name them in the event note ("also pushed: from_upsell, list_position"), do not add rows.

## Where the event lives (set the source)

After triggering, read `window.__dlqa`. If the push is there, `source = "Top frame"`. If nothing appears, do not conclude "missing" yet: the event may fire in a **sandboxed / cross-origin iframe** (Shopify custom pixels and the whole Shopify checkout work this way), QA it the sandbox way (platform playbook below) and set `source = "Web pixel"`. Only if it fires nowhere, `source = "Not fired"` (a finding: every row of that block fails on Present).

## Capturing pushes reliably

- **Hook whatever bus THIS site uses, not just `dataLayer`.** Do not assume. Sites emit through GTM (`dataLayer.push`), GA4 direct (`gtag`), Tealium (`utag`), Adobe (`_satellite` / `digitalData`), a vendor pub/sub bus (e.g. `Shopify.analytics.publish`), or a bespoke `window.tracking`-style builder. `capture_hook.js` wraps all of these that it finds. If `window.dataLayer` and `window.__dlqa` are both empty after a known event, run the discovery probe (REFERENCE) to find the emitter this site uses, then hook that.
- **Click-then-navigate events** (e.g. `select_item`, which fires just before the PDP loads) are lost because the page unloads. Capture them with the `pagehide` sessionStorage carry: the hook writes `window.__dlqa` to `sessionStorage.__dlqa_carry` on unload; read and parse it on the next page.
- **Load-only events** (e.g. `view_item_list`) fire once at document load, before any hook can be injected. Do NOT give up and leave them blank without exhausting the re-fire path below, they are almost always capturable. Work through these in order and stop at the first that yields a payload (see REFERENCE "Re-firing a load-only builder event" for the exact snippets):
  1. **Re-invoke the theme builder** (most reliable). With the hook installed, call the builder that produced it (e.g. `window.tracking.collectionViewed`). If it throws `... reading 'map'/'forEach'` you passed the wrong shape: read the builder's `.toString()` in-page and return ONLY the parameter's first property access (a short safe token like `products` or `items`), then re-call with the theme's own product data in that exact shape (`{ <prop>: <productObjects> }`). Get the product objects from a page JSON blob, a `window.*` product array, or `window.(ShopifyAnalytics.)meta.products`. Also try the raw array, `{products:arr}`, `{items:arr}`, `{collection:{products:arr}}`.
  2. **Trigger a real re-render** if the builder arg cannot be reconstructed: use the collection's own sort / filter / pagination / "load more" / currency toggle, which re-fires the builder client-side with the hook alive.
  3. **Only if 1 and 2 both fail**, record `push: null` with a `push_note` explaining it fires pre-hook, set `source` from the pixel subscription (it is still wired), leave that block's checks blank, and say in its note to confirm in GA4 DebugView. The block stays In progress, which is the truth. This is the last resort, not the default.
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
   - If you cannot (the usual case for a sandbox), reproduce the **object shape from the source** and set every value you cannot read to the string `"(Can't read values in web pixel)"`. Keep the real param **keys**, so Present is still judged; `build_report.py` leaves those Value checks blank and notes why.
4. Judge coverage from the code (e.g. a param hardcoded to `null` in the builder means it is not implemented, regardless of cart state): set that row's `value_ok` to Fail with a note like "null, hardcoded in the pixel source". Annotate hardcoded values in the push, e.g. `"null (hardcoded in pixel source)"`.

## What `value`, `quantity` and `items` should mean (read before judging any cart event)

Getting this backwards is the most common QA mistake, so decide which kind of event you are looking at **before** you judge a value. Two kinds:

**Delta events: `add_to_cart`, `remove_from_cart`.** These describe *the thing that just moved*, not the cart it moved into or out of. What is already in the cart is irrelevant.

- `items` = **only** the item(s) added or removed in that one interaction.
- `items[].quantity` = **how many units moved in that interaction**, not the resulting line quantity in the cart.
- `value` = the money that moved: sum of `price * quantity` over those items only. **Not** the cart subtotal, and **not** the cart total after the change.

Worked examples, judge against these:

| Interaction | Correct `quantity` | Correct `value` |
|---|---|---|
| Cart already holds 2 x Product X (£10), user adds 1 more | `1` | `10` |
| Same, but the qty selector was set to 3 before adding | `3` | `30` |
| Qty stepper on a 3-unit cart line clicked down to 2 | `1` (remove_from_cart) | `10` |
| Trash / "remove" clicked on a 3-unit cart line | `3` | `30` |

Note the last two rows: the trash button legitimately removes the whole line, so there `quantity` *equals* the line quantity. That is the delta, not the cart state, and it is a pass. A stepper decrement is always `1`.

So: if the cart holds 2 and the user adds 1, `quantity: 3` and `value: 30` are **failures**, not passes. Note it as what it is, e.g. "the resulting line, not the 1 unit added" or "cart total after the add, not the item added".

**Whole-cart events: `view_cart`, `begin_checkout`, `add_shipping_info`, `add_payment_info`, `purchase`.** These *do* describe the entire cart: `items` = every line, each `quantity` = that line's full quantity, `value` = the cart total. Do not apply the delta rule here.

(`view_item` and `view_item_list` describe what is on screen: the viewed product, or one item per product in the list. `quantity` is usually `1`, and a missing or `1` quantity is not a finding unless the spec asks for it.)

Always defer to the user's own spec if it says something different, and if the spec is silent on this, these are the expectations.

## Filling the checks

`build_report.py` settles everything the push answers by itself, so you never retype a value:

- **Present / fired?** Pass when the key is in the push (top level, under `ecommerce`, or on every `items[]` entry). Missing: Fail if Required is Yes, N/A otherwise; missing on some items: Fail, noted. Not fired: Fail.
- **Value correct?** Fail when the value's JSON type contradicts the Type column ("sent as string 'false', spec says Boolean"). Pass when it equals the expected value exactly. N/A when the key is absent.
- **Notes** gets `Seen: <value>` whenever the pushed value differs from the expected one.

What is left is judgement, and it is yours: a value that is present, correctly typed, and not the spec's example. Decide whether it is right **for what you did**: the product you clicked, the list you were on, the storefront's currency, and for cart events the delta rule above. Set `value_ok` to Pass or Fail. On a Fail add a note: a fragment naming the deviation ("cart total, not the item added"), nothing more. The audience is analysts.

- **Only fail what is actually wrong or risky.** A param legitimately empty at that stage (a coupon when none was applied, tax before the address step) is `value_ok: "N/A"`, no note. Standard GA4 params the spec does not ask for are not findings.
- **Leave a check blank only when it genuinely cannot be judged**: values unreadable in a web pixel sandbox, a load-only event whose push you could not capture. Say why in the event note ("values read from the pixel source; confirm in GA4 DebugView"). That block stays In progress, which is the truth.
- **The event `note` is for findings, in fragments**: the real problems, a genuine cross-event inconsistency (a flag typed as a string here and a boolean in view_item_list), params pushed that the spec lacks. `build_report.py` adds "Did not fire" / "Fires in the web pixel sandbox" itself. Never narrate passes. The build warns when a note runs long.

Example: add_to_cart, cart already holding 2 x Product X at £10, user adds 1 more. The rows that are not plain passes:

| Parameter | Present / fired? | Value correct? | Notes |
|---|---|---|---|
| quantity | Pass | Fail *(yours)* | Seen: 3; the resulting line, not the 1 unit added |
| value | Pass | Fail *(yours)* | Seen: 30; cart total after the add, not the item added |
| from_mini_bag | Pass | Fail *(automatic)* | sent as string 'false', spec says Boolean |

## Location screenshots (show the trigger)

One tight, readable screenshot per event. Never embed a whole-page shot for an interaction, and never centre on a debug/pixel-helper panel.

**Interaction events** (`add_to_cart`, `remove_from_cart`, `select_item`, variant/kit change, mini-bag `+`): crop to the control itself, like a zoomed product-card or button close-up (think: just the "Add to basket" button, or just the mini-bag line with its qty stepper and trash icon).
1. Get the control's box: `const r = el.getBoundingClientRect()`.
2. Pad it so context is visible but the control dominates: ~12px each side; for a small icon button (< 60px) expand to include its row/label, aiming for a crop ~240-420px wide.
3. `el.scrollIntoView({block:'center'})`, then `computer` `zoom` with `region:[x-pad, y-pad, x+w+pad, y+h+pad]` and `save_to_disk:true`. Use that saved crop as `location_image`.
4. If nothing meaningful is visible after the click (AJAX with no visual change), capture the control in its pre-click state instead.

**Page-load events** (`view_item_list`, `view_item`, `begin_checkout`): one screenshot of the page, trimmed to the content column, not the raw window. With the viewport locked to 1280 the gutter is already minimal; if a gutter remains, `zoom` to `[0, 0, contentWidth, viewportHeight]` where `contentWidth = document.querySelector('main, #MainContent, [role=main]')?.getBoundingClientRect().right || window.innerWidth`. Prefer the buy-box / relevant section over a tall full-page dump.

Because screenshots at the locked 1280 viewport are ~1:1 with CSS pixels, `getBoundingClientRect()` values can be used directly as `zoom` regions with no scaling factor. Save every crop into the screenshots directory you pass to `build_report.py`, which fits each image to the Captured pushes tab's screenshot column and sizes the row to it.

## The report

- **Summary**: how to use it, one row per block (category, event, variant, what triggered it, parameter count, status) and `Passed: n / N`.
- **QA Checklist**: the blocks. Status formulas stay live, so a tester can change any check and the statuses follow. The layout is the QA team's template, identical to the Doc Creator's export.
- **Captured pushes**: per block, the push verbatim, its source, what you did, and the screenshot. Each block's **Push** link and each row's **#** link jump between the two tabs.

See [REFERENCE.md](REFERENCE.md) for the events.json schema, the spec shape and the standard GA4 default spec, capture snippets, the pixel-source fetch technique, and the sandbox caveat.
