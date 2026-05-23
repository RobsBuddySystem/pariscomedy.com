// pariscomedy.com lightweight visitor tracking.
// Sends one page-view event per page load to /api/track. No third-party
// service, no cookies — just a sessionStorage random session_id so we can
// roughly count unique visits without persistent fingerprinting.
(function () {
  if (window.__pcTracked) return;
  window.__pcTracked = true;
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
  const payload = {
    path: location.pathname + location.search,
    referrer: (document.referrer || '').slice(0, 300),
    session_id: sid,
  };
  // Resolve API base from /api-config.json if present.
  fetch('/api-config.json', {cache: 'no-store'})
    .then(r => r.json()).catch(() => ({}))
    .then(c => {
      const api = (c && c.api) || '';
      fetch(api + '/api/track', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
        keepalive: true,
      }).catch(() => {});
    });
})();
