'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const childProcess = require('node:child_process');

const vendor = path.resolve(__dirname, '../../vendor/twinleafgg');
const pinned = '3348ebdc898f175a2ed8f999133cd13d1afd01f5';
const revision = childProcess.execFileSync('git', ['rev-parse', 'HEAD'], {
  cwd: vendor, encoding: 'utf8'
}).trim();
assert.equal(revision, pinned, 'Inspect a new Twinleaf pin before reusing this audit');
const server = path.join(vendor, 'ptcg-server');
process.env.TS_NODE_PROJECT = path.join(server, 'tsconfig.json');
require(require.resolve('ts-node/register/transpile-only', { paths: [server] }));
/** @param {string} name @returns {any} */
const engine = name => require(path.join(server, 'src', name));
const {CardManager} = engine('game/cards/card-manager.ts');
const {State, GamePhase} = engine('game/store/state/state.ts');
const {Player} = engine('game/store/state/player.ts');
const {Format} = engine('game/store/card/card-types.ts');
const {PlayTrainerTactic} = engine('simple-bot/simple-tactics/play-trainer-tactic.ts');
const {defaultStateScores, defaultArbiterOptions, allPromptResolvers} =
  engine('simple-bot/simple-bot-definitions.ts');
const {Pokegear30} = engine('sets/10-scarlet-and-violet/set-scarlet-and-violet/pokegear-30.ts');
const {BossOrders} = engine('sets/10-scarlet-and-violet/set-paldea-evolved/boss-orders.ts');
const {RegidragoV} = engine('sets/09-sword-and-shield/set-silver-tempest/regidrago-v.ts');
const {GrassEnergy} = engine('sets/06-black-and-white/set-black-and-white/basic-energies.ts');

/**
 * Construct two physically possible engine states with identical known
 * information and deck multiset. The only change is the secret position of
 * Boss's Orders inside the player's deck.
 * @param {boolean} supporterInTopSeven
 * @returns {any}
 */
function fixture(supporterInTopSeven) {
  const manager = CardManager.getInstance();
  for (const card of [new Pokegear30(), new BossOrders(), new RegidragoV(), new GrassEnergy()]) {
    if (!manager.isCardDefined(card.fullName)) manager.defineCard(card);
  }

  const state = new State();
  state.phase = GamePhase.PLAYER_TURN;
  state.turn = 2;
  state.activePlayer = 0;
  state.gameSettings.format = Format.EXPANDED;
  const player = new Player();
  player.id = 1;
  player.name = 'Decision player';
  player.hand.cards = [new Pokegear30()];
  player.active.cards = [new RegidragoV()];
  player.active.pokemonPlayedTurn = 1;
  player.deck.cards = Array.from({length: 44}, () => new GrassEnergy());
  const supporter = new BossOrders();
  player.deck.cards.splice(supporterInTopSeven ? 0 : 10, 0, supporter);
  player.prizes = Array.from({length: 6}, () => {
    const slot = new (engine('game/store/state/card-list.ts').CardList)();
    slot.cards.push(new GrassEnergy());
    return slot;
  });

  const opponent = new Player();
  opponent.id = 2;
  opponent.name = 'Same opponent';
  opponent.active.cards = [new RegidragoV()];
  opponent.active.pokemonPlayedTurn = 1;
  opponent.prizes = Array.from({length: 6}, () => {
    const slot = new (engine('game/store/state/card-list.ts').CardList)();
    slot.cards.push(new GrassEnergy());
    return slot;
  });
  state.players = [player, opponent];
  return state;
}

const settings = {
  scores: defaultStateScores,
  arbiter: defaultArbiterOptions,
  promptResolvers: allPromptResolvers,
};
const tactic = new PlayTrainerTactic(settings);
const hit = fixture(true);
const miss = fixture(false);
const visibleSnapshot = state => JSON.stringify({
  turn: state.turn,
  active: state.activePlayer,
  ownHand: state.players[0].hand.cards.map(card => card.fullName),
  ownDeckSize: state.players[0].deck.cards.length,
  ownActive: state.players[0].active.cards.map(card => card.fullName),
  opponentHandSize: state.players[1].hand.cards.length,
  opponentActive: state.players[1].active.cards.map(card => card.fullName),
  ownPrizesLeft: state.players[0].getPrizeLeft(),
  opponentPrizesLeft: state.players[1].getPrizeLeft(),
});
assert.equal(visibleSnapshot(hit), visibleSnapshot(miss),
  'Comparison must preserve all advertised public information');
const deckInventory = state => state.players[0].deck.cards.map(card => card.fullName).sort();
assert.deepEqual(deckInventory(hit), deckInventory(miss),
  'Both branches must have exactly the same actual remaining deck multiset');
assert.equal(hit.players[0].deck.cards[0].name, "Boss's Orders");
assert.equal(miss.players[0].deck.cards[10].name, "Boss's Orders");
const hitAction = tactic.useTactic(hit, hit.players[0]);
const missAction = tactic.useTactic(miss, miss.players[0]);
console.log('[hidden-order-audit] ' + JSON.stringify({
  pinned,
  same_observation: true,
  same_deck_multiset: true,
  hit_action: hitAction ? hitAction.type : null,
  miss_action: missAction ? missAction.type : null,
}));
assert.equal(hitAction?.type, 'PLAY_CARD_ACTION',
  'Native tactic should prefer Pokégear when the hidden top seven contain a Supporter');
assert.equal(missAction, undefined,
  'Native tactic should decline Pokégear after secretly peeking at a seven-card whiff');
console.log('[hidden-order-audit] PASS: native Item decision depends on unrevealed deck order');
