'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {loadMewWally2Tapu1Deck} = require('./mew-wally2-tapu1-deck.cjs');
const {loadMewTapuWallyDeck} = require('./mew-tapu-wally-deck.cjs');
const {loadTournamentDecks} = require('./tournament-deck-loader.cjs');
const {loadImplementedCards} = require('./print-coverage.cjs');

const sourceDeck = loadTournamentDecks().find(deck => deck.id === 'mew_genesect');
const intermediate = loadMewTapuWallyDeck();
const candidate = loadMewWally2Tapu1Deck();
assert.ok(sourceDeck && sourceDeck.status === 'strictly_mappable');
assert.equal(candidate.status, 'strictly_mappable');
assert.equal(candidate.engine_names.length, 60);
assert.equal(sourceDeck.engine_names.length, 60);
assert.equal(intermediate.engine_names.length, 60);

const catalog = new Map(loadImplementedCards().map(card => [card.fullName, card]));
/** @param {{engine_names:string[]}} deck */
function countByName(deck) {
  const counts = new Map();
  for (const name of deck.engine_names) {
    const card = catalog.get(name);
    assert.ok(card, 'Twinleaf implemented fullName not found');
    counts.set(card.name, (counts.get(card.name) || 0) + 1);
  }
  return counts;
}
const original = countByName(sourceDeck);
const midway = countByName(intermediate);
const observed = countByName(candidate);
assert.equal(original.get('Wally'), 1);
assert.equal(original.get('Special Red Card'), 2);
assert.equal(original.get('Tapu Lele-GX') || 0, 0);
assert.equal(midway.get('Wally'), 1);
assert.equal(midway.get('Special Red Card'), 1);
assert.equal(midway.get('Tapu Lele-GX'), 1);
assert.equal(observed.get('Wally'), 2);
assert.equal(observed.get('Special Red Card') || 0, 0);
assert.equal(observed.get('Tapu Lele-GX'), 1);

const changed = new Set([...original.keys(), ...observed.keys()]);
assert.deepEqual([...changed].filter(
  name => (original.get(name) || 0) !== (observed.get(name) || 0)
).sort(), ['Special Red Card', 'Tapu Lele-GX', 'Wally']);
const manifestPath = path.resolve(
  __dirname, '../../results/decks/mew-genesect-wally2-tapu1/deck.json'
);
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
assert.equal(manifest.id, 'mew-genesect-wally2-tapu1');
assert.equal(manifest.as_of, '2026-10-13');
assert.equal(manifest.cards.reduce((total, entry) => total + entry.quantity, 0), 60);
assert.equal(manifest.cards.length, observed.size);
for (const entry of manifest.cards) {
  assert.equal(observed.get(entry.name), entry.quantity,
    'Candidate manifest and pinned engine disagree for ' + entry.name);
}
assert.equal(candidate.transformation, manifest.transformation);
console.log('[mew-wally2-tapu1] PASS: 60 exact pinned Twinleaf cards, ' +
  'canonical manifest, +Wally +Lele -2Red, source deck immutable. ' +
  'No effect or match-strength fidelity claimed.');
