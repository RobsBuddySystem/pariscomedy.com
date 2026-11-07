/* ParisComedy booker shows embed. Dependency-free; all text via textContent.
   <div data-pariscomedy-shows="your-handle"></div>
   <script src="https://pariscomedy.com/js/pc-embed.js" async></script>
   Optional: data-api="https://api.pariscomedy.com" on the script tag. */
(function () {
  'use strict';
  var SCRIPT = document.currentScript || (function () {
    var s = document.getElementsByTagName('script'); return s[s.length - 1];
  })();
  var API = (SCRIPT && SCRIPT.getAttribute('data-api')) || 'https://api.pariscomedy.com';
  var SAFE = /^https?:\/\//i;

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function link(href, text, cls) {
    var a = el('a', cls, text);
    if (SAFE.test(href || '')) { a.href = href; a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    return a;
  }
  function style() {
    if (document.getElementById('pcs-style')) return;
    var s = el('style'); s.id = 'pcs-style';
    s.textContent = '.pcs{font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;color:inherit;max-width:100%}' +
      '.pcs-show{border:1px solid rgba(128,128,128,.35);border-radius:10px;padding:12px 14px;margin:0 0 10px}' +
      '.pcs-when{font-size:13px;opacity:.75}.pcs-title{font-weight:700;font-size:17px;margin:2px 0}' +
      '.pcs-venue{font-size:14px}.pcs-lineup{margin:6px 0 0;font-size:14px}' +
      '.pcs a{color:inherit;text-decoration:underline}.pcs-btn{display:inline-block;margin-top:8px;padding:6px 12px;border:1px solid currentColor;border-radius:6px;text-decoration:none!important;font-size:14px}' +
      '.pcs-credit{font-size:12px;opacity:.65;margin-top:6px}.pcs-empty{opacity:.7}';
    document.head.appendChild(s);
  }
  function fmt(s) {
    try {
      var d = new Date(s.start || (s.date + 'T12:00:00'));
      var day = d.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Europe/Paris' });
      if (!s.start) return day;
      return day + ' · ' + d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Paris' });
    } catch (e) { return s.date || ''; }
  }
  function render(root, data) {
    root.textContent = '';
    var box = el('div', 'pcs');
    var shows = (data && data.shows) || [];
    if (!shows.length) box.appendChild(el('div', 'pcs-empty', 'No upcoming shows right now.'));
    shows.forEach(function (s) {
      var c = el('div', 'pcs-show');
      c.appendChild(el('div', 'pcs-when', fmt(s)));
      c.appendChild(el('div', 'pcs-title', s.title || ''));
      var v = s.venue || {};
      if (v.name) c.appendChild(el('div', 'pcs-venue', v.name + (v.address ? ' — ' + v.address : '')));
      if (s.lineup && s.lineup.length) {
        var l = el('div', 'pcs-lineup', 'With: ');
        s.lineup.forEach(function (a, i) {
          if (i) l.appendChild(document.createTextNode(', '));
          l.appendChild(a.page_url ? link(a.page_url, a.name) : document.createTextNode(a.name));
        });
        c.appendChild(l);
      }
      var t = s.ticket_url || s.show_url;
      if (t && SAFE.test(t)) c.appendChild(link(t, 'Tickets', 'pcs-btn'));
      box.appendChild(c);
    });
    var cr = el('div', 'pcs-credit');
    cr.appendChild(link('https://pariscomedy.com', 'Listings by ParisComedy'));
    box.appendChild(cr);
    root.appendChild(box);
  }
  function init() {
    style();
    var nodes = document.querySelectorAll('[data-pariscomedy-shows]');
    Array.prototype.forEach.call(nodes, function (root) {
      var slug = (root.getAttribute('data-pariscomedy-shows') || '').toLowerCase();
      if (!/^[a-z0-9-]{3,40}$/.test(slug)) return;
      root.textContent = 'Loading shows…';
      fetch(API + '/api/public/booker/' + slug + '/shows.json')
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (d) { render(root, d); })
        .catch(function () { root.textContent = ''; });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
