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

1. **Did the interaction actually happen?** Re-read the page. An AJAX add-to-cart that silently
   failed sends nothing because nothing happened, which is a site bug, not a tracking bug.
2. **Wait longer and re-read.** Beacons are async. Wait 1 to 2 seconds, read again.
3. **Was the mark set before the click?** A mark set after the beacon filters it out.
4. **Did the hook survive the navigation?** Re-install `net_hook.js` after every page load.
5. **Is it a POST-body vendor** (TikTok, Segment) with the hook missing? The performance buffer
   sees the request but has no body, so the hit looks empty rather than absent.
6. **Did the vendor's library load at all?** Check for `gtag/js`, `fbevents.js`, `events.js` in
   the performance buffer, and for the globals: `window.dataLayer`, `window.fbq`, `window.ttq`,
   `window.uetq`, `window.google_tag_manager`. Library present but nothing sent = installed and
   gated. Library absent = not installed on this page.
7. **Is it gated on consent?** If the consent check ran with consent denied, a vendor sending
   nothing is the expected behaviour of a consent-gated tag, not a missing tag. Grant consent
   and retry before recording a miss.
8. **Is it fired only on a different page or template?** Check the spec for where it should fire.

Only after all of these: record `sent: false`, verdict `fail`, and say in the notes which of the
above you ruled out. Never guess a payload for a hit you did not see.

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
- `vendor`: `"GA4"` | `"Meta"` | `"TikTok"` | ... Drives the Vendor column colour.
- `sent`: `true` | `false`. `false` renders the request cell as "No request observed".
- `method`: `"GET"` | `"POST"`.
- `endpoint`: host + path only, e.g. `metrics.example.com/g/collect`. Keeps the column readable.
- `url`: the **verbatim** full URL. Never trimmed or rewritten.
- `body`: the verbatim request body, or null.
- `payload`: a dict of decoded params (`{"en": "add_to_cart", "epn.value": 29.99, "pr1": {...}}`).
  Dumped with `indent=2`. Vendor param names, not renamed.
- `conditions`: what you did to trigger it.
- `location_image`: filename inside the screenshots dir. Prefer a tight crop saved via the
  `computer` `zoom` action.
- `verdict`: `pass` | `fail` | `warn` | `na`. `notes`: list of `"- ..."` bullets, no em/en dashes.
- `count`: optional integer, how many identical hits fired for the one interaction. Rendered
  when > 1, so duplicate tagging is visible.

## consent.json schema

A list, one object per vendor, plus optionally one `state` object first.

- `state`: `"not_accepted"` | `"already_accepted"`. When `already_accepted`, one row is enough:
  say pre-consent behaviour was not observed and offer a clean-profile re-run.
- `vendor`: vendor name.
- `before`: what was observed before consent, e.g. `"1 hit (page_view)"` or `"No hits observed"`.
- `signal`: the consent signal on those hits, e.g. `"gcs=G100 (ad_storage denied, analytics_storage denied)"`, or `"n/a (no consent parameter)"`.
- `after`: what was observed after granting consent.
- `observation`: one or two plain descriptive sentences. **Describe, do not grade.** No verdict
  field exists on this sheet by design.
- `location_image`: optional, normally the cookie banner screenshot.

## Report columns

**Sheet 1, "Network QA":** Event name | Vendor | Conditions tested | Request (method, endpoint,
verbatim URL, body) | Decoded payload | Location screenshot | Pass / Fail.

**Sheet 2, "Consent":** Vendor | Before consent | Consent signal | After consent | Observation |
Screenshot. No pass/fail column, by design.

Rows auto-size to fit. Keep the output filename short (~12 chars max, generic): deep session
paths hit the Windows 259-char limit and the workbook will not open.
