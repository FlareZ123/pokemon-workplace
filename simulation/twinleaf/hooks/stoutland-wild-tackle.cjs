'use strict';
/**
 * Stoutland BCR 122 Wild Tackle: printed self-hit on tails is 20 damage.
 * Pinned upstream implementation resolves only 10. Retain native coin flip
 * and native damage effects while replacing the incorrect magnitude.
 */
const path=require('node:path');
const base=path.resolve(__dirname,'../../../vendor/twinleafgg/ptcg-server/output');
const load=name=>require(path.join(base,name));
const {Stoutland}=load('sets/06-black-and-white/set-boundaries-crossed/stoutland');
const {DealDamageEffect}=load('game/store/effects/attack-effects');
const {WAS_ATTACK_USED,COIN_FLIP_PROMPT}=load('game/store/prefabs/prefabs');
const MARK=Symbol.for('pokemon-research.stoutland-wild-tackle-self-damage');

/** @returns {boolean} True only if newly installed. */
function install(){
  const proto=Stoutland.prototype;
  if(proto[MARK])return false;
  const original=proto.reduceEffect;
  proto.reduceEffect=function(store,state,effect){
    if(!WAS_ATTACK_USED(effect,0,this))return original.call(this,store,state,effect);
    return COIN_FLIP_PROMPT(store,state,effect.player,result=>{
      if(!result){
        const selfDamage=new DealDamageEffect(effect,20);
        selfDamage.target=effect.player.active;
        store.reduceEffect(state,selfDamage);
      }
    });
  };
  Object.defineProperty(proto,MARK,{value:true});
  return true;
}
module.exports={install};
