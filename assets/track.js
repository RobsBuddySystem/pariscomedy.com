// pariscomedy.com lightweight visitor tracking.
// Sends one page-view event per page load to /api/track, plus a page-leave
// ping (time on page + max scroll depth) via sendBeacon. No third-party
// service, no cookies — just a sessionStorage random session_id so we can
// roughly count unique visits without persistent fingerprinting.
//
// GA4 (2026-08-01): also loads Google's gtag.js and fires the standard
// 'config' call for Robert's existing GA4 property (G-1Q74JY864H). This is
// the SAME measurement ID and the SAME minimal call shape already live on
// comedyatlas.app via atlas-track.js — that file's header comment names
// THIS file as its origin, so this is the one pattern, not a second one.
// No custom event parameters are ever passed: only gtag's own automatic
// page_location/page_referrer. Nothing this file constructs (session id,
// path, referrer, screen size) is sent to GA4 — that data stays in the
// first-party /api/track beacon below. No PII: no email, no name, no
// booker/comic identifier is ever read or sent by this file.
(function () {
  if (window.__pcTracked) return;
  window.__pcTracked = true;

  try {
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', 'G-1Q74JY864H');

    const gaTag = document.createElement('script');
    gaTag.async = true;
    gaTag.src = 'https://www.googletagmanager.com/gtag/js?id=G-1Q74JY864H';
    document.head.appendChild(gaTag);
  } catch (_) {
    // Google Analytics is optional; keep the first-party tracker below reliable.
  }

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
