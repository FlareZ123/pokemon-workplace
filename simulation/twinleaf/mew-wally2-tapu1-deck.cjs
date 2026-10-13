'use strict';

const assert = require('node:assert/strict');
const {loadMewTapuWallyDeck} = require('./mew-tapu-wally-deck.cjs');
const {loadTournamentDecks} = require('./tournament-deck-loader.cjs');
const {loadImplementedCards} = require('./print-coverage.cjs');

/**
 * Preserve the original Aichi 2026 60, transform the validated one-Lele
 * counterfactual and replace its final Special Red Card with a second Wally
 * of exactly the original English xy6-94 engine fullName.
 *
 * @returns {{id:string,status:string,engine_names:string[],source:string,transformation:string}}
 */
function loadMewWally2Tapu1Deck() {
  const source = loadTournamentDecks().find(deck => deck.id === 'mew_genesect');
  assert.ok(source && source.status === 'strictly_mappable');
  const oneLele = loadMewTapuWallyDeck();
  assert.equal(oneLele.status, 'strictly_mappable');

  const catalog = new Map(loadImplementedCards().map(card => [card.fullName, card]));
  /** @param {string[]} names @param {string} cardName */
  const copies = (names, cardName) => names.filter(
    fullName => catalog.get(fullName).name === cardName
  );
  const originalWally = copies(source.engine_names, 'Wally');
  const remainingRed = copies(oneLele.engine_names, 'Special Red Card');
  assert.equal(originalWally.length, 1, 'Aichi source has one Wally');
  assert.equal(remainingRed.length, 1, 'First Tapu variant retains one Red Card');
  assert.equal(copies(oneLele.engine_names, 'Tapu Lele-GX').length, 1);

  const engineNames = [...oneLele.engine_names];
  const index = engineNames.indexOf(remainingRed[0]);
  assert.ok(index >= 0);
  engineNames[index] = originalWally[0];
  assert.equal(engineNames.length, 60);
  assert.equal(copies(engineNames, 'Special Red Card').length, 0);
  assert.equal(copies(engineNames, 'Wally').length, 2);
  assert.equal(copies(engineNames, 'Tapu Lele-GX').length, 1);

  return {
    id: 'mew_genesect_wally2_tapu1',
    status: 'strictly_mappable',
    engine_names: engineNames,
    source: 'experimental_exact_print_from_mew_genesect',
    transformation: '+1 Wally (xy6-94), +1 Tapu Lele-GX (sm2-60), -2 Special Red Card (me4-82)'
  };
}

module.exports = {loadMewWally2Tapu1Deck};
