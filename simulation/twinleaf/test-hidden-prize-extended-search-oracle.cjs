'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const childProcess = require('node:child_process');

const vendor = path.resolve(__dirname, '../../vendor/twinleafgg');
const pin = '3348ebdc898f175a2ed8f999133cd13d1afd01f5';
assert.equal(childProcess.execFileSync('git', ['rev-parse', 'HEAD'],
  {cwd: vendor, encoding: 'utf8'}).trim(), pin,
'New Twinleaf pin requires revalidation of this policy audit');
const server = path.join(vendor, 'ptcg-server');
process.env.TS_NODE_PROJECT = path.join(server, 'tsconfig.json');
require(require.resolve('ts-node/register/transpile-only', {paths: [server]}));
/** @param {string} modulePath @returns {any} */
const engine = modulePath => require(path.join(server, 'src', modulePath));
const {State, GamePhase} = engine('game/store/state/state.ts');
const {Player} = engine('game/store/state/player.ts');
const {CardList} = engine('game/store/state/card-list.ts');
const {CardManager} = engine('game/cards/card-manager.ts');
const {Format, Stage, CardType, TrainerType} = engine('game/store/card/card-types.ts');
const {TrainerCard} = engine('game/store/card/trainer-card.ts');
const {PokemonCard} = engine('game/store/card/pokemon-card.ts');
const {pokemonHasCardType} = engine('game/index.ts');
const {PlayCardAction, PlayerType, SlotType} = engine('game/store/actions/play-card-action.ts');
const {StateScore} = engine('simple-bot/state-score/state-score.ts');
const {makeBlindPaidSearchTactic} = require('./blind-paid-search-tactic.cjs');
const {UltraBall} = engine('sets/10-scarlet-and-violet/set-scarlet-and-violet/ultra-ball.ts');
const {MysteriousTreasure} = engine('sets/08-sun-and-moon/set-forbidden-light/mysterious-treasure.ts');
const {RegidragoV} = engine('sets/09-sword-and-shield/set-silver-tempest/regidrago-v.ts');
const {GrassEnergy} = engine('sets/06-black-and-white/set-black-and-white/basic-energies.ts');
const {PlayTrainerTactic} = engine('simple-bot/simple-tactics/play-trainer-tactic.ts');
const {SimpleTacticsAi} = engine('simple-bot/simple-tactics-ai.ts');
const {defaultStateScores, defaultArbiterOptions, allPromptResolvers} =
  engine('simple-bot/simple-bot-definitions.ts');

const cases = [
  {name: 'Ultra Ball SVI', Item: UltraBall, payment: 2},
  {name: 'Mysterious Treasure FLI', Item: MysteriousTreasure, payment: 1},
];
const manager = CardManager.getInstance();
for (const card of [new UltraBall(), new MysteriousTreasure(),
  new RegidragoV(), new GrassEnergy()]) {
  if (!manager.isCardDefined(card.fullName)) manager.defineCard(card);
}
const grass = count => Array.from({length: count}, () => new GrassEnergy());
/** @returns {any[]} Six independent face-down Prize slots */
const prizes = () => Array.from({length: 6}, () => {
  const slot = new CardList();
  slot.cards = grass(1);
  return slot;
});

/**
 * Legal-size synthetic state with one hidden target across deck or Prizes.
 * A Dragon-type Regidrago V is eligible for both exact implemented search
 * Items. No information is exchanged before the decision in these fixtures.
 * @param {Function} Item Pinned engine card constructor
 * @param {'deck'|'prize'} zone Zone containing the hidden Basic
 * @param {number} position Zero-based position in that zone
 * @returns {any}
 */
function world(Item, zone, position) {
  assert.ok(zone === 'deck' || zone === 'prize');
  assert.ok(Number.isSafeInteger(position) && position >= 0);
  assert.ok(position < (zone === 'deck' ? 46 : 6));
  const state = new State();
  state.phase = GamePhase.PLAYER_TURN;
  state.turn = 2;
  state.activePlayer = 0;
  state.gameSettings.format = Format.EXPANDED;

  const player = new Player();
  player.id = 1;
  player.name = 'Hidden-Prize audit actor';
  player.hand.cards = [new Item(), ...grass(6)];
  player.active.cards = [new RegidragoV()];
  player.active.pokemonPlayedTurn = 1;
  player.deck.cards = grass(46);
  player.prizes = prizes();
  if (zone === 'deck') player.deck.cards[position] = new RegidragoV();
  else player.prizes[position].cards[0] = new RegidragoV();

  const opponent = new Player();
  opponent.id = 2;
  opponent.name = 'Fixed opponent';
  opponent.hand.cards = grass(7);
  opponent.deck.cards = grass(46);
  opponent.prizes = prizes();
  opponent.active.cards = [new RegidragoV()];
  opponent.active.pokemonPlayedTurn = 1;
  state.players = [player, opponent];

  for (const actor of state.players) {
    const count = actor.hand.cards.length + actor.deck.cards.length +
      actor.prizes.reduce((sum, slot) => sum + slot.cards.length, 0) +
      actor.active.cards.length + actor.bench.reduce((sum, slot) => sum + slot.cards.length, 0);
    assert.equal(count, 60);
  }
  return state;
}

/** @param {any} state @returns {string} */
function visible(state) {
  const actor = state.players[0], rival = state.players[1];
  return JSON.stringify({
    turn: state.turn, activePlayer: state.activePlayer,
    phase: state.phase, ownHand: actor.hand.cards.map(card => card.fullName),
    ownActive: actor.active.cards.map(card => card.fullName),
    ownBench: actor.bench.map(slot => slot.cards.map(card => card.fullName)),
    ownDeckSize: actor.deck.cards.length, ownPrizes: actor.getPrizeLeft(),
    opponentActive: rival.active.cards.map(card => card.fullName),
    opponentHandSize: rival.hand.cards.length,
    opponentDeckSize: rival.deck.cards.length, opponentPrizes: rival.getPrizeLeft(),
  });
}
/** @param {any} state @returns {string} */
function hiddenPool(state) {
  const actor = state.players[0];
  return JSON.stringify([...actor.deck.cards, ...actor.prizes.flatMap(slot => slot.cards)]
    .map(card => card.fullName).sort());
}
const opts = {
  scores: defaultStateScores,
  arbiter: defaultArbiterOptions,
  promptResolvers: allPromptResolvers,
};
const native = new PlayTrainerTactic(opts);
const BlindPaidSearchTactic = makeBlindPaidSearchTactic(PlayTrainerTactic, {
  TrainerCard, TrainerType, PokemonCard, Stage, CardType,
  pokemonHasCardType, PlayCardAction, PlayerType, SlotType, StateScore
});
const blind = new BlindPaidSearchTactic(opts);
for (const {name, Item, payment} of cases) {
  const deckWorld = world(Item, 'deck', 0);
  const prizeWorld = world(Item, 'prize', 0);
  assert.equal(visible(deckWorld), visible(prizeWorld));
  assert.equal(hiddenPool(deckWorld), hiddenPool(prizeWorld));
  assert.equal(deckWorld.players[0].hand.cards.length - 1 >= payment, true);
  assert.equal(deckWorld.players[0].deck.cards[0].fullName, 'Regidrago V SIT');
  assert.equal(prizeWorld.players[0].prizes[0].cards[0].fullName, 'Regidrago V SIT');
  let playedWhenDeck = 0, playedWhenPrize = 0;
  for (const zone of ['deck', 'prize']) {
    const count = zone === 'deck' ? 46 : 6;
    for (let pos = 0; pos < count; pos++) {
      const state = world(Item, zone, pos);
      assert.equal(visible(state), visible(deckWorld));
      assert.equal(hiddenPool(state), hiddenPool(deckWorld));
      const action = native.useTactic(state, state.players[0]);
      const blindAction = blind.useTactic(state, state.players[0]);
      assert.equal(blindAction?.type, 'PLAY_CARD_ACTION',
        name+' K0 action must be invariant to hidden allocation '+zone+'/'+pos);
      assert.equal(blindAction.handIndex, 0);
      assert.equal(action?.type === 'PLAY_CARD_ACTION', zone === 'deck',
        name + ': inaccessible Basic location changed the native Item choice: '+zone+'/'+pos);
      if (action) {
        if (zone === 'deck') playedWhenDeck++;
        else playedWhenPrize++;
      }
    }
  }
  // The oracle reaches the actual full bot, not merely the isolated tactic.
  for (const zone of ['deck', 'prize']) {
    const state = world(Item, zone, 0);
    const bot = new SimpleTacticsAi({id: 1, name: 'Native search bot'},
      {...opts, tactics: [PlayTrainerTactic]}, null);
    const action = bot.decodeNextAction(state);
    assert.equal(action?.type, zone === 'deck' ? 'PLAY_CARD_ACTION' : 'PASS_TURN');
    const safeBot = new SimpleTacticsAi({id: 1, name: 'K0-blind paid search'},
      {...opts, tactics: [BlindPaidSearchTactic]}, null);
    assert.equal(safeBot.decodeNextAction(world(Item, zone, 0))?.type, 'PLAY_CARD_ACTION');
  }
  console.log('[hidden-prize-extended] ' + JSON.stringify({
    item: name,
    discard_payment: payment,
    target: 'Regidrago V SIT',
    same_public_state_and_hidden_multiset: true,
    deck_positions_played: playedWhenDeck,
    total_deck_positions: 46,
    prize_positions_played: playedWhenPrize,
    total_prize_positions: 6,
    full_bot_reproduced: true,
    pin,
  }));
}
console.log('[hidden-prize-extended] PASS: 104 private worlds across both paid search Items');

for (const {Item, payment, name} of cases) {
  const noTargets = world(Item, 'deck', 0);
  noTargets.players[0].deck.cards[0] = new GrassEnergy();
  assert.equal(blind.useTactic(noTargets, noTargets.players[0]), undefined,
    name+' cannot be profitable with no eligible target even in the combined K0 pool');
  const noPayment = world(Item, 'deck', 0);
  const removals = noPayment.players[0].hand.cards.splice(1);
  noPayment.players[0].deck.cards.push(...removals);
  assert.equal(noPayment.players[0].hand.cards.length - 1 < payment, true);
  assert.equal(blind.useTactic(noPayment, noPayment.players[0]), undefined,
    name+' must respect its printed payment requirement');
}
console.log('[blind-paid-search] PASS: 104 hidden extended Item placements yield the same native-bot policy action');
