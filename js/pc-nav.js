/* pc-nav.js - marks the current page in the shared nav and closes the "More" menu on outside tap / Esc. No tracking. */
(function () {
  'use strict';
  var nav = document.querySelector('nav.pc-nav'); if (!nav) return;
  var here = location.pathname.replace(/\/index\.html$/, '/');
  [].forEach.call(nav.querySelectorAll('a[href^="/"]'), function (a) {
    var p = a.getAttribute('href').split('?')[0];
    if (p === here || (p === '/shows.html' && /^\/show(s)?\//.test(here))) a.setAttribute('aria-current', 'page');
  });
  var more = nav.querySelector('details.nav-more');
  if (more) {
    if (more.querySelector('[aria-current]')) more.querySelector('summary').style.color = '#f0f0f0';
    document.addEventListener('click', function (e) { if (!more.contains(e.target)) more.removeAttribute('open'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') more.removeAttribute('open'); });
  }
})();
