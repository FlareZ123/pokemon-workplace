'use strict';
const assert = require('node:assert/strict');
const {loadTournamentDecks} = require('./tournament-deck-loader.cjs');
const {loadAbsolTwinleaf} = require('./absol-twinleaf-deck.cjs');
const {loadImplementedCards} = require('./print-coverage.cjs');

/**
 * Materialize candidate lists by swapping physical copies whose exact prints
 * are already strictly verified in the unchanged published Aichi references.
 * Never synthesize an unavailable implementation or rewrite a baseline.
 * @returns {Array<object>}
 */
function loadCandidateDecks() {
  const baselines = loadTournamentDecks();
  const prototypes = new Map(loadImplementedCards().map(card => [card.fullName, card]));
  /** @param {string} fullName */
  const printedName = fullName => {
    const card = prototypes.get(fullName);
    assert.ok(card, 'No pinned implementation for ' + fullName);
    return card.name;
  };

  const swaps = [
    {
      baseline: 'mew_genesect', id: 'mew_genesect_vip4',
      remove: 'Special Red Card', originalRemove: 2,
      add: 'Battle VIP Pass', originalAdd: 3,
      transformation: '+1 Battle VIP Pass (swsh8-225), -1 Special Red Card (me4-82)'
    },
    {
      baseline: 'regidrago', id: 'regidrago_dragapult_2',
      remove: 'Battle VIP Pass', originalRemove: 3,
      add: 'Dragapult ex', originalAdd: 1,
      transformation: '+1 Dragapult ex (sv6-130), -1 Battle VIP Pass (swsh8-225)'
    }
  ];
  const candidates = swaps.map(swap => {
    const original = baselines.find(deck => deck.id === swap.baseline);
    assert.ok(original && original.status === 'strictly_mappable',
      'Exact original source baseline must be verified: ' + swap.baseline);
    assert.equal(original.engine_names.length, 60);

    const removed = original.engine_names.filter(name => printedName(name) === swap.remove);
    const added = original.engine_names.filter(name => printedName(name) === swap.add);
    assert.equal(removed.length, swap.originalRemove, 'Published source copy count changed: ' + swap.remove);
    assert.equal(added.length, swap.originalAdd, 'Published source copy count changed: ' + swap.add);

    const engineNames = [...original.engine_names];
    const index = engineNames.indexOf(removed[0]);
    assert.ok(index >= 0);
    engineNames[index] = added[0];
    assert.equal(engineNames.filter(name => printedName(name) === swap.remove).length, swap.originalRemove-1);
    assert.equal(engineNames.filter(name => printedName(name) === swap.add).length, swap.originalAdd+1);
    assert.equal(engineNames.length, 60);

    return {
      ...original,
      id: swap.id,
      status: 'strictly_mappable',
      engine_names: engineNames,
      source: 'experimental_exact_print_counterfactual_from_' + swap.baseline,
      transformation: swap.transformation,
    };
  });

  const absol=loadAbsolTwinleaf();
  assert.equal(absol.status,'verified_full_print_mapping',
    'Mega Absol must preserve both documented same-print alias checks');
  assert.equal(absol.engine_names.length,60);
  return [...baselines, ...candidates, {
    ...absol,
    status:'strictly_mappable',
    source:'2026_aichi_eighth_source_with_audited_same_print_aliases'
  }];
}
module.exports = {loadCandidateDecks};
