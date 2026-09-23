// pariscomedy.com lightweight visitor tracking.
// Sends one page-view event per page load to /api/track, plus a page-leave
// ping (time on page + max scroll depth) via sendBeacon. No third-party
// service, no cookies — just a sessionStorage random session_id so we can
// roughly count unique visits without persistent fingerprinting.
//
// CONSENT GATE (2026-08-02): this file previously loaded Google's gtag.js
// and fired 'config' for GA4 property G-1Q74JY864H unconditionally, the
// instant this script ran, on every one of this site's pages. That is the
// same defect (same measurement ID, same unconditional call shape) fixed
// on comedyatlas.app the same day (atlas-track.js, P0-6) — Robert's
// decision there (Option B, carried over here) is: keep GA, gate it,
// don't remove it. This file is the ONE script every public page includes
// (<script src="/assets/track.js">), so gating GA here, once, gates it
// everywhere this file is included.
//
// Rule: NO request to googletagmanager.com/google-analytics.com of any
// kind fires until the visitor has affirmatively clicked "Accept" on the
// banner below (or already has a stored 'granted' choice from a previous
// visit). "Reject" is exactly as easy as "Accept" — same size, same click
// count, no pre-ticked box, no follow-up nag. The choice persists in
// localStorage (scoped to THIS origin only — it does not carry over
// to/from comedyatlas.app, a separate origin with separate storage) and is
// changeable at any time via window.PCConsent or the "reopen the
// analytics choice" control on privacy.html.
//
// The first-party beacon below (POST /api/track, plus the leave/scroll
// beacon) is UNCHANGED and NOT gated: it carries no name/email/account id,
// sets no cross-site cookie, and privacy.html describes it as the
// strictly-necessary traffic count the site needs to operate — so it
// keeps firing on every visit exactly as it always has.
(function () {
  if (window.__pcTracked) return;
  window.__pcTracked = true;

  var GA_MEASUREMENT_ID = 'G-1Q74JY864H';
  var CONSENT_KEY = 'pc_analytics_consent'; // localStorage: 'granted' | 'denied'

  function readConsent() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (_) { return null; }
  }
  function writeConsent(value) {
    try { localStorage.setItem(CONSENT_KEY, value); } catch (_) { /* storage unavailable */ }
  }

  // ---- Google Analytics: consent-gated, never loaded any other way ------
  var gaLoaded = false;
  function loadGA() {
    if (gaLoaded) return;
    gaLoaded = true;
    try {
      window.dataLayer = window.dataLayer || [];
      window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
      // Cross-domain linking: pariscomedy.com and comedyatlas.app share
      // this ONE GA4 property. Without this, a visitor moving between the
      // two domains reads as a self-referral — two disconnected sessions
      // instead of one — which pollutes both properties' traffic-source/
      // attribution reports. atlas-track.js carries the matching config on
      // the other side (its own header comment flagged this file as the
      // pending half of that pair; this closes it).
      window.gtag('set', 'linker', {
        domains: ['pariscomedy.com', 'comedyatlas.app'],
        accept_incoming: true,
      });
      // Per-hostname reporting (2026-08-03): pariscomedy.com and comedyatlas.app
      // share ONE GA4 property/measurement ID (see the linker comment above), so
      // without an explicit signal every hit from either domain looks identical in
      // GA reports. GA4 does auto-populate a built-in "Hostname" dimension from
      // page_location, but this sends it as its own named, event-scoped parameter
      // too so it survives independently of page_location and reads the same way
      // in both DebugView and BigQuery export. It rides on every hit (config +
      // later events) because 'set' (unlike 'config') applies to the whole
      // session, not just the next call. NOTE: for this to appear as a report
      // dimension (not just raw event data), it still needs a one-time GA4 Admin
      // step — Admin > Custom definitions > Create custom dimension, scope
      // "Event", parameter name "site_hostname" — same one-time registration this
      // parameter name would need on the atlas-track.js side too. This does NOT
      // touch consent state, which stays independent per origin (see file header).
      window.gtag('set', 'site_hostname', location.hostname);
      window.gtag('js', new Date());
      window.gtag('config', GA_MEASUREMENT_ID, { anonymize_ip: true });

      var gaTag = document.createElement('script');
      gaTag.async = true;
      gaTag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_MEASUREMENT_ID);
      document.head.appendChild(gaTag);
    } catch (_) {
      // Google Analytics is optional; keep the first-party tracker below reliable.
    }
  }

  // ---- Consent banner -----------------------------------------------------
  // Fixed to the viewport bottom (position:fixed is out of normal flow, so
  // injecting it never reflows/shifts anything already on the page — no
  // Core Web Vitals CLS hit). flex-wrap + box-sizing:border-box keep it
  // inside 390px with no horizontal overflow. Both controls are real
  // <button> elements (native keyboard/tab reachable) of equal size and
  // weight — no dark pattern, no listener captures Tab or blocks
  // interaction with the rest of the page (no focus trap). English only —
  // this site does not run bilingual copy (see the standing brand rule).
  var BANNER_ID = 'pc-ga-consent-banner';

  function removeBanner() {
    var el = document.getElementById(BANNER_ID);
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function injectBannerCSS() {
    if (document.getElementById('pc-ga-consent-style')) return;
    var style = document.createElement('style');
    style.id = 'pc-ga-consent-style';
    style.textContent =
      '#' + BANNER_ID + '{position:fixed;left:0;right:0;bottom:0;z-index:2147483000;' +
      'background:#0a0a0a;color:#f0f0f0;border-top:1px solid #2a2a2a;' +
      'padding:14px 16px;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;' +
      'display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;' +
      'box-sizing:border-box;max-width:100vw}' +
      '#' + BANNER_ID + ' .pc-ga-consent-text{flex:1 1 240px;min-width:0;font-size:13.5px;color:inherit}' +
      '#' + BANNER_ID + ' .pc-ga-consent-text a{color:#f0c674;text-decoration:underline}' +
      '#' + BANNER_ID + ' .pc-ga-consent-actions{display:flex;gap:8px;flex-wrap:wrap;flex:0 0 auto}' +
      '#' + BANNER_ID + ' button{font:inherit;font-size:13.5px;font-weight:700;padding:10px 18px;' +
      'border-radius:8px;cursor:pointer;border:1px solid #f0c674;min-height:40px;box-sizing:border-box}' +
      '#' + BANNER_ID + ' .pc-ga-consent-accept{background:#f0c674;color:#0a0a0a}' +
      '#' + BANNER_ID + ' .pc-ga-consent-reject{background:transparent;color:inherit}' +
      '@media (prefers-color-scheme: light){' +
      '#' + BANNER_ID + '{background:#ffffff;color:#171512;border-top-color:#e2ddd2}' +
      '#' + BANNER_ID + ' .pc-ga-consent-text a{color:#7a5c10}' +
      '#' + BANNER_ID + ' button{border-color:#7a5c10}}' +
      '@media(max-width:420px){#' + BANNER_ID + '{padding:12px}' +
      '#' + BANNER_ID + ' .pc-ga-consent-actions{width:100%;justify-content:stretch}' +
      '#' + BANNER_ID + ' button{flex:1 1 0}}';
    document.head.appendChild(style);
  }

  function showBanner() {
    if (document.getElementById(BANNER_ID) || !document.body) return;
    injectBannerCSS();
    var el = document.createElement('div');
    el.id = BANNER_ID;
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'Analytics consent');
    el.innerHTML =
      '<div class="pc-ga-consent-text">We use Google Analytics to understand site ' +
      'traffic. Accept or reject &mdash; either choice works the same everywhere else ' +
      'on the site, and you can change it any time. ' +
      '<a href="/privacy.html">Privacy details</a></div>' +
      '<div class="pc-ga-consent-actions">' +
      '<button type="button" class="pc-ga-consent-reject">Reject</button>' +
      '<button type="button" class="pc-ga-consent-accept">Accept</button>' +
      '</div>';
    document.body.appendChild(el);
    el.querySelector('.pc-ga-consent-accept').addEventListener('click', function () {
      writeConsent('granted');
      loadGA();
      removeBanner();
    });
    el.querySelector('.pc-ga-consent-reject').addEventListener('click', function () {
      writeConsent('denied');
      removeBanner();
    });
  }

  function initConsent() {
    var consent = readConsent();
    if (consent === 'granted') {
      loadGA();
    } else if (consent === 'denied') {
      // Decision already made — no GA, no banner.
    } else {
      showBanner();
    }
  }

  // Public, small API so the choice is changeable later (privacy.html's
  // "reopen the analytics choice" control, or any future settings surface)
  // without needing to know this file's internals.
  window.PCConsent = {
    getStatus: readConsent,
    grant: function () { writeConsent('granted'); loadGA(); removeBanner(); },
    deny: function () { writeConsent('denied'); removeBanner(); },
    showBanner: function () { showBanner(); },
  };

  if (document.body) {
    initConsent();
  } else {
    document.addEventListener('DOMContentLoaded', initConsent);
  }

  // ---- First-party beacon: always fires, not gated by the GA choice -----
  let sid = '';
  try {
    sid = sessionStorage.getItem('pc_sid') || '';
    if (!sid) {
      sid = Math.random().toString(36).slice(2) + Date.now().toString(36);
      sessionStorage.setItem('pc_sid', sid);
    }
  } catch (_) {
    // Storage unavailable; ship without session id.
  }
  const params = new URLSearchParams(location.search);
  const path = location.pathname + location.search;
  const payload = {
    path: path,
    referrer: (document.referrer || '').slice(0, 300),
    session_id: sid,
    screen: (screen && screen.width && screen.height) ? (screen.width + 'x' + screen.height) : '',
    lang: (navigator.language || '').slice(0, 20),
    utm_source: (params.get('utm_source') || '').slice(0, 100),
    utm_campaign: (params.get('utm_campaign') || '').slice(0, 100),
  };
  let apiBase = '';
  const startedAt = Date.now();
  let maxScroll = 0;
  const trackScroll = () => {
    try {
      const doc = document.documentElement;
      const scrollable = Math.max(1, doc.scrollHeight - doc.clientHeight);
      const pct = Math.round(100 * Math.min(1, (window.scrollY || 0) / scrollable));
      if (pct > maxScroll) maxScroll = pct;
    } catch (_) { /* ignore */ }
  };
  window.addEventListener('scroll', trackScroll, {passive: true});

  const sendLeave = () => {
    try {
      const durationS = Math.round((Date.now() - startedAt) / 1000);
      const leavePayload = JSON.stringify({
        session_id: sid, path: path, duration_s: durationS, scroll_pct: maxScroll,
      });
      if (navigator.sendBeacon) {
        navigator.sendBeacon(apiBase + '/api/track/leave',
          new Blob([leavePayload], {type: 'application/json'}));
      }
    } catch (_) { /* best-effort only */ }
  };
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') sendLeave();
  });
  window.addEventListener('pagehide', sendLeave);

  // Resolve API base from /api-config.json if present.
  fetch('/api-config.json', {cache: 'no-store'})
    .then(r => r.json()).catch(() => ({}))
    .then(c => {
      apiBase = (c && c.api) || '';
      fetch(apiBase + '/api/track', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
        keepalive: true,
      }).catch(() => {});
    });
})();
