'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const childProcess = require('node:child_process');
const vendor = path.resolve(__dirname, '../../vendor/twinleafgg');
const pinned = '3348ebdc898f175a2ed8f999133cd13d1afd01f5';
assert.equal(childProcess.execFileSync('git', ['rev-parse', 'HEAD'],
  {cwd: vendor, encoding: 'utf8'}).trim(), pinned);
const server = path.join(vendor, 'ptcg-server');
process.env.TS_NODE_PROJECT = path.join(server, 'tsconfig.json');
require(require.resolve('ts-node/register/transpile-only', {paths: [server]}));
/** @param {string} file @returns {any} */
const engine = file => require(path.join(server, 'src', file));
const {CardManager} = engine('game/cards/card-manager.ts');
const {Store} = engine('game/store/store.ts');
const {makeSupporterSelectionGuard} = require('./supporter-selection-guard.cjs');
const {State, GamePhase} = engine('game/store/state/state.ts');
const {Player} = engine('game/store/state/player.ts');
const {CardList} = engine('game/store/state/card-list.ts');
const {PokemonCardList} = engine('game/store/state/pokemon-card-list.ts');
const {Format} = engine('game/store/card/card-types.ts');
const {PlaySupporterTactic} = engine('simple-bot/simple-tactics/play-supporter-tactic.ts');
const {defaultStateScores, defaultArbiterOptions, allPromptResolvers} =
  engine('simple-bot/simple-bot-definitions.ts');
const {BossOrders} = engine('sets/10-scarlet-and-violet/set-paldea-evolved/boss-orders.ts');
const {RegidragoV} = engine('sets/09-sword-and-shield/set-silver-tempest/regidrago-v.ts');
const {GrassEnergy} = engine('sets/06-black-and-white/set-black-and-white/basic-energies.ts');

/** @param {number} size @returns {any[]} */
const grass = size => Array.from({length: size}, () => new GrassEnergy());
/** @returns {any[]} */
const prizes = () => Array.from({length: 6}, () => {
  const slot = new CardList();
  slot.cards = grass(1);
  return slot;
});
function makeState() {
  const manager = CardManager.getInstance();
  for(const card of [new BossOrders(),new RegidragoV(),new GrassEnergy()]) {
    if(!manager.isCardDefined(card.fullName)) manager.defineCard(card);
  }
  const state = new State();
  state.phase = GamePhase.PLAYER_TURN;
  state.turn = 2;
  state.activePlayer = 0;
  state.gameSettings.format = Format.EXPANDED;
  const me = new Player();
  me.id = 1;
  me.name = 'Actor';
  me.active.cards=[new RegidragoV()];
  me.active.pokemonPlayedTurn = 1;
  me.hand.cards=[new BossOrders(),...grass(6)];
  me.deck.cards=grass(46);
  me.prizes=prizes();
  const rival = new Player();
  rival.id = 2;
  rival.name = 'Opposing board';
  rival.active.cards=[new RegidragoV()];
  rival.active.pokemonPlayedTurn=1;
  const bench = new PokemonCardList();
  bench.cards=[new RegidragoV()];
  bench.pokemonPlayedTurn=1;
  rival.bench=[bench];
  rival.hand.cards=grass(7);
  rival.deck.cards=grass(45);
  rival.prizes=prizes();
  state.players=[me,rival];
  for(const player of state.players) {
    const total=player.hand.cards.length+player.deck.cards.length+
      player.prizes.reduce((sum,p)=>sum+p.cards.length,0)+player.active.cards.length+
      player.bench.reduce((sum,p)=>sum+p.cards.length,0);
    assert.equal(total,60,'Every participant must have 60 physical cards');
  }
  return state;
}
const opts={
  scores: defaultStateScores,
  promptResolvers: allPromptResolvers,
  arbiter: defaultArbiterOptions
};
const state=makeState();
const actor=state.players[0];
assert.equal(actor.supporterTurn,0);
assert.equal(actor.hand.cards[0].name,"Boss's Orders");
assert.equal(state.players[1].bench[0].cards[0].name,'Regidrago V');
const tactic=new PlaySupporterTactic(opts);
const action=tactic.useTactic(state,actor);
assert.equal(action?.type,'PLAY_CARD_ACTION',
  'Native tactic should select the otherwise legal Boss Orders from hand');
const mutatedCounter=actor.supporterTurn;
const store=new Store({onStateChange:()=>{}});
store.state=state;
let dispatchError;
try{store.dispatch(action);}
catch(error){dispatchError=error;}
console.log('[supporter-mutation] '+JSON.stringify({
  pin:pinned,turn:state.turn,selected_action:action.type,
  counter_before:0,counter_after_native_selection:mutatedCounter,
  rejected_live_action:dispatchError ? {
    type: dispatchError.constructor?.name || typeof dispatchError,
    code: dispatchError.code || null,
    message: dispatchError.message || null,
    keys: Object.keys(dispatchError)
  } : null
}));
assert.equal(mutatedCounter,state.turn,
  'Pinned PlaySupporterTactic must reproduce premature live counter mutation');
assert.equal(dispatchError?.message, 'SUPPORTER_ALREADY_PLAYED',
  'Native counter mutation must produce the engine Supporter-already-played error');
// A throwing Store dispatch need not roll back intermediate card movements,
// so retry the same policy in an independent, otherwise identical game state.
const recovered=makeState();
const recoveredActor=recovered.players[0];
const guard=makeSupporterSelectionGuard();
const recoveredAction=guard.decode({
  decodeNextAction: state => new PlaySupporterTactic(opts).useTactic(state,state.players[0])
},recovered,recoveredActor.id);
assert.equal(recoveredAction?.type, action.type);
assert.equal(recoveredAction?.handIndex, action.handIndex);
assert.equal(recoveredActor.supporterTurn, 0,
  'Policy guard must restore before Store.dispatch');
assert.equal(guard.snapshot().restored_live_supporter_counters, 1);
const recoveredStore=new Store({onStateChange:()=>{}});
recoveredStore.state=recovered;
recoveredStore.dispatch(recoveredAction);
assert.ok(recoveredActor.supporterTurn > 0,
  'Successfully played Supporter must increment actual usage');
assert.equal(recoveredActor.hand.cards.some(card=>card.name==="Boss's Orders"),false,
  'Successful dispatch must move played Supporter out of hand');
const exceptionState=makeState();
assert.throws(()=>guard.decode({
  decodeNextAction: state => {
    state.players[0].supporterTurn=state.turn;
    throw new Error('policy evaluation failed');
  }
},exceptionState,1),/policy evaluation failed/);
assert.equal(exceptionState.players[0].supporterTurn,0,
  'Even failed policy evaluation must restore native live counter');
assert.equal(guard.snapshot().restored_live_supporter_counters,2);
console.log('[supporter-mutation] PASS: guarded Supporter action dispatches legally and restores counter even after policy exceptions');
