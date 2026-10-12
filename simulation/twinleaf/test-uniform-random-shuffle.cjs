'use strict';
const assert=require('node:assert/strict');
const {makeUniformShuffleArbiter}=require('./hooks/uniform-random-shuffle.cjs');
class UpstreamArbiter {
  shuffle() { throw Error('The biased upstream shuffle must be overridden'); }
  resolve(cards) { return this.shuffle(cards); }
}
function main() {
  const Arbiter=makeUniformShuffleArbiter(UpstreamArbiter);
  const arbiter=new Arbiter();
  assert.ok(arbiter instanceof UpstreamArbiter);
  const cards={cards:[{id:0},{id:1},{id:2}]};
  const original=cards.cards.slice();
  const seen=new Map();
  const oldRandom=Math.random;
  try {
    for(let j2=0;j2<3;j2++) {
      for(let j1=0;j1<2;j1++) {
        const sequence=[(j2+0.5)/3,(j1+0.5)/2];
        let calls=0;
        Math.random=()=>sequence[calls++];
        const output=arbiter.resolve(cards);
        assert.equal(calls,2);
        assert.deepEqual([...output].sort(),[0,1,2]);
        const key=output.join(',');
        seen.set(key,(seen.get(key)||0)+1);
      }
    }
    assert.equal(seen.size,6,'Every permutation must have an equal-width RNG preimage');
    assert.ok([...seen.values()].every(n=>n===1));
    Math.random=()=>0;
    assert.deepEqual(arbiter.resolve({cards:[]}),[]);
    assert.deepEqual(arbiter.resolve({cards:[0]}),[0]);
    assert.deepEqual(arbiter.resolve({cards:[0,1]}),[1,0]);
  } finally {
    Math.random=oldRandom;
  }
  assert.deepEqual(cards.cards,original,'Shuffle must return indices without mutating cards');
  console.log('[uniform-shuffle] PASS: six equiprobable 3-card permutations, proper 2-card swap, no input mutation');
}
if(require.main===module)main();
module.exports={main};
