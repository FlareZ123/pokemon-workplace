'use strict';
/** Single runnable pinned-source regression for runner-up Vileplume's Stoutland. */
const assert=require('node:assert/strict');
const path=require('node:path');
const root=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=name=>require(path.join(root,name));
const {Stoutland}=load('sets/06-black-and-white/set-boundaries-crossed/stoutland');
const {Player}=load('game/store/state/player');
const {State}=load('game/store/state/state');
const {AttackEffect}=load('game/store/effects/game-effects');
const {DealDamageEffect}=load('game/store/effects/attack-effects');
const {CoinFlipEffect}=load('game/store/effects/play-card-effects');
const {install}=require('./hooks/stoutland-wild-tackle.cjs');
const MARK=Symbol.for('pokemon-research.stoutland-wild-tackle-self-damage');

/** @param {boolean} heads
 * @returns {{dealt:number[],target:object,attacker:object}}
 */
function attack(heads){
  const state=new State(),owner=new Player(),opponent=new Player();
  owner.id=1;opponent.id=2;state.players=[owner,opponent];
  const attacker=new Stoutland();
  owner.active.cards=[attacker];
  const dealt=[];
  const store={reduceEffect(s,e){
    if(e instanceof CoinFlipEffect){e.callback(heads);return s;}
    assert.ok(e instanceof DealDamageEffect,'Unrecognized effect in Wild Tackle');
    assert.equal(e.target,owner.active,'Self-damage must target the actual attacker');
    dealt.push(e.damage);
    return s;
  }};
  attacker.reduceEffect(store,state,new AttackEffect(owner,opponent,attacker.attacks[0]));
  return {dealt,target:owner.active,attacker};
}
function run(){
  assert.equal(Stoutland.prototype[MARK],undefined);
  assert.deepEqual(attack(false).dealt,[10],
    'Pinned engine baseline should reproduce its wrong 10 self-damage on tails');
  assert.equal(install(),true);
  assert.equal(install(),false);
  assert.equal(Stoutland.prototype[MARK],true);
  assert.deepEqual(attack(false).dealt,[20],
    'Source Stoutland BCR 122 Wild Tackle demands 20 self-damage on tails');
  assert.deepEqual(attack(true).dealt,[],
    'On heads there is no self-damage effect');
  console.log('[Stoutland Wild Tackle] PASS: baseline 10 incorrect, research hook tails 20, heads 0, one installation');
}
try{run();}catch(error){console.error('[Stoutland Wild Tackle] FAIL',error);process.exitCode=1;}
