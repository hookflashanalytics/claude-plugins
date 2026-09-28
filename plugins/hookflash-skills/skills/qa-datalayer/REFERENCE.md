# qa-datalayer - Reference

## Standard GA4 ecommerce events (default QA set)

| Event | Fires when |
|---|---|
| `view_item_list` | PLP / collection load. Expect one item per product (the visible variant). Often a load-only event (see caveat below). |
| `select_item` | Product clicked from a list. Fires just before navigation, capture via the pagehide carry. Often NOT implemented, flag as missing if nothing fires. |
| `view_item` | PDP load, and again on every variant/option change (use the variant change to capture it live). |
| `add_to_cart` | Add from PDP and from the mini-bag/drawer, plus any upsell/bundle add. **Delta event:** `items` = just the added item, `quantity` = units added in that interaction, `value` = `price * quantity` of the added item only. |
| `view_cart` | Opening the cart page or mini-bag. **Whole-cart event:** every line, `value` = cart total. |
| `remove_from_cart` | Removing an item, test every control: quantity-decrement, the trash/remove button, and any add-on remove, on both cart page and mini-bag. **Delta event:** `items` = just the removed item, `quantity` = units removed (a stepper decrement is 1; a trash click is the whole line). |
| `begin_checkout` | Entering checkout. On Shopify this fires inside the checkout sandbox (web pixel). **Whole-cart event.** |
| `add_shipping_info` | Shipping step (Shopify pixel: `checkout_address_info_submitted`). **Whole-cart event.** |
| `add_payment_info` | Payment step (Shopify pixel: `payment_info_submitted`). Stop before paying; do not enter card data. **Whole-cart event.** |
| `purchase` | Order confirmation. Do not test unless the user explicitly authorises a real/test order. **Whole-cart event.** |

Default coverage expectation (when the user has no spec): see "The standard GA4 spec" below. Always prefer the user's own spec over this default.

### Delta vs whole-cart (the most common misjudgement)

`add_to_cart` and `remove_from_cart` report **what moved**, never the cart that it moved into or out of. If the cart already holds 2 x Product X at £10 and the user adds one more, the correct push is `quantity: 1` and `value: 10`. A push carrying `quantity: 3` and `value: 30` there is reporting the resulting cart line, which is a **fail**, not a pass. Every other cart-stage event (`view_cart`, `begin_checkout`, `add_shipping_info`, `add_payment_info`, `purchase`) is the opposite: whole cart, `value` = cart total. See "What `value`, `quantity` and `items` should mean" in SKILL.md for the worked table.

## The spec

What each event should carry. `scripts/checklist_to_spec.py` writes it from any QA checklist workbook (the Doc Creator's export, the QA team's template, a previous run); for a dataLayer guide you write it yourself, one event per slide, the parameter table as the rows:

```json
{
  "client": "Example Store", "batch": "Batch 1", "source": "Example Store DataLayer Guide",
  "events": [
    {"category": "Ecom", "event": "add_to_cart", "variant": "",
     "trigger": "When a user adds an item to their cart.", "note": "",
     "params": [
       {"name": "event", "type": "String", "required": "Yes", "expected": "add_to_cart"},
       {"name": "value", "type": "Number", "required": "Yes", "expected": "129.99"},
       {"name": "coupon", "type": "String", "required": "If available", "expected": "SUMMER10"}
     ]}
  ]
}
```

- `category`: `Ecom` (GA4 ecommerce events), `Non-Ecom` (custom events) or `Recurring` (anything under a guide's "Recurring Events" divider).
- `type`: as the spec says: `String`, `Number`, `Double`, `Boolean`, `Array`, `Object`. `required`: `Yes`, `No` or `If available` (a guide without a Required column: `Yes`, or `If available` where it says "if available/applicable").
- `expected`: the example value, as a string, exactly as the push should carry it. The `event` row comes first; a grouped event's rows are `event` (the group name) then `event_name`.
- Item-level params (`item_id`, `price`, ...) are one row each, for the first item: `build_report.py` checks them on every entry of `items[]`.

### The standard GA4 spec (no spec given)

Every event: `event` (String, Yes, the event name). Then:

| Event | Params (type, required) |
|---|---|
| `view_item_list` | currency (String, Yes), item_list_name (String, If available), item_id (String, Yes), item_name (String, Yes), index (Number, If available), item_brand, item_category, item_variant (String, If available), price (Number, Yes) |
| `select_item`, `view_item`, `add_to_cart`, `remove_from_cart`, `view_cart`, `begin_checkout`, `add_shipping_info`, `add_payment_info` | currency (String, Yes), value (Number, Yes), item_id, item_name (String, Yes), item_brand, item_category, item_variant (String, If available), price, quantity (Number, Yes) |
| `purchase` | the row above, plus transaction_id (String, Yes), tax, shipping (Number, If available), coupon (String, If available) |

Leave `expected` blank in the default spec (there is no guide to take examples from): every Value check is then yours to judge, which the build lists for you.

## events.json schema

The spec's shape, plus what you captured. One entry per event **tested**, in funnel order (see the header of `scripts/build_report.py` for the authoritative list):

- `client`, `batch`, `source` (where the expected params came from), `site`, `tested` (date): the title bars.
- Per event: `category`, `event`, `variant` (which trigger, e.g. `PDP` / `Mini-bag` / `Cart trash`, `""` if only one), `trigger` (what you did), `note` (findings, fragments), `params` (the spec's rows for this event).
- `source`: `"Top frame"` | `"Web pixel"` | `"Not fired"`.
- `push`: the captured object (a dict), dumped verbatim with `indent=2` onto Captured pushes, and read for the checks. `null` only when nothing was captured and there is no shape to show (then set `push_note`).
- `push_note`: shown only when `push` is null.
- `name_seen`: the event name when it rides beside the payload rather than in it (gtag's second argument, Tealium's `tealium_event`, `Shopify.analytics.publish`'s first). Lets the `event` row pass.
- `location_image`: filename in the screenshots dir. Prefer a **tight crop saved via the `computer` `zoom` action** (no further cropping needed). `location_bbox` `[x,y,w,h]` + `viewport_w` are still supported as a fallback but should be avoided, ship a pre-cropped image instead.
- On a param row, optionally: `present` / `value_ok` (`Pass` | `Fail` | `N/A`) to set or override a check, and `notes` (a fragment). No em/en dashes in anything you write.

### Web-pixel push with unreadable values

When an event fires in a sandbox and you can read the source but not the runtime values, build `push` from the code with placeholder values, e.g.:

```json
{
  "event": "begin_checkout",
  "ecommerce": {
    "currency": "(Can't read values in web pixel)",
    "value": "(Can't read values in web pixel)",
    "tax": "(Can't read values in web pixel)",
    "contains_from_mini_bag": "null (hardcoded in pixel source)",
    "contains_from_upsell": "(Can't read values in web pixel)",
    "items": "(Can't read values in web pixel)"
  }
}
```

Keep the real param keys so coverage is reviewable, and annotate any value the source hardcodes (e.g. `null (hardcoded in pixel source)`), which is a stronger finding than a single runtime sample.

## Set a deterministic viewport first

Call `resize_window` to `1280 x 900` at the very start. Screenshots then come back ~1:1 with CSS pixels, so `getBoundingClientRect()` values are usable directly as `zoom` regions with no scaling factor, and the site content fills the frame with no empty gutter. Do not resize again mid-run.

## Identify how the site emits events (do this first, do not assume)

Sites send analytics through different layers. Probe for all of them before capturing:

```js
({
  dataLayer:  Array.isArray(window.dataLayer),                 // GTM / GA4 via GTM
  gtag:       typeof window.gtag === "function",               // GA4 direct
  gaGlobal:   !!window.google_tag_manager,                     // GTM present
  tealium:    !!window.utag,                                   // Tealium (utag.link / utag.view)
  adobe:      !!(window._satellite || window.digitalData),     // Adobe Launch / DTM
  shopify:    !!(window.Shopify && Shopify.analytics),         // Shopify analytics bus
  trackingMod:!!window.tracking,                               // bespoke theme/site module
  candidates: Object.keys(window).filter(k => /track|analytic|dataLayer|gtag|utag|pixel|tag/i.test(k)).slice(0,40)
})
```

Common patterns and how to capture each:

- **GTM / GA4 (`dataLayer.push`)** - the universal case. Hooked directly.
- **GA4 direct (`gtag('event', ...)`)** - `gtag` funnels into `dataLayer`, but wrap `gtag` too for the raw call args.
- **Tealium (`utag.link` / `utag.view`)** - wrap those; the payload is the data object passed in.
- **Adobe (`_satellite.track` / `digitalData`)** - wrap `_satellite.track` and/or snapshot `digitalData` at each step.
- **Vendor pub/sub bus (e.g. `Shopify.analytics.publish('<name>', payload)`)** - custom events often prefixed (e.g. `tbtg:view_item`); a pixel subscribes and relays to GA4. Hook the publish method.
- **Bespoke module (e.g. `window.tracking.viewItem(...)`)** - a global that builds and publishes each event; wrap its methods to capture the arguments too.

`capture_hook.js` wraps `dataLayer.push`, `gtag`, `utag.link`/`utag.view`, `Shopify.analytics.publish`, and any `window.tracking.*`. Extend the method lists in the hook for other module/vendor names as needed. If `window.__dlqa` stays empty after a known event, re-run the discovery probe, the site is using an emitter not yet wrapped; add it to the hook.

## Scope: JS push layer only (not network / GA4 hits)

This QA validates what the site pushes into its dataLayer (or equivalent JS layer), which is normally implemented BEFORE the GTM/GA4 tags that forward it. At that stage there are usually no analytics network beacons firing at all, so do not try to QA network requests (`/collect`, `/tr`, etc.), they would be empty or misleading. The captured JS push is the sole source of truth.

When the tags DO exist and the question is whether the data reached the vendors, that is `/qa-network-requests`, not this skill.

## Capturing an element's box (for tight location shots)

```js
const el = /* the button/control you clicked */;
const r = el.getBoundingClientRect();
const pad = r.width < 60 ? 60 : 12;   // widen the crop for tiny icon buttons
el.scrollIntoView({ block: 'center' });
({ region: [Math.round(r.x - pad), Math.round(r.y - pad),
             Math.round(r.x + r.width + pad), Math.round(r.y + r.height + pad)] });
```

Then screenshot with the `computer` `zoom` action, `region:` as above, `save_to_disk: true`, and use that saved file as `location_image`. The shot must show the control that caused the push, not any debug panel and not the whole page.

## Reading the captured push (top frame)

```js
window.__dlqa.map(e => e.name || (e.payload && e.payload.event));       // what fired
window.__dump(window.__dlqa[window.__dlqa.length - 1].payload);          // last push, verbatim + output-filter-safe
window.__dlqa = [];                                                      // reset before next trigger
```

`window.__dump(x)` = `JSON.stringify(x)` with `?`, `=`, `&`, `%` unicode-escaped so the browser tool's output filter does not blank query-string-looking results. It is still valid JSON and parses back byte-for-byte. Use it for every payload you return.

If a funnel action produces no entry, do not conclude "missing" yet, check for a web pixel (next section), and remember load-only events fire before the hook.

### Click-then-navigate and load-only events

- **Click-then-navigate** (`select_item`): the hook installs a `pagehide` listener that writes `window.__dlqa` to `sessionStorage.__dlqa_carry`. After the navigation, read and parse `sessionStorage.__dlqa_carry` on the new page.
- **Load-only** (`view_item_list`): fires once at document load before any injectable hook. It is almost always still capturable by re-firing the builder, see next section. Only fall back to `push: null` + `push_note` + blank checks + GA4 DebugView after every re-fire attempt fails. Do not fabricate values.

## Re-firing a load-only builder event (do this before giving up)

`view_item_list` (and any load-only event) fires before the hook exists, but the builder function persists on the page and can be called again with the hook installed. Ordered attempts:

**1. Re-invoke the builder with the correct argument.**

```js
// a) probe: call with no arg, note the error (usually "... reading 'map' of undefined")
try { window.tracking.collectionViewed(); } catch (e) { /* wrong/absent arg */ }

// b) discover the argument shape WITHOUT returning raw code (dodges the output filter):
//    return only the first property the builder reads off its parameter, a short safe token.
const fn = window.tracking.collectionViewed.toString();
const param = (fn.match(/^\s*function[^(]*\(\s*([^),\s]+)/) || fn.match(/\(?\s*([A-Za-z_$][\w$]*)\s*\)?\s*=>/) || [])[1] || 'e';
const prop = (fn.match(new RegExp(param.replace('$','\\$') + '\\.([A-Za-z_$][\\w$]*)')) || [])[1];  // e.g. "products" or "items"

// c) get the theme's own product objects (try these in order):
const prods =
  (window.meta && window.meta.products) ||
  (window.ShopifyAnalytics && ShopifyAnalytics.meta && ShopifyAnalytics.meta.products) ||
  (() => { try { return JSON.parse(document.querySelector('script[type="application/json"][id*="product"], script[type="application/json"][id*="collection"]').textContent); } catch (e) { return null; } })();

// d) re-call using the discovered property name, then read window.__dlqa:
window.__dlqa = [];
const shapes = [ prods, { [prop || 'products']: prods }, { products: prods }, { items: prods }, { collection: { products: prods } } ];
for (const s of shapes) { try { window.tracking.collectionViewed(s); if (window.__dlqa.length) break; } catch (e) {} }
window.__dump(window.__dlqa[window.__dlqa.length - 1]);
```

The wrapped hook captures whatever the builder publishes, that payload is the ground truth for the report.

**2. Trigger a real re-render** if the arg cannot be reconstructed. Use the collection's own controls, changing sort, applying/removing a filter, clicking pagination or "load more", or toggling country/currency, which makes the theme re-run the builder client-side while the hook is alive. Reset `window.__dlqa = []` first, then read it after.

**3. Last resort only:** `push: null`, `push_note` explaining it fires pre-hook, `source` from the pixel subscription, the block's checks left blank (it stays In progress), and a note recommending GA4 DebugView.

## Reading a web pixel / sandboxed source

The sandbox `sandbox` attribute forces an opaque origin, so you cannot read `iframe.contentWindow` or see its network from the top frame. But the pixel document is usually served from the site's own origin, so fetch it:

```js
const f = [...document.querySelectorAll('iframe')].find(f => /web-pixel-sandbox-CUSTOM/.test(f.name));
const src = f.src; // same-origin URL like https://<shop>/web-pixels@<hash>/custom/web-pixel...
const code = await fetch(src, { credentials: 'include' }).then(r => r.text());
window.__pixelSrc = code; // then inspect
```

Find the event handlers (`analytics.subscribe('checkout_started', ...)` etc.) and the object each pushes. Shopify checkout events map: `checkout_started` -> begin_checkout, `checkout_address_info_submitted` -> add_shipping_info, `payment_info_submitted` -> add_payment_info, `checkout_completed` -> purchase. Read which params are set, and which are hardcoded (`from_mini_bag: null`, `contains_from_mini_bag: null` etc.). A single shared builder (e.g. `buildEcommercePayload(checkout)`) usually feeds all checkout events, confirm and report them together.

**Output-filter workaround:** the browser tool may block raw minified JS in its response (it looks like tokens/query strings). Do not return raw code. Instead process it in-page and return only clean data: e.g. check which expected param names appear, or return a sanitised snippet that preserves short param-name tokens but masks long hashes and strips URL characters:

```js
const clean = s => s.replace(/[A-Za-z0-9_$]{27,}/g,'@').replace(/https?:\/\/[^\s"']+/g,'@url').replace(/[=&?%]/g,' ').replace(/\s+/g,' ').trim();
clean(window.__pixelSrc.slice(idx-90, idx+320));
```

(Keep the mask threshold above ~26 chars so real param names like `contains_from_mini_bag` survive; only long minified identifiers get masked.) If the source cannot be fetched (truly third-party origin, no CORS), fall back to verifying those events in GTM Preview / Tag Assistant or GA4 DebugView, and say so in the notes. Never guess values.

## The workbook

The QA team's checklist layout, built by `scripts/qa_checklist.py` (the same file ships in Tapa's DataLayer Doc Creator, keep the two identical):

- **Summary**: How to use, then `# | Category | Event | Variant / label | Trigger | Params | Status`, and `Passed: n / N`.
- **QA Checklist**: per block, the title (`N.  event   ·   variant`), category badge, status and a **Push** link; the `Trigger: ...   |   Note: ...` strip; then `Parameter | Type | Required | Expected value / example | Present / fired? | Value correct? | Notes`. Status = Fail if any check fails, In progress if any listed parameter has a blank check, Pass otherwise (N/A counts as passed). The formulas stay live and carry cached results, so Protected View and file previewers show the statuses too.
- **Captured pushes**: `# | Event | Source | Conditions tested | dataLayer push (verbatim JSON) | Location screenshot`, one row per block. A push longer than ~34 lines passes Excel's 409pt row ceiling: the cell still holds all of it (select it to read the rest).

Keep the output filename short (~12 chars max, generic), deep session paths hit the Windows 259-char limit and the workbook will not open.
