'use strict';
/**
 * Mega Absol ex MEG 86 Terminal Period is a conditional direct Knock Out,
 * not 999 damage. Route it through the engine's preventable attack-effect
 * and Knock Out/prize resolution instead of mutating damage counters.
 * Pinned Twinleaf: 3348ebdc898f175a2ed8f999133cd13d1afd01f5.
 */
const path=require('node:path');
const base=path.resolve(__dirname,'../../../vendor/twinleafgg/ptcg-server/output');
const load=name=>require(path.join(base,name));
const {MegaAbsolex}=load('sets/11-mega-evolution/set-mega-evolution/mega-absol-ex');
const {KnockOutOpponentEffect}=load('game/store/effects/attack-effects');
const {WAS_ATTACK_USED}=load('game/store/prefabs/prefabs');
const MARK=Symbol.for('pokemon-research.mega-absol-terminal-period-direct-ko');

/** @returns {boolean} Whether a previously uninstalled correction was added. */
function install(){
  const proto=MegaAbsolex.prototype;
  if(proto[MARK])return false;
  const original=proto.reduceEffect;
  proto.reduceEffect=function(store,state,effect){
    if(!WAS_ATTACK_USED(effect,0,this))
      return original.call(this,store,state,effect);
    if(effect.opponent.active.damage!==60)return state;
    return store.reduceEffect(state,new KnockOutOpponentEffect(effect));
  };
  Object.defineProperty(proto,MARK,{value:true});
  return true;
}
module.exports={install};
