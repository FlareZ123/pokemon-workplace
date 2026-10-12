'use strict';

const assert = require('node:assert/strict');
const {loadTournamentDecks} = require('./tournament-deck-loader.cjs');
const {loadImplementedCards} = require('./print-coverage.cjs');

/**
 * Build the exact-print Aichi fifth-place Mew/Genesect counterfactual
 * (+Tapu Lele-GX sm2-60, -Special Red Card me4-82) without editing
 * the immutable tournament reference, pinned Twinleaf, or shared mapping.
 *
 * Tapu is sourced from the strictly mapped Regidrago Aichi baseline,
 * which independently proves the *same English physical print* is
 * represented by Twinleaf's recorded fullName.
 *
 * This only proves deck physical materialization. It says nothing about
 * native Wonder Tag/Wally/CardManager effect fidelity or bot decision quality.
 * @returns {{id: string, status: string, engine_names: string[], source: string, transformation: string}}
 */
function loadMewTapuWallyDeck() {
  const references = loadTournamentDecks();
  const mew = references.find(deck => deck.id === 'mew_genesect');
  const regidrago = references.find(deck => deck.id === 'regidrago');
  assert.ok(mew && mew.status === 'strictly_mappable', 'Mew tournament print mapping must pass');
  assert.ok(regidrago && regidrago.status === 'strictly_mappable',
    'Regidrago donor print mapping must pass');
  assert.equal(mew.engine_names.length, 60);
  assert.equal(regidrago.engine_names.length, 60);

  const catalog = new Map(loadImplementedCards().map(card => [card.fullName, card]));

  /** @param {object} deck @param {string} name */
  const occurrences = (deck, name) => deck.engine_names.filter(
    fullName => catalog.get(fullName).name === name
  );
  const red = occurrences(mew, 'Special Red Card');
  const lele = occurrences(regidrago, 'Tapu Lele-GX');
  assert.equal(red.length, 2, 'Published fifth-place list has two Special Red Cards');
  assert.equal(occurrences(mew, 'Tapu Lele-GX').length, 0,
    'Never replace a pre-existing Tapu from the original deck');
  assert.equal(lele.length, 1, 'Source Regidrago print has one Tapu Lele-GX');

  const engineNames = [...mew.engine_names];
  const index = engineNames.indexOf(red[0]);
  assert.ok(index >= 0);
  engineNames[index] = lele[0];
  assert.equal(engineNames.length, 60);

  return {
    id: 'mew_genesect_tapu_wally',
    status: 'strictly_mappable',
    engine_names: engineNames,
    source: 'experimental_exact_print_counterfactual_from_mew_genesect',
    transformation: '+1 Tapu Lele-GX (sm2-60), -1 Special Red Card (me4-82)',
  };
}

module.exports = {loadMewTapuWallyDeck};
