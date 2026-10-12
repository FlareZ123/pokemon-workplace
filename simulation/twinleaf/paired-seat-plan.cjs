'use strict';
const assert = require('node:assert/strict');
const {createHash} = require('node:crypto');

/**
 * @typedef {{id: string, engine_names: string[]}} MappedDeck
 * @typedef {{pair_id: number, seed: number, orientation: 'AB'|'BA', seat1: MappedDeck, seat2: MappedDeck}} SeatPairRun
 */

/**
 * Stable identifier for a physical deck multiset, independent of list order.
 * @param {MappedDeck} deck
 * @returns {string}
 */
function deckDigest(deck) {
  assert.equal(deck.engine_names.length, 60, 'Tournament deck must contain 60 physical cards');
  assert.ok(deck.engine_names.every(name => typeof name === 'string' && name.length > 0));
  return createHash('sha256')
    .update(JSON.stringify([...deck.engine_names].sort()))
    .digest('hex');
}

/**
 * Each seed is replayed with the two complete physical lists exchanging seats.
 * This controls the PRNG's starting state, not turn order or individual draws.
 * @param {MappedDeck} deckA
 * @param {MappedDeck} deckB
 * @param {number[]} seeds
 * @returns {SeatPairRun[]}
 */
function makeSeatPairs(deckA, deckB, seeds) {
  assert.notEqual(deckA.id, deckB.id, 'Distinct deck identities are required');
  deckDigest(deckA);
  deckDigest(deckB);
  assert.ok(seeds.length > 0, 'At least one seed is required');
  assert.equal(new Set(seeds).size, seeds.length, 'Seeds must identify distinct pairs');
  const runs = [];
  for (const [pair_id, seed] of seeds.entries()) {
    assert.ok(Number.isSafeInteger(seed) && seed >= 0 && seed <= 0xffffffff, 'Seed must be a uint32');
    runs.push({pair_id, seed, orientation: 'AB', seat1: deckA, seat2: deckB});
    runs.push({pair_id, seed, orientation: 'BA', seat1: deckB, seat2: deckA});
  }
  return runs;
}

module.exports = {deckDigest, makeSeatPairs};
