'use strict';
/**
 * SFT: a real bounded-match invocation must install the existing rules hook.
 * Uses legal-length engine fixture decks, not competitive research decks.
 */
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=name=>require(path.join(base,name));
const {CardManager}=load('game/cards/card-manager');
const {RegidragoV}=load('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {Stoutland}=load('sets/06-black-and-white/set-boundaries-crossed/stoutland');
const {GrassEnergy,FireEnergy}=load('sets/06-black-and-white/set-black-and-white/basic-energies');
const {ShadowRiderCalyrexVMAX}=load('sets/09-sword-and-shield/set-chilling-reign/shadow-rider-calyrex-vmax');
const {runOne,ensureResearchEngineHooks}=require('./tournament-bounded-match.cjs');
const hookKey=Symbol.for('pokemon-research.shadow-rider-underworld-door-guard');
const celestialKey=Symbol.for('pokemon-research.regidrago-celestial-roar-energy-guard');
const stoutlandKey=Symbol.for('pokemon-research.stoutland-wild-tackle-self-damage');
const hookLabels=['shadow_rider_underworld_door_guard_v1','regidrago_celestial_roar_any_energy_v1',
  'stoutland_wild_tackle_self20_v1'];
function run() {
  assert.equal(Stoutland.prototype[stoutlandKey],undefined);
  assert.equal(RegidragoV.prototype[celestialKey],undefined);
  assert.equal(ShadowRiderCalyrexVMAX.prototype[hookKey],undefined,
    'No hook should have been installed just by loading the runner');
  const manager=CardManager.getInstance();
  for(const card of [new RegidragoV(),new GrassEnergy(),new FireEnergy()]) {
    if(!manager.isCardDefined(card.fullName))manager.defineCard(card);
  }
  const deck=[...Array(4).fill('Regidrago V SIT'),
    ...Array(28).fill('Grass Energy BLW'),
    ...Array(28).fill('Fire Energy BLW')];
  assert.equal(deck.length,60);
  const trace=runOne(deck,deck,20261012,2,5000);
  assert.deepEqual(trace.engine_hooks,hookLabels);
  assert.equal(Stoutland.prototype[stoutlandKey],true,
    'Live match path failed to install the Stoutland self-damage guard');
  assert.equal(RegidragoV.prototype[celestialKey],true,
    'Live match path failed to install the Celestial Roar guard');
  assert.equal(ShadowRiderCalyrexVMAX.prototype[hookKey],true,
    'Live match path failed to install the Underworld Door guard');
  assert.deepEqual(ensureResearchEngineHooks(),trace.engine_hooks,
    'Repeated installation must leave the hook set stable');
  assert.ok(trace.actions>0,'Fixture did not execute a real engine action');
  console.log('[tournament-engine-hooks] PASS: live match installs verified hook and reports its version');
}
try{run();}catch(error){console.error('[tournament-engine-hooks] FAIL',error);process.exitCode=1;}
