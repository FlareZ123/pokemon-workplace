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
const {TrainersMail} = engine('sets/07-x-and-y/set-roaring-skies/trainers-mail.ts');
const {BossOrders} = engine('sets/10-scarlet-and-violet/set-paldea-evolved/boss-orders.ts');
const {RegidragoV} = engine('sets/09-sword-and-shield/set-silver-tempest/regidrago-v.ts');
const {GrassEnergy} = engine('sets/06-black-and-white/set-black-and-white/basic-energies.ts');

/**
 * Construct two physically possible engine states with identical known
 * information and deck multiset. The only change is the secret position of
 * Boss's Orders inside the player's deck.
 * @param {number} supporterPosition Zero-based, 0 through 45
 * @param {'pokegear'|'mail'} [searchItem]
 * @returns {any}
 */
function fixture(supporterPosition, searchItem = 'pokegear') {
  assert.ok(Number.isSafeInteger(supporterPosition) && supporterPosition >= 0 && supporterPosition < 46);
  const manager = CardManager.getInstance();
  for (const card of [new Pokegear30(), new TrainersMail(), new BossOrders(), new RegidragoV(), new GrassEnergy()]) {
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
  player.hand.cards = [searchItem === 'mail' ? new TrainersMail() : new Pokegear30(),
    ...Array.from({length: 6}, () => new GrassEnergy())];
  player.active.cards = [new RegidragoV()];
  player.active.pokemonPlayedTurn = 1;
  player.deck.cards = Array.from({length: 45}, () => new GrassEnergy());
  const supporter = new BossOrders();
  player.deck.cards.splice(supporterPosition, 0, supporter);
  player.prizes = Array.from({length: 6}, () => {
    const slot = new (engine('game/store/state/card-list.ts').CardList)();
    slot.cards.push(new GrassEnergy());
    return slot;
  });

  const opponent = new Player();
  opponent.id = 2;
  opponent.name = 'Same opponent';
  opponent.active.cards = [new RegidragoV()];
  opponent.hand.cards = Array.from({length: 7}, () => new GrassEnergy());
  opponent.deck.cards = Array.from({length: 46}, () => new GrassEnergy());
  opponent.active.pokemonPlayedTurn = 1;
  opponent.prizes = Array.from({length: 6}, () => {
    const slot = new (engine('game/store/state/card-list.ts').CardList)();
    slot.cards.push(new GrassEnergy());
    return slot;
  });
  state.players = [player, opponent];
  for (const participant of state.players) {
    const count = participant.hand.cards.length + participant.deck.cards.length +
      participant.discard.cards.length + participant.active.cards.length +
      participant.prizes.reduce((sum, slot) => sum + slot.cards.length, 0);
    assert.equal(count, 60, 'Each constructed game state must conserve 60 physical cards');
  }
  return state;
}

const settings = {
  scores: defaultStateScores,
  arbiter: defaultArbiterOptions,
  promptResolvers: allPromptResolvers,
};
const tactic = new PlayTrainerTactic(settings);
const hit = fixture(0);
const miss = fixture(10);
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
const mailHit = fixture(0, 'mail');
const mailMiss = fixture(10, 'mail');
assert.equal(visibleSnapshot(mailHit), visibleSnapshot(mailMiss));
assert.deepEqual(deckInventory(mailHit), deckInventory(mailMiss));
const mailHitAction = tactic.useTactic(mailHit, mailHit.players[0]);
const mailMissAction = tactic.useTactic(mailMiss, mailMiss.players[0]);
console.log('[hidden-order-audit] ' + JSON.stringify({
  print: 'Trainers Mail ROS 92',
  paper_deck: 'Aichi 2026 fifth-place Mew VMAX / Genesect V',
  same_observation: true,
  same_deck_multiset: true,
  hit_action: mailHitAction ? mailHitAction.type : null,
  miss_action: mailMissAction ? mailMissAction.type : null,
}));
assert.equal(mailHitAction?.type, 'PLAY_CARD_ACTION',
  'Native tactic should play Trainers Mail when one of its secret top four is a Trainer');
assert.equal(mailMissAction, undefined,
  'Native tactic should decline Trainers Mail after seeing the hidden top-four whiff');
for (const {item, searchItem, window} of [
  {item: 'Pokegear SVI', searchItem: 'pokegear', window: 7},
  {item: 'Trainers Mail ROS', searchItem: 'mail', window: 4},
]) {
  let playedPositions = 0;
  for (let position = 0; position < 46; position++) {
    const world = fixture(position, searchItem);
    const action = tactic.useTactic(world, world.players[0]);
    assert.equal(action?.type === 'PLAY_CARD_ACTION', position < window,
      item + ' native choice differed from exact secret search window at position ' + position);
    if (action) playedPositions++;
  }
  assert.equal(playedPositions, window);
  console.log('[hidden-order-audit] ' + JSON.stringify({
    item, full_hidden_positions: 46, played_positions: playedPositions,
    held_on_hidden_miss: 46 - playedPositions,
    exact_play_probability_uniform_shuffle: window + '/46'
  }));
}
console.log('[hidden-order-audit] PASS: all 92 private deck placements mapped to the native oracle choices');
