'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=p=>require(path.join(base,p));
const {ShadowRiderCalyrexVMAX}=load('sets/09-sword-and-shield/set-chilling-reign/shadow-rider-calyrex-vmax');
const {ShadowRiderCalyrexV}=load('sets/09-sword-and-shield/set-chilling-reign/shadow-rider-calyrex-v');
const {RegidragoV}=load('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {PsychicEnergy}=load('sets/06-black-and-white/set-black-and-white/basic-energies');
const {Player}=load('game/store/state/player');
const {State}=load('game/store/state/state');
const {PokemonCardList}=load('game/store/state/pokemon-card-list');
const {PowerEffect}=load('game/store/effects/game-effects');
const {GameMessage}=load('game/game-message');
const {PlayerType,SlotType}=load('game/store/actions/play-card-action');
const {install}=require('./hooks/shadow-rider-underworld-door.cjs');
function run() {
  const state=new State(),owner=new Player(),other=new Player();
  owner.id=1;other.id=2;state.players=[owner,other];
  owner.hand.cards=[new PsychicEnergy()];
  owner.bench=[new PokemonCardList(),new PokemonCardList()];
  owner.bench[0].cards=[new ShadowRiderCalyrexV()];
  owner.bench[1].cards=[new RegidragoV()];
  const vmax=new ShadowRiderCalyrexVMAX();
  const effect=new PowerEffect(owner,vmax.powers[0],vmax);
  let captured;
  const store={prompt:(s,p)=>{captured=p;return s;}};
  const source={to:{player:PlayerType.BOTTOM_PLAYER,slot:SlotType.BENCH,index:1},index:0};
  const valid={to:{player:PlayerType.BOTTOM_PLAYER,slot:SlotType.BENCH,index:0},index:0};
  vmax.reduceEffect(store,state,effect);
  assert.ok(captured,'Engine must offer an Underworld Door prompt');
  assert.equal(captured.validate(captured.decode([source],state)),true,
    'Pinned baseline unexpectedly already rejects non-Psychic target');
  assert.equal(install(),true,'Install research hook exactly once');
  assert.equal(install(),false,'Repeated hook installation must be idempotent');
  captured=undefined;
  vmax.reduceEffect(store,state,effect);
  assert.ok(captured);
  assert.equal(captured.validate(captured.decode([source],state)),false);
  assert.equal(captured.validate(captured.decode([valid],state)),true);
  assert.ok(captured.options.blockedTo.some(t=>t.index===1));
  // Without any eligible Psychic Bench destination, even announcing the
  // optional Ability would have no legal state-changing effect.
  owner.bench[0].cards=[new RegidragoV()];
  captured=undefined;
  assert.throws(
    ()=>vmax.reduceEffect(store,state,effect),
    error=>error && error.message===GameMessage.CANNOT_USE_POWER,
    'Underworld Door must reject activation with only Dragon Bench targets'
  );
  assert.equal(captured,undefined,'Invalid Ability may not expose a prompt');
  console.log('[Underworld Door] Baseline erroneous target accepted; hook rejects non-Psychic and retains legal target');
  console.log('[Underworld Door] PASS: pinned engine behavior and research-side remedy checked');
}
try {run();} catch(error) {console.error('[Underworld Door] FAIL',error);process.exitCode=1;}
