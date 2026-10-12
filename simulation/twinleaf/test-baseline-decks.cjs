'use strict';

const assert = require('node:assert/strict');
const { getAichiEngineDeck } = require('./baseline-deck-loader.cjs');
const { loadImplementedCards } = require('./print-coverage.cjs');
const { CardManager } = require('../../vendor/twinleafgg/ptcg-server/output/game/cards/card-manager');
const { DeckAnalyser } = require('../../vendor/twinleafgg/ptcg-server/output/game/cards/deck-analyser');
const { Format } = require('../../vendor/twinleafgg/ptcg-server/output/game/store/card/card-types');

/** @returns {void} */
function main() {
  const sets = ['vileplume', 'shadow_rider'];
  const lists = Object.fromEntries(sets.map(name => [name, getAichiEngineDeck(name)]));
  const byFullName = new Map(loadImplementedCards().map(card => [card.fullName, card]));
  const names = [...new Set(sets.flatMap(name => lists[name].deck))];
  const cards = names.map(name => byFullName.get(name));
  assert.ok(cards.every(Boolean), 'Every baseline identifier must be implemented');
  CardManager.getInstance().defineSet(cards);

  for (const [name, { deck, resolved }] of Object.entries(lists)) {
    assert.equal(deck.length, 60);
    assert.equal(resolved.reduce((sum, card) => sum + card.qty, 0), 60);
    assert.equal(new DeckAnalyser(deck).isValid(Format.EXPANDED), true,
      `Twinleaf deck syntax validation failed for ${name}`);
    console.log(`[engine-baseline] ${name} 60/60 mapped; ${resolved.length} distinct prints; ${names.length} total distinct registry IDs`);
  }

  const shadow = lists.shadow_rider;
  assert.equal(shadow.deck.filter(name => name === 'Battle Compressor PHF').length, 1);
  assert.equal(shadow.deck.filter(name => name === 'Trevenant & Dusknoir-GX SMP').length, 1);
  const vileplume = lists.vileplume;
  assert.equal(vileplume.deck.filter(name => name === 'Karen XYP').length, 1);
  console.log('[engine-baseline] PASS: both real 60-card tournament baselines translate to valid pinned Twinleaf deck identifiers');
}

try {
  main();
} catch (error) {
  console.error('[engine-baseline] FAIL:', error);
  process.exitCode = 1;
}
