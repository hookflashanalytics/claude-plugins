// qa-datalayer capture hook.
// Install once per page via the browser javascript_tool. RE-INSTALL AFTER EVERY NAVIGATION
// (page load wipes it). Reset before triggering an event with:  window.__dlqa = [];
//
// PLATFORM-AGNOSTIC. Captures pushes from whichever mechanisms the site actually uses:
//   1. window.dataLayer.push              (GTM / GA4 via GTM)   - universal
//   2. window.gtag(...)                    (GA4 direct)
//   3. window.utag.link / window.utag.view (Tealium)
//   4. Shopify.analytics.publish(name, payload)   (Shopify / vendor pub-sub bus; custom events
//                                                   often prefixed, e.g. 'tbtg:view_item')
//   5. window.tracking.<method>(...)       (bespoke site/theme module that BUILDS + publishes)
// It only wraps what exists on the page, so it is safe on any stack. For Adobe (_satellite) or
// other vendors, add a wrapper following the same pattern. Scope is the JS push layer only, this
// skill runs before analytics tags forward the dataLayer, so there are no network beacons to read.
// Everything lands on window.__dlqa. Read it verbatim (and output-filter-safe) with window.__dump():
//   window.__dump(window.__dlqa[window.__dlqa.length - 1].payload)
//
// Also installs a pagehide sessionStorage "carry" so click-then-navigate events (e.g. select_item,
// which fires just before the PDP loads) survive the navigation: read sessionStorage.__dlqa_carry
// on the next page and JSON.parse it.
(function () {
  window.__dlqa = window.__dlqa || [];

  // Output-filter-safe serialiser: escapes ? = & % so the browser tool does not blank a
  // query-string-looking result. Still valid JSON, decodes back byte-for-byte.
  window.__dump = window.__dump || function (x) {
    return JSON.stringify(x)
      .replace(/\?/g, "\\u003f")
      .replace(/=/g, "\\u003d")
      .replace(/&/g, "\\u0026")
      .replace(/%/g, "\\u0025");
  };

  // --- 1. Standard dataLayer (GTM / GA4) ---
  window.dataLayer = window.dataLayer || [];
  if (!window.__dlqaHooked) {
    var origPush = window.dataLayer.push.bind(window.dataLayer);
    window.dataLayer.push = function () {
      var args = Array.prototype.slice.call(arguments);
      try {
        args.forEach(function (a) {
          window.__dlqa.push({ t: Date.now(), source: "dataLayer", payload: JSON.parse(JSON.stringify(a)) });
        });
      } catch (e) {}
      return origPush.apply(null, args);
    };
    window.__dlqaHooked = true;
  }

  // --- 2. gtag (GA4 direct) ---
  try {
    if (typeof window.gtag === "function" && !window.__dlqaGtagHooked) {
      var ogtag = window.gtag;
      window.gtag = function () {
        var args = Array.prototype.slice.call(arguments);
        try {
          if (args[0] === "event") {
            window.__dlqa.push({ t: Date.now(), source: "gtag", name: args[1], payload: JSON.parse(JSON.stringify(args[2] || null)) });
          }
        } catch (e) {}
        return ogtag.apply(this, args);
      };
      window.__dlqaGtagHooked = true;
    }
  } catch (e) {}

  // --- 3. Tealium (utag.link / utag.view) ---
  try {
    if (window.utag && !window.__dlqaUtagHooked) {
      ["link", "view"].forEach(function (m) {
        if (typeof window.utag[m] === "function") {
          var ou = window.utag[m].bind(window.utag);
          window.utag[m] = function (data) {
            try { window.__dlqa.push({ t: Date.now(), source: "utag." + m, name: (data && (data.tealium_event || data.event_name)) || m, payload: JSON.parse(JSON.stringify(data || null)) }); } catch (e) {}
            return ou.apply(null, arguments);
          };
        }
      });
      window.__dlqaUtagHooked = true;
    }
  } catch (e) {}

  // --- 4. Shopify / vendor analytics bus (top-frame publisher) ---
  try {
    if (window.Shopify && Shopify.analytics && Shopify.analytics.publish && !window.__dlqaShopifyHooked) {
      var op = Shopify.analytics.publish.bind(Shopify.analytics);
      Shopify.analytics.publish = function (name, payload, opts) {
        try {
          window.__dlqa.push({ t: Date.now(), source: "shopify.publish", name: name, payload: JSON.parse(JSON.stringify(payload || null)) });
        } catch (e) {}
        return op(name, payload, opts);
      };
      window.__dlqaShopifyHooked = true;
    }
  } catch (e) {}

  // --- 5. Bespoke tracking module (builds + publishes each event) ---
  // Method names below are common on Shopify themes; extend the list for other sites/vendors.
  try {
    if (window.tracking && !window.__dlqaTrackingHooked) {
      ["addToCart", "cartViewed", "cartItemRemoved", "selectItem", "viewItem", "collectionViewed"].forEach(function (m) {
        if (typeof window.tracking[m] === "function") {
          var orig = window.tracking[m].bind(window.tracking);
          window.tracking[m] = function () {
            var r = orig.apply(null, arguments);
            var a;
            try { a = JSON.parse(JSON.stringify([].slice.call(arguments))); } catch (e) { a = "(unserialisable args)"; }
            window.__dlqa.push({ t: Date.now(), source: "tracking." + m, name: m, args: a });
            return r;
          };
        }
      });
      window.__dlqaTrackingHooked = true;
    }
  } catch (e) {}

  // --- Carry captured events across a navigation (for click-then-navigate events) ---
  if (!window.__dlqaCarryHooked) {
    window.addEventListener("pagehide", function () {
      try { sessionStorage.setItem("__dlqa_carry", JSON.stringify({ from: location.href, events: window.__dlqa })); } catch (e) {}
    });
    window.__dlqaCarryHooked = true;
  }

  return { hooked: window.__dlqaHooked, shopify: !!window.__dlqaShopifyHooked, tracking: !!window.__dlqaTrackingHooked, captured: window.__dlqa.length };
})();
