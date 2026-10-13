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
const {MegaAbsolex}=load('sets/11-mega-evolution/set-mega-evolution/mega-absol-ex');
const {GrassEnergy,FireEnergy}=load('sets/06-black-and-white/set-black-and-white/basic-energies');
const {ShadowRiderCalyrexVMAX}=load('sets/09-sword-and-shield/set-chilling-reign/shadow-rider-calyrex-vmax');
const {TrevenantDusknoirGX}=load('sets/08-sun-and-moon/set-sun-and-moon-promos/trevenant-dusknoir-gx');
const {runOne,ensureResearchEngineHooks}=require('./tournament-bounded-match.cjs');
const {MARKER:randomOneKey,buildPinnedSingleCardSpecs}=
  require('./random-hand-single-card-hook.cjs');
const randomOneSpecs=buildPinnedSingleCardSpecs(load);
const hookKey=Symbol.for('pokemon-research.shadow-rider-underworld-door-guard');
const celestialKey=Symbol.for('pokemon-research.regidrago-celestial-roar-energy-guard');
const stoutlandKey=Symbol.for('pokemon-research.stoutland-wild-tackle-self-damage');
const absolKey=Symbol.for('pokemon-research.mega-absol-terminal-period-direct-ko');
const nightWatchKey=Symbol.for('pokemon-workplace.twinleaf.night-watch-random-v1');
const hookLabels=['shadow_rider_underworld_door_guard_v1','regidrago_celestial_roar_any_energy_v1',
  'stoutland_wild_tackle_self20_v1','mega_absol_terminal_period_direct_ko_v1',
  'night_watch_uniform_discard_v1',
  'random_hand_ten_single_card_prints_v1'];
function run() {
  for(const spec of randomOneSpecs) {
    assert.equal(spec.CardClass.prototype.reduceEffect[randomOneKey],undefined,
      'Hooks must not be installed just by importing the runner');
  }
  assert.equal(TrevenantDusknoirGX.prototype.reduceEffect[nightWatchKey],undefined);
  assert.equal(Stoutland.prototype[stoutlandKey],undefined);
  assert.equal(MegaAbsolex.prototype[absolKey],undefined);
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
  assert.deepEqual(trace.policy_hooks,['supporter_prevalidation_and_dispatch_counter_restore_v2']);
  assert.ok(Number.isSafeInteger(trace.policy_repair_stats.restored_live_supporter_counters));
  assert.equal(typeof TrevenantDusknoirGX.prototype.reduceEffect[nightWatchKey],'function',
    'Live match did not install the Night Watch random-pair interception');
  for(const spec of randomOneSpecs) {
    assert.equal(typeof spec.CardClass.prototype.reduceEffect[randomOneKey],'function',
      'Live match missed source guard for '+spec.label);
  }
  assert.equal(MegaAbsolex.prototype[absolKey],true,
    'Live match failed to install Mega Absol direct Knock Out guard');
  assert.equal(Stoutland.prototype[stoutlandKey],true,
    'Live match path failed to install the Stoutland self-damage guard');
  assert.equal(RegidragoV.prototype[celestialKey],true,
    'Live match path failed to install the Celestial Roar guard');
  assert.equal(ShadowRiderCalyrexVMAX.prototype[hookKey],true,
    'Live match path failed to install the Underworld Door guard');
  assert.deepEqual(ensureResearchEngineHooks(),trace.engine_hooks,
    'Repeated installation must leave the hook set stable');
  assert.ok(trace.actions>0,'Fixture did not execute a real engine action');
  console.log('[tournament-engine-hooks] PASS: live match installs verified engine hooks for eleven randomized-hand prints and reports versions');
}
try{run();}catch(error){console.error('[tournament-engine-hooks] FAIL',error);process.exitCode=1;}
