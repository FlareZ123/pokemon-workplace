'use strict';

/**
 * Single runnable live-hook test for pinned Trevenant & Dusknoir-GX Night Watch.
 *
 * Exercises the source card's real reducer through the hook installed by the
 * match runner. The controlled store resolves source move effects using its
 * real CardList operations and records reveal/shuffle prompts. Exhaustive
 * fixed RNG bins establish equal physical unordered-pair frequencies.
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const base = path.resolve(__dirname, '../../vendor/twinleafgg/ptcg-server/output');
const load = name => require(path.join(base, name));
const { Player } = load('game/store/state/player');
const { AttackEffect, MoveCardsEffect } = load('game/store/effects/game-effects');
const { TrevenantDusknoirGX } = load(
  'sets/08-sun-and-moon/set-sun-and-moon-promos/trevenant-dusknoir-gx'
);
const { ensureResearchEngineHooks } = require('./tournament-bounded-match.cjs');

/**
 * Call the actual Night Watch reducer while controlling its physical-game RNG.
 * @param {number[]} randomUnits
 * @param {number} handSize
 * @returns {{selected:number[],rngCalls:number,events:string[],reveal:number[],remaining:number[],deck:number[]}}
 */
function exercise(randomUnits, handSize = 3) {
  const attacker = new Player();
  attacker.id = 1;
  const defender = new Player();
  defender.id = 2;
  for (let i = 0; i < handSize; i++) {
    const physical = new TrevenantDusknoirGX();
    physical.id = 100 + i;
    defender.hand.cards.push(physical);
  }
  const source = new TrevenantDusknoirGX();
  const effect = new AttackEffect(attacker, defender, source.attacks[0]);
  const state = { players: [attacker, defender] };
  const events = [];
  const revealed = [];
  const originalRandom = Math.random;
  let rngCalls = 0;
  Math.random = () => {
    assert.ok(rngCalls < randomUnits.length,
      'Expected only one random card selection per sample position');
    return randomUnits[rngCalls++];
  };
  const store = {
    /** @param {any} stateValue @param {any} move */
    reduceEffect(stateValue, move) {
      assert.ok(move instanceof MoveCardsEffect,
        'Unexpected effect, review pinned reducer before accepting this test');
      assert.equal(move.source, defender.hand);
      assert.equal(move.destination, defender.deck);
      assert.equal(move.cards.length, Math.min(2, handSize));
      events.push('MOVE_CARDS');
      move.source.moveCardsTo(move.cards, move.destination);
      return stateValue;
    },
    /** @param {any} stateValue @param {any} prompt */
    prompt(stateValue, prompt) {
      const name = prompt.constructor.name;
      events.push(name);
      assert.notEqual(name, 'ChooseCardsPrompt',
        'Attacker may not choose random Night Watch targets');
      if (name === 'ShowCardsPrompt') {
        const cards = prompt.cards || prompt.cardsToShow;
        assert.ok(Array.isArray(cards),
          'The actual reveal prompt must retain selected card objects');
        revealed.push(...cards.map(card => card.id));
      } else {
        assert.equal(name, 'ShuffleDeckPrompt',
          'Only the original reveal/shuffle tail is expected');
      }
      return stateValue;
    }
  };

  try {
    source.reduceEffect(store, state, effect);
  } finally {
    Math.random = originalRandom;
  }
  const deck = defender.deck.cards.map(card => card.id);
  return {
    selected: deck,
    rngCalls,
    events,
    reveal: revealed,
    remaining: defender.hand.cards.map(card => card.id),
    deck
  };
}

/** @returns {void} */
function run() {
  assert.deepEqual(ensureResearchEngineHooks(), [
    'shadow_rider_underworld_door_guard_v1',
    'regidrago_celestial_roar_any_energy_v1',
    'stoutland_wild_tackle_self20_v1',
    'night_watch_uniform_discard_v1'
  ]);
  const bins = [1 / 6, 3 / 6, 5 / 6];
  const tails = [1 / 4, 3 / 4];
  const pairs = new Map();
  for (const head of bins) {
    for (const tail of tails) {
      const outcome = exercise([head, tail]);
      assert.equal(outcome.rngCalls, 2);
      assert.deepEqual(outcome.events,
        ['MOVE_CARDS', 'ShowCardsPrompt', 'ShuffleDeckPrompt']);
      assert.deepEqual(outcome.reveal, outcome.deck);
      assert.equal(outcome.remaining.length, 1);
      assert.equal(new Set([...outcome.deck, ...outcome.remaining]).size, 3);
      const pair = outcome.selected.slice().sort((a, b) => a - b).join(',');
      pairs.set(pair, (pairs.get(pair) || 0) + 1);
    }
  }
  assert.deepEqual([...pairs].sort(), [
    ['100,101', 2], ['100,102', 2], ['101,102', 2]
  ]);
  // A randomized two-of-n sample has n*(n-1) equally likely ordered
  // selections, and each unordered pair appears in exactly two of them.
  for (const n of [5, 7]) {
    const counts = new Map();
    let hitsOnSingleton = 0;
    for (let first = 0; first < n; first++) {
      for (let second = 0; second < n - 1; second++) {
        const result = exercise([
          (first + 0.5) / n, (second + 0.5) / (n - 1)
        ], n);
        assert.equal(result.rngCalls, 2);
        assert.equal(new Set([...result.deck, ...result.remaining]).size, n);
        const pair = result.selected.slice().sort((a, b) => a - b).join(',');
        counts.set(pair, (counts.get(pair) || 0) + 1);
        if (result.selected.includes(100)) hitsOnSingleton++;
      }
    }
    assert.equal(counts.size, n * (n - 1) / 2);
    assert.ok([...counts.values()].every(value => value === 2));
    assert.equal(hitsOnSingleton, 2 * (n - 1),
      'Random Night Watch removes one named critical card with chance 2/n');
    console.log('[night-watch-live-hook] PASS: ' + n +
      '-card hand: ' + counts.size + ' unordered pairs, each exactly 2/' +
      (n * (n - 1)) + '; singleton-hit probability 2/' + n);
  }
  const singleton = exercise([0.99], 1);
  assert.deepEqual(singleton.selected, [100]);
  assert.equal(singleton.rngCalls, 1);
  assert.deepEqual(singleton.remaining, []);
  assert.deepEqual(exercise([], 0).events, []);
  assert.deepEqual(ensureResearchEngineHooks(), [
    'shadow_rider_underworld_door_guard_v1',
    'regidrago_celestial_roar_any_energy_v1',
    'stoutland_wild_tackle_self20_v1',
    'night_watch_uniform_discard_v1'
  ], 'Repeated hook installation must be idempotent');
  console.log('[night-watch-live-hook] PASS: real reducer selects exactly two random physical cards');
  console.log('[night-watch-live-hook] PASS: all three unordered two-of-three pairs have 2/6 weight');
  console.log('[night-watch-live-hook] PASS: physical cards moved, revealed, then shuffle requested');
  console.log('[night-watch-live-hook] PASS: singleton, empty hand, live installation, seeded RNG');
}

if (require.main === module) {
  run();
}

module.exports = { run, exercise };
