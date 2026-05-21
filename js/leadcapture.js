/* Paris Comedy — revenue-safe lead capture.
 * Every public form routes through LeadCapture.submit().
 *  1. tries the backend API
 *  2. on failure, stores the lead in localStorage (pending_leads)
 *  3. returns a prefilled mailto so the user can send by email in one click
 *  4. flushes pending leads automatically on every page load
 * Never reports success unless the API accepted it OR the user is given the
 * mailto fallback — no silent/fake success.
 */
window.LeadCapture = (function () {
  var apiBase = null;
  var PAY_EMAIL = 'payments@pariscomedy.com';

  async function getApi() {
    if (apiBase !== null) return apiBase;
    try {
      var c = await fetch('/api-config.json', {cache: 'no-store'}).then(function (r) { return r.json(); });
      apiBase = c.api || '';
    } catch (e) { apiBase = ''; }
    return apiBase;
  }

  function pending() {
    try { return JSON.parse(localStorage.getItem('pending_leads') || '[]'); }
    catch (e) { return []; }
  }
  function savePending(arr) {
    try { localStorage.setItem('pending_leads', JSON.stringify(arr)); } catch (e) {}
  }

  async function postLead(route, payload) {
    var api = await getApi();
    if (!api) throw new Error('no-api');
    var r = await fetch(api + route, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    if (!r.ok) throw new Error('http-' + r.status);
    return r.json();
  }

  function buildMailto(subject, body) {
    return 'mailto:' + PAY_EMAIL + '?subject=' + encodeURIComponent(subject) +
           '&body=' + encodeURIComponent(body);
  }

  /* opts = {route, formType, payload, mailtoSubject, mailtoBody} */
  async function submit(opts) {
    var payload = Object.assign({
      form_type: opts.formType || 'lead',
      source_page: location.pathname.replace(/^\//, '') || 'index.html',
      referrer: document.referrer || '',
      utm: location.search || ''
    }, opts.payload || {});

    var mailto = buildMailto(opts.mailtoSubject || 'Paris Comedy enquiry',
                             opts.mailtoBody || JSON.stringify(payload, null, 2));
    try {
      var data = await postLead(opts.route, payload);
      return {status: 'sent', mailto: mailto, data: data};
    } catch (e) {
      var p = pending();
      p.push({route: opts.route, payload: payload, ts: Date.now()});
      savePending(p);
      return {status: 'pending', mailto: mailto};
    }
  }

  /* Retry every stored lead. Returns {flushed, remaining}. */
  async function flush() {
    var p = pending();
    if (!p.length) return {flushed: 0, remaining: 0};
    var remain = [];
    for (var i = 0; i < p.length; i++) {
      try { await postLead(p[i].route, p[i].payload); }
      catch (e) { remain.push(p[i]); }
    }
    savePending(remain);
    return {flushed: p.length - remain.length, remaining: remain.length};
  }

  /* Render a result into a container element. */
  function renderResult(el, res, planLabel) {
    el.style.display = 'block';
    if (res.status === 'sent') {
      el.innerHTML = '<strong>' + (planLabel || 'Request received') + '</strong><br>' +
        'Saved — we&rsquo;ll be in touch by email shortly.';
    } else {
      el.innerHTML = '<strong>' + (planLabel || 'Almost there') + '</strong><br>' +
        'We saved your request locally because the server is temporarily unavailable. ' +
        'Please also send it to us with one click:<br>' +
        '<a href="' + res.mailto + '" style="display:inline-block;margin-top:8px;padding:9px 16px;' +
        'border-radius:8px;background:#f5c518;color:#000;font-weight:700">Send by email →</a> ' +
        '<button onclick="LeadCapture.retry(this)" style="margin-top:8px;padding:9px 14px;' +
        'border-radius:8px;border:1px solid #444;background:transparent;color:#aaa;cursor:pointer">' +
        'Retry now</button>';
    }
  }

  async function retry(btn) {
    btn.textContent = 'Retrying…';
    var r = await flush();
    btn.textContent = r.remaining === 0 ? 'Sent ✓' : 'Still offline — use email';
  }

  // Auto-flush any pending leads on load.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', flush);
  } else { flush(); }

  return {submit: submit, flush: flush, retry: retry, pending: pending,
          buildMailto: buildMailto, renderResult: renderResult, PAY_EMAIL: PAY_EMAIL};
})();
