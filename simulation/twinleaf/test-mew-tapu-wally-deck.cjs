'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {loadTournamentDecks} = require('./tournament-deck-loader.cjs');
const {loadImplementedCards} = require('./print-coverage.cjs');
const {loadMewTapuWallyDeck} = require('./mew-tapu-wally-deck.cjs');

const references = loadTournamentDecks();
const original = references.find(deck => deck.id === 'mew_genesect');
const donor = references.find(deck => deck.id === 'regidrago');
const candidate = loadMewTapuWallyDeck();

assert.ok(original && donor);
assert.equal(candidate.status, 'strictly_mappable');
assert.equal(candidate.engine_names.length, 60);
assert.equal(original.engine_names.length, 60);
assert.equal(donor.engine_names.length, 60);
assert.notDeepEqual(candidate.engine_names, original.engine_names);

const byFullName = new Map(loadImplementedCards().map(card => [card.fullName, card]));

/** @param {{engine_names: string[]}} deck */
function cardCounts(deck) {
  const count = new Map();
  for (const fullName of deck.engine_names) {
    const card = byFullName.get(fullName);
    assert.ok(card, 'Exact pinned Twinleaf fullName missing from registry');
    count.set(card.name, (count.get(card.name) || 0) + 1);
  }
  return count;
}

const a = cardCounts(original);
const b = cardCounts(candidate);
const donorCounts = cardCounts(donor);
assert.equal(a.get('Special Red Card'), 2);
assert.equal(a.get('Tapu Lele-GX') || 0, 0);
assert.equal(donorCounts.get('Tapu Lele-GX'), 1);
assert.equal(b.get('Special Red Card'), 1);
assert.equal(b.get('Tapu Lele-GX'), 1);

const allNames = new Set([...a.keys(), ...b.keys()]);
const changed = [...allNames].filter(name => (a.get(name) || 0) !== (b.get(name) || 0));
assert.deepEqual(changed.sort(), ['Special Red Card', 'Tapu Lele-GX']);
assert.equal(candidate.transformation,
  '+1 Tapu Lele-GX (sm2-60), -1 Special Red Card (me4-82)');

const manifest = JSON.parse(fs.readFileSync(path.join(
  __dirname, '../../results/decks/mew-genesect-tapu-wally-counterfactual/deck.json'
), 'utf8'));
assert.equal(manifest.id, 'mew-genesect-tapu-wally-counterfactual');
assert.equal(manifest.cards.reduce((total, card) => total + card.quantity, 0), 60);
for (const card of manifest.cards) {
  assert.equal(b.get(card.name), card.quantity,
    'Pinned Twinleaf candidate must preserve exactly each manifest name and quantity');
}
const leleManifest = manifest.cards.find(card => card.name === 'Tapu Lele-GX');
assert.deepEqual(leleManifest, {quantity: 1, name: 'Tapu Lele-GX', print_id: 'sm2-60'});
console.log('[tapu-wally-deck] PASS: exact English print donor, immutable original, ' +
  '60 materialized cards and source manifest agreement; no effect-behavior claim');
