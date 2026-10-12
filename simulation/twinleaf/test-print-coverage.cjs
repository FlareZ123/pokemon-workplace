'use strict';

const assert = require('node:assert/strict');
const {
  parseBaselineDecks, matchPaperPrint, auditAichiBaselines
} = require('./print-coverage.cjs');

/** @returns {void} */
function run() {
  const sample = [
    '## 2026 Aichi champion: Shadow Rider Calyrex',
    ...Array.from({ length: 20 }, (_, i) => `| 3 | Test ${i} | sm5-${i + 1} |`),
    '## Some other heading'
  ].join('\n');
  assert.throws(() => parseBaselineDecks(sample), /Incomplete vileplume baseline/);

  const paperSets = new Map([['swsh6', 'CRE']]);
  const examples = [
    { set: 'CRE', setNumber: '074', name: 'Shadow Rider Calyrex V', fullName: 'Shadow Rider Calyrex V CRE' },
    { set: 'CRE', setNumber: '75', name: 'Shadow Rider Calyrex VMAX', fullName: 'Shadow Rider Calyrex VMAX CRE' }
  ];
  const valid = matchPaperPrint({ qty: 3, name: 'Shadow Rider Calyrex V', printId: 'swsh6-74' }, paperSets, examples);
  assert.equal(valid.status, 'exact');
  assert.equal(valid.matches[0].fullName, examples[0].fullName);
  const wrongName = matchPaperPrint({ qty: 3, name: 'Mewtwo', printId: 'swsh6-74' }, paperSets, examples);
  assert.equal(wrongName.status, 'name_mismatch_review');
  const unknown = matchPaperPrint({ qty: 1, name: 'Unknown', printId: 'foo-74' }, paperSets, examples);
  assert.equal(unknown.status, 'unmapped_set');
  console.log('[print-coverage] Synthetic collision and set-resolution checks passed');

  const decks = auditAichiBaselines();
  for (const [name, entries] of Object.entries(decks)) {
    assert.equal(entries.reduce((sum, item) => sum + item.qty, 0), 60);
    const counts = {};
    for (const entry of entries) {
      counts[entry.status] = (counts[entry.status] ?? 0) + entry.qty;
    }
    console.log(`[print-coverage] ${name}: ${JSON.stringify(counts)}`);
    for (const entry of entries) {
      if (entry.status !== 'exact') {
        console.log(`[print-coverage] REVIEW ${name} ${entry.qty}x ${entry.printId} ${entry.name}: ${entry.status} ${JSON.stringify(entry.matches)}`);
      }
    }
  }

  const shadow = decks.shadow_rider;
  const v = shadow.find(entry => entry.printId === 'swsh6-74');
  const vmax = shadow.find(entry => entry.printId === 'swsh6-75');
  assert.equal(v.status, 'exact');
  assert.equal(v.matches[0].fullName, 'Shadow Rider Calyrex V CRE');
  assert.equal(vmax.status, 'exact');
  assert.equal(vmax.matches[0].fullName, 'Shadow Rider Calyrex VMAX CRE');
  console.log('[print-coverage] PASS: pinned source semantics and conservative Aichi print coverage classified');
}

try {
  run();
} catch (error) {
  console.error('[print-coverage] FAIL:', error);
  process.exitCode = 1;
}
