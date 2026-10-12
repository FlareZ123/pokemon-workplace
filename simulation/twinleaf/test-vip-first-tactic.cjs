'use strict';
const assert = require('node:assert/strict');
const {makeVipFirstTactic} = require('./vip-first-tactic.cjs');
class PlayCardAction {
  constructor(id, handIndex, target) {
    this.type = 'PLAY_CARD_ACTION';
    this.id = id;
    this.handIndex = handIndex;
    this.target = target;
  }
}
const PlayerType={ANY:0},SlotType={BOARD:0};
const Tactic=makeVipFirstTactic(PlayCardAction,PlayerType,SlotType);
const tactic=new Tactic({});
/** @param {number} turn @param {string[]} hand @param {number} emptySlots */
function play(turn,hand,emptySlots) {
  const player={id:2,hand:{cards:hand.map(name=>({name}))},
    bench:Array.from({length:5},(_,i)=>({cards:i<emptySlots?[]:[{name:'Mew V'}]}))};
  return tactic.useTactic({turn},player);
}
assert.deepEqual(play(1,['Genesect V','Battle VIP Pass'],2),
  new PlayCardAction(2,1,{player:0,slot:0,index:0}));
assert.deepEqual(play(2,['Battle VIP Pass','Battle VIP Pass'],1),
  new PlayCardAction(2,0,{player:0,slot:0,index:0}));
assert.equal(play(0,['Battle VIP Pass'],5),undefined);
assert.equal(play(3,['Battle VIP Pass'],5),undefined);
assert.equal(play(1,['Battle VIP Pass'],0),undefined);
assert.equal(play(1,['Quick Ball'],3),undefined);
assert.throws(()=>makeVipFirstTactic({},PlayerType,SlotType));
assert.throws(()=>makeVipFirstTactic(PlayCardAction,{ANY:null},SlotType));
console.log('[vip-first] PASS: exact first-turn window, Bench capacity, item presence and native PlayCardAction semantics');
