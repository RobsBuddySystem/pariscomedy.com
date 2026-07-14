/*
 * COMEDY ATLAS — shared client helpers (site/comedy-atlas/atlas-common.js)
 *
 * Loaded by both index.html (hub) and city.html (per-city view). No build
 * step, no external CDN — plain script tag, same-origin fetch only.
 *
 * Data contract: data/comedy-atlas/upcoming_events.json + MANIFEST.json,
 * published by scripts/publish_atlas_data.py from the public_upcoming_events
 * view (migration 0046). That view is NOT city-scoped — it already carries
 * every city with approved, English-only (or explicitly-null-language)
 * upcoming events, so both pages read the exact same file.
 */
(function (global) {
  "use strict";

  var DATA_URL = "../data/comedy-atlas/upcoming_events.json";
  var MANIFEST_URL = "../data/comedy-atlas/MANIFEST.json";

  // Known Edinburgh Fringe free-festival umbrella organizations. These are
  // ORG names that appear on Edinburgh events (source IS the org — see
  // BUILD_STATE.md "EDINBURGH" section) — there is no separate `festivals`
  // table row for them yet (public_festivals is empty today), so the
  // festivals section is derived directly from event organizer names.
  var FESTIVAL_ORGS = ["PBH's Free Fringe", "Laughing Horse Free Festival"];

  function escapeHtml(s) {
    if (s === null || s === undefined) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function fmtDayHeading(d) {
    return d.toLocaleDateString("en-GB", {
      weekday: "long", day: "numeric", month: "long", timeZone: "Europe/Paris"
    });
  }

  function fmtTime(d) {
    return d.toLocaleTimeString("en-GB", {
      hour: "2-digit", minute: "2-digit", timeZone: "Europe/Paris"
    });
  }

  // Price 0 always renders as "Free" — true both for Paris free open-mics
  // and for every Edinburgh Free Fringe / Laughing Horse show (donation
  // model, price_min = 0.00 in the data, never a real currency amount).
  function fmtPrice(ev) {
    if (ev.price_min == null && ev.price_max == null) return null;
    var cur = ev.currency ? (" " + ev.currency) : "";
    if (ev.price_min != null && ev.price_max != null && ev.price_min !== ev.price_max) {
      if (ev.price_min === 0) return "Free" + (ev.price_max ? (" – " + ev.price_max + cur) : "");
      return ev.price_min + "–" + ev.price_max + cur;
    }
    var p = ev.price_min != null ? ev.price_min : ev.price_max;
    return (Number(p) === 0 ? "Free" : (p + cur));
  }

  function statusBadge(ev) {
    if (ev.status === "cancelled") return '<span class="badge cancelled">Cancelled</span>';
    if (ev.sold_out_status === "sold_out") return '<span class="badge soldout">Sold out</span>';
    return '<span class="badge verified">Verified</span>';
  }

  // Defense in depth, mirroring publish_atlas_data.py's own French refusal:
  // never RENDER a French-labeled event even if one somehow reached the
  // JSON. Never infers language for anything the data leaves blank.
  function dropFrench(events) {
    return events.filter(function (ev) { return ev.language !== "fr"; });
  }

  function fetchEvents() {
    return fetch(DATA_URL, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).then(function (data) {
      if (!Array.isArray(data)) throw new Error("unexpected payload shape");
      return dropFrench(data);
    });
  }

  function fetchManifest() {
    return fetch(MANIFEST_URL, { cache: "no-store" })
      .then(function (r) { if (!r.ok) throw new Error("no manifest"); return r.json(); })
      .catch(function () { return null; });
  }

  function setFreshness(dotEl, textEl, manifest) {
    if (!manifest || !manifest.generated_at) {
      textEl.textContent = "Freshness unknown.";
      dotEl.classList.add("stale");
      return;
    }
    var when = new Date(manifest.generated_at);
    if (isNaN(when.getTime())) {
      textEl.textContent = "Freshness unknown.";
      dotEl.classList.add("stale");
      return;
    }
    var ageHours = (Date.now() - when.getTime()) / 36e5;
    if (ageHours > 48) dotEl.classList.add("stale");
    textEl.textContent = "Data updated " + when.toLocaleString("en-GB", {
      timeZone: "Europe/Paris", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"
    }) + " (Paris time).";
  }

  function groupByCity(events) {
    var counts = {};
    events.forEach(function (ev) {
      var city = ev.city_name || "Unknown";
      counts[city] = (counts[city] || 0) + 1;
    });
    return Object.keys(counts).map(function (city) {
      return { city: city, count: counts[city] };
    }).sort(function (a, b) { return b.count - a.count; });
  }

  function groupFestivals(events) {
    var counts = {};
    events.forEach(function (ev) {
      if (FESTIVAL_ORGS.indexOf(ev.organization_name) === -1) return;
      var key = ev.organization_name + "||" + (ev.city_name || "");
      if (!counts[key]) counts[key] = { org: ev.organization_name, city: ev.city_name, count: 0 };
      counts[key].count += 1;
    });
    return Object.keys(counts).map(function (k) { return counts[k]; })
      .sort(function (a, b) { return b.count - a.count; });
  }

  // Groups already-filtered events into day-buckets in chronological order,
  // then returns the HTML for the shared event-card list markup. Used by
  // both the hub's "recently verified" strip (small N) and the full
  // per-city view (all matching events).
  function renderEventCards(events) {
    var withDates = events.map(function (ev) {
      return { ev: ev, d: new Date(ev.starts_at) };
    }).filter(function (x) {
      return !isNaN(x.d.getTime());
    }).sort(function (a, b) { return a.d - b.d; });

    var groups = [];
    var lastKey = null;
    withDates.forEach(function (x) {
      var key = x.d.toLocaleDateString("en-GB", { timeZone: "Europe/Paris" });
      if (key !== lastKey) {
        groups.push({ key: key, day: x.d, items: [] });
        lastKey = key;
      }
      groups[groups.length - 1].items.push(x);
    });

    var html = "";
    groups.forEach(function (g) {
      html += '<section class="day-group">';
      html += '<div class="day-heading">' + escapeHtml(fmtDayHeading(g.day)) + '</div>';
      g.items.forEach(function (x) {
        var ev = x.ev;
        var venueBit = ev.venue_name ? escapeHtml(ev.venue_name) : null;
        var orgBit = ev.organization_name ? escapeHtml(ev.organization_name) : null;
        var price = fmtPrice(ev);
        var metaParts = [];
        if (venueBit) metaParts.push(venueBit);
        if (orgBit && orgBit !== venueBit) metaParts.push(orgBit);
        if (ev.language === "en") metaParts.push("English");
        if (price) metaParts.push(price);
        var meta = metaParts.join(' <span class="sep">·</span> ');

        var hasUrl = ev.canonical_event_url && /^https?:\/\//.test(ev.canonical_event_url);
        var ticket = hasUrl
          ? '<a class="ticket-link" href="' + escapeHtml(ev.canonical_event_url) + '" rel="noopener noreferrer" target="_blank">Official tickets →</a>'
          : '<span class="ticket-link disabled">No ticket link yet</span>';

        html += '<article class="event-card">';
        html += '  <div class="event-top">';
        html += '    <div class="event-title">' + escapeHtml(ev.title || "Untitled show") + "</div>";
        html += '    <div class="event-time">' + escapeHtml(fmtTime(x.d)) + "</div>";
        html += "  </div>";
        html += '  <div class="event-meta">' + meta + " " + statusBadge(ev) + "</div>";
        html += '  <div class="event-actions">' + ticket + "</div>";
        html += "</article>";
      });
      html += "</section>";
    });
    return html;
  }

  global.AtlasCommon = {
    DATA_URL: DATA_URL,
    MANIFEST_URL: MANIFEST_URL,
    FESTIVAL_ORGS: FESTIVAL_ORGS,
    escapeHtml: escapeHtml,
    fmtDayHeading: fmtDayHeading,
    fmtTime: fmtTime,
    fmtPrice: fmtPrice,
    statusBadge: statusBadge,
    dropFrench: dropFrench,
    fetchEvents: fetchEvents,
    fetchManifest: fetchManifest,
    setFreshness: setFreshness,
    groupByCity: groupByCity,
    groupFestivals: groupFestivals,
    renderEventCards: renderEventCards
  };
})(window);
