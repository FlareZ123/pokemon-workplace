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

/** Reallocate an unknown private card pool without inspecting its original ordering. */
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

/** Make hypothetical decision state without changing the authoritative game.
 * Research assumption: entire unknown opponent inventory is an open-list prior.
 * @param {Function} deepClone Pinned engine deepClone, with no Card exclusions
 * @returns {(state:object,actorId:number)=>object}
 */
function makeK0HiddenWorldSampler(deepClone){
  assert.equal(typeof deepClone,'function');
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
/** Sample a K1 world only AFTER legitimate first deck inspection.
 * Prize contents are then known as a multiset, but face-down slot identities
 * and deck ordering are still unknown. Calling this at K0 would leak secrets.
 * @param {Function} deepClone Pinned engine deepClone with Card preservation
 * @returns {(state:object,actorId:number,knownPrizeNames:string[])=>object}
 */
function makeK1HiddenWorldSampler(deepClone){
  assert.equal(typeof deepClone,'function');
  return (state,actorId,knownPrizeNames)=>{
    assert.ok(!state.prompts.some(p=>p.result===undefined),
      'Do not sample unresolved prompt states');
    const actor=state.players.find(p=>p.id===actorId);
    assert.ok(actor,'Actor missing');
    assert.ok(Array.isArray(knownPrizeNames),
      'K1 requires an externally recorded, observed Prize multiset');
    const observed=[...knownPrizeNames].sort();
    const physical=actor.prizes.flatMap(slot=>slot.cards.map(card=>card.fullName)).sort();
    assert.deepEqual(observed,physical,
      'K1 Prize record is stale or inconsistent with physical state');
    const key=createHash('sha256').update(
      JSON.stringify({public:publicKey(state,actorId),knowledge:'K1',
        knownPrizeNames:observed})).digest('hex');
    const clone=deepClone(state,[]);
    for(const p of clone.players){
      if(p.id!==actorId){
        redistribute(p,true,key+':'+p.id);
        continue;
      }
      p.deck.cards=permute(p.deck.cards,key+':own-deck');
      const shuffled=permute(p.prizes.flatMap(slot=>slot.cards),key+':own-prizes');
      let start=0;
      for(const slot of p.prizes){
        const size=slot.cards.length;
        slot.cards=shuffled.slice(start,start+size);
        start+=size;
      }
      assert.equal(start,shuffled.length,'Conservation of known Prize cards');
    }
    return clone;
  };
}
module.exports={permute,publicKey,makeK0HiddenWorldSampler,makeK1HiddenWorldSampler};
