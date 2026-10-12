'use strict';
/** SFT: pinned native Celestial Roar discards Double Dragon incorrectly;
 * the research-only hook attaches all revealed Energy, preserving physical cards.
 */
const assert=require('node:assert/strict');
const path=require('node:path');
const engine=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=name=>require(path.join(engine,name));
const {RegidragoV}=load('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {DoubleDragonEnergy}=load('sets/07-x-and-y/set-roaring-skies/double-dragon-energy');
const {GrassEnergy}=load('sets/06-black-and-white/set-black-and-white/basic-energies');
const {Player}=load('game/store/state/player');
const {State}=load('game/store/state/state');
const {AttackEffect,MoveCardsEffect}=load('game/store/effects/game-effects');
const {install}=require('./hooks/regidrago-celestial-roar.cjs');
const MARK=Symbol.for('pokemon-research.regidrago-celestial-roar-energy-guard');

/** @param {Array<object>} revealed
 * @returns {{player:object,attack:object,store:object,state:object,attacker:object}}
 */
function fixture(revealed) {
  const state=new State(),player=new Player(),opponent=new Player();
  player.id=1;opponent.id=2;state.players=[player,opponent];
  const attacker=new RegidragoV();
  player.active.cards=[attacker];
  player.deck.cards=[...revealed];
  const store={
    prompt(){throw Error('Celestial Roar must resolve without an optional Energy prompt');},
    reduceEffect(s,e){
      assert.ok(e instanceof MoveCardsEffect,'Expected the native MoveCardsEffect');
      const cards=e.cards??e.source.cards.slice(0,e.count??e.source.cards.length);
      e.source.moveCardsTo([...cards],e.destination);
      return s;
    }
  };
  return {player,attack:new AttackEffect(player,opponent,attacker.attacks[0]),
    store,state,attacker};
}
function run() {
  assert.equal(RegidragoV.prototype[MARK],undefined);
  // Baseline pinned engine incorrectly discards the Special Energy entirely.
  const nativeSpecial=new DoubleDragonEnergy();
  const baseline=fixture([nativeSpecial,new RegidragoV(),new RegidragoV()]);
  baseline.attacker.reduceEffect(baseline.store,baseline.state,baseline.attack);
  assert.equal(baseline.player.active.energies.cards.length,0);
  assert.ok(baseline.player.discard.cards.includes(nativeSpecial));
  assert.equal(baseline.player.deck.cards.length,0);

  assert.equal(install(),true);
  assert.equal(install(),false,'Hook installation must be idempotent');
  assert.equal(RegidragoV.prototype[MARK],true);

  const special=new DoubleDragonEnergy(),basic=new GrassEnergy(),filler=new RegidragoV();
  const mixed=fixture([special,basic,filler]);
  mixed.attacker.reduceEffect(mixed.store,mixed.state,mixed.attack);
  assert.deepEqual(mixed.player.active.energies.cards,[special,basic],
    'Both Double Dragon and Grass must attach to the Dragon attacker');
  assert.ok(mixed.player.active.cards.includes(special));
  assert.ok(mixed.player.active.cards.includes(basic));
  assert.deepEqual(mixed.player.discard.cards,[filler]);
  assert.equal(mixed.player.deck.cards.length,0);

  const onlySpecials=[new DoubleDragonEnergy(),new DoubleDragonEnergy(),
    new DoubleDragonEnergy()];
  const specialOnly=fixture(onlySpecials);
  specialOnly.attacker.reduceEffect(specialOnly.store,specialOnly.state,specialOnly.attack);
  assert.deepEqual(specialOnly.player.active.energies.cards,onlySpecials);
  assert.equal(specialOnly.player.discard.cards.length,0);

  const nonEnergy=[new RegidragoV(),new RegidragoV()];
  const noEnergy=fixture(nonEnergy);
  noEnergy.attacker.reduceEffect(noEnergy.store,noEnergy.state,noEnergy.attack);
  assert.deepEqual(noEnergy.player.discard.cards,nonEnergy);
  assert.equal(noEnergy.player.active.energies.cards.length,0);
  assert.equal(noEnergy.player.deck.cards.length,0);

  console.log('[Celestial Roar] Pinned native discarded a revealed Double Dragon Energy');
  console.log('[Celestial Roar] PASS: hook attaches Basic and Special Energy, handles short deck, conserves cards, and is idempotent');
}
try{run();}catch(error){console.error('[Celestial Roar] FAIL',error);process.exitCode=1;}
