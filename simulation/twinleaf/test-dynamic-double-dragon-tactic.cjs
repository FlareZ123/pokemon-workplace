'use strict';
/** SFT for opt-in Double Dragon attachment on pinned Twinleaf. */
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=p=>require(path.join(base,p));
const {DynamicDoubleDragonTactic}=require('./dynamic-double-dragon-tactic.cjs');
const {PlayCardAction,SlotType,PlayerType}=load('game/store/actions/play-card-action');
const {Player}=load('game/store/state/player');
const {State}=load('game/store/state/state');
const {RegidragoV}=load('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {DoubleDragonEnergy}=load('sets/07-x-and-y/set-roaring-skies/double-dragon-energy');
const {GrassEnergy}=load('sets/06-black-and-white/set-black-and-white/basic-energies');
function setup(){
  const s=new State(),p=new Player(),q=new Player();
  p.id=1;q.id=2;s.players=[p,q];s.turn=1;p.energyPlayedTurn=-1;
  p.hand.cards=[new DoubleDragonEnergy()];
  return {s,p};
}
function main(){
  const tactic=new DynamicDoubleDragonTactic({});
  const direct=setup();
  direct.p.active.cards=[new RegidragoV()];
  const play=tactic.useTactic(direct.s,direct.p);
  assert.ok(play instanceof PlayCardAction);
  assert.equal(play.handIndex,0);
  assert.deepEqual(play.target,{player:PlayerType.BOTTOM_PLAYER,slot:SlotType.ACTIVE,index:0});
  direct.p.energyPlayedTurn=1;
  assert.equal(tactic.useTactic(direct.s,direct.p),undefined);
  const bench=setup();
  bench.p.active.cards=[new GrassEnergy()];
  bench.p.bench[0].cards=[new RegidragoV()];
  const b=tactic.useTactic(bench.s,bench.p);
  assert.ok(b instanceof PlayCardAction);
  assert.equal(b.target.slot,SlotType.BENCH);
  const absent=setup();
  assert.equal(tactic.useTactic(absent.s,absent.p),undefined);
  console.log('[Double Dragon tactic] PASS: eligible Dragon targeting, bench selection, once-per-turn guard');
}
try{main();}catch(e){console.error('[Double Dragon tactic] FAIL',e);process.exitCode=1;}
