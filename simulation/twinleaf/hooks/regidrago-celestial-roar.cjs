'use strict';
/**
 * Pinned Twinleaf's Regidrago V (SIT) Celestial Roar filters the discarded
 * top-three cards to BASIC Energy. Printed Celestial Roar attaches all
 * revealed Energy cards, including Special Energy such as Double Dragon.
 * Research-owned runtime correction; no upstream files are modified.
 */
const path=require('node:path');
const engine=path.resolve(__dirname,'../../../vendor/twinleafgg/ptcg-server/output');
const load=name=>require(path.join(engine,name));
const {RegidragoV}=load('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {CardList}=load('game/store/state/card-list');
const {EnergyCard}=load('game/store/card/energy-card');
const {WAS_ATTACK_USED,MOVE_CARDS}=load('game/store/prefabs/prefabs');
const MARK=Symbol.for('pokemon-research.regidrago-celestial-roar-energy-guard');

/** Install the source-pinned Celestial Roar rule correction once.
 * @returns {boolean} Whether this call installed the guard.
 */
function install() {
  const proto=RegidragoV.prototype;
  if(proto[MARK])return false;
  const original=proto.reduceEffect;
  proto.reduceEffect=function(store,state,effect) {
    if(!WAS_ATTACK_USED(effect,0,this))return original.call(this,store,state,effect);
    const player=effect.player;
    const revealed=new CardList();
    state=MOVE_CARDS(store,state,player.deck,revealed,{count:3,sourceCard:this});
    // Every revealed Energy card is attached; every other card is discarded.
    // Iterate a copy because every physical move mutates the source CardList.
    for(const card of [...revealed.cards]) {
      const target=card instanceof EnergyCard?player.active:player.discard;
      state=MOVE_CARDS(store,state,revealed,target,{cards:[card],sourceCard:this});
    }
    return state;
  };
  Object.defineProperty(proto,MARK,{value:true});
  return true;
}
module.exports={install};
