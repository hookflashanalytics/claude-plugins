---
name: qa-network-requests
description: QA the analytics network requests a site actually sends (GA4 hits, Meta/Facebook pixel, TikTok, Google Ads, Microsoft UET, or whatever vendor the spec names) by driving a connected Chrome browser, walking the funnel, capturing every outgoing tag request with its decoded payload, forcing a cookie-consent check to report how the tags behave before and after consent, and building an .xlsx with a Consent tab plus one tab per platform (one row per hit: verbatim request, full payload, just the spec's own parameters, a screenshot of the trigger, and a bulleted audit against the spec). Use when the user runs /qa-network-requests, asks to QA / test / verify that tags, pixels or hits are actually FIRING or being SENT, asks to check network requests, beacons, collect hits or a Facebook/TikTok/GA4 pixel against a tracking spec, or asks how the tags behave before and after cookie consent. For QAing the dataLayer pushes themselves, before the tags that forward them exist, use qa-datalayer instead.
---

# QA network requests

Drive the user's connected Chrome, walk the funnel, and for every analytics request the site sends, capture the request and its payload, then audit both against the user's spec. Hand back an `.xlsx` with a **Consent tab first**, then **one tab per platform**: one row per hit, carrying the verbatim request, the full payload, just the spec's own parameters, a tight screenshot of the trigger, and a bulleted verdict. Requires the Claude-in-Chrome browser tools.

**Vendor-agnostic. The spec decides what is checked, not GA4.** GA4 is the most common case but it is not the point. If the spec covers Meta, TikTok, Google Ads, Floodlight, Microsoft UET, Pinterest, LinkedIn, Snapchat, Segment, an affiliate network, or a first-party server-side endpoint, QA those with equal weight. Run the discovery pass (below) to learn what this site actually sends before deciding what to look for, and audit each vendor against what the spec says about that vendor.

## Scope, and how this differs from /qa-datalayer

| | `/qa-datalayer` | this skill |
|---|---|---|
| Source of truth | the JS push into `dataLayer` (or equivalent) | the **outgoing HTTP request** and its payload |
| When in the build | after the dataLayer is implemented, **before** the tags exist | **after** the tags are built |
| Question answered | "is the site pushing the right data?" | "is that data actually reaching the vendors, with the right values?" |

If the tags have not been built yet there will be no hits to read, and the user wants `/qa-datalayer`. If they ask for both, run this one second: a dataLayer push that looks perfect can still arrive at GA4 mangled by the tag mapping, and that gap is exactly what this skill exists to find.

## Gather inputs first (use AskUserQuestion)

1. **Test URL** - page/store to start from (staging/preview is fine; any theme/preview params must survive redirects).
2. **The spec (required, any format).** Ask for whatever they have: a dataLayer document, an event design or measurement plan, a tagging spec, a Google Sheet, a Doc, a Notion page, a deck, a GTM export, or just a list of events in the chat. **Do not assume a PowerPoint.** Read it before touching the browser and restate, in two or three lines, which vendors and which events you are about to check, so a misread spec is caught before the walk, not after.
3. **Which vendors** - default to every vendor the spec names, plus anything the discovery pass finds that the spec does not mention (an undocumented vendor firing is itself a finding). Ask if they want a subset.
4. **Which events** - default to everything in the spec. Skip `purchase` / conversion hits unless asked (never complete a real payment).

If they genuinely have no spec, say plainly that this becomes a description of what the site sends rather than an audit, offer the standard GA4 ecommerce expectations in [REFERENCE.md](REFERENCE.md) as the fallback yardstick, and label every verdict accordingly.

## Golden rules

- **Never complete a purchase.** Stop at the payment step. Pause and ask before anything irreversible, account, or payment related. Never enter real personal or payment data into checkout forms.
- **The request and payload columns come from the browser, never rewritten.** Dump the captured URL and body verbatim. Decode the payload into readable key/value pairs, but never invent, tidy or complete a value. If a param is absent, it is absent.
- **An empty read is not a finding.** A filter that returns nothing means *your filter found nothing*, which is not the same as *nothing was sent*. Every "did not fire" claim needs positive evidence before it goes in the report. See "Claiming something did not fire".
- **The network request is the only evidence that a hit was sent. The dataLayer is not.** Do not read `dataLayer` (or `gtag`, or a theme module) to decide whether an event reached a vendor: sites customise the push shape (`{event: "ecommerce", event_name: "view_item_list"}` is common), so filtering it on a guessed field name produces false negatives while the hit is sitting in the network log. `dataLayer` is a diagnostic for *is the tagging stack installed*, nothing more.
- **Escape every payload you return, or you will get blank results.** The browser tool blanks any result containing `?`, `=` or `&`, and every tag hit is one long query string, so this bites on literally every read. Always return through `window.__dump(...)` (see "The output filter"). This is the single most common way a run stalls.
- **Never paste hashed or raw user data into the report.** Advanced-matching params (Meta `ud[em]` / `ud[ph]`, GA4 user-provided data, UET `em`) carry hashed emails and phone numbers. Record that the param was **present** and its length, never its value. Same for `cid` / `_ga` client IDs: note presence, truncate to the first few characters.
- **Consent is reported, never graded.** See "Consent check". Describe what the tags did; do not tell the user it is wrong.
- **No em dashes or en dashes anywhere in the report text.** Use commas, parentheses, or hyphens. (`build_report.py` also strips them from prose cells as a safety net.)
- **Do not screenshot any debug overlay, tag assistant or pixel helper.** Screenshots must show the real page, and for interactions a tight crop of the element interacted with.
- **Output filename must be tiny.** The session output directory is already ~200 characters; a long descriptive filename blows past the Windows 259-char path limit and the workbook will not open. See "Output filename".

## Workflow

1. Read the spec and restate the vendors and events you are checking (input 2 above).
2. Open a **fresh tab** and navigate to the test URL.
3. **Do the consent check now, before anything else.** It clears cookies, so running it later would empty the cart and log you out mid-walk. See "Consent check".
4. **Lock the viewport.** Call `resize_window` to **1280 x 900** before capturing anything. Screenshot pixels stay ~1:1 with CSS pixels, so `getBoundingClientRect()` values work directly as crop regions, and coordinates stay reproducible. Do not resize again mid-run.
5. **Hide dev overlays** so they never leak into a screenshot (tag assistant panels, Shopify's `web-pixels-helper-sandbox-container`, CMP debug badges). Re-hide after each navigation.
6. **Discovery pass: learn what this site actually sends.** Install `scripts/net_hook.js` and run `window.__nqaAll()` after a page load and one interaction. It returns every outgoing request the vendor matcher recognises **plus** an `unclassified` list of other third-party requests. Read the unclassified list: that is where a vendor the matcher does not know, or a first-party server-side endpoint, shows up. Add anything real to the audit. See REFERENCE "Vendor endpoints and payload shapes".
7. Walk the funnel, **marking before each trigger and reading after** (see "Attributing a hit to an interaction"): PLP load -> click a product -> PDP (and change variant to re-fire) -> add to cart from the PDP **and** from the mini-bag/drawer, including any upsell/bundle add -> open cart/mini-bag -> remove via **every** control (quantity-decrement, trash/remove, add-on remove) on both cart page and mini-bag -> checkout -> shipping -> payment (**stop before paying**). Adjust to the spec's event list and to a non-ecommerce funnel (forms, sign-ups, calls) where that is what the spec describes.
8. For each hit record: `event`, `vendor` (this decides which tab it lands on), the request (method + endpoint), the verbatim URL, the full decoded payload, **`spec_params`** (see "The two payload columns"), a **tight location screenshot**, and a bulleted verdict audited against the spec.
9. **A spec'd event that sends nothing is a finding, and one of the most valuable ones, which is exactly why it has to be proved.** Record it with `vendor` from the spec, `sent: false`, verdict `fail`, and a mandatory `absence_evidence` string. See "Claiming something did not fire" before writing any of those.
10. Build the report: write `events.json` and `consent.json` (schemas in REFERENCE) and run `python scripts/build_report.py events.json consent.json <screenshots_dir> <out.xlsx>`.
11. **Verify**: reopen the workbook and confirm the tab list is Consent followed by one tab per platform, that every row has a request, a full payload, a spec-parameter cell and a readable screenshot, and that nothing clips. Say in chat which vendors and events you covered and which you could not.

### Workbook layout

**One tab per platform, with Consent first.** `build_report.py` builds this from the `vendor` field, so the only thing you control is spelling `vendor` consistently (use `"GA4"`, not `"ga4"` on one row and `"Google Analytics"` on the next, or you get two tabs for one platform).

| Tab | What is on it |
|---|---|
| **Consent** (always first) | One row per vendor: before consent, the consent signal, after consent, and a plain descriptive observation. No pass/fail column. |
| **GA4**, **Meta**, **TikTok**, ... | One row per hit for that platform, in funnel order. Tabs appear in the order the vendors first show up in `events.json`, so lead with the platform the spec cares most about. |

Vendors with no hits at all still deserve a Consent row and, if the spec expected events from them, a tab whose rows are `sent: false`.

### The two payload columns

Every hit gets both, and they answer different questions:

- **Full payload** - every decoded param the hit carried, verbatim. The evidence, and where someone debugging goes.
- **Spec parameters** - *only* what the spec actually asked about. If the spec describes a nav click with an event name and two params, this cell holds exactly those three things, and none of the `cid`, `gcs`, `sr`, `ul`, `_p` transport noise.

You supply `spec_params` as a list of the param names **as this vendor sends them** (you have just decoded the hit, so you know them):

```json
"spec_params": ["en", "ep.link_text", "ep.link_url"]
```

`build_report.py` pulls the values out of the Full payload for you, so the two columns can never disagree and you cannot retype a value wrongly. Anything the spec wants that the hit does not carry renders as `(absent)` and the cell is tinted red: that is the most useful cell in the whole report, so get the list right. Supported forms:

| Form | Use |
|---|---|
| `"en"`, `"epn.value"`, `"cd[value]"` | a literal param key (dots and brackets are fine) |
| `"items[].item_id"` | an item-level param, one value per item |
| `"__body_json.properties.value"` | a dotted path into a JSON body (TikTok, Segment) |

Use `spec_payload` (an explicit dict) instead only when the spec-to-vendor mapping is not a lookup, e.g. the spec asks for one value that the vendor splits across two params. Prefer `spec_params` everywhere else.

If the spec says nothing about a hit you captured, leave `spec_params` off; the cell will say so, and the hit is still on record.

### Output filename (hard rule)

The output `.xlsx` name must be **short and generic: at most ~12 characters before `.xlsx`, with no client/theme/description in it** (e.g. `CB_NQA.xlsx`, `net_qa.xlsx`). Never a long descriptive name like `CurrentBody_IE_network_request_QA.xlsx`. Put the descriptive title (client, date, spec version) inside the workbook, not in the filename. After saving, assert `len(full_windows_path) < 259` and shorten further if not.

## Consent check (forced, first, and only describe what you see)

The point is to **report how the tags reacted to consent**, not to grade the implementation. There is no correct answer here, and several perfectly legitimate setups look different from each other.

**Always force the pre-consent state rather than hoping for it.** If the browser has already accepted cookies for this site, you would otherwise never see the interesting half. So clear the site's cookies and storage and reload, which brings the banner back.

**Step 1: warn the user, then reset.** `scripts/reset_consent.js` is destructive to the site session, so say what it will do before running it, and get a yes if any of it would cost them something:

- It **logs you out of the site.** On a password-protected staging or preview build, you will have to sign in again after the reload.
- It **empties the cart**, which is why the consent check runs before you walk the funnel and never in the middle of it.
- Shopify (and others) consume **theme/preview params into a session cookie** and strip them from the URL, so clearing cookies can drop you out of the previewed theme. Keep the original preview link, re-apply it after the reload, and confirm the right theme/pixel is live (e.g. `window.Shopify.theme.id`) before continuing.

Then run the script and **reload the page**.

**Step 2: check the reset actually worked.** The script returns the cookie names that survived; anything left is almost certainly `HttpOnly`, which JS cannot touch. Confirm the banner is back:

```js
!!document.querySelector('[id*=onetrust], [class*=ot-sdk], #CybotCookiebotDialog, [id*=usercentrics], [class*=cky-], [id*=cookie], [class*=consent], [class*=gdpr]')
```

Also check the CMP API (`window.OnetrustActiveGroups`, `window.Cookiebot?.consent`, `window.__tcfapi`) and Google's consent state (`window.google_tag_data?.ics?.getConsentState?.()`).

If **no banner returns**, do not pretend the check ran. Consent may be held server-side or against the account, an `HttpOnly` cookie may have survived, or the site may show no banner in this region at all. Set `state` to `already_accepted`, say which of those you could rule out, and carry on with the payload QA.

**Step 3: capture the pre-consent state.** Do not touch the banner yet. Install the hook, then **let the page settle and read twice**:

```js
window.__nqaAll()          // read 1: page-load hits via the performance buffer
// wait 2 seconds
window.__nqaAll()          // read 2: catches what had not been sent yet
window.__nqaRequests()     // unfiltered, for the count that backs any "no hits" claim
```

**Reading once, immediately, is how this step goes wrong.** Vendors do not fire together: Google's consent ping (`/ccm/collect`) goes out noticeably before GA4's own `/g/collect`, so a single early read catches the ping, misses the hit, and produces a confident "no GA4 hits before consent" while the hit is in the log a moment later. This is not hypothetical, it has happened on a real run.

For each vendor in the spec, record: did **any** hit go out, and if so what consent signal did it carry. **A "no hits" row needs an `evidence` string** with the number of requests searched, exactly as in "Claiming something did not fire". Remember the endpoint is often first-party, so search the **path** (`/g/collect`), not `google-analytics.com`.

**Step 4: grant consent** (click Accept all, or whatever the spec's scenario is), then read again with a fresh mark. Note which vendors started sending, and whether the consent signal changed. Screenshot the banner for the Consent tab while it is still on screen.

**Step 5: write it up descriptively**, one row per vendor on the Consent tab. Report, do not prescribe:

- **No hits at all before consent, hits after** - basic consent mode, or the tag is simply gated on consent. Describe it as observed.
- **GA4 hits before consent carrying `gcs=G100`** - advanced consent mode: the hit is a cookieless ping with `ad_storage` and `analytics_storage` both denied. This is a normal, deliberate configuration. Report it as advanced consent mode, **not** as a failure.
- **GA4 hits before consent carrying `gcs=G111`** - the hit claims full consent before the user gave any. Say exactly that, in plain descriptive language ("the pre-consent page_view reported both storage types as granted"), and leave the judgement to the reader.
- **`gcs=G1--`** - no default consent state was set before the hit, i.e. consent mode is not configured for that hit. Report as observed.
- **Meta / TikTok / Google Ads hits before consent** - these vendors have no cookieless-ping equivalent, so a hit before consent is a fully-fledged hit. Report which vendors sent one and which did not. This is the check the user most often wants: for Meta, "no `facebook.com/tr` requests were observed before consent" is the expected shape of the answer.

`gcs` decodes as `G` + a status digit + `ad_storage` + `analytics_storage`, each `1` granted / `0` denied, `-` unset. So `G100` = both denied, `G101` = analytics granted only, `G110` = ads granted only, `G111` = both granted. The `gcd` param carries the fuller default/update signal and is useful corroboration; do not attempt to fully decode it, quote it verbatim.

Keep the whole Consent tab descriptive. **No pass/fail column on it**, by design, and `build_report.py` does not provide one. If the user asks you to judge it, then judge it in chat, but do not volunteer a verdict.

Once consent is granted, the funnel walk proceeds normally in the consented state, which is what the rest of the QA is about.

## Reading hits reliably (two layers, use both)

**`read_network_requests` misses tag traffic.** On a page that made 95 requests including every GA4 hit, it returned 40 image requests and "No network requests recorded" for every analytics filter. Do not build the QA on it. Use these two instead:

**Layer 1: the performance buffer (sees everything, URLs only).**
`performance.getEntriesByType('resource')` lists every request the page made, including hits fired at document load before any hook could exist. For GET-based tags (GA4 GET hits, Meta `/tr`, Google Ads, UET, Pinterest) the query string **is** the payload, so this layer alone fully QAs them. Two traps:

- **The buffer resets on every page navigation.** Proved: homepage then a second page left zero homepage entries. So a multi-page funnel needs one read per page, before you navigate. A true SPA funnel never resets, and one read at the end is enough.
- It gives no request body and no response status, so POST-body vendors need layer 2.

**Layer 2: the hook (`scripts/net_hook.js`), which attaches bodies.**
It wraps `fetch`, `XMLHttpRequest`, `navigator.sendBeacon` and the `HTMLImageElement.prototype.src` setter, and resolves `Blob` bodies asynchronously. This is the only way to see a POST body, which matters because **TikTok, Segment and GA4 batched hits put the payload in the body, not the URL**. **Re-install after every navigation** (page load wipes it).

`window.__nqaAll()` merges both layers, keyed on URL, so a POST hit arrives with its body attached and a load-time GET arrives from the performance buffer. Use it rather than reading either layer by hand.

## Claiming something did not fire

The two worst findings this skill can produce are both false negatives: "this event never fired" and "nothing was sent before consent". Both have been produced on a real run while the hits were plainly in the network log, because a read came back empty and the empty result was written up as a finding. An empty read is a question, not an answer.

**The rule: to assert an absence, show the set you searched.** Never conclude from a filtered view.

```js
window.__nqaRequests()            // EVERY request, unfiltered, with a total
window.__nqaRequests('/g/collect')   // or narrow it, and see what you narrowed
```

It returns a `verdict` line that does the reasoning for you, so read that before writing anything:

- `"MATCHES FOUND (2 of 4) - this is NOT an absence, read the urls below"` -> **stop.** The hit is there. Go and decode it.
- `"0 of 68 requests matched - safe to record as absent, evidence: \"68 requests searched, none matching /g/collect\""` -> paste that evidence sentence straight into `absence_evidence` (or `evidence` on a Consent row) and add what else you ruled out:

> `"68 requests searched, none matching /g/collect. gtag/js loaded and window.google_tag_manager exists, so GTM is installed and this tag is not firing."`

The count is what makes the claim falsifiable, and it is self-correcting: if the hit was there, you cannot miss it while counting. `build_report.py` stamps any absence claim with no evidence as **`!! UNVERIFIED`** in the workbook and prints a warning at the end of the run, so an unproved negative cannot quietly ship.

Work through these before recording the miss (full list in REFERENCE "Nothing fired"):

1. **Settle, then read twice.** Beacons are async and vendors do not fire together. Wait 1 to 2 seconds, read, wait, read again.
2. **Search unfiltered**, per the rule above. Match on **path**, never host: under server-side tagging the endpoint is first-party (`data.<client>.com/g/collect`), so a search for `google-analytics.com` finds nothing on a site sending thousands of hits.
3. **Did the interaction actually happen?** An AJAX add-to-cart that silently failed sends nothing because nothing happened.
4. **Did the hook survive the last navigation?** Re-install after every page load.
5. **Did the vendor's library load?** Library present but nothing sent is "installed and gated", a much sharper finding than "missing".

**If an assumption turns out to be wrong, re-audit every earlier absence.** Discovering mid-run that the site uses a custom event shape, a first-party endpoint, or a vendor you had not matched invalidates every "did not fire" verdict you wrote before you knew it. Go back and re-check them against the corrected understanding. Findings are provisional until the run ends; a null result recorded early is the one most likely to be wrong, because you knew least at the time.

## Attributing a hit to an interaction

The buffer is cumulative, so "what fired when I clicked" needs a baseline, not a filter:

```js
window.__nqaMark()               // immediately BEFORE the click
// ... perform the interaction, then wait ~1.5s for the beacon ...
window.__nqaSince()              // only hits that started after the mark, escaped and decoded
```

Mark before **every** trigger. Without it you will attribute a page-load `page_view` to an add-to-cart click, which is the most common way this QA produces a confidently wrong report.

**Click-then-navigate hits** (a `select_item` that fires as the PDP loads) can be lost to the unload. The hook writes captured hits to `sessionStorage.__nqa_carry` on `pagehide`; read and parse it on the next page. The performance buffer of the *new* page will not contain them.

Beacons are asynchronous: after an interaction, wait ~1 to 2 seconds before reading, and if nothing appears, read once more before concluding it did not fire.

## The output filter (this will bite on every read)

The browser tool blanks any result that looks like a query string. Every tag hit is a query string. Return payloads only through:

`JSON.stringify(x).replace(/\?/g,'\\u003f').replace(/=/g,'\\u003d').replace(/&/g,'\\u0026').replace(/%/g,'\\u0025')`

`net_hook.js` exposes this as `window.__dump(obj)`, and `__nqaAll()` / `__nqaSince()` already return through it. The output stays valid JSON and decodes back byte-for-byte, so the verbatim URL you put in the report is exactly what the browser sent. If a read comes back blank or truncated, that is the filter, not a missing hit: re-read through `__dump`.

## Decoding the payload

For each hit, produce a readable key/value payload alongside the verbatim URL. `__nqaDecode()` (called for you by `__nqaSince`) handles the shapes:

- **Query-string hit** (GA4 GET, Meta, UET, Ads): parse the query into params.
- **Form-encoded body**: parse the body the same way, and merge it over the URL params (GA4 POSTs carry the common params in the URL and the event params in the body).
- **JSON body** (TikTok, Segment): parse it and keep the object structure.
- **Newline-delimited body**: a GA4 **batched** hit, one event per line, each line its own query string. **Split it and report each event as its own row**, or you will report four events as one and miss three.

**GA4 item decoding.** Items travel as `pr1`, `pr2`, ... each a `~`-delimited string of two-character prefixed fields, e.g. `idSKU123~nmBlue Shirt~pr29.99~qt2`. Decode by splitting on `~` and reading the prefix; the common ones are in REFERENCE. **Keep any prefix you do not recognise verbatim rather than guessing at it**, and sanity-check your decode against the same event's dataLayer push or the spec before you rely on it.

Rename nothing. The report shows the vendor's own param names (`en`, `epn.value`, `cd[value]`), because that is what the person fixing the tag will search for. Put the plain-English meaning in the verdict, not in the payload.

## Auditing against the spec

Work param by param, in the spec's own terms:

- **Present but wrong** - the param arrived with a value the spec does not allow. Quote both: "`epn.value` arrived as 118.00, the cart total, where the spec asks for the added item's value (29.99)".
- **Missing** - in the spec, absent from the hit.
- **Extra** - not in the spec but being sent. Worth a line, especially if it carries user data.
- **Wrong type or format** - a number sent as a string, a currency as `gbp` where the spec says `GBP`, a boolean as `"true"`.
- **Wrong event name** - the vendor's event name does not match what the spec maps to (e.g. Meta receiving `AddToCart` where the spec says the custom event `Add_To_Basket`).
- **Sent to the wrong destination** - check `tid` / pixel ID / tag ID against the spec. A perfectly-formed hit going to the wrong property is a silent, expensive failure and it is easy to miss because everything else looks right.
- **Fired more than once** - duplicate hits for one interaction (a common double-tagging symptom: GTM plus a hardcoded snippet). The mark-then-read discipline is what makes these visible, so report the count.

**Cart-event semantics.** `add_to_cart` and `remove_from_cart` describe **what moved**, not the resulting cart: quantity is the units added or removed in that interaction and value is `price * quantity` for those items alone, so adding one unit to a cart that already holds two is `qt1` and value `1 x price`, never `qt3`. Whole-cart events (`view_cart`, `begin_checkout`, `add_shipping_info`, `add_payment_info`, `purchase`) are the opposite: every line, value equal to the cart total. This is the most common misjudgement in tracking QA, in both directions.

## Writing the verdict (Pass / Fail column)

Keep this column tight and skimmable, it is read at a glance:

- **One short bullet per real finding.** Lead with a single "Matches spec" line when the hit is clean, then list only the problems.
- **Only flag what is actually wrong or risky.** Do not narrate non-issues: standard vendor params absent but not in the spec, transport params (`_p`, `_s`, `sr`, `ul`, `_et`) that the spec never mentions, or values that are legitimately empty at that funnel stage.
- **Say what is wrong in plain language**, and name the param once so it is searchable: "Value is the cart total, not the item added (`epn.value`)".
- `build_report.py` renders a blank line between bullets automatically, so keep each finding as its own bullet, never one congealed block of prose.

Example (`add_to_cart`, Meta), this is the whole cell:

- Matches spec on event name, pixel ID and content_ids
- cd[value] is 118.00, the cart total, where the spec asks for the value of the item added (29.99)
- cd[currency] is missing, so Meta will fall back to the pixel default
- Hit fired twice on one click, once from GTM and once from a hardcoded snippet

## Location screenshots (show the trigger)

One tight, readable screenshot per hit, using the same rules as `/qa-datalayer`.

**Interaction hits**: crop to the control itself.
1. Get the control's box: `const r = el.getBoundingClientRect()`.
2. Pad it so context is visible but the control dominates: ~12px each side; for a small icon button (< 60px) expand to include its row/label, aiming for a crop ~240-420px wide.
3. `el.scrollIntoView({block:'center'})`, then `computer` `zoom` with `region:[x-pad, y-pad, x+w+pad, y+h+pad]` and `save_to_disk:true`. Use that saved crop as `location_image`.
4. If nothing is visible after the click (AJAX with no visual change), capture the control in its pre-click state.

**Page-load hits**: one screenshot of the page trimmed to the content column, preferring the relevant section over a tall full-page dump.

**Consent rows**: screenshot the cookie banner itself while it is on screen, so the reader can see exactly which state was being described.

Because screenshots at the locked 1280 viewport are ~1:1 with CSS pixels, `getBoundingClientRect()` values work directly as `zoom` regions with no scaling factor. Save every crop into the screenshots directory you pass to `build_report.py`, which scales each image to fit inside the screenshot column so nothing overhangs.

See [REFERENCE.md](REFERENCE.md) for vendor endpoints and payload shapes, the GA4 param and item-prefix tables, the events.json / consent.json schemas, worked `spec_params` examples per vendor, the discovery snippets, and what to do when nothing fired.
