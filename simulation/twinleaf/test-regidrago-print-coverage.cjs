'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {
  matchPaperPrint, loadImplementedCards, makePaperSetCodes,
} = require('./print-coverage.cjs');

const ROOT = path.resolve(__dirname, '../..');

/**
 * Parse the independent, source-checked 2026 Aichi Regidrago 10th-place
 * sixty-card manifest without inventing engine substitutions.
 *
 * @returns {{qty:number,name:string,printId:string}[]}
 */
function regidragoEntries() {
  const file = path.join(
    ROOT, 'results/regidrago_aichi_top10_playable/yoshioka_regidrago_2026.json'
  );
  const manifest = JSON.parse(fs.readFileSync(file, 'utf8'));
  const rows = Object.values(manifest.groups).flatMap(group =>
    group.map(card => ({
      qty: card.count,
      name: card.name,
      printId: card.print_id,
    }))
  );
  assert.equal(rows.reduce((n, row) => n + row.qty, 0), 60);
  assert.equal(new Set(rows.map(row => row.printId)).size, rows.length);
  return rows;
}

/**
 * Resolve known printed exact-ID correspondence against instantiated pinned
 * Twinleaf cards. A same-set/number different-name result is REVIEW only;
 * it cannot automatically become an exact semantic match.
 *
 * @returns {ReturnType<typeof matchPaperPrint>[]}
 */
function auditRegidrago() {
  const sets = JSON.parse(fs.readFileSync(
    path.join(ROOT, 'resources/sets/en.json'), 'utf8'
  ));
  const codeBySet = makePaperSetCodes(sets);
  const implemented = loadImplementedCards();
  return regidragoEntries().map(entry =>
    matchPaperPrint(entry, codeBySet, implemented)
  );
}

/** @returns {void} */
function run() {
  const results = auditRegidrago();
  const counts = {};
  const copies = {};
  for (const row of results) {
    counts[row.status] = (counts[row.status] ?? 0) + row.qty;
    copies[row.name] = (copies[row.name] ?? 0) + row.qty;
    if (row.status !== 'exact') {
      console.log('[aichi-regidrago-coverage] REVIEW', row.qty,
        row.printId, row.name, row.status, JSON.stringify(row.matches));
    }
  }
  assert.equal(copies['Regidrago V'], 4);
  assert.equal(copies['Regidrago VSTAR'], 3);
  assert.equal(copies['Dialga-GX'], 1);
  assert.equal(copies['Budew'], 2);
  console.log('[aichi-regidrago-coverage] 60 physical copies:', JSON.stringify(counts));
  for (const printId of ['swsh12-135', 'swsh12-136', 'sm5-100']) {
    const record = results.find(entry => entry.printId === printId);
    assert.ok(record, 'missing source-print entry ' + printId);
    assert.equal(record.status, 'exact',
      'core implemented gameplay print needed: ' + printId);
  }
  console.log('[aichi-regidrago-coverage] PASS: conservative exact-print coverage classified');
}

if (require.main === module) {
  run();
}

module.exports = { regidragoEntries, auditRegidrago, run };
