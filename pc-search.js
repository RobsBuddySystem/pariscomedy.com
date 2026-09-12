/* pc-search.js — shared as-you-type site search for pariscomedy.com
 * Groups: Cities (COMEDY ATLAS, shown first when matched), Shows, Venues,
 * Comedians (local + COMEDY ATLAS).
 * Pattern lifted from comedians.html's own search + Atlas cross-search
 * (fetch /api/listings + /api/comics, fetch api.comedyatlas.app/v1/comics,
 * only ever trust an href on comedyatlas.app). No new CDN, no tracking, no cookies.
 */
(function () {
  'use strict';

  var MIN_CHARS = 2;
  var DEBOUNCE_MS = 200;
  var GROUP_CAP = 5;
  var ATLAS_CITIES_URL = 'https://comedyatlas.app/data/comedy-atlas/cities.json';

  function normName(s) {
    return String(s == null ? '' : s)
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .toLowerCase().replace(/\s+/g, ' ').trim();
  }
  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
    });
  }
  function isAtlasUrl(u) { return /^https:\/\/comedyatlas\.app\//.test(String(u || '')); }
  function slugify(name) {
    return normName(name).replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  }

  // ---- matching / ranking ---------------------------------------------------
  // Word-prefix match (used for comedians/shows/venues): the query must be a
  // prefix of the WHOLE string, or a prefix of one of its words — never just
  // an arbitrary substring. This is what keeps "Lon" from matching "Coulon"
  // or "Villalón" (both only contain "lon" mid-word).
  // Returns a rank: 0 = exact, 1 = whole-string prefix, 2 = word-prefix, -1 = no match.
  function fieldRank(fieldStr, nq) {
    if (!nq) return -1;
    var h = normName(fieldStr);
    if (!h) return -1;
    if (h === nq) return 0;
    if (h.indexOf(nq) === 0) return 1;
    var words = h.split(/[^a-z0-9]+/).filter(Boolean);
    for (var i = 0; i < words.length; i++) {
      if (words[i].indexOf(nq) === 0) return 2;
    }
    return -1;
  }
  function bestRank(fields, nq) {
    var best = -1;
    for (var i = 0; i < fields.length; i++) {
      var r = fieldRank(fields[i], nq);
      if (r !== -1 && (best === -1 || r < best)) best = r;
    }
    return best;
  }
  // Cities intentionally keep WHOLE-NAME prefix matching only (no word-prefix):
  // a city's name is short and single-purpose, so mid-word Atlas-style fuzziness
  // isn't wanted there either — "Lon" should match "London", not "West London".
  function cityRank(name, nq) {
    var h = normName(name);
    if (!nq || !h) return -1;
    if (h === nq) return 0;
    if (h.indexOf(nq) === 0) return 1;
    return -1;
  }
  function sortByRank(list) {
    // Array.prototype.sort is stable in every engine we ship to, so equal
    // ranks keep their original (API/data) order.
    return list.slice().sort(function (a, b) { return a._rank - b._rank; });
  }

  // ---- lazily-fetched, memoised data sources -------------------------------
  var _apiBase = null;
  function apiBase() {
    if (_apiBase) return _apiBase;
    _apiBase = fetch('/api-config.json', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (c) { return (c && c.api) || 'https://api.pariscomedy.com'; })
      .catch(function () { return 'https://api.pariscomedy.com'; });
    return _apiBase;
  }

  var _listings = null;
  function listings() {
    if (_listings) return _listings;
    _listings = apiBase().then(function (api) {
      return fetch(api + '/api/listings', { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : []; })
        .catch(function () { return []; });
    }).then(function (rows) { return Array.isArray(rows) ? rows : []; });
    return _listings;
  }

  var _comics = null;
  function localComics() {
    if (_comics) return _comics;
    _comics = apiBase().then(function (api) {
      return fetch(api + '/api/comics', { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : []; })
        .catch(function () { return []; });
    }).then(function (rows) { return Array.isArray(rows) ? rows : []; });
    return _comics;
  }

  // COMEDY ATLAS's static city list (42,818 bytes, CORS "*") — NOT the 2.9MB
  // search_index.json. Fetched only on the user's first real search (>= 2
  // chars typed), never on focus/page load.
  //
  // cities.json ships name/country_name/country_iso2/region_name/id/lat/lon/
  // timezone — NO slug and NO url field. The slug is derived client-side:
  // accent-strip (NFD, drop combining marks) -> lowercase -> non-alnum runs
  // -> single hyphen -> trim. This was verified OFFLINE against Atlas's own
  // search_index.json (which DOES carry a url per city): all 115/115
  // cities.json names slugify to the exact slug in that file's
  // type=="city" url, zero mismatches — so no name->url override map is
  // needed. (cities.json's 115 names are all plain ASCII; multi-word names
  // like "New York" / "Salt Lake City" / "Hong Kong" / "Saint Paul" were
  // spot-checked too — curl confirms all resulting /comedy-atlas/city/<slug>/
  // URLs return 200.)
  var _atlasCities = null;
  function atlasCities() {
    if (_atlasCities) return _atlasCities;
    _atlasCities = fetch(ATLAS_CITIES_URL)
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (rows) {
        return (Array.isArray(rows) ? rows : []).map(function (c) {
          return {
            name: c.name,
            region: c.region_name || '',
            country: c.country_name || c.country_iso2 || '',
            url: 'https://comedyatlas.app/comedy-atlas/city/' + slugify(c.name) + '/'
          };
        });
      })
      .catch(function () { return []; });
    return _atlasCities;
  }

  function atlasComicsSearch(q) {
    var controller = ('AbortController' in window) ? new AbortController() : null;
    var timeoutId = controller ? setTimeout(function () { controller.abort(); }, 5000) : null;
    return fetch('https://api.comedyatlas.app/v1/comics?q=' + encodeURIComponent(q) + '&limit=20',
      controller ? { signal: controller.signal } : {})
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (timeoutId) clearTimeout(timeoutId);
        return (data && Array.isArray(data.comics)) ? data.comics : [];
      })
      .catch(function () { if (timeoutId) clearTimeout(timeoutId); return []; });
  }

  // ---- per-group search -------------------------------------------------
  function searchShows(q) {
    var nq = normName(q);
    return listings().then(function (rows) {
      var matched = [];
      rows.forEach(function (s) {
        if (!s || !(s.booking_url || s.show_url)) return;
        var venue = s.venue_name || (s.venue && s.venue.name) || s.venue_name_raw || '';
        var r = bestRank([s.name, venue], nq);
        if (r === -1) return;
        matched.push({
          _rank: r, group: 'Shows', label: s.name || '', sub: venue,
          href: s.slug ? ('/show.html?slug=' + encodeURIComponent(s.slug)) : '/shows.html'
        });
      });
      return sortByRank(matched).slice(0, GROUP_CAP);
    });
  }

  function searchVenues(q) {
    var nq = normName(q);
    return listings().then(function (rows) {
      var byVenue = {};
      rows.forEach(function (s) {
        if (!s || !(s.booking_url || s.show_url)) return;
        var vn = s.venue_name || (s.venue && s.venue.name) || s.venue_name_raw || '';
        if (!vn) return;
        var r = fieldRank(vn, nq);
        if (r === -1) return;
        if (!byVenue[vn] || byVenue[vn]._rank > r) byVenue[vn] = { _rank: r, show: s };
      });
      var matched = Object.keys(byVenue).map(function (vn) {
        var entry = byVenue[vn];
        var s = entry.show;
        return {
          _rank: entry._rank, group: 'Venues', label: vn,
          sub: (s.venue && s.venue.neighborhood) || '',
          // No dedicated per-venue page exists on the site: send the user to
          // that venue's own show detail page, the closest real destination.
          href: s.slug ? ('/show.html?slug=' + encodeURIComponent(s.slug)) : '/venues.html'
        };
      });
      return sortByRank(matched).slice(0, GROUP_CAP);
    });
  }

  function searchComedians(q) {
    var nq = normName(q);
    return localComics().then(function (rows) {
      var localSlugs = {}, localNames = {};
      rows.forEach(function (c) { if (c && c.slug) localSlugs[c.slug] = true; if (c) localNames[normName(c.stage_name || c.name)] = true; });
      var localMatched = [];
      rows.forEach(function (c) {
        if (!c) return;
        var r = fieldRank(c.stage_name || c.name, nq);
        if (r === -1) return;
        localMatched.push({ _rank: r, group: 'Comedians', label: c.stage_name || c.name || c.slug, sub: 'Paris Comedy', href: '/c/' + encodeURIComponent(c.slug) + '.html' });
      });
      var localItems = sortByRank(localMatched).slice(0, GROUP_CAP);
      if (localItems.length >= GROUP_CAP) return localItems;
      return atlasComicsSearch(q).then(function (atlasList) {
        // The Atlas API matches substrings server-side, so re-apply the same
        // word-prefix filter client-side — otherwise "Lon" comes back with
        // Atlas comics like "Villalón" that only contain "lon" mid-word.
        var extraMatched = [];
        atlasList.forEach(function (c) {
          if (!c || !c.slug) return;
          if (localSlugs[c.slug]) return;
          var nn = normName(c.stage_name);
          if (!nn || localNames[nn]) return;
          if (!isAtlasUrl(c.atlas_url)) return;
          var r = fieldRank(c.stage_name, nq);
          if (r === -1) return;
          extraMatched.push({ _rank: r, group: 'Comedians', label: c.stage_name, sub: (c.home_city ? c.home_city + ' · ' : '') + 'COMEDY ATLAS', href: c.atlas_url, external: true });
        });
        var extra = sortByRank(extraMatched).slice(0, GROUP_CAP - localItems.length);
        return localItems.concat(extra);
      });
    });
  }

  function searchCities(q) {
    var nq = normName(q);
    return atlasCities().then(function (rows) {
      var matched = [];
      rows.forEach(function (r) {
        var rank = cityRank(r.name, nq);
        if (rank === -1) return;
        if (!isAtlasUrl(r.url)) return;
        matched.push({ _rank: rank, group: 'Cities', label: r.name, sub: [r.region, r.country].filter(Boolean).join(', '), href: r.url, external: true });
      });
      return sortByRank(matched).slice(0, GROUP_CAP);
    });
  }

  // ---- UI --------------------------------------------------------------
  var CSS = '\n'
    + '.pcs-wrap{position:relative;min-width:180px;flex:0 1 260px}\n'
    + '.pcs-input{width:100%;padding:9px 14px;border-radius:8px;border:1px solid var(--border,#1e2a3a);'
    + 'background:var(--panel,var(--card,#111827));color:var(--text,#f0f0f0);font-size:14px;outline:none;'
    + 'font-family:inherit}\n'
    + '.pcs-input:focus{border-color:#445566}\n'
    + '.pcs-panel{position:absolute;top:calc(100% + 6px);left:0;right:0;min-width:280px;max-height:70vh;overflow-y:auto;'
    + 'background:var(--panel,var(--card,#111827));border:1px solid var(--border,#1e2a3a);border-radius:10px;'
    + 'box-shadow:0 10px 32px rgba(0,0,0,.4);z-index:500;padding:6px}\n'
    + '.pcs-group-label{font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;'
    + 'color:var(--gold,#c9a84c);padding:8px 10px 4px}\n'
    + '.pcs-opt{display:block;padding:8px 10px;border-radius:6px;cursor:pointer;color:var(--text,#f0f0f0);text-decoration:none}\n'
    + '.pcs-opt-name{font-size:14px;font-weight:600}\n'
    + '.pcs-opt-sub{font-size:12px;color:var(--muted,#8899aa)}\n'
    + '.pcs-opt.pcs-active,.pcs-opt:hover{background:rgba(201,168,76,.12)}\n'
    + '.pcs-empty{padding:14px 10px;font-size:13px;color:var(--muted,#8899aa)}\n'
    + '.pcs-loading{padding:10px 10px;font-size:12px;color:var(--muted,#8899aa)}\n'
    + '@media(max-width:620px){.pcs-wrap{flex:1 1 100%;order:99;min-width:0}}\n';

  function injectCss() {
    if (document.getElementById('pcs-style')) return;
    var style = document.createElement('style');
    style.id = 'pcs-style';
    style.textContent = CSS;
    document.head.appendChild(style);
  }

  function buildMount(mount) {
    mount.classList.add('pcs-wrap');
    mount.innerHTML =
      '<label for="pcs-input" style="position:absolute;left:-9999px">Search shows, venues, comedians, cities</label>'
      + '<input type="text" id="pcs-input" class="pcs-input" placeholder="Search shows, venues, comedians, cities…" '
      + 'autocomplete="off" role="combobox" aria-expanded="false" aria-haspopup="listbox" aria-controls="pcs-listbox" aria-autocomplete="list">'
      + '<div class="pcs-panel" id="pcs-panel" hidden><ul class="pcs-listbox" id="pcs-listbox" role="listbox"></ul></div>';
  }

  function init(mount) {
    injectCss();
    buildMount(mount);
    var input = mount.querySelector('#pcs-input');
    var panel = mount.querySelector('#pcs-panel');
    var listbox = mount.querySelector('#pcs-listbox');
    var timer = null;
    var seq = 0;
    var items = []; // flat list in display order, mirrors rendered <a>s
    var activeIndex = -1;
    var warmed = false;

    // Only the small local listings/comics warm on focus. The Atlas cities
    // list is fetched lazily inside searchCities(), triggered only by the
    // user's first real (>= 2 char) search.
    function warm() {
      if (warmed) return;
      warmed = true;
      listings(); localComics();
    }

    function closePanel() {
      panel.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
      activeIndex = -1;
    }

    function renderEmpty(msg) {
      listbox.innerHTML = '<li class="pcs-empty">' + escapeHtml(msg) + '</li>';
      panel.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }

    function setActive(idx) {
      var opts = listbox.querySelectorAll('.pcs-opt');
      opts.forEach(function (el) { el.classList.remove('pcs-active'); });
      activeIndex = idx;
      if (idx >= 0 && opts[idx]) {
        opts[idx].classList.add('pcs-active');
        opts[idx].scrollIntoView({ block: 'nearest' });
        input.setAttribute('aria-activedescendant', opts[idx].id);
      } else {
        input.removeAttribute('aria-activedescendant');
      }
    }

    function navigate(item) {
      if (!item) return;
      if (item.external && !isAtlasUrl(item.href)) return; // never trust a non-Atlas external href
      window.location.href = item.href;
    }

    function render(groups) {
      items = [];
      var html = '';
      // Cities lead the list whenever there's a city match at all — e.g.
      // "Lon" + Enter must open London's Atlas page, not a Paris comedian.
      var order = (groups.Cities && groups.Cities.length)
        ? ['Cities', 'Shows', 'Venues', 'Comedians']
        : ['Shows', 'Venues', 'Comedians', 'Cities'];
      order.forEach(function (g) {
        var list = groups[g] || [];
        if (!list.length) return;
        html += '<div class="pcs-group-label">' + escapeHtml(g) + '</div>';
        list.forEach(function (it) {
          var idx = items.length;
          items.push(it);
          html += '<a href="' + escapeHtml(it.href) + '" class="pcs-opt" role="option" id="pcs-opt-' + idx + '" '
            + (it.external ? 'target="_blank" rel="noopener" ' : '')
            + 'data-idx="' + idx + '">'
            + '<div class="pcs-opt-name">' + escapeHtml(it.label) + '</div>'
            + (it.sub ? '<div class="pcs-opt-sub">' + escapeHtml(it.sub) + '</div>' : '')
            + '</a>';
        });
      });
      if (!items.length) {
        renderEmpty('No matches.');
        return;
      }
      listbox.innerHTML = html;
      panel.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      activeIndex = -1;
      // Plain anchors with real hrefs already navigate on click (and open a
      // new tab for external/target=_blank items) — no click handler needed.
      // Just keep hover in sync with keyboard highlighting.
      listbox.querySelectorAll('.pcs-opt').forEach(function (el) {
        el.addEventListener('mouseenter', function () {
          var idx = parseInt(el.getAttribute('data-idx'), 10);
          setActive(idx);
        });
      });
    }

    function runSearch(q) {
      var mySeq = ++seq;
      renderEmpty('Searching…');
      Promise.all([searchCities(q), searchShows(q), searchVenues(q), searchComedians(q)])
        .then(function (res) {
          if (mySeq !== seq) return; // superseded by a newer keystroke
          render({ Cities: res[0], Shows: res[1], Venues: res[2], Comedians: res[3] });
        })
        .catch(function () { if (mySeq === seq) renderEmpty('Search unavailable right now.'); });
    }

    input.addEventListener('focus', warm);
    input.addEventListener('input', function () {
      warm();
      clearTimeout(timer);
      var q = input.value.trim();
      if (q.length < MIN_CHARS) { closePanel(); return; }
      timer = setTimeout(function () { runSearch(q); }, DEBOUNCE_MS);
    });

    input.addEventListener('keydown', function (e) {
      if (panel.hidden && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
        var q = input.value.trim();
        if (q.length >= MIN_CHARS) runSearch(q);
        return;
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (!items.length) return;
        setActive(Math.min(activeIndex + 1, items.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (!items.length) return;
        setActive(Math.max(activeIndex - 1, 0));
      } else if (e.key === 'Enter') {
        if (activeIndex >= 0 && items[activeIndex]) {
          e.preventDefault();
          navigate(items[activeIndex]);
        } else if (items.length) {
          // Enter with nothing highlighted: go to the single best match
          // (items[0] — Cities first when a city matched, per group order above).
          e.preventDefault();
          navigate(items[0]);
        }
      } else if (e.key === 'Escape') {
        closePanel();
      }
    });

    document.addEventListener('click', function (e) {
      if (!mount.contains(e.target)) closePanel();
    });
  }

  function boot() {
    var mounts = document.querySelectorAll('[data-pc-search]');
    mounts.forEach(init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
