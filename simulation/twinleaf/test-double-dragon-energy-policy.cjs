'use strict';
/** Pinned SimpleTacticsAi's static EnergyScore misses Double Dragon's dynamic Energy. */
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=p=>require(path.join(base,p));
const {AttachEnergyTactic}=load('simple-bot/simple-tactics/attach-energy-tactic');
const {defaultStateScores}=load('simple-bot/simple-bot-definitions');
const {Player}=load('game/store/state/player');
const {State}=load('game/store/state/state');
const {RegidragoV}=load('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {DoubleDragonEnergy}=load('sets/07-x-and-y/set-roaring-skies/double-dragon-energy');
const {GrassEnergy}=load('sets/06-black-and-white/set-black-and-white/basic-energies');
/** @param {object} energy */
function setup(energy){
  const state=new State(),player=new Player(),other=new Player();
  player.id=1;other.id=2;state.players=[player,other];state.turn=1;
  player.energyPlayedTurn=-1;
  player.active.cards=[new RegidragoV()];
  player.hand.cards=[energy];
  return {state,player};
}
function main(){
  const tactic=new AttachEnergyTactic({scores:defaultStateScores});
  const dynamic=new DoubleDragonEnergy();
  assert.deepEqual(dynamic.provides,[]);
  const d=setup(dynamic);
  assert.equal(tactic.useTactic(d.state,d.player),undefined,
    'Native tactic cannot value a legal Dragon target for Double Dragon Energy');
  const b=setup(new GrassEnergy());
  assert.ok(tactic.useTactic(b.state,b.player),
    'Control: basic Grass is valued as energy for Regidrago');
  console.log('[Double Dragon policy] PASS: native dynamic-special-energy blindness reproduced');
}
try{main();}catch(e){console.error('[Double Dragon policy] FAIL',e);process.exitCode=1;}
