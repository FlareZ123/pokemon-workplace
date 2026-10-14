'use strict';
const assert=require('node:assert/strict');
const {createHash}=require('node:crypto');

/** Canonically shuffle a multiset into a stable counter-derived physical order. */
function permute(cards,key){
  const output=[...cards].sort((a,b)=>a.fullName.localeCompare(b.fullName) || a.id-b.id);
  let counter=0;
  const random=bound=>{
    const limit=4294967296-(4294967296%bound);
    while(true){
      const x=createHash('sha256').update(key+':'+counter++).digest().readUInt32BE(0);
      if(x<limit)return x%bound;
    }
  };
  for(let i=output.length-1;i>0;i--){
    const j=random(i+1);
    [output[i],output[j]]=[output[j],output[i]];
  }
  return output;
}

/** Public snapshot excludes both players' secret deck order and Prize identities. */
function publicKey(state,actorId){
  const view=state.players.map(p=>({
    id:p.id,
    hand:p.id===actorId?p.hand.cards.map(c=>c.fullName):p.hand.cards.length,
    deck_size:p.deck.cards.length,
    prizes:p.prizes.map(s=>s.cards.length),
    active:p.active.cards.map(c=>c.fullName),
    bench:p.bench.map(s=>s.cards.map(c=>c.fullName)),
    discard:p.discard.cards.map(c=>c.fullName),
    lostzone:p.lostzone.cards.map(c=>c.fullName),
    stadium:p.stadium.cards.map(c=>c.fullName),
    supporter:p.supporter.cards.map(c=>c.fullName)
  }));
  return JSON.stringify({actorId,phase:state.phase,turn:state.turn,
    activePlayer:state.activePlayer,view});
}

/** Make hypothetical decision state without changing the authoritative game.
 * Research assumption: entire unknown opponent inventory is an open-list prior.
 * @param {Function} deepClone Pinned engine deepClone, with no Card exclusions
 * @returns {(state:object,actorId:number)=>object}
 */
function makeK0HiddenWorldSampler(deepClone){
  assert.equal(typeof deepClone,'function');
  function redistribute(p,hideHand,seed){
    const lengths=[...(hideHand?[p.hand.cards.length]:[]),
      p.deck.cards.length,...p.prizes.map(x=>x.cards.length)];
    const pool=[...(hideHand?p.hand.cards:[]),...p.deck.cards,
      ...p.prizes.flatMap(x=>x.cards)];
    const shuffled=permute(pool,seed);
    let start=0,slot=0;
    if(hideHand){p.hand.cards=shuffled.slice(start,start+lengths[slot]);start+=lengths[slot++];}
    p.deck.cards=shuffled.slice(start,start+lengths[slot]);start+=lengths[slot++];
    for(const prize of p.prizes){
      prize.cards=shuffled.slice(start,start+lengths[slot]);start+=lengths[slot++];
    }
    assert.equal(start,shuffled.length,'Conservation of private cards');
  }
  return (state,actorId)=>{
    const key=createHash('sha256').update(publicKey(state,actorId)).digest('hex');
    assert.ok(!state.prompts.some(p=>p.result===undefined),
      'Do not sample unresolved prompt states');
    const clone=deepClone(state,[]);
    assert.ok(clone.players.some(p=>p.id===actorId),'Actor missing');
    for(const p of clone.players)redistribute(p,p.id!==actorId,key+':'+p.id);
    return clone;
  };
}
module.exports={permute,publicKey,makeK0HiddenWorldSampler};
