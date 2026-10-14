'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const childProcess = require('node:child_process');

const vendor = path.resolve(__dirname, '../../vendor/twinleafgg');
const pinned = '3348ebdc898f175a2ed8f999133cd13d1afd01f5';
const actual = childProcess.execFileSync('git', ['rev-parse', 'HEAD'],
  {cwd: vendor, encoding: 'utf8'}).trim();
assert.equal(actual, pinned, 'Review an updated engine before reusing the regression');
const server = path.join(vendor, 'ptcg-server');
process.env.TS_NODE_PROJECT = path.join(server, 'tsconfig.json');
require(require.resolve('ts-node/register/transpile-only', {paths: [server]}));
/** @param {string} modulePath @returns {any} */
const engine = modulePath => require(path.join(server, 'src', modulePath));
const {State, GamePhase} = engine('game/store/state/state.ts');
const {Player} = engine('game/store/state/player.ts');
const {CardList} = engine('game/store/state/card-list.ts');
const {CardManager} = engine('game/cards/card-manager.ts');
const {Format} = engine('game/store/card/card-types.ts');
const {QuickBall} = engine('sets/09-sword-and-shield/set-sword-and-shield/quick-ball.ts');
const {RegidragoV} = engine('sets/09-sword-and-shield/set-silver-tempest/regidrago-v.ts');
const {GrassEnergy} = engine('sets/06-black-and-white/set-black-and-white/basic-energies.ts');
const {PlayTrainerTactic} = engine('simple-bot/simple-tactics/play-trainer-tactic.ts');
const {SimpleTacticsAi} = engine('simple-bot/simple-tactics-ai.ts');
const {defaultStateScores, defaultArbiterOptions, allPromptResolvers} =
  engine('simple-bot/simple-bot-definitions.ts');

const manager = CardManager.getInstance();
for (const card of [new QuickBall(), new RegidragoV(), new GrassEnergy()]) {
  if (!manager.isCardDefined(card.fullName)) manager.defineCard(card);
}

/** @param {number} count @returns {any[]} */
const grass = count => Array.from({length: count}, () => new GrassEnergy());
/** @returns {any[]} */
const prizes = () => Array.from({length: 6}, () => {
  const position = new CardList();
  position.cards = grass(1);
  return position;
});
/**
 * Same known 60-card inventory and public state in every world. One extra
 * Regidrago V is either at a secret deck position or a face-down Prize.
 * @param {'deck'|'prize'} zone
 * @param {number} position Zero-based index inside the chosen hidden zone
 * @returns {any}
 */
function fixture(zone, position) {
  assert.ok(zone === 'deck' || zone === 'prize');
  assert.ok(Number.isSafeInteger(position));
  assert.ok(position >= 0 && position < (zone === 'deck' ? 46 : 6));

  const state = new State();
  state.phase = GamePhase.PLAYER_TURN;
  state.turn = 2;
  state.activePlayer = 0;
  state.gameSettings.format = Format.EXPANDED;

  const actor = new Player();
  actor.id = 1;
  actor.name = 'Blind-search actor';
  actor.active.cards = [new RegidragoV()];
  actor.active.pokemonPlayedTurn = 1;
  actor.hand.cards = [new QuickBall(), ...grass(6)];
  actor.deck.cards = grass(46);
  actor.prizes = prizes();
  if (zone === 'deck') actor.deck.cards[position] = new RegidragoV();
  else actor.prizes[position].cards[0] = new RegidragoV();

  const opponent = new Player();
  opponent.id = 2;
  opponent.name = 'Constant opponent';
  opponent.active.cards = [new RegidragoV()];
  opponent.active.pokemonPlayedTurn = 1;
  opponent.hand.cards = grass(7);
  opponent.deck.cards = grass(46);
  opponent.prizes = prizes();
  state.players = [actor, opponent];

  for (const player of state.players) {
    const count = player.hand.cards.length + player.deck.cards.length +
      player.prizes.reduce((sum, slot) => sum + slot.cards.length, 0) +
      player.active.cards.length + player.bench.reduce((sum, slot) => sum + slot.cards.length, 0);
    assert.equal(count, 60, 'The constructed game must conserve exactly 60 cards per player');
  }
  return state;
}

/** @param {any} state @returns {string} */
function publicObservation(state) {
  const actor = state.players[0];
  const opponent = state.players[1];
  return JSON.stringify({
    turn: state.turn, phase: state.phase, activePlayer: state.activePlayer,
    ownHand: actor.hand.cards.map(card => card.fullName),
    ownDeckCount: actor.deck.cards.length,
    ownPrizeCount: actor.getPrizeLeft(),
    ownActive: actor.active.cards.map(card => card.fullName),
    ownBench: actor.bench.map(slot => slot.cards.map(card => card.fullName)),
    opponentHandSize: opponent.hand.cards.length,
    opponentDeckSize: opponent.deck.cards.length,
    opponentActive: opponent.active.cards.map(card => card.fullName),
    opponentPrizeCount: opponent.getPrizeLeft(),
  });
}

/** @param {any} state @returns {string} */
function hiddenInventory(state) {
  const actor = state.players[0];
  return JSON.stringify([...actor.deck.cards,
    ...actor.prizes.flatMap(slot => slot.cards)].map(card => card.fullName).sort());
}

const options = {
  scores: defaultStateScores,
  arbiter: defaultArbiterOptions,
  promptResolvers: allPromptResolvers,
};
const native = new PlayTrainerTactic(options);
const hit = fixture('deck', 0);
const miss = fixture('prize', 0);
assert.equal(publicObservation(hit), publicObservation(miss));
assert.equal(hiddenInventory(hit), hiddenInventory(miss));
assert.equal(hit.players[0].deck.cards[0].fullName, 'Regidrago V SIT');
assert.equal(miss.players[0].prizes[0].cards[0].fullName, 'Regidrago V SIT');

const nativeHit = native.useTactic(hit, hit.players[0]);
const nativeMiss = native.useTactic(miss, miss.players[0]);
console.log('[hidden-prize-search] ' + JSON.stringify({
  pin: pinned,
  item: 'Quick Ball SSH',
  target: 'Regidrago V SIT',
  same_visible_observation: true,
  same_total_hidden_inventory: true,
  target_in_deck: nativeHit?.type || null,
  target_in_prizes: nativeMiss?.type || null,
}));
assert.equal(nativeHit?.type, 'PLAY_CARD_ACTION',
  'Native Item score should select Quick Ball when a Basic target is secretly searchable');
assert.equal(nativeMiss, undefined,
  'Native Item score should hold Quick Ball when the same Basic is secretly Prized');

let deckPlays = 0;
let prizePlays = 0;
for (const zone of ['deck', 'prize']) {
  for (let position = 0; position < (zone === 'deck' ? 46 : 6); position++) {
    const state = fixture(zone, position);
    assert.equal(publicObservation(state), publicObservation(hit));
    assert.equal(hiddenInventory(state), hiddenInventory(hit));
    const action = native.useTactic(state, state.players[0]);
    assert.equal(action?.type === 'PLAY_CARD_ACTION', zone === 'deck',
      'The native choice must track secret Basic location ' + zone + '/' + position);
    if (action) {
      if (zone === 'deck') deckPlays++;
      else prizePlays++;
    }
  }
}
assert.equal(deckPlays, 46);
assert.equal(prizePlays, 0);

// Verify that the leak survives through the complete SimpleTacticsAi decision,
// including its internal action validity simulation.
for (const zone of ['deck', 'prize']) {
  const state = fixture(zone, 0);
  const bot = new SimpleTacticsAi({id: 1, name: 'Native Quick Ball bot'},
    {...options, tactics: [PlayTrainerTactic]}, null);
  const action = bot.decodeNextAction(state);
  assert.equal(action?.type, zone === 'deck' ? 'PLAY_CARD_ACTION' : 'PASS_TURN');
}
console.log('[hidden-prize-search] PASS: 46 unseen deck slots cause Quick Ball play, ' +
  'six face-down Prize slots cause hold; the full native bot reproduces the divergence');
