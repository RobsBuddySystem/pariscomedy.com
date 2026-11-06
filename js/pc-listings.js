/* pc-listings.js - the ONE place pariscomedy.com fetches its show listings.
 *
 * 2026-11-04 (Robert): COMEDY ATLAS is the single source of truth for shows.
 * pariscomedy.com keeps its brand and hand-made pages; its listings become an
 * English/Paris view of Atlas, published at
 *   https://comedyatlas.app/data/comedy-atlas/pariscomedy_listings.json
 * in the exact shape of GET api.pariscomedy.com/api/listings.
 *
 * Which feed is used is decided by /api-config.json, never by a page:
 *   "listings_source": "backend" (default) | "atlas"
 *   "listings_url":    the Atlas file above
 * With "atlas", a failed or empty-shaped Atlas response falls back to the
 * backend, so flipping the flag is safe and flipping it back is the rollback.
 * Rows are fetched at runtime on every load (rule R10: never a static array).
 *
 *   PCListings.load()                 -> Promise<listing[]>
 *   PCListings.load({featured: true}) -> only paid/editorial featured rows
 */
(function (root) {
  'use strict';
  var DEFAULT_API = 'https://api.pariscomedy.com';
  var _cfg = null;

  function config() {
    if (!_cfg) {
      _cfg = fetch('/api-config.json', { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : {}; })
        .catch(function () { return {}; });
    }
    return _cfg;
  }

  function fetchJson(url, ms) {
    var ctl = ('AbortController' in root) ? new AbortController() : null;
    var t = ctl ? setTimeout(function () { ctl.abort(); }, ms) : null;
    return fetch(url, { cache: 'no-store', signal: ctl ? ctl.signal : undefined })
      .then(function (r) {
        if (t) clearTimeout(t);
        if (!r.ok) throw new Error(url + ' -> HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        var rows = Array.isArray(data) ? data : (data && data.listings);
        if (!Array.isArray(rows)) throw new Error(url + ' -> not a listings array');
        return rows;
      });
  }

  function fromBackend(api, featured) {
    return fetchJson(api + '/api/listings' + (featured ? '?featured=1' : ''), 8000);
  }

  // Partner tagging (audit 2026-11-04): pariscomedy.com linked BilletReduc
  // straight to billetreduc.com, bypassing the Awin wrap, so those clicks
  // earned nothing. Apply COMEDY ATLAS's live partner rules -- the same
  // file and the same logic as comedyatlas.app/comedy-atlas/go.html
  // (PARTNER_PARAMS appended, PARTNER_REDIRECTS wrapping, #fragment dropped
  // before an Awin wrap) -- so there is one source of truth for partner
  // codes. If the file cannot be read, links are left exactly as they are.
  var PARTNER_CONFIG_URL = 'https://comedyatlas.app/comedy-atlas/partner-config.json';
  var _partners = null;

  function partnerConfig() {
    if (!_partners) {
      _partners = fetch(PARTNER_CONFIG_URL, { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .catch(function () { return null; });
    }
    return _partners;
  }

  function tagUrl(raw, cfg) {
    if (!raw || !cfg) return raw;
    var u;
    try { u = new URL(raw); } catch (e) { return raw; }
    if (u.protocol !== 'https:' && u.protocol !== 'http:') return raw;
    var host = u.hostname.toLowerCase().replace(/^www\./, '');
    var params = (cfg.PARTNER_PARAMS || {})[host] || {};
    Object.keys(params).forEach(function (k) {
      if (!u.searchParams.has(k)) u.searchParams.set(k, params[k]);
    });
    var template = (cfg.PARTNER_REDIRECTS || {})[host];
    if (template && template.indexOf('{url}') !== -1) {
      var networkHost = '';
      try { networkHost = new URL(template.split('{url}')[0]).hostname.toLowerCase().replace(/^www\./, ''); } catch (e) { return u.toString(); }
      if (host !== networkHost) {
        u.hash = '';
        return template.replace('{url}', encodeURIComponent(u.toString()));
      }
    }
    return u.toString();
  }

  function tagRows(rows, cfg) {
    if (!cfg) return rows;
    return rows.map(function (r) {
      if (!r) return r;
      var o = Object.assign({}, r);
      o.booking_url = tagUrl(r.booking_url, cfg);
      o.show_url = tagUrl(r.show_url, cfg);
      if (Array.isArray(r.dates)) {
        o.dates = r.dates.map(function (d) {
          return (d && d.url) ? Object.assign({}, d, { url: tagUrl(d.url, cfg) }) : d;
        });
      }
      return o;
    });
  }

  function loadRaw(opts) {
    var featured = !!(opts && opts.featured);
    return config().then(function (c) {
      var api = (c && c.api) || DEFAULT_API;
      if (!(c && c.listings_source === 'atlas' && c.listings_url)) {
        return fromBackend(api, featured);
      }
      return fetchJson(c.listings_url, 8000)
        .then(function (rows) {
          return featured ? rows.filter(function (r) { return r && r.featured; }) : rows;
        })
        .catch(function (e) {
          console.warn('[pc] Atlas listings failed, using backend', e);
          return fromBackend(api, featured);
        });
    });
  }

  function load(opts) {
    return Promise.all([loadRaw(opts), partnerConfig()]).then(function (res) {
      return tagRows(res[0], res[1]);
    });
  }

  root.PCListings = { load: load, config: config, tagUrl: tagUrl };
})(window);
