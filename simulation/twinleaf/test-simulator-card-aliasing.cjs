'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const engine=p=>require(path.join(ROOT,p));
const {Simulator}=engine('game/bots/simulator');
const {State,GamePhase}=engine('game/store/state/state');
const {Player}=engine('game/store/state/player');
const {PokemonCardList}=engine('game/store/state/pokemon-card-list');
const {CardList}=engine('game/store/state/card-list');
const {PlayCardAction,PlayerType,SlotType}=engine('game/store/actions/play-card-action');
const {ResolvePromptAction}=engine('game/store/actions/resolve-prompt-action');
const {ChoosePokemonPrompt}=engine('game/store/prompts/choose-pokemon-prompt');
const {deepClone}=engine('utils/utils');
// Initialize core game modules before card classes due native circular-import overrides.
const {Switch}=engine('sets/10-scarlet-and-violet/set-scarlet-and-violet/switch');
const {RegidragoV}=engine('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');

/** Real native board for a legal Switch SVI action during a player turn. */
function scenario() {
  const state=new State();
  state.phase=GamePhase.PLAYER_TURN;
  state.turn=4;
  state.activePlayer=0;
  const players=[new Player(),new Player()];
  players.forEach((player,index)=>{
    player.id=index+1;
    player.name='Aliasing audit '+player.id;
    const active=new RegidragoV();
    active.id=index+100;
    player.active.cards.push(active);
    player.active.hp=active.hp;
    player.deck.cards.push(new RegidragoV());
    player.prizes=Array.from({length:6},()=>{
      const prize=new CardList();
      prize.cards.push(new RegidragoV());
      return prize;
    });
  });
  const benchCard=new RegidragoV();
  benchCard.id=200;
  const bench=new PokemonCardList();
  bench.cards.push(benchCard);
  bench.hp=benchCard.hp;
  players[0].bench.push(bench);
  players[0].hand.cards.push(new Switch());
  state.players=players;
  return state;
}

/** @param {any} nativeState */
function simulateSwitch(nativeState) {
  const sim=new Simulator(nativeState);
  sim.dispatch(new PlayCardAction(1,0,{player:PlayerType.ANY,slot:SlotType.BOARD,index:0}));
  const prompt=sim.store.state.prompts.find(p=>p.result===undefined);
  assert.ok(prompt instanceof ChoosePokemonPrompt,
    'Expected native Switch target prompt, got '+(prompt?.constructor.name??'none'));
  sim.dispatch(new ResolvePromptAction(prompt.id,[sim.store.state.players[0].bench[0]]));
  assert.ok(sim.store.state.prompts.every(p=>p.result!==undefined));
  assert.equal(sim.store.state.players[0].active.getPokemonCard().id,200);
  return sim;
}

function main() {
  const live=scenario();
  const liveCard=live.players[0].bench[0].getPokemonCard();
  assert.equal(liveCard.movedToActiveThisTurn,false);
  const simulated=simulateSwitch(live);
  assert.equal(live.players[0].active.getPokemonCard().id,100,
    'The live board position must remain unchanged by a simulated Switch');
  assert.strictEqual(simulated.store.state.players[0].active.getPokemonCard(),liveCard,
    'Pinned Simulator directly aliases the live Pokemon Card object');
  assert.equal(liveCard.movedToActiveThisTurn,true,
    'The simulated Switch mutated live Card metadata despite unchanged live board');

  const safeLive=scenario();
  const safeCard=safeLive.players[0].bench[0].getPokemonCard();
  const detached=deepClone(safeLive,[]);
  assert.notStrictEqual(detached.players[0].bench[0].getPokemonCard(),safeCard,
    'Full preclone must detach card identity before native Simulator copies it');
  const safeSim=simulateSwitch(detached);
  assert.equal(safeCard.movedToActiveThisTurn,false,
    'A precloned counterfactual Switch must preserve live Card metadata');
  assert.equal(safeSim.store.state.players[0].active.getPokemonCard().movedToActiveThisTurn,true);
  assert.equal(safeLive.players[0].active.getPokemonCard().id,100);
  console.log('[sim-card-alias] '+JSON.stringify({
    engine_pin:'3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    source_card:'Switch SVI 194',pokemon:'Regidrago V SIT 135',
    native_live_board_unchanged:true,
    native_live_card_flag_polluted:liveCard.movedToActiveThisTurn,
    fully_precloned_live_card_flag_polluted:safeCard.movedToActiveThisTurn,
    cloned_simulation_active_id:safeSim.store.state.players[0].active.getPokemonCard().id
  }));
  console.log('[sim-card-alias] PASS: pinned card identity aliasing is reproducible, full-state preclone isolates this fixture');
}
if(require.main===module)main();
module.exports={scenario,simulateSwitch,main};
