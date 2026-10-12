'use strict';
const assert = require('node:assert/strict');
const {loadCandidateDecks} = require('./candidate-deck-loader.cjs');
const {loadImplementedCards} = require('./print-coverage.cjs');
const {deckDigest} = require('./paired-seat-plan.cjs');

const decks = loadCandidateDecks();
assert.deepEqual(decks.map(deck => deck.id), [
  'vileplume', 'shadow_rider', 'regidrago', 'mew_genesect', 'mew_genesect_vip4', 'regidrago_dragapult_2', 'absol_garbodor'
]);
const original = decks.find(deck => deck.id === 'mew_genesect');
const changed = decks.find(deck => deck.id === 'mew_genesect_vip4');
assert.ok(original && changed);
assert.equal(original.engine_names.length, 60);
assert.equal(changed.engine_names.length, 60);
assert.equal(original.status, 'strictly_mappable');
assert.equal(changed.status, 'strictly_mappable');
assert.notEqual(deckDigest(original), deckDigest(changed));

const byName = new Map(loadImplementedCards().map(card => [card.fullName, card]));
/** @param {object} deck */
function counts(deck) {
  const result = new Map();
  for (const name of deck.engine_names) {
    const card = byName.get(name);
    assert.ok(card, 'Missing pinned card ' + name);
    result.set(card.name, (result.get(card.name) || 0) + 1);
  }
  return result;
}
const a = counts(original), b = counts(changed);
assert.equal(a.get('Battle VIP Pass'), 3);
assert.equal(a.get('Special Red Card'), 2);
assert.equal(b.get('Battle VIP Pass'), 4);
assert.equal(b.get('Special Red Card'), 1);
const changedNames = new Set([...a.keys(), ...b.keys()].filter(name => a.get(name) !== b.get(name)));
assert.deepEqual([...changedNames].sort(), ['Battle VIP Pass', 'Special Red Card']);
assert.equal(counts(original).get('Battle VIP Pass'), 3, 'Source tournament baseline must remain unchanged');
assert.equal(changed.transformation, '+1 Battle VIP Pass (swsh8-225), -1 Special Red Card (me4-82)');
const regOriginal = decks.find(deck => deck.id === 'regidrago');
const regChanged = decks.find(deck => deck.id === 'regidrago_dragapult_2');
assert.ok(regOriginal && regChanged);
assert.equal(regOriginal.engine_names.length, 60);
assert.equal(regChanged.engine_names.length, 60);
assert.equal(regChanged.status, 'strictly_mappable');
assert.notEqual(deckDigest(regOriginal), deckDigest(regChanged));
const rA=counts(regOriginal), rB=counts(regChanged);
assert.equal(rA.get('Battle VIP Pass'), 3);
assert.equal(rA.get('Dragapult ex'), 1);
assert.equal(rB.get('Battle VIP Pass'), 2);
assert.equal(rB.get('Dragapult ex'), 2);
assert.deepEqual([...new Set([...rA.keys(),...rB.keys()].filter(name=>rA.get(name)!==rB.get(name)))].sort(),
  ['Battle VIP Pass','Dragapult ex']);
assert.equal(counts(regOriginal).get('Battle VIP Pass'), 3);
assert.equal(regChanged.transformation,
  '+1 Dragapult ex (sv6-130), -1 Battle VIP Pass (swsh8-225)');
const absol=decks.find(deck=>deck.id==='absol_garbodor');
assert.ok(absol);
assert.equal(absol.status,'strictly_mappable');
assert.equal(absol.engine_names.length,60);
assert.deepEqual([...absol.verified_aliases].sort(),['sm9-51','xy4-92']);
assert.notEqual(deckDigest(absol),deckDigest(original));
assert.equal(absol.source,'2026_aichi_eighth_source_with_audited_same_print_aliases');
console.log('[candidate-decks] PASS: both printed 60-card references unchanged; Mew VIP4 and Regidrago 2-Dragapult differ by exactly one source-verified print each');

