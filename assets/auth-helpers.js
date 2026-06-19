/* assets/auth-helpers.js
 * ParisComedy frontend auth helpers — vanilla JS, no deps.
 * Exposes window.PCAuth with:
 *   clearAllAuth(), signOut(), authFetch(url, opts), stripTokenFromURL()
 *
 * Doctrine: tokens MUST NEVER live in URL after page load.
 *           Stale tokens MUST be cleared on 401/403.
 *           Sign Out MUST wipe all known auth surfaces.
 *
 * P3.AUTH.2 — closes FIND-1, FIND-2, FIND-3 (frontend portion), FIND-5, FIND-6, FIND-8, FIND-9.
 */
(function (w) {
  'use strict';

  // ---- Known auth keys (extend if a new flow adds a key) -----------------
  var KNOWN_KEYS = [
    'token',
    'pc_token',
    'pc_session_token',
    'pc_auth_email',
    'pc_owner_token',
    'pc_admin_secret',
    'booker_token',
    'booker_email',
    'comic_token',
    'admin_token',
    'dev_token',
    'magic_link_token',
    'pending_claim_slug'
  ];

  // Matches any extra namespaced auth key (e.g. pc_<role>/auth)
  var KEY_PATTERN = /^pc_[^/]+\/auth/;

  // ---- Storage helpers ---------------------------------------------------
  function _wipeStore(store) {
    if (!store) return;
    try {
      var toRemove = [];
      for (var i = 0; i < store.length; i++) {
        var k = store.key(i);
        if (!k) continue;
        if (KNOWN_KEYS.indexOf(k) !== -1 || KEY_PATTERN.test(k)) {
          toRemove.push(k);
        }
      }
      toRemove.forEach(function (k) {
        try { store.removeItem(k); } catch (_) {}
      });
    } catch (_) { /* storage may be blocked */ }
  }

  function _wipeCookies() {
    try {
      var parts = (document.cookie || '').split(';');
      for (var i = 0; i < parts.length; i++) {
        var nv = parts[i].split('=');
        var name = (nv[0] || '').trim();
        if (!name) continue;
        var lower = name.toLowerCase();
        if (name.indexOf('pc_') === 0 || /token|auth/i.test(lower)) {
          // Expire on root path AND current path; both with and without domain
          var bases = [
            '; Path=/; Max-Age=0; SameSite=Lax',
            '; Path=' + (location.pathname || '/') + '; Max-Age=0; SameSite=Lax'
          ];
          bases.forEach(function (b) {
            try { document.cookie = name + '=' + b; } catch (_) {}
          });
        }
      }
    } catch (_) {}
  }

  function clearAllAuth() {
    _wipeStore(w.localStorage);
    _wipeStore(w.sessionStorage);
    _wipeCookies();
  }

  function signOut() {
    clearAllAuth();
    try { w.location.assign('/login.html'); }
    catch (_) { w.location.href = '/login.html'; }
  }

  // ---- authFetch ---------------------------------------------------------
  function _readBearerToken() {
    try {
      return (
        w.localStorage.getItem('pc_session_token') ||  // performer/portal magic-link session
        w.localStorage.getItem('pc_token') ||
        w.localStorage.getItem('token') ||
        w.localStorage.getItem('booker_token') ||
        null
      );
    } catch (_) { return null; }
  }

  function authFetch(url, opts) {
    opts = opts || {};
    var headers = new Headers(opts.headers || {});
    var tok = _readBearerToken();
    if (tok && !headers.has('Authorization')) {
      headers.set('Authorization', 'Bearer ' + tok);
    }
    var nextOpts = Object.assign({}, opts, { headers: headers });
    return w.fetch(url, nextOpts).then(function (resp) {
      if (resp && (resp.status === 401 || resp.status === 403)) {
        try { clearAllAuth(); } catch (_) {}
        try {
          w.location.assign('/login.html?reason=session_expired');
        } catch (_) {
          w.location.href = '/login.html?reason=session_expired';
        }
      }
      return resp;
    });
  }

  // ---- stripTokenFromURL -------------------------------------------------
  // Tokens we will pull out of the URL and persist into localStorage by name.
  // Matches the audit's persistent-token-in-URL findings.
  var URL_TOKEN_PARAMS = [
    { param: 'token',        store: 'pc_token' },
    { param: 't',            store: 'pc_token' },
    { param: 'magic',        store: 'magic_link_token' },
    { param: 'magic_token',  store: 'magic_link_token' },
    { param: 'claim_token',  store: 'pc_token' },
    { param: 'dev_token',    store: 'dev_token' },
    { param: 'owner_token',  store: 'pc_owner_token' }
  ];

  function stripTokenFromURL() {
    try {
      if (!w.location || !w.location.search) return;
      var url = new URL(w.location.href);
      var sp  = url.searchParams;
      var touched = false;
      URL_TOKEN_PARAMS.forEach(function (entry) {
        if (sp.has(entry.param)) {
          var v = sp.get(entry.param);
          if (v) {
            try { w.localStorage.setItem(entry.store, v); } catch (_) {}
          }
          sp.delete(entry.param);
          touched = true;
        }
      });
      if (touched) {
        var clean = url.pathname + (sp.toString() ? ('?' + sp.toString()) : '') + url.hash;
        try { w.history.replaceState({}, '', clean); } catch (_) {}
      }
    } catch (_) { /* URL constructor missing on ancient browsers — ignore */ }
  }

  // ---- Auto-run stripTokenFromURL on load --------------------------------
  if (w.document && w.document.readyState !== 'loading') {
    try { stripTokenFromURL(); } catch (_) {}
  } else if (w.document && w.document.addEventListener) {
    w.document.addEventListener('DOMContentLoaded', function () {
      try { stripTokenFromURL(); } catch (_) {}
    });
  }

  // ---- Export ------------------------------------------------------------
  w.PCAuth = {
    clearAllAuth: clearAllAuth,
    signOut: signOut,
    authFetch: authFetch,
    stripTokenFromURL: stripTokenFromURL,
    KNOWN_KEYS: KNOWN_KEYS.slice()
  };
})(window);
