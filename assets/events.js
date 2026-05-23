/**
 * Paris Comedy — unified client-side event tracker
 * Privacy: cookieless, sessionStorage session_id, no fingerprinting
 * Consent modes: 'essential' (default) | 'all'
 */
(function () {
  'use strict';

  const API = '/api/events';
  const CONSENT_KEY = 'pc_consent';
  const SESSION_KEY  = 'pc_session';

  // ── session id ────────────────────────────────────────────────────────────
  function sessionId() {
    let sid = sessionStorage.getItem(SESSION_KEY);
    if (!sid) {
      sid = Math.random().toString(36).slice(2) + Date.now().toString(36);
      sessionStorage.setItem(SESSION_KEY, sid);
    }
    return sid;
  }

  // ── consent ───────────────────────────────────────────────────────────────
  function getConsent() {
    return localStorage.getItem(CONSENT_KEY) || 'essential';
  }
  function setConsent(val) {
    localStorage.setItem(CONSENT_KEY, val);
    document.dispatchEvent(new CustomEvent('pc:consent', { detail: val }));
  }

  // ── core send ─────────────────────────────────────────────────────────────
  function send(eventType, extra) {
    const payload = Object.assign({
      event_type: eventType,
      session_id: sessionId(),
      path:       location.pathname,
      referrer:   document.referrer || '',
      source:     new URLSearchParams(location.search).get('utm_source') || '',
      consent:    getConsent(),
    }, extra || {});
    try {
      navigator.sendBeacon
        ? navigator.sendBeacon(API, JSON.stringify(payload))
        : fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), keepalive: true });
    } catch (_) {}
  }

  // ── public API ────────────────────────────────────────────────────────────
  window.pcTrack = function (eventType, metadata) {
    send(eventType, { metadata: metadata || {} });
  };

  // ── page view ─────────────────────────────────────────────────────────────
  send('page_view', {});

  // ── outbound ticket clicks ────────────────────────────────────────────────
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';

    // Ticket / outbound
    if (/eventbrite|dice\.fm|shotgun|ticketmaster|festicket/.test(href)) {
      send('ticket_click', { target_type: 'ticket_url', target_id: href.slice(0, 200),
        metadata: { show_id: a.dataset.showId || '', url: href.slice(0, 200) } });
    }
    // Affiliate redirect
    if (href.startsWith('/r.html')) {
      send('affiliate_click', { target_type: 'affiliate', target_id: href.slice(0, 200),
        metadata: { href: href.slice(0, 200) } });
    }
    // Claim show
    if (a.href && (a.href.includes('claim') || a.dataset.trackEvent === 'claim_show_click')) {
      send('claim_show_click', { metadata: { href: href.slice(0, 200) } });
    }
    // Booker CTA
    if (a.href && (a.href.includes('/booker') || a.dataset.trackEvent === 'booker_cta_click')) {
      send('booker_cta_click', { metadata: { href: href.slice(0, 200) } });
    }
    // Pricing CTA
    if (a.href && (a.href.includes('/pricing') || a.dataset.trackEvent === 'pricing_cta_click')) {
      send('pricing_cta_click', { metadata: { href: href.slice(0, 200) } });
    }
  }, true);

  // ── comic profile open ────────────────────────────────────────────────────
  document.addEventListener('pc:comic_open', function (e) {
    send('comic_profile_open', { target_type: 'comic', target_id: (e.detail && e.detail.slug) || '',
      metadata: e.detail || {} });
  });

  // ── form tracking ─────────────────────────────────────────────────────────
  document.addEventListener('pc:form_attempt',  function (e) { send('form_submit_attempt',  { metadata: e.detail || {} }); });
  document.addEventListener('pc:form_success',  function (e) { send('form_submit_success',  { metadata: e.detail || {} }); });
  document.addEventListener('pc:form_error',    function (e) { send('form_submit_error',    { metadata: e.detail || {} }); });
  document.addEventListener('pc:lineup_export', function (e) { send('lineup_export',        { metadata: e.detail || {} }); });
  document.addEventListener('pc:notify_booked', function (e) { send('notify_booked_comics', { metadata: e.detail || {} }); });
  document.addEventListener('pc:search',        function (e) { send('search_filter',        { metadata: e.detail || {} }); });

  // ── consent banner ────────────────────────────────────────────────────────
  function mountBanner() {
    if (localStorage.getItem(CONSENT_KEY)) return; // already chosen
    var banner = document.createElement('div');
    banner.id = 'pc-consent-banner';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Cookie consent');
    banner.innerHTML = [
      '<style>',
      '#pc-consent-banner{position:fixed;bottom:0;left:0;right:0;background:#111;color:#ccc;',
      'font-size:13px;padding:10px 16px;display:flex;align-items:center;gap:12px;',
      'z-index:9999;border-top:1px solid #333;flex-wrap:wrap;}',
      '#pc-consent-banner a{color:#9d5ff5;text-decoration:underline;}',
      '#pc-consent-banner button{padding:5px 12px;border:none;border-radius:4px;cursor:pointer;font-size:13px;}',
      '#pc-cb-essential{background:#333;color:#fff;}',
      '#pc-cb-all{background:#7c3aed;color:#fff;}',
      '</style>',
      '<span>We collect anonymous usage data to improve the site. No cookies, no personal data.</span>',
      '<button id="pc-cb-essential">Essential only</button>',
      '<button id="pc-cb-all">Accept all</button>',
    ].join('');
    document.body.appendChild(banner);
    document.getElementById('pc-cb-essential').onclick = function () {
      setConsent('essential'); banner.remove();
    };
    document.getElementById('pc-cb-all').onclick = function () {
      setConsent('all'); banner.remove();
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountBanner);
  } else {
    mountBanner();
  }

  // ── expose consent helpers ────────────────────────────────────────────────
  window.pcConsent = { get: getConsent, set: setConsent };

})();
