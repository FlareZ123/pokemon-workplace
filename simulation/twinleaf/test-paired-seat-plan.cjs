'use strict';
const assert = require('node:assert/strict');
const {deckDigest, makeSeatPairs} = require('./paired-seat-plan.cjs');

/** @param {string} id @returns {{id:string,engine_names:string[]}} */
function fixture(id) {
  return {id, engine_names: Array.from({length:60}, (_, i) => id + ':' + i)};
}

function main() {
  const a=fixture('a'), b=fixture('b');
  const aBefore=a.engine_names.slice(), bBefore=b.engine_names.slice();
  const plan=makeSeatPairs(a,b,[17,29,41]);
  assert.equal(plan.length,6);
  for(let k=0;k<3;k++) {
    const first=plan[2*k],second=plan[2*k+1];
    assert.equal(first.pair_id,k);
    assert.equal(second.pair_id,k);
    assert.equal(first.seed,[17,29,41][k]);
    assert.equal(second.seed,first.seed);
    assert.equal(first.orientation,'AB');
    assert.equal(second.orientation,'BA');
    assert.strictEqual(first.seat1,a);
    assert.strictEqual(first.seat2,b);
    assert.strictEqual(second.seat1,b);
    assert.strictEqual(second.seat2,a);
  }
  const aDigest=deckDigest(a);
  assert.match(aDigest,/^[0-9a-f]{64}$/);
  assert.equal(aDigest,deckDigest({...a,engine_names:[...a.engine_names].reverse()}));
  assert.notEqual(aDigest,deckDigest(b));
  assert.notEqual(aDigest,deckDigest({...a,engine_names:[...a.engine_names.slice(0,59),'changed-print']}));
  assert.deepStrictEqual(a.engine_names,aBefore);
  assert.deepStrictEqual(b.engine_names,bBefore);
  assert.throws(()=>makeSeatPairs(a,b,[]),/seed/i);
  assert.throws(()=>makeSeatPairs(a,b,[2,2]),/Seeds must/);
  assert.throws(()=>makeSeatPairs(a,b,[-1]),/uint32/);
  assert.throws(()=>makeSeatPairs(a,b,[2**32]),/uint32/);
  assert.throws(()=>makeSeatPairs(a,{...b,id:a.id},[1]),/Distinct deck/);
  assert.throws(()=>makeSeatPairs({...a,engine_names:a.engine_names.slice(1)},b,[1]),/60 physical cards/);
  console.log('[paired-seat-plan] PASS: three identical-seed seat reversals, canonical hashes, invalid-input guards');
}
if(require.main===module)main();
module.exports={main};
