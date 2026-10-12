'use strict';
const assert = require('node:assert/strict');
const {loadTournamentDecks} = require('./tournament-deck-loader.cjs');
const {loadImplementedCards} = require('./print-coverage.cjs');

/**
 * Preserve the four independently audited Aichi decks and append one
 * separately labeled legal single-print substitution from the existing Mew
 * benchmark. Both physical prints are already verified by the strict loader.
 * @returns {Array<object>}
 */
function loadCandidateDecks() {
  const baselines = loadTournamentDecks();
  const mew = baselines.find(deck => deck.id === 'mew_genesect');
  assert.ok(mew && mew.status === 'strictly_mappable', 'Mew source baseline must be verified');

  const prototypes = new Map(loadImplementedCards().map(card => [card.fullName, card]));
  /** @param {string} fullName */
  const printedName = fullName => {
    const card = prototypes.get(fullName);
    assert.ok(card, 'No pinned implementation for ' + fullName);
    return card.name;
  };
  const source = mew.engine_names;
  assert.equal(source.length, 60);
  const vip = source.filter(name => printedName(name) === 'Battle VIP Pass');
  const red = source.filter(name => printedName(name) === 'Special Red Card');
  assert.equal(vip.length, 3, 'Published Mew list must contain three verified VIP Passes');
  assert.equal(red.length, 2, 'Published Mew list must contain two verified Special Red Cards');

  const candidate = [...source];
  const replacedIndex = candidate.indexOf(red[0]);
  assert.ok(replacedIndex >= 0);
  candidate[replacedIndex] = vip[0];
  assert.equal(candidate.filter(name => printedName(name) === 'Battle VIP Pass').length, 4);
  assert.equal(candidate.filter(name => printedName(name) === 'Special Red Card').length, 1);
  assert.equal(candidate.length, 60);

  return [...baselines, {
    ...mew,
    id: 'mew_genesect_vip4',
    status: 'strictly_mappable',
    engine_names: candidate,
    source: 'experimental_exact_print_counterfactual_from_mew_genesect',
    transformation: '+1 Battle VIP Pass (swsh8-225), -1 Special Red Card (me4-82)',
  }];
}
module.exports = {loadCandidateDecks};
