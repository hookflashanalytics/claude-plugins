# qa-network-requests - Reference

## Vendor endpoints and payload shapes

Match on the **path**, never the host. Under server-side tagging the collect endpoint is
first-party: Hookflash runs `hf-serverside-tagging`, and clients such as 123.ie post to
`metrics.123.ie/g/collect`. Matching `google-analytics.com` would report "no GA4 hits" on a
site sending thousands of them. `net_hook.js` matches on path for exactly this reason.

| Vendor | Endpoint (match the path) | Method | Where the payload lives |
|---|---|---|---|
| **GA4** | `/g/collect`, `/mp/collect`, `/ccm/collect` (any host, incl. first-party) | GET, or POST when batched/long | Query string; batched events in the body, one per line |
| **Meta (Facebook)** | `facebook.com/tr` | GET (image) | Query string |
| **TikTok** | `analytics.tiktok.com/api/v2/pixel` | POST | **JSON body only** |
| **Google Ads** | `googleads.g.doubleclick.net/pagead/viewthroughconversion/<id>/`, `googleadservices.com/pagead/conversion/` | GET | Query string |
| **Floodlight** | `ad.doubleclick.net/ddm/activity/` | GET | Path segments (`;`-delimited) plus query |
| **Microsoft UET** | `bat.bing.com/action/` | GET | Query string |
| **Pinterest** | `ct.pinterest.com/` | GET | Query string |
| **LinkedIn** | `px.ads.linkedin.com/collect` | GET | Query string |
| **Snapchat** | `tr.snapchat.com/` | GET | Query string |
| **Segment** | `api.segment.io/v1/` | POST | JSON body |

**Libraries are not hits.** `gtag/js`, `gtm.js`, `connect.facebook.net/*/fbevents.js`,
`analytics.tiktok.com/i18n/pixel/events.js`, `bat.bing.com/bat.js` are the tag libraries
loading. Seeing them proves the vendor is installed, **not** that anything was sent. Their
presence is still useful: a library that loaded but never sent tells you the tag is installed
and gated (often on consent or a trigger), which is a much sharper finding than "nothing fired".

Anything else that looks like a beacon (a path containing `collect`, `track`, `event`, `pixel`,
`/tr`, `/p`) lands in the `unclassified` list from `__nqaAll()`. **Read that list on every run.**
It is where an undocumented vendor, an affiliate network (Awin, Rakuten, Impact), a CDP, or a
first-party endpoint the matcher does not know will show up.

## GA4 parameters worth knowing

| Param | Meaning |
|---|---|
| `v=2` | GA4 protocol version (`v=1` is Universal Analytics, i.e. a legacy tag still firing) |
| `tid` | Measurement ID (`G-XXXXXXX`). **Check this against the spec**: right hit, wrong property is a silent failure |
| `en` | Event name (`page_view`, `add_to_cart`, ...) |
| `cid` | Client ID. Note presence only, truncate the value |
| `sid`, `sct`, `seg` | Session ID, session count, session engaged |
| `dl`, `dr`, `dt` | Document location, referrer, title |
| `cu` | Currency (this is where currency lives, not `ep.currency`) |
| `epn.<name>` | Event parameter, **numeric** (`epn.value`, `epn.quantity`) |
| `ep.<name>` | Event parameter, **string** (`ep.item_list_name`, `ep.coupon`) |
| `up.<name>` / `upn.<name>` | User property, string / numeric |
| `pr1` ... `prN` | Items, one per product (see below) |
| `gcs`, `gcd` | Consent state and consent defaults (see the consent section in SKILL.md) |
| `npa` | Non-personalised ads flag |
| `_et` | Engagement time in ms |
| `sr`, `ul`, `vp` | Screen resolution, language, viewport. Transport detail, not spec material |
| `_p`, `_s`, `tfd` | Internal page/hit counters and time-to-first-dispatch. Ignore unless debugging ordering |

A number arriving as `ep.value` rather than `epn.value` means GA4 received it as a **string**,
which is a real finding: it will not aggregate as a metric.

### GA4 item prefixes (inside `pr1`, `pr2`, ...)

Each item is a `~`-delimited string of two-character prefixed fields, e.g.
`idSKU123~nmBlue Shirt~brAcme~caShirts~vaBlue~pr29.99~qt2`.

| Prefix | Field |
|---|---|
| `id` | item_id |
| `nm` | item_name |
| `br` | item_brand |
| `ca` | item_category (`ca2`..`ca5` for category2 to category5) |
| `va` | item_variant |
| `pr` | price |
| `qt` | quantity |
| `cp` | coupon |
| `ds` | discount |
| `af` | affiliation |
| `li` | item_list_id |
| `ln` | item_list_name |
| `lp` | index / list position |
| `lo` | location_id |

**Keep any prefix not in this table verbatim rather than guessing at it**, and sanity-check the
whole decode against the same event's dataLayer push or the spec before relying on it. A
mis-decoded prefix produces a confident, wrong finding.

## Nothing fired: work through this before recording a miss

**Nothing here is optional, and none of it is satisfied by prose.** The claim ships with an
`absence_evidence` string of the form "N requests searched, none matching X", or
`build_report.py` stamps the row `!! UNVERIFIED`. See SKILL.md "Claiming something did not fire".

0. **Search unfiltered, and count what you searched.** `window.__nqaRequests()` returns every
   request with a total; `window.__nqaRequests('collect')` narrows it so you can see what you
   narrowed. Match on **path**, never host: server-side tagging puts the endpoint on the
   client's own domain (`data.<client>.com/g/collect`), so searching `google-analytics.com`
   returns nothing on a site sending thousands of hits.
1. **Did the interaction actually happen?** Re-read the page. An AJAX add-to-cart that silently
   failed sends nothing because nothing happened, which is a site bug, not a tracking bug.
2. **Wait longer and re-read.** Beacons are async and vendors do not fire together (Google's
   `/ccm/collect` consent ping lands before GA4's `/g/collect`). Wait 1 to 2 seconds, read again.
3. **Was the mark set before the click?** A mark set after the beacon filters it out.
4. **Did the hook survive the navigation?** Re-install `net_hook.js` after every page load.
5. **Is it a POST-body vendor** (TikTok, Segment) with the hook missing? The performance buffer
   sees the request but has no body, so the hit looks empty rather than absent.
6. **Did the vendor's library load at all?** Check for `gtag/js`, `fbevents.js`, `events.js` in
   the performance buffer, and for the globals: `window.dataLayer`, `window.fbq`, `window.ttq`,
   `window.uetq`, `window.google_tag_manager`. Library present but nothing sent = installed and
   gated. Library absent = not installed on this page. **This is the only legitimate use of
   `window.dataLayer` in this skill**: it tells you the stack is installed. It is never evidence
   about whether a hit was sent, and its contents must never be filtered to decide that (sites
   customise the push shape, so a guessed field name yields a false negative).
7. **Is it gated on consent?** If the consent check ran with consent denied, a vendor sending
   nothing is the expected behaviour of a consent-gated tag, not a missing tag. Grant consent
   and retry before recording a miss.
8. **Is it fired only on a different page or template?** Check the spec for where it should fire.

Only after all of these: record `sent: false`, verdict `fail`, an `absence_evidence` string
carrying the number of requests you searched, and notes saying which of the above you ruled out.
Never guess a payload for a hit you did not see.

**And if you later learn you were wrong about a shape, an endpoint or a vendor, come back and
re-audit every absence you recorded before you knew it.** A null recorded early in the run is the
one most likely to be wrong, because that is when you knew least.

## Discovery snippets

**Install the hook** (via `javascript_tool`, re-run after every navigation):

```js
// paste the contents of scripts/net_hook.js
```

**What is this site sending?**

```js
window.__nqaAll()        // recognised hits (decoded) + an `unclassified` list + `libraries`
```

**Attribute hits to one interaction:**

```js
window.__nqaMark();      // BEFORE the click
// ... click, wait ~1.5s ...
window.__nqaSince();     // decoded hits since the mark, escaped for the output filter
```

**Which analytics globals exist:**

```js
({
  dataLayer: Array.isArray(window.dataLayer), gtag: typeof window.gtag === 'function',
  gtm: !!window.google_tag_manager, fbq: !!window.fbq, ttq: !!window.ttq,
  uetq: !!window.uetq, pintrk: !!window.pintrk, lintrk: !!window.lintrk,
  snaptr: !!window.snaptr, analytics: !!window.analytics,
  consentState: (() => { try { return window.google_tag_data.ics.getConsentState(); } catch (e) { return null; } })()
})
```

**Force the pre-consent state** (run `scripts/reset_consent.js`, then reload). It clears cookies,
localStorage, sessionStorage and best-effort IndexedDB for the origin, and returns the cookie
names that survived. Survivors are almost certainly `HttpOnly` and cannot be cleared from JS; if
a consent cookie is among them, say the reset was partial rather than claiming a clean slate.
**It logs the user out and empties the cart**, and can drop a Shopify preview out of its theme,
so warn first and always run it before the funnel walk.

**Consent surface:**

```js
({
  banner: !!document.querySelector('[id*=onetrust], [class*=ot-sdk], #CybotCookiebotDialog, [id*=usercentrics], [class*=cky-], [id*=cookie], [class*=consent], [class*=gdpr]'),
  onetrust: window.OnetrustActiveGroups || null,
  tcf: typeof window.__tcfapi === 'function',
  cookies: document.cookie.split(';').map(c => c.trim().split('=')[0]).filter(n => /consent|ot|cook|cky|euconsent|usercentrics/i.test(n))
})
```

Note the last line uses `split('=')`, so return it through `window.__dump()` like everything else.

## Standard GA4 ecommerce expectations (fallback only, when the user has no spec)

Prefer the user's spec always. With no spec, check that item events carry `cu`, `epn.value`, and
per item `id`, `nm`, `br`, `ca`, `va`, `pr`, `qt`; that `tid` is the expected property; and that
`en` matches the standard names (`view_item_list`, `select_item`, `view_item`, `add_to_cart`,
`view_cart`, `remove_from_cart`, `begin_checkout`, `add_shipping_info`, `add_payment_info`,
`purchase`). Coupon, discount and tax fields are frequently empty pre-checkout. Label every
verdict as measured against the default expectations, not against a client spec.

Cart-event semantics (delta vs whole-cart) are in SKILL.md under "Auditing against the spec";
they matter as much here as in `/qa-datalayer`.

## events.json schema

A list, one object per hit, in funnel order. See the header of `scripts/build_report.py` for the
authoritative list.

- `event`: the event name as the **spec** calls it (e.g. `add_to_cart`).
- `vendor`: `"GA4"` | `"Meta"` | `"TikTok"` | ... **Decides which tab the hit lands on**, so spell
  it identically on every row for a platform or you get two tabs for one vendor.
- `sent`: `true` | `false`. `false` renders the request cell as "No request observed".
- `method`: `"GET"` | `"POST"`.
- `endpoint`: host + path only, e.g. `metrics.example.com/g/collect`. Keeps the column readable.
- `url`: the **verbatim** full URL. Never trimmed or rewritten.
- `body`: the verbatim request body, or null.
- `payload`: a dict of every decoded param (`{"en": "add_to_cart", "epn.value": 29.99, ...}`).
  Renders as **Full payload**, dumped with `indent=2`. Vendor param names, not renamed.
- `spec_params`: list of the param names **the spec cares about**, as this vendor sends them.
  Renders as **Spec parameters**, with values pulled out of `payload` by the script (see below).
- `spec_payload`: optional explicit dict, overrides `spec_params`. Only for mappings that are not
  a lookup.
- `conditions`: what you did to trigger it.
- `location_image`: filename inside the screenshots dir. Prefer a tight crop saved via the
  `computer` `zoom` action.
- `verdict`: `pass` | `fail` | `warn` | `na`. `notes`: list of `"- ..."` bullets, no em/en dashes.
- `count`: optional integer, how many identical hits fired for the one interaction. Rendered
  when > 1, so duplicate tagging is visible.

### Worked `spec_params`, per vendor

The point of this column is to answer "did the spec get what it asked for" without the reader
wading through `cid`, `gcs`, `sr`, `ul` and `_p`. Values are resolved out of `payload`, so they
cannot disagree with the Full payload beside them, and anything missing renders `(absent)` in a
red cell.

| Spec asks for | GA4 | Meta | TikTok |
|---|---|---|---|
| event name | `en` | `ev` | `__body_json.event` |
| value | `epn.value` | `cd[value]` | `__body_json.properties.value` |
| currency | `cu` | `cd[currency]` | `__body_json.properties.currency` |
| a custom param | `ep.link_text` | `cd[link_text]` | `__body_json.properties.link_text` |
| destination ID | `tid` | `id` | `__body_json.context.pixel.code` |
| item id / name | `items[].item_id`, `items[].item_name` | `cd[content_ids]` | `__body_json.properties.contents` |

So a nav-click spec with an event name and two params is simply:

```json
"spec_params": ["en", "ep.link_text", "ep.link_url"]
```

Include `tid` / pixel ID whenever the spec names a property or pixel: a perfectly-formed hit sent
to the wrong destination is a silent, expensive failure that every other column would pass.

## consent.json schema

A list, one object per vendor, plus optionally one state object first.

- `state`: `"forced"` (the normal case: you cleared cookies and reloaded) | `"already_accepted"`
  (the reset did not bring the banner back) | `"not_accepted"` (a banner was up anyway).
- `reset`: optional sentence describing what the reset actually cleared, e.g.
  `"Cleared 14 cookies and 22 localStorage keys, then reloaded."` Appended to the banner line.
- `vendor`: vendor name.
- `before`: what was observed before consent, e.g. `"1 hit (page_view)"` or `"No hits observed"`.
- `signal`: the consent signal on those hits, e.g. `"gcs=G100 (ad_storage denied, analytics_storage denied)"`, or `"n/a (no consent parameter)"`.
- `after`: what was observed after granting consent.
- `observation`: one or two plain descriptive sentences. **Describe, do not grade.** No verdict
  field exists on this tab by design.
- `location_image`: optional, normally the cookie banner screenshot.

## Workbook layout

**Tab 1, "Consent"** (always first): Vendor | Before consent | Consent signal | After consent |
Observation | Screenshot. No pass/fail column, by design.

**Tab 2..N, one per platform** (`GA4`, `Meta`, `TikTok`, ... in the order they first appear in
`events.json`): Event name | Conditions tested | Request (method, endpoint, verbatim URL, body) |
Full payload | Spec parameters | Location screenshot | Pass / Fail.

There is no Vendor column on the platform tabs; the tab name is the vendor. Tab names are
sanitised for Excel (31 chars, no `: \ / ? * [ ]`, deduplicated) and tinted per vendor.

Rows auto-size to fit. Keep the output filename short (~12 chars max, generic): deep session
paths hit the Windows 259-char limit and the workbook will not open.
