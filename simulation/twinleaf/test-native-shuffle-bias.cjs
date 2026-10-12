'use strict';
const assert=require('node:assert/strict');
const {BotArbiter}=require('../../vendor/twinleafgg/ptcg-server/output/game/bots/bot-arbiter');
const {makeUniformShuffleArbiter}=require('./hooks/uniform-random-shuffle.cjs');
/** @param {object} arbiter @param {number} cards @param {number[]} samples */
function drive(arbiter,cards,samples) {
  const before=Math.random;let i=0;
  try {
    Math.random=()=>samples[i++];
    const order=arbiter.shuffle({cards:Array.from({length:cards},(_,j)=>j)});
    assert.equal(i,samples.length);
    assert.deepEqual([...order].sort((a,b)=>a-b),Array.from({length:cards},(_,j)=>j));
    return order.join(',');
  } finally { Math.random=before; }
}
function main() {
  const bad=new BotArbiter();
  const good=new (makeUniformShuffleArbiter(BotArbiter))();
  const two=new Map(),three=new Map(),uniform=new Map();
  for(let x=0;x<4;x++)for(let y=0;y<4;y++) {
    const key=drive(bad,2,[(x+.5)/4,(y+.5)/4]);
    two.set(key,(two.get(key)||0)+1);
  }
  assert.deepEqual(Object.fromEntries([...two].sort()),{'0,1':6,'1,0':10});
  for(let x=0;x<6;x++)for(let y=0;y<6;y++)for(let z=0;z<6;z++) {
    const key=drive(bad,3,[(x+.5)/6,(y+.5)/6,(z+.5)/6]);
    three.set(key,(three.get(key)||0)+1);
  }
  assert.deepEqual(Object.fromEntries([...three].sort()),
    {'0,1,2':24,'0,2,1':26,'1,0,2':42,'1,2,0':40,'2,0,1':44,'2,1,0':40});
  for(let x=0;x<3;x++)for(let y=0;y<2;y++) {
    const key=drive(good,3,[(x+.5)/3,(y+.5)/2]);
    uniform.set(key,(uniform.get(key)||0)+1);
  }
  assert.equal(uniform.size,6);
  assert.ok([...uniform.values()].every(n=>n===1));
  console.log('[native-shuffle-bias] PASS: pinned n2 6:10, n3 exact 216-state nonuniform distribution, hook six uniform paths');
}
if(require.main===module)main();
module.exports={main};
