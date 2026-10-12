'use strict';
/** SFT: exercise Celestial Roar's Special Energy attachment through the
 * actual pinned Twinleaf Store.reduceEffect and card type/energy engine.
 */
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=name=>require(path.join(base,name));
const {Store}=load('game/store/store');
const {Player}=load('game/store/state/player');
const {RegidragoV}=load('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {DoubleDragonEnergy}=load('sets/07-x-and-y/set-roaring-skies/double-dragon-energy');
const {GrassEnergy}=load('sets/06-black-and-white/set-black-and-white/basic-energies');
const {AttackEffect}=load('game/store/effects/game-effects');
const {CheckProvidedEnergyEffect}=load('game/store/effects/check-effects');
const {CardManager}=load('game/cards/card-manager');
const {CardType}=load('game/store/card/card-types');
const {install}=require('./hooks/regidrago-celestial-roar.cjs');

function run() {
  const regidrago=new RegidragoV();
  const special=new DoubleDragonEnergy(),basic=new GrassEnergy(),other=new RegidragoV();
  const manager=CardManager.getInstance();
  for(const card of [regidrago,special,basic]){
    if(!manager.isCardDefined(card.fullName))manager.defineCard(card);
  }
  assert.equal(install(),true);
  const store=new Store({onStateChange:()=>{}});
  const player=new Player(),opponent=new Player();
  player.id=1;opponent.id=2;
  store.state.players=[player,opponent];
  player.active.cards=[regidrago];
  player.deck.cards=[special,basic,other];

  const attack=new AttackEffect(player,opponent,regidrago.attacks[0]);
  regidrago.reduceEffect(store,store.state,attack);

  assert.deepEqual(player.active.energies.cards,[special,basic],
    'Live Store must attach both Special and Basic cards to Regidrago V');
  assert.deepEqual(player.discard.cards,[other],
    'Live Store must discard only the non-Energy reveal');
  assert.equal(player.deck.cards.length,0);
  const energy=new CheckProvidedEnergyEffect(player,player.active);
  store.reduceEffect(store.state,energy);
  const double=energy.energyMap.find(x=>x.card===special);
  assert.ok(double,'Double Dragon must appear in native provided-Energy map');
  assert.deepEqual(double.provides,[CardType.ANY,CardType.ANY]);
  console.log('[Celestial Roar Store] PASS: native reducer attached Double Dragon + Grass and exposed two ANY Energy units');
}
try{run();}catch(error){console.error('[Celestial Roar Store] FAIL',error);process.exitCode=1;}
