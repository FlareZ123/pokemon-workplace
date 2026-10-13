'use strict';

/**
 * Reproducible pinned-Twinleaf diagnostic for three unrelated random-hand
 * defects. The tests prove observable reducer behavior and pass only while
 * those known defects remain. They do not install or require speculative
 * replacement hooks.
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const compiled = path.resolve(__dirname, '../../vendor/twinleafgg/ptcg-server/output');
const engine = name => require(path.join(compiled, name));
const { Player } = engine('game/store/state/player');
const { AttackEffect } = engine('game/store/effects/game-effects');
const { CoinFlipEffect, TrainerEffect } = engine('game/store/effects/play-card-effects');
const { Honchkrow } = engine('sets/08-sun-and-moon/set-ultra-prism/honchkrow');
const { Wimpod } = engine('sets/10-scarlet-and-violet/set-paradox-rift/wimpod');
const { TormentingSpray } = engine('sets/08-sun-and-moon/set-burning-shadows/tormenting-spray');
const { ChooseCardsPrompt } = engine('game/store/prompts/choose-cards-prompt');

/** @returns {{player: any,opponent:any,state:any}} */
function opposingHand() {
  const player = new Player();
  const opponent = new Player();
  player.id = 1;
  opponent.id = 2;
  const first = new Honchkrow();
  first.id = 100;
  const second = new Wimpod();
  second.id = 101;
  opponent.hand.cards.push(first, second);
  return { player, opponent, state: { players: [player, opponent] } };
}

function verifyHonchkrowMissesNonemptyHand() {
  const card = new Honchkrow();
  assert.equal(card.attacks[0].name, 'Rip and Run');
  assert.match(card.attacks[0].text, /Discard a random card/);
  const {player,opponent,state} = opposingHand();
  player.active.cards.push(card);
  let promptCount = 0;
  card.reduceEffect({
    prompt() { promptCount++; return state; },
    reduceEffect() { throw new Error('Unexpected effect'); }
  }, state, new AttackEffect(player, opponent, card.attacks[0]));
  assert.equal(promptCount, 0,
    'Pinned Honchkrow should omit its printed random discard on nonempty hands');
  assert.equal(opponent.hand.cards.length, 2);
  console.log('[source-gaps] CONFIRMED: Honchkrow UPR Rip and Run misses nonempty-hand discard');
}

function verifyWimpodDiscardsOnTails() {
  const card = new Wimpod();
  assert.equal(card.attacks[0].name, 'Sneaky Snacking');
  assert.match(card.attacks[0].text, /If heads, discard a random card/);
  const {player,opponent,state} = opposingHand();
  player.active.cards.push(card);
  let gotTails = false;
  let attemptedChoice = false;
  const store = {
    reduceEffect(s, effect) {
      assert.ok(effect instanceof CoinFlipEffect);
      gotTails = true;
      effect.callback(false);
      return s;
    },
    prompt(s, prompt) {
      if (prompt instanceof ChooseCardsPrompt &&
          prompt.cards === opponent.hand) {
        attemptedChoice = true;
      }
      return s;
    }
  };
  card.reduceEffect(store,state,new AttackEffect(player,opponent,card.attacks[0]));
  assert.equal(gotTails, true);
  assert.equal(attemptedChoice, true,
    'Pinned Wimpod should wrongly request opponent-hand discard even on tails');
  console.log('[source-gaps] CONFIRMED: Wimpod PAR Sneaky Snacking requests discard after tails');
}

function verifyTormentingSprayChoice() {
  const card = new TormentingSpray();
  assert.match(card.text, /random card/);
  const {player,opponent,state} = opposingHand();
  let chooser;
  card.reduceEffect({
    prompt(s, prompt) { chooser = prompt; return s; }
  },state,new TrainerEffect(player,card));
  assert.ok(chooser instanceof ChooseCardsPrompt);
  assert.equal(chooser.playerId,player.id);
  assert.equal(chooser.cards,opponent.hand);
  assert.equal(chooser.options.isSecret,true);
  assert.equal(chooser.options.min,1);
  assert.equal(chooser.options.max,1);
  for (const index of [0,1]) {
    const selected = chooser.decode([index]);
    assert.equal(chooser.validate(selected),true);
    assert.equal(selected[0],opponent.hand.cards[index]);
  }
  console.log('[source-gaps] CONFIRMED: Tormenting Spray BUS gives attacker both supposedly random target choices');
}

function main() {
  verifyHonchkrowMissesNonemptyHand();
  verifyWimpodDiscardsOnTails();
  verifyTormentingSprayChoice();
}

if(require.main===module) {
  main();
}

module.exports={ main };
