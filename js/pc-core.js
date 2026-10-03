/* pc-core.js - ONE source of truth for show dates, times and counts on pariscomedy.com.
 * Used by index.html (Tonight panel + counts), shows.html (calendar), venues.html (cards) and show.html (detail).
 * Rules:
 *   - an occurrence is a CONFIRMED dated entry in listing.dates (synced from the ticket page). A weekday pattern
 *     (listing.days) is never proof of a date and is never turned into one.
 *   - the time of a show on a date is that occurrence's own time; only when the occurrence carries none do we fall
 *     back to the listing's template start_time.
 *   - non-English listings are filtered here (English-only rule) - data is never deleted.
 * No network, no storage, no tracking.
 */
(function (root) {
  'use strict';
  function parisToday() { return new Date().toLocaleDateString('sv-SE', { timeZone: 'Europe/Paris' }); }
  function isEnglish(L) { return [].concat((L && L.language) || 'en').join(',').toLowerCase().indexOf('en') !== -1; }
  function occurrences(L) {
    var d = Array.isArray(L && L.dates) ? L.dates : [], out = [], seen = {};
    for (var i = 0; i < d.length; i++) {
      var o = d[i]; if (!o || !o.date || seen[o.date]) continue;
      seen[o.date] = 1; out.push({ date: o.date, time: o.time || '', url: o.url || '' });
    }
    return out.sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
  }
  function timeOn(L, ds) {
    var o = occurrences(L).filter(function (x) { return x.date === ds; })[0];
    return (o && o.time) || (L && L.start_time) || '';
  }
  function nextOccurrence(L, todayISO) {
    var t = todayISO || parisToday();
    return occurrences(L).filter(function (x) { return x.date >= t; })[0] || null;
  }
  /* time to print when no particular date is in play (venue cards, show page): next confirmed occurrence, else template */
  function displayTime(L, todayISO) {
    var n = nextOccurrence(L, todayISO);
    return (n && n.time) || (L && L.start_time) || '';
  }
  /* every confirmed occurrence of every English listing on one date, sorted by time - THE count used everywhere */
  function occurrencesOn(listings, ds) {
    var out = [];
    (listings || []).forEach(function (L) {
      if (!isEnglish(L)) return;
      occurrences(L).forEach(function (o) {
        if (o.date === ds) out.push({ listing: L, date: ds, time: o.time || L.start_time || '', url: o.url });
      });
    });
    return out.sort(function (a, b) { return (a.time || '').localeCompare(b.time || ''); });
  }
  function hasConfirmedDates(L) { return occurrences(L).length > 0; }
  root.PC = { parisToday: parisToday, isEnglish: isEnglish, occurrences: occurrences, timeOn: timeOn,
              nextOccurrence: nextOccurrence, displayTime: displayTime, occurrencesOn: occurrencesOn,
              hasConfirmedDates: hasConfirmedDates };
})(window);
