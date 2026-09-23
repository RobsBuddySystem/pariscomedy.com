#!/usr/bin/env node
// show.html Event schema must carry the real Europe/Paris offset for the
// event's own date (+01:00 in winter), not a hard-coded +02:00. Extracts the
// shipped parisOffset() from show.html. Usage: node tests/test_event_schema_offset.js
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const src = fs.readFileSync(path.join(__dirname, '..', 'show.html'), 'utf8');
const i = src.indexOf('function parisOffset(');
if (i === -1) { console.log('FAIL - parisOffset not found in show.html'); process.exit(1); }
let j = src.indexOf('{', i), depth = 0;
for (; j < src.length; j++) { if (src[j] === '{') depth++; else if (src[j] === '}' && --depth === 0) { j++; break; } }
const box = {}; vm.createContext(box); vm.runInContext(src.slice(i, j) + ';this.parisOffset=parisOffset;', box);
let fails = 0;
for (const [d, t, want] of [['2026-09-30','20:00','+02:00'], ['2026-10-24','22:00','+02:00'],
                            ['2026-10-25','20:00','+01:00'], ['2026-12-31','23:30','+01:00'],
                            ['2027-03-28','20:00','+02:00']]) {
  const got = box.parisOffset(d, t);
  console.log((got === want ? 'PASS' : 'FAIL') + ` - ${d} ${t} -> ${got} (want ${want})`);
  if (got !== want) fails++;
}
if (/:00\+02:00'/.test(src)) { console.log("FAIL - a hard-coded ':00+02:00' remains in show.html"); fails++; }
console.log(fails ? `${fails} assertion(s) FAILED` : 'All assertions passed.');
process.exit(fails ? 1 : 0);
