'use strict';
const assert = require('node:assert/strict');
const {loadCandidateDecks} = require('./candidate-deck-loader.cjs');
const {loadImplementedCards} = require('./print-coverage.cjs');
const {deckDigest} = require('./paired-seat-plan.cjs');

const decks = loadCandidateDecks();
assert.deepEqual(decks.map(deck => deck.id), [
  'vileplume', 'shadow_rider', 'regidrago', 'mew_genesect', 'mew_genesect_vip4'
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
console.log('[candidate-decks] PASS: source 60 unchanged; strictly-mapped paper Expanded VIP4 counterfactual differs by precisely one printed card');
