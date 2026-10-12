'use strict';
const assert = require('node:assert/strict');
const {summarizePairedTraces} = require('./paired-result-summary.cjs');

const a = {id: 'vileplume'};
const b = {id: 'mew_genesect'};
const pairs = [
  {pair_id: 0, seed: 77, orientation: 'AB', seat1: a, seat2: b},
  {pair_id: 0, seed: 77, orientation: 'BA', seat1: b, seat2: a},
  {pair_id: 1, seed: 78, orientation: 'AB', seat1: a, seat2: b},
  {pair_id: 1, seed: 78, orientation: 'BA', seat1: b, seat2: a},
];
/** @param {number} seed @param {string} status @param {string} phase @param {number} winner @param {string|null} error */
function trace(seed, status, phase, winner, error = null) {
  return {seed, status, phase, winner, error};
}

const diagnostic = summarizePairedTraces(pairs, [
  trace(77, 'finished', 'FINISHED', 0),
  trace(77, 'finished', 'FINISHED', 1),
  trace(78, 'wall_cap', 'ATTACK', -1),
  trace(78, 'dispatch_error', 'PLAYER_TURN', -1, 'rejected action'),
]);
assert.equal(diagnostic.paired_seed_count, 2);
assert.equal(diagnostic.fully_decided_pairs, 1);
assert.equal(diagnostic.completed_decisions, 2);
assert.equal(diagnostic.drawn_games, 0);
assert.equal(diagnostic.censored_games, 1);
assert.equal(diagnostic.error_games, 1);
assert.equal(diagnostic.terminal_unresolved_games, 0);
assert.deepEqual(diagnostic.by_deck, {
  vileplume: {wins: 2, losses: 0, draws: 0, unresolved: 2},
  mew_genesect: {wins: 0, losses: 2, draws: 0, unresolved: 2},
});
assert.deepEqual(diagnostic.games.map(g => g.winner_deck), ['vileplume', 'vileplume', null, null]);
assert.equal(diagnostic.games[3].error, 'rejected action');
console.log('[paired-result] Seat swap translates raw winner index correctly.');

const seatOneWins = summarizePairedTraces(pairs.slice(0, 2), [
  trace(77, 'finished', 'FINISHED', 0),
  trace(77, 'finished', 'FINISHED', 0),
]);
assert.equal(seatOneWins.by_deck.vileplume.wins, 1);
assert.equal(seatOneWins.by_deck.mew_genesect.wins, 1);
console.log('[paired-result] The identical winner index represents different winning decks after swap.');

const unresolved = summarizePairedTraces(pairs.slice(0, 2), [
  trace(77, 'finished', 'FINISHED', -1),
  trace(77, 'action_cap', 'ATTACK', -1),
]);
assert.equal(unresolved.completed_decisions, 0);
assert.equal(unresolved.terminal_unresolved_games, 1);
assert.equal(unresolved.censored_games, 1);
assert.equal(unresolved.by_deck.vileplume.wins, 0);
console.log('[paired-result] Unresolved terminal and action-capped outcomes never become wins.');

const drawn = summarizePairedTraces(pairs.slice(0, 2), [
  trace(77, 'finished', 'FINISHED', 3),
  trace(77, 'finished', 'FINISHED', 0),
]);
assert.equal(drawn.drawn_games, 1);
assert.equal(drawn.completed_decisions, 1);
assert.equal(drawn.by_deck.vileplume.draws, 1);
assert.equal(drawn.by_deck.mew_genesect.draws, 1);
assert.equal(drawn.by_deck.vileplume.wins, 0);
assert.equal(drawn.by_deck.mew_genesect.wins, 1);
console.log('[paired-result] Pinned engine GameWinner.DRAW=3 is not a win for either deck.');

assert.throws(() => summarizePairedTraces(pairs.slice(0, 2), [trace(77, 'finished', 'FINISHED', 0)]),
  /one trace per seat assignment/);
assert.throws(() => summarizePairedTraces(pairs.slice(0, 2), [trace(77, 'finished', 'FINISHED', 0), trace(999, 'finished', 'FINISHED', 1)]),
  /seeds differ/);
assert.throws(() => summarizePairedTraces(pairs.slice(0, 2), [trace(77, 'unexpected', 'ATTACK', -1), trace(77, 'finished', 'FINISHED', 1)]),
  /Unknown engine trace status/);
assert.throws(() => summarizePairedTraces([pairs[0], pairs[0]], [trace(77, 'finished', 'FINISHED', 0),trace(77, 'finished', 'FINISHED', 0)]),
  /two orientations/);
console.log('[paired-result] PASS: paired invariants, census, censoring, and malformed inputs');
