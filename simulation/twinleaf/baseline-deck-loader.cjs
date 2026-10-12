'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { auditAichiBaselines, loadImplementedCards } = require('./print-coverage.cjs');

/**
 * A deliberately narrow, text-checked name difference in the Aichi champion
 * list. The paper source appends the Team Flare Gear classification to the
 * title; Twinleaf implements the matching PHF #92 print as Battle Compressor.
 *
 * @param {object} entry audited paper list entry
 * @param {Map<string, object>} implementedByFullName pinned engine catalog
 * @returns {string|null}
 */
function verifyBattleCompressorLabel(entry, implementedByFullName) {
  if (entry.printId !== 'xy4-92' ||
      entry.name !== 'Battle Compressor Team Flare Gear' ||
      entry.status !== 'name_mismatch_review' ||
      entry.matches.length !== 1 ||
      entry.matches[0].fullName !== 'Battle Compressor PHF') return null;

  const file = path.resolve(__dirname, '../../resources/cards/en/xy4.json');
  const printed = JSON.parse(fs.readFileSync(file, 'utf8'))
    .find(card => card.id === entry.printId);
  const engine = implementedByFullName.get('Battle Compressor PHF');
  assert.ok(printed && engine, 'Exact Battle Compressor printing must exist in both sources');
  assert.equal(printed.name, entry.name);
  assert.equal(printed.supertype, 'Trainer');
  assert.ok(printed.subtypes.includes('Item'));
  assert.equal(engine.name, 'Battle Compressor');
  assert.equal(engine.set, 'PHF');
  assert.equal(String(engine.setNumber), '92');
  assert.equal(engine.text, printed.rules[0],
    'Battle Compressor functionality must be independently verified if text changes');
  return engine.fullName;
}

/**
 * Translate a 60-card printed Aichi baseline to the exact pinned Twinleaf
 * implementation identifiers, rejecting any unverified source mismatch.
 *
 * @param {'vileplume'|'shadow_rider'} name
 * @returns {{deck:string[], resolved:{printId:string,fullName:string,qty:number,status:string}[]}}
 */
function getAichiEngineDeck(name) {
  const all = auditAichiBaselines();
  const entries = all[name];
  if (!entries) throw new Error(`Unknown baseline: ${name}`);
  const byFull = new Map(loadImplementedCards().map(card => [card.fullName, card]));
  const resolved = entries.map(entry => {
    let fullName;
    if (entry.status === 'exact' || entry.status === 'qualified_exact') {
      assert.equal(entry.matches.length, 1);
      fullName = entry.matches[0].fullName;
    } else {
      fullName = verifyBattleCompressorLabel(entry, byFull);
    }
    if (!fullName || !byFull.has(fullName)) {
      throw new Error(`Unverified Twinleaf correspondence: ${entry.printId} ${entry.name}: ${entry.status}`);
    }
    return { printId: entry.printId, fullName, qty: entry.qty, status: entry.status };
  });
  const deck = resolved.flatMap(entry => Array(entry.qty).fill(entry.fullName));
  assert.equal(deck.length, 60);
  return { deck, resolved };
}

module.exports = { verifyBattleCompressorLabel, getAichiEngineDeck };
