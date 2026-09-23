#!/usr/bin/env node
// Regression test for the homepage date-fabrication defect (fixed 2026-09-23).
//
// Bug: expandListings() in index.html placed every recurring show on every
// matching weekday for the next 7 days, ignoring the API's confirmed `dates`
// array. That put shows with upcoming_count:0 / dates:[] (e.g. Choumi in
// English, Comedy Lab, Oh My God She's Parisian!, Funny Women Paris) on
// specific calendar dates nobody confirmed.
//
// This test extracts the ACTUAL expandListings() function straight out of
// index.html (no reimplementation) and runs it against a fixture listing set
// with a mix of confirmed and unconfirmed shows, in a sandboxed vm context
// with `todayParis` pinned so the test is deterministic regardless of when
// it runs.
//
// Usage: node tests/test_expand_listings.js
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const REPO_ROOT = path.join(__dirname, '..');
const INDEX_HTML = fs.readFileSync(path.join(REPO_ROOT, 'index.html'), 'utf8');

// Pull the *exact* source of expandListings() (and its two small helpers)
// out of index.html so the test always exercises the real shipped code, not
// a hand-copied reimplementation that could drift from it.
function extractFunction(src, name) {
  const startMarker = `function ${name}(`;
  const start = src.indexOf(startMarker);
  assert(start !== -1, `${name} not found in index.html`);
  // Walk braces from the first "{" after the signature to find the matching close.
  let i = src.indexOf('{', start);
  let depth = 0;
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) { i++; break; } }
  }
  return src.slice(start, i);
}

const fnSource = [
  extractFunction(INDEX_HTML, '_venueName'),
  extractFunction(INDEX_HTML, '_hood'),
  extractFunction(INDEX_HTML, 'expandListings'),
].join('\n\n');

// Pin "today" to a fixed Friday-anchored week so the test is deterministic.
// (todayParis is a `const` computed from Date.now() at module load in the
// real file; here we inject it directly into the sandbox instead.)
const TODAY_PARIS = '2026-09-21'; // a Monday
const DAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

function isoPlusDays(iso, n) {
  const [y, m, d] = iso.split('-').map(Number);
  const dt = new Date(y, m - 1, d);
  dt.setDate(dt.getDate() + n);
  const p2 = (x) => String(x).padStart(2, '0');
  return `${dt.getFullYear()}-${p2(dt.getMonth() + 1)}-${p2(dt.getDate())}`;
}

// Next Friday on/after TODAY_PARIS (2026-09-21 is a Monday -> next Friday is 2026-09-25).
const NEXT_FRIDAY = isoPlusDays(TODAY_PARIS, (5 - new Date(TODAY_PARIS).getDay() + 7) % 7);
const NEXT_FRIDAY_PLUS_7 = isoPlusDays(NEXT_FRIDAY, 7); // outside the 7-day homepage window

let fixtureRaw = fs.readFileSync(path.join(__dirname, 'fixture_listings.json'), 'utf8');
fixtureRaw = fixtureRaw.split('__NEXT_FRIDAY_PLUS_7__').join(NEXT_FRIDAY_PLUS_7);
fixtureRaw = fixtureRaw.split('__NEXT_FRIDAY__').join(NEXT_FRIDAY);
const ONEOFF = isoPlusDays(TODAY_PARIS, 1); // a Tuesday, not on any weekly pattern
fixtureRaw = fixtureRaw.split('__ONEOFF__').join(ONEOFF);
const fixture = JSON.parse(fixtureRaw);

const sandbox = {
  todayParis: TODAY_PARIS,
  DAYS,
  console,
};
vm.createContext(sandbox);
vm.runInContext(fnSource, sandbox);

const result = sandbox.expandListings(fixture);

// ── Assertions ──────────────────────────────────────────────────────────
let failures = 0;
function check(cond, msg) {
  if (cond) { console.log('PASS -', msg); }
  else { console.log('FAIL -', msg); failures++; }
}

const unconfirmedEntries = result.filter(r => r.slug === 'unconfirmed-thursday-show');
check(
  unconfirmedEntries.length === 0,
  'no dated entry exists for the show without confirmed dates (unconfirmed-thursday-show)'
);

const noDaysEntries = result.filter(r => r.slug === 'no-days-show');
check(
  noDaysEntries.length === 0,
  'no dated entry exists for the show with no recurrence info at all (no-days-show)'
);

const confirmedEntries = result.filter(r => r.slug === 'confirmed-friday-show');
check(
  confirmedEntries.length === 1,
  'the show WITH a confirmed date within the 7-day window still appears (confirmed-friday-show)'
);
if (confirmedEntries.length === 1) {
  check(
    confirmedEntries[0].date === NEXT_FRIDAY,
    `confirmed-friday-show is dated on its confirmed occurrence ${NEXT_FRIDAY} (got ${confirmedEntries[0].date})`
  );
  check(
    confirmedEntries[0].ticket_url === 'https://example.com/tickets/1',
    'confirmed-friday-show carries the per-occurrence ticket URL from L.dates, not the generic booking_url'
  );
}

const oneOff = result.filter(r => r.slug === 'one-off-tuesday-special');
check(
  oneOff.length === 1 && oneOff[0].date === ONEOFF && oneOff[0].start_time === '21:00',
  `a confirmed date with no weekly pattern is shown exactly once on ${ONEOFF} (got ${JSON.stringify(oneOff.map(r => r.date))})`
);

console.log('');
if (failures > 0) {
  console.log(`${failures} assertion(s) FAILED`);
  process.exit(1);
} else {
  console.log('All assertions passed.');
  process.exit(0);
}
