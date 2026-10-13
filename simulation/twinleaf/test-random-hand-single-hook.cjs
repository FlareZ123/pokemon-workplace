'use strict';

/**
 * SFT for ten exact-print one-card random-hand compatibility hooks.
 * All three physical opponent-hand cards must be equally likely under
 * three equiprobable RNG bins. The source reducer owns movement and reveal.
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const compiled = path.resolve(__dirname, '../../vendor/twinleafgg/ptcg-server/output');
const engine = name => require(path.join(compiled,name));
const { Player } = engine('game/store/state/player');
const { AttackEffect, MoveCardsEffect } = engine('game/store/effects/game-effects');
const { TrainerEffect } = engine('game/store/effects/play-card-effects');
const { ChooseCardsPrompt } = engine('game/store/prompts/choose-cards-prompt');
const { TrevenantDusknoirGX } = engine(
  'sets/08-sun-and-moon/set-sun-and-moon-promos/trevenant-dusknoir-gx'
);
const {
  MARKER,
  buildPinnedSingleCardSpecs,
  installPinnedSingleCardRandomHooks
} = require('./random-hand-single-card-hook.cjs');

const specs = buildPinnedSingleCardSpecs(engine);

/** @param {{CardClass:Function,kind:string,attackIndex?:number,label:string}} spec
 * @param {number} chosenIndex
 */
function exercise(spec,chosenIndex) {
  const source = new spec.CardClass();
  const effectText = spec.kind === 'trainer'
    ? source.text : source.attacks[spec.attackIndex].text;
  assert.match(effectText,/random card from your opponent.s hand/i,
    'Source print no longer promises a randomized opponent-hand card');
  const attacker = new Player();
  const defender = new Player();
  attacker.id = 1;
  defender.id = 2;
  const cards = [];
  for (let index=0;index<3;index++) {
    const physical = new TrevenantDusknoirGX();
    physical.id = 100 + index;
    defender.hand.cards.push(physical);
    cards.push(physical);
  }
  const state = {players:[attacker,defender]};
  const effect = spec.kind === 'trainer'
    ? new TrainerEffect(attacker,source)
    : new AttackEffect(attacker,defender,source.attacks[spec.attackIndex]);
  const events = [];
  const moved = [];
  const revealed = [];
  const store = {
    /** @param {any} s @param {any} move */
    reduceEffect(s,move) {
      assert.ok(move instanceof MoveCardsEffect,
        'Unexpected source effect for '+spec.label);
      assert.equal(move.source,defender.hand);
      assert.ok(move.destination === defender.discard ||
        move.destination === defender.deck);
      events.push('MOVE_CARDS');
      moved.push(...move.cards.map(card=>card.id));
      move.source.moveCardsTo(move.cards,move.destination);
      return s;
    },
    /** @param {any} s @param {any} prompt */
    prompt(s,prompt) {
      const name = prompt.constructor.name;
      assert.notEqual(name,'ChooseCardsPrompt',
        spec.label+' exposed a random target chooser');
      events.push(name);
      if(name === 'ShowCardsPrompt') {
        revealed.push(...prompt.cards.map(card=>card.id));
      } else {
        assert.equal(name,'ShuffleDeckPrompt',
          'Unknown prompt type in source reducer '+spec.label);
      }
      return s;
    }
  };
  const previousRandom = Math.random;
  let randomCalls = 0;
  Math.random = () => {
    randomCalls++;
    return (chosenIndex + 0.5) / 3;
  };
  try {
    source.reduceEffect(store,state,effect);
  } finally {
    Math.random = previousRandom;
  }

  assert.equal(randomCalls,1,spec.label+' must select one uniformly random card');
  assert.equal(events.includes('ChooseCardsPrompt'),false);
  const chosenIdentity = 100 + chosenIndex;
  if(spec.kind === 'trainer') {
    assert.deepEqual(revealed,[chosenIdentity]);
    assert.equal(defender.hand.cards.length,3,
      'Pokemon was revealed and retained by conditional Tormenting Spray');
    assert.equal(moved.length,0);
  } else {
    assert.deepEqual(moved,[chosenIdentity]);
    assert.equal(defender.hand.cards.length,2);
    assert.equal(new Set([...defender.hand.cards, ...defender.deck.cards,
      ...defender.discard.cards]).size,3);
    assert.equal(revealed.length <= 1,true);
  }
  return {label:spec.label,index:chosenIndex,events,moved,revealed};
}

function main() {
  assert.equal(specs.length,10);
  const names = installPinnedSingleCardRandomHooks({
    specs,AttackEffect,TrainerEffect,ChooseCardsPrompt,
    random:()=>Math.random()
  });
  assert.equal(names.length,10);
  assert.deepEqual(installPinnedSingleCardRandomHooks({
    specs,AttackEffect,TrainerEffect,ChooseCardsPrompt,
    random:()=>Math.random()
  }),names,'Hook install must be idempotent');

  for(const spec of specs) {
    assert.equal(typeof spec.CardClass.prototype.reduceEffect[MARKER],
      'function','Missing uninstall marker on '+spec.label);
    for(const index of [0,1,2]) {
      exercise(spec,index);
    }
    console.log('[single-random-hand] PASS: '+spec.label +
      ' selected each physical opposing card once across three equal RNG bins');
  }
  console.log('[single-random-hand] PASS: 10 exact print classes x 3 independent choices');
}

if(require.main === module) {
  main();
}

module.exports = {main};
