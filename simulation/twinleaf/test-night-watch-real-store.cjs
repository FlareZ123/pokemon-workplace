'use strict';

/**
 * SFT: pinned Twinleaf Store handles Night Watch after research hook
 * installation without exposing an attacker-owned choice prompt.
 *
 * This executes the real Store, real MoveCardsEffect reducer, printed card
 * reducer, CardList movement and prompt registry. It does not play a match.
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const compiled = path.resolve(__dirname, '../../vendor/twinleafgg/ptcg-server/output');
const engine = name => require(path.join(compiled, name));
const { Store } = engine('game/store/store');
const { Player } = engine('game/store/state/player');
const { AttackEffect } = engine('game/store/effects/game-effects');
const { TrevenantDusknoirGX } = engine(
  'sets/08-sun-and-moon/set-sun-and-moon-promos/trevenant-dusknoir-gx'
);
const { ensureResearchEngineHooks } = require('./tournament-bounded-match.cjs');

/** @param {number[]} randomValues @param {number} opposingHand */
function runCase(randomValues, opposingHand) {
  const store = new Store({ onStateChange() {} });
  const attacker = new Player();
  const defender = new Player();
  attacker.id = 1;
  defender.id = 2;
  attacker.name = 'Attacker';
  defender.name = 'Defender';
  store.state.players.push(attacker, defender);
  const source = new TrevenantDusknoirGX();
  source.id = 44;
  attacker.active.cards.push(source);
  for (let index = 0; index < opposingHand; index++) {
    const physical = new TrevenantDusknoirGX();
    physical.id = 100 + index;
    defender.hand.cards.push(physical);
  }

  const effect = new AttackEffect(attacker, defender, source.attacks[0]);
  const oldRandom = Math.random;
  let calls = 0;
  Math.random = () => {
    assert.ok(calls < randomValues.length);
    return randomValues[calls++];
  };
  try {
    source.reduceEffect(store, store.state, effect);
  } finally {
    Math.random = oldRandom;
  }
  const selected = defender.deck.cards.map(c => c.id);
  const remaining = defender.hand.cards.map(c => c.id);
  const prompts = store.state.prompts.map(prompt => prompt.constructor.name);
  assert.equal(new Set([...selected, ...remaining]).size, opposingHand);
  assert.equal(selected.length, Math.min(2, opposingHand));
  assert.equal(remaining.length, opposingHand - selected.length);
  assert.equal(calls, Math.min(2, opposingHand));
  assert.equal(prompts.includes('ChooseCardsPrompt'), false);
  assert.deepEqual(prompts,
    opposingHand > 0 ? ['ShowCardsPrompt', 'ShuffleDeckPrompt'] : []);
  return { selected, remaining, prompts, calls };
}

function main() {
  assert.ok(ensureResearchEngineHooks().includes('night_watch_uniform_discard_v1'));
  const a = runCase([0.01, 0.99], 3);
  assert.deepEqual(a.selected, [100, 102]);
  const b = runCase([0.99, 0.01], 3);
  assert.deepEqual(b.selected, [102, 101]);
  const one = runCase([0.9], 1);
  assert.deepEqual(one.selected, [100]);
  const empty = runCase([], 0);
  assert.deepEqual(empty.selected, []);
  console.log('[night-watch-real-store] PASS: actual Store moved uniformly selected physical cards');
  console.log('[night-watch-real-store] PASS: source reveal/shuffle queued; no attacker choice prompt');
}

if (require.main === module) {
  main();
}

module.exports = { main, runCase };
