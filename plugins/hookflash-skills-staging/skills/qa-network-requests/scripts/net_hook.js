/* qa-network-requests: outgoing analytics request capture.
 *
 * Paste the whole file into javascript_tool. RE-INSTALL AFTER EVERY NAVIGATION
 * (a page load wipes it). Installing twice is safe, it no-ops.
 *
 * Two layers, merged:
 *   1. performance.getEntriesByType('resource') - sees EVERY request including
 *      page-load hits fired before this hook existed, but URLs only, no bodies.
 *      Resets on every navigation.
 *   2. these wrappers (fetch / XHR / sendBeacon / img.src) - attach request
 *      BODIES, which is the only way to read TikTok, Segment or a batched GA4 hit.
 *
 * API:
 *   window.__nqaMark()      -> set a baseline immediately BEFORE an interaction
 *   window.__nqaSince()     -> decoded hits that started after the mark (escaped)
 *   window.__nqaAll()       -> every hit this page has made + unclassified + libraries
 *   window.__nqaRequests(f) -> EVERY request, unfiltered, optionally substring/regex
 *                              filtered. Required evidence before claiming absence.
 *   window.__dump(obj)      -> JSON escaped so the tool's output filter cannot blank it
 *   window.__nqaRaw         -> the raw hook-captured array, if you need it
 */
(function () {
  if (window.__nqa_installed) { return "net_hook already installed"; }
  window.__nqa_installed = true;

  var MAX_BODY = 20000;
  var raw = [];
  window.__nqaRaw = raw;
  var mark = 0;

  /* ---- the output-filter escape. Every read must go through this. ---- */
  window.__dump = function (x) {
    return JSON.stringify(x)
      .replace(/\?/g, "\\u003f").replace(/=/g, "\\u003d")
      .replace(/&/g, "\\u0026").replace(/%/g, "\\u0025");
  };

  /* ---- vendor matching: PATH first, never host. Server-side tagging makes the
         collect endpoint first-party (e.g. metrics.client.com/g/collect). ---- */
  var VENDORS = [
    [/\/(g|mp|ccm)\/collect/i,                                        "GA4"],
    [/facebook\.com\/tr/i,                                            "Meta"],
    [/analytics\.tiktok\.com\/api\//i,                                "TikTok"],
    [/googleads\.g\.doubleclick\.net\/pagead|googleadservices\.com\/pagead\/conversion/i, "Google Ads"],
    [/ad\.doubleclick\.net\/ddm\/activity/i,                          "Floodlight"],
    [/bat\.bing\.com\/action/i,                                       "Microsoft UET"],
    [/ct\.pinterest\.com/i,                                           "Pinterest"],
    [/px\.ads\.linkedin\.com/i,                                       "LinkedIn"],
    [/tr\.snapchat\.com/i,                                            "Snapchat"],
    [/api\.segment\.io\/v1/i,                                         "Segment"],
    [/google-analytics\.com\/(collect|r\/collect)|\/__utm\.gif/i,      "Universal Analytics (legacy)"]
  ];
  /* Libraries loading, NOT hits. Seeing one proves the vendor is installed only. */
  var LIBS = /gtag\/js|gtm\.js|fbevents\.js|i18n\/pixel\/events\.js|bat\.bing\.com\/bat\.js|analytics\.js|snap\.min\.js|insight\.min\.js|pinit|tiktok.*config\.js/i;
  /* Anything else beacon-shaped, so an unknown vendor still surfaces. */
  var MAYBE = /\/(collect|track|tracking|event|events|pixel|beacon|analytics|tr|p|i)(\/|\?|$)|\/v\d\/(t|track|pixel)/i;

  function vendorOf(url) {
    for (var i = 0; i < VENDORS.length; i++) {
      if (VENDORS[i][0].test(url)) { return VENDORS[i][1]; }
    }
    return null;
  }

  /* ---- body normalisation. sendBeacon and fetch often send a Blob, which is
         async to read, so the entry is created now and patched when it resolves. ---- */
  function setBody(entry, body) {
    if (body == null) { entry.body = null; return; }
    try {
      if (typeof body === "string") { entry.body = body.slice(0, MAX_BODY); return; }
      if (typeof URLSearchParams !== "undefined" && body instanceof URLSearchParams) {
        entry.body = body.toString().slice(0, MAX_BODY); return;
      }
      if (typeof Blob !== "undefined" && body instanceof Blob) {
        entry.body = "(blob, reading...)";
        body.text().then(function (t) { entry.body = t.slice(0, MAX_BODY); })
                   .catch(function () { entry.body = "(blob, unreadable)"; });
        return;
      }
      if (typeof FormData !== "undefined" && body instanceof FormData) {
        var out = [];
        body.forEach(function (v, k) { out.push(k + "=" + v); });
        entry.body = out.join("&").slice(0, MAX_BODY); return;
      }
      if (body.byteLength != null) {
        entry.body = new TextDecoder().decode(body).slice(0, MAX_BODY); return;
      }
      entry.body = "(unreadable body: " + Object.prototype.toString.call(body) + ")";
    } catch (e) {
      entry.body = "(body read failed: " + e.message + ")";
    }
  }

  function record(method, url, body, via) {
    try {
      url = String(url);
      if (url.indexOf("data:") === 0 || url.indexOf("blob:") === 0) { return; }
      var abs = url;
      try { abs = new URL(url, location.href).href; } catch (e) {}
      var entry = { t: Math.round(performance.now()), method: method, url: abs, body: null, via: via };
      setBody(entry, body);
      raw.push(entry);
    } catch (e) {}
  }

  /* ---- fetch ---- */
  var _fetch = window.fetch;
  if (_fetch) {
    window.fetch = function (input, init) {
      try {
        var u = (input && input.url) ? input.url : input;
        var m = (init && init.method) || (input && input.method) || "GET";
        record(String(m).toUpperCase(), u, init && init.body, "fetch");
      } catch (e) {}
      return _fetch.apply(this, arguments);
    };
  }

  /* ---- XMLHttpRequest ---- */
  var _open = XMLHttpRequest.prototype.open;
  var _send = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (m, u) {
    try { this.__nqa_m = String(m || "GET").toUpperCase(); this.__nqa_u = u; } catch (e) {}
    return _open.apply(this, arguments);
  };
  XMLHttpRequest.prototype.send = function (body) {
    try { record(this.__nqa_m || "GET", this.__nqa_u, body, "xhr"); } catch (e) {}
    return _send.apply(this, arguments);
  };

  /* ---- navigator.sendBeacon (how most tags leave on unload) ---- */
  if (navigator.sendBeacon) {
    var _beacon = navigator.sendBeacon.bind(navigator);
    navigator.sendBeacon = function (u, data) {
      try { record("POST", u, data, "sendBeacon"); } catch (e) {}
      return _beacon(u, data);
    };
  }

  /* ---- image pixels (new Image().src = ...), how Meta and most GET pixels fire.
         The performance buffer also catches these; this gives ordering. ---- */
  try {
    var d = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, "src");
    if (d && d.set) {
      Object.defineProperty(HTMLImageElement.prototype, "src", {
        get: d.get,
        set: function (v) { try { record("GET", v, null, "img"); } catch (e) {} return d.set.call(this, v); },
        configurable: true, enumerable: d.enumerable
      });
    }
  } catch (e) {}

  /* ---- carry captured hits across a click-then-navigate unload ---- */
  window.addEventListener("pagehide", function () {
    try { sessionStorage.__nqa_carry = JSON.stringify(raw.slice(-80)); } catch (e) {}
  });

  /* ================= decoding ================= */

  function parseQS(s) {
    var out = {};
    if (!s) { return out; }
    s.replace(/^[?&]/, "").split("&").forEach(function (kv) {
      if (!kv) { return; }
      var i = kv.indexOf("=");
      var k = i < 0 ? kv : kv.slice(0, i);
      var v = i < 0 ? "" : kv.slice(i + 1);
      try { k = decodeURIComponent(k.replace(/\+/g, " ")); } catch (e) {}
      try { v = decodeURIComponent(v.replace(/\+/g, " ")); } catch (e) {}
      if (out[k] === undefined) { out[k] = v; }
      else if (Array.isArray(out[k])) { out[k].push(v); }
      else { out[k] = [out[k], v]; }
    });
    return out;
  }

  /* GA4 items: pr1 = "idSKU~nmName~pr29.99~qt2". Unknown prefixes are kept
     VERBATIM under their raw prefix rather than guessed at. */
  var PR = { id: "item_id", nm: "item_name", br: "item_brand", ca: "item_category",
             ca2: "item_category2", ca3: "item_category3", ca4: "item_category4",
             ca5: "item_category5", va: "item_variant", pr: "price", qt: "quantity",
             cp: "coupon", ds: "discount", af: "affiliation", li: "item_list_id",
             ln: "item_list_name", lp: "index", lo: "location_id" };

  function decodeItem(s) {
    var item = {};
    String(s).split("~").forEach(function (f) {
      if (!f) { return; }
      var key = null;
      /* longest prefix first so ca2..ca5 beat ca */
      var cands = Object.keys(PR).sort(function (a, b) { return b.length - a.length; });
      for (var i = 0; i < cands.length; i++) {
        if (f.indexOf(cands[i]) === 0) { key = cands[i]; break; }
      }
      if (key) { item[PR[key] + " (" + key + ")"] = f.slice(key.length); }
      else { item["(unrecognised prefix) " + f.slice(0, 2)] = f.slice(2); }
    });
    return item;
  }

  function decodeGA4(params) {
    var items = [];
    Object.keys(params).forEach(function (k) {
      if (/^pr\d+$/.test(k)) { items.push(decodeItem(params[k])); delete params[k]; }
    });
    if (items.length) { params.items = items; }
    return params;
  }

  /* One hit -> one or more decoded events (a batched GA4 POST is many). */
  function decode(hit) {
    var vendor = vendorOf(hit.url) || "unclassified";
    var u, qs = "", endpoint = hit.url;
    try { u = new URL(hit.url); qs = u.search; endpoint = u.host + u.pathname; } catch (e) {}

    var base = parseQS(qs);
    var body = hit.body;
    var events = [];

    if (body && typeof body === "string" && body.indexOf("(blob") !== 0) {
      var t = body.trim();
      if (t.charAt(0) === "{" || t.charAt(0) === "[") {
        try { base.__body_json = JSON.parse(t); }
        catch (e) { base.__body_raw = t; }
        events.push(base);
      } else if (t.indexOf("\n") >= 0) {
        /* GA4 batch: one event per line, each its own query string */
        t.split("\n").forEach(function (line) {
          if (!line.trim()) { return; }
          var merged = {};
          Object.keys(base).forEach(function (k) { merged[k] = base[k]; });
          var lp = parseQS(line);
          Object.keys(lp).forEach(function (k) { merged[k] = lp[k]; });
          events.push(merged);
        });
      } else {
        var bp = parseQS(t);
        Object.keys(bp).forEach(function (k) { base[k] = bp[k]; });
        events.push(base);
      }
    } else {
      if (body) { base.__body = body; }
      events.push(base);
    }

    if (vendor === "GA4") { events = events.map(decodeGA4); }

    return events.map(function (p) {
      return {
        vendor: vendor, method: hit.method || "GET", endpoint: endpoint,
        /* en=GA4, ev=Meta, Ev/evt=Microsoft UET, event/type=JSON-body vendors */
        event: p.en || p.ev || p.Ev || p.evt || p.event ||
               (p.__body_json && (p.__body_json.event || p.__body_json.event_name || p.__body_json.type)) || null,
        url: hit.url, body: hit.body, payload: p, via: hit.via, t: hit.t
      };
    });
  }

  /* ================= reading ================= */

  /* performance entries -> hit shape, so load-time hits (page_view, consent
     pings) are visible even though they fired before this hook existed. */
  function perfHits(since) {
    var out = [];
    try {
      performance.getEntriesByType("resource").forEach(function (e) {
        if (since != null && e.startTime <= since) { return; }
        if (!vendorOf(e.name)) { return; }
        out.push({ t: Math.round(e.startTime), method: "GET", url: e.name, body: null, via: "performance" });
      });
    } catch (e) {}
    return out;
  }

  /* Merge the two layers on URL, preferring the hook entry (it has the body). */
  function merge(hookHits, pHits) {
    var seen = {}, out = [];
    hookHits.forEach(function (h) { seen[h.url] = true; out.push(h); });
    pHits.forEach(function (h) { if (!seen[h.url]) { out.push(h); } });
    out.sort(function (a, b) { return a.t - b.t; });
    return out;
  }

  window.__nqaMark = function () {
    mark = performance.now();
    return "marked at " + Math.round(mark) + "ms, now perform the interaction";
  };

  window.__nqaSince = function () {
    var hookHits = raw.filter(function (h) { return h.t > mark && vendorOf(h.url); });
    var hits = merge(hookHits, perfHits(mark));
    var events = [];
    hits.forEach(function (h) { events = events.concat(decode(h)); });
    return window.__dump({ mark: Math.round(mark), count: events.length, events: events });
  };

  window.__nqaAll = function () {
    var hookHits = raw.filter(function (h) { return vendorOf(h.url); });
    var hits = merge(hookHits, perfHits(null));
    var events = [];
    hits.forEach(function (h) { events = events.concat(decode(h)); });

    /* everything else, so an unknown vendor cannot hide.
       NOTE: same-host beacons are included too. Under server-side tagging the
       collect endpoint is first-party, so filtering to cross-origin only would
       hide exactly the hits this skill most needs to find. */
    var unclassified = [], libraries = [];
    try {
      performance.getEntriesByType("resource").forEach(function (e) {
        var host = ""; try { host = new URL(e.name).host; } catch (x) {}
        if (LIBS.test(e.name)) { libraries.push(host + (new URL(e.name).pathname)); return; }
        if (vendorOf(e.name)) { return; }
        if (MAYBE.test(e.name)) {
          unclassified.push({ url: e.name.slice(0, 300), initiator: e.initiatorType,
                              firstParty: host === location.host });
        }
      });
    } catch (e) {}

    return window.__dump({
      recognised: events.length, events: events,
      unclassified: unclassified, libraries: libraries.filter(function (v, i, a) { return a.indexOf(v) === i; }),
      carry: (function () { try { return sessionStorage.__nqa_carry ? JSON.parse(sessionStorage.__nqa_carry).length : 0; } catch (e) { return 0; } })()
    });
  };

  /* EVERY request this page has made, unfiltered, with an optional substring or
     regex filter. This is the evidence source for an ABSENCE claim: you cannot
     write "no GA4 hits" off a filtered view that might be filtering wrongly, so
     dump the whole set, search it yourself, and report the count you searched.
       window.__nqaRequests()             -> all of them
       window.__nqaRequests('collect')    -> just those containing "collect"
     Returns {total, shown, urls}: `total` is the number you actually searched,
     which is the number that belongs in the report. */
  window.__nqaRequests = function (filter) {
    var all = [];
    try {
      all = performance.getEntriesByType("resource").map(function (e) {
        return { url: e.name, initiator: e.initiatorType };
      });
    } catch (e) {}
    /* the hook sees things the buffer can miss (and vice versa), so union them */
    raw.forEach(function (h) {
      if (!all.some(function (a) { return a.url === h.url; })) {
        all.push({ url: h.url, initiator: h.via });
      }
    });
    var shown = all;
    if (filter) {
      var re = (filter instanceof RegExp) ? filter : new RegExp(String(filter), "i");
      shown = all.filter(function (a) { return re.test(a.url); });
    }
    /* Say it in words as well as numbers. A filter that matched something is not
       an absence, and "shown: 1" is too easy to skim past while writing "none
       matching" underneath it. */
    var hint;
    if (!filter) {
      hint = all.length + " requests seen on this page";
    } else if (shown.length) {
      hint = "MATCHES FOUND (" + shown.length + " of " + all.length +
             ") - this is NOT an absence, read the urls below";
    } else {
      hint = "0 of " + all.length + " requests matched - safe to record as absent, " +
             "evidence: \"" + all.length + " requests searched, none matching " +
             String(filter) + "\"";
    }

    return window.__dump({
      total: all.length,
      shown: shown.length,
      filter: filter ? String(filter) : null,
      verdict: hint,
      urls: shown.map(function (a) { return a.initiator + " " + a.url.slice(0, 300); })
    });
  };

  /* hits carried across a click-then-navigate unload */
  window.__nqaCarry = function () {
    var c = [];
    try { c = JSON.parse(sessionStorage.__nqa_carry || "[]"); } catch (e) {}
    var events = [];
    c.filter(function (h) { return vendorOf(h.url); }).forEach(function (h) { events = events.concat(decode(h)); });
    return window.__dump({ count: events.length, events: events });
  };

  return "net_hook installed (fetch, xhr, sendBeacon, img) + performance layer";
})();
