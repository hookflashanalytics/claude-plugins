/* qa-network-requests: force the pre-consent state.
 *
 * Clears the site's own cookies and web storage so the CMP banner comes back, then
 * you RELOAD and observe what fires before consent. Run this BEFORE the capture hook
 * and BEFORE building any cart state.
 *
 * READ THIS FIRST, it is destructive to the site session:
 *   - It logs you out of the site. On a password-protected staging or preview site,
 *     you will have to sign in again after the reload.
 *   - It empties the cart. Always run the consent check before walking the funnel.
 *   - Shopify (and others) consume theme/preview params into a session cookie and
 *     strip them from the URL, so clearing cookies can drop you out of the previewed
 *     theme. Re-apply the original preview link after the reload and confirm the
 *     right theme/pixel is active before continuing.
 * Ask the user before running it if any of those would cost them something.
 *
 * Limits, state them honestly rather than assuming success:
 *   - HttpOnly cookies are invisible to JS and WILL survive. Most CMP consent cookies
 *     are not HttpOnly (the CMP's own JS has to read them), so this usually works.
 *   - A cookie scoped to a path you are not currently on is not in document.cookie at
 *     all, so its name cannot be read and it cannot be expired. Consent cookies are
 *     effectively always path=/ (they have to apply site-wide), so this rarely bites.
 *   - Server-side or account-level consent, and geo rules that show no banner at all,
 *     will not be reset by this. If no banner returns after the reload, say so.
 *
 * Returns cookie NAMES only (no values), so the output filter cannot blank it.
 */
(function () {
  var namesOf = function () {
    return document.cookie.split(";")
      .map(function (c) { return c.split("=")[0].trim(); })
      .filter(Boolean);
  };

  var before = namesOf();

  /* A cookie is only deleted by matching its domain and path, and we cannot read
     either from document.cookie. So expire each name across every plausible
     (domain, path) pair: the host and each parent domain, "/" and each ancestor
     of the current path. */
  var host = location.hostname;
  var domains = [null, host, "." + host];
  var hp = host.split(".");
  for (var i = 1; i < hp.length - 1; i++) {
    domains.push("." + hp.slice(i).join("."));
  }

  var paths = ["/"];
  var segs = location.pathname.split("/").filter(Boolean);
  for (var j = 0; j < segs.length; j++) {
    paths.push("/" + segs.slice(0, j + 1).join("/"));
  }
  if (paths.indexOf(location.pathname) < 0) { paths.push(location.pathname); }

  var EXPIRED = "; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  before.forEach(function (n) {
    domains.forEach(function (d) {
      paths.forEach(function (p) {
        try {
          document.cookie = n + "=" + EXPIRED + "; path=" + p + (d ? "; domain=" + d : "");
        } catch (e) {}
      });
    });
  });

  var ls = 0, ss = 0, idb = [];
  try { ls = localStorage.length; localStorage.clear(); } catch (e) {}
  try { ss = sessionStorage.length; sessionStorage.clear(); } catch (e) {}
  /* Some CMPs persist consent in IndexedDB. Best effort, async, so it may land
     just after this returns; the reload is what matters. */
  try {
    if (indexedDB && indexedDB.databases) {
      indexedDB.databases().then(function (dbs) {
        dbs.forEach(function (d) { try { indexedDB.deleteDatabase(d.name); } catch (e) {} });
      }).catch(function () {});
      idb = ["attempted"];
    }
  } catch (e) {}

  var survived = namesOf();
  return {
    cookiesBefore: before.length,
    cookiesAfter: survived.length,
    /* Anything here is almost certainly HttpOnly. If a consent cookie is among
       them, the reset did not fully work: say so instead of claiming a clean slate. */
    survived: survived,
    localStorageKeysCleared: ls,
    sessionStorageKeysCleared: ss,
    indexedDB: idb,
    next: "reload the page, then install net_hook.js and read the pre-consent hits"
  };
})();
