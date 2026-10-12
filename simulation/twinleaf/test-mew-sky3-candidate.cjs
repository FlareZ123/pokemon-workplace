'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { loadDecks, ROOT } = require('./tournament-baselines.cjs');
const { loadTournamentDecks } = require('./tournament-deck-loader.cjs');
const { loadImplementedCards, cleanNumber } = require('./print-coverage.cjs');
const { registerLists, runOne } = require('./tournament-bounded-match.cjs');
const { DeckAnalyser } = require('../../vendor/twinleafgg/ptcg-server/output/game/cards/deck-analyser');
const { Format } = require('../../vendor/twinleafgg/ptcg-server/output/game/store/card/card-types');

const VARIANT = path.join(ROOT, 'results/decks/mew-genesect-sky3-path1-aichi-counterfactual/deck.json');

/**
 * Return the unique printed card implementation in the pinned engine.
 * @param {object[]} cards
 * @param {string} set
 * @param {string} number
 * @param {string} name
 * @returns {object}
 */
function findEngineCard(cards, set, number, name) {
  const matched = cards.filter(card =>
    card.set === set && cleanNumber(card.setNumber) === number &&
    card.name === name);
  assert.equal(matched.length, 1, 'Engine print must have exactly one implementation');
  return matched[0];
}

/** @returns {{original:string[],candidate:string[]}} */
function buildCandidate() {
  const manifest = JSON.parse(fs.readFileSync(VARIANT, 'utf8'));
  assert.equal(manifest.id, 'mew-genesect-sky3-path1-aichi-counterfactual');
  assert.equal(manifest.as_of, '2026-10-12');
  const source = loadDecks().find(deck => deck.id === 'mew_genesect');
  const baseline = loadTournamentDecks().find(deck => deck.id === 'mew_genesect');
  assert.ok(source && baseline);
  assert.equal(baseline.status, 'strictly_mappable');

  const sourceByPrint = new Map(source.cards.map(c => [c.print_id, c.quantity]));
  assert.equal(manifest.cards.length, sourceByPrint.size);
  const seen = new Set();
  for (const card of manifest.cards) {
    assert.ok(sourceByPrint.has(card.print_id), 'New print introduced: ' + card.print_id);
    assert.ok(!seen.has(card.print_id), 'Duplicate printed card entry');
    seen.add(card.print_id);
    const offset = card.print_id === 'xy6-89' ? 1 :
      card.print_id === 'swsh6-148' ? -1 : 0;
    assert.equal(card.quantity, sourceByPrint.get(card.print_id) + offset);
  }
  assert.equal(manifest.cards.reduce((sum, c) => sum + c.quantity, 0), 60);

  const implemented = loadImplementedCards();
  const sky = findEngineCard(implemented, 'ROS', '89', 'Sky Field');
  const pathCard = findEngineCard(implemented, 'CRE', '148', 'Path to the Peak');
  const candidate = baseline.engine_names.slice();
  const pathIndex = candidate.indexOf(pathCard.fullName);
  assert.ok(pathIndex >= 0);
  candidate.splice(pathIndex, 1, sky.fullName);
  assert.equal(candidate.length, 60);
  assert.equal(candidate.filter(name => name === sky.fullName).length, 3);
  assert.equal(candidate.filter(name => name === pathCard.fullName).length, 1);
  return {original: baseline.engine_names, candidate};
}

function run() {
  const { original, candidate } = buildCandidate();
  registerLists([original, candidate]);
  assert.equal(new DeckAnalyser(original).isValid(Format.EXPANDED), true);
  assert.equal(new DeckAnalyser(candidate).isValid(Format.EXPANDED), true);

  // Paired-seat engine smoke only; SimpleTacticsAi is an unvalidated game policy.
  const seed = 20261012;
  const traces = [
    runOne(original, candidate, seed, 200, 12000),
    runOne(candidate, original, seed, 200, 12000),
  ];
  for (const trace of traces) {
    assert.ok(trace.turn >= 1, 'The deck must enter a real player turn');
    assert.equal(trace.error, null, 'Source deck caused a policy/engine error');
    assert.ok(!['dispatch_error', 'policy_error', 'unknown_actor'].includes(trace.status));
  }
  console.log('[mew-sky3-Path1] ' + JSON.stringify({
    scope: 'bounded pinned Twinleaf setup, unvalidated SimpleTacticsAi',
    seed, paper_card_count: 60, pin: '3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    seat_traces: traces.map(t => ({
      status: t.status, turn: t.turn, actions: t.actions,
      attacks: t.attacks, first_actor: t.first_actor,
      game_random_calls: t.game_random_calls,
      policy_random_calls: t.policy_random_calls,
      error: t.error,
    })),
  }));
  console.log('[mew-sky3-Path1] PASS: exact print manifest and paired-seat smoke');
}
if (require.main === module) {
  try { run(); } catch (error) {
    console.error('[mew-sky3-Path1] FAIL', error);
    process.exitCode = 1;
  }
}
module.exports = { buildCandidate };
