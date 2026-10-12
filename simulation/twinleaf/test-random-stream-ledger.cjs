'use strict';
const assert=require('node:assert/strict');
const {seededRandom,makeRandomStreamLedger}=require('./random-stream-ledger.cjs');

/** Single runnable regression with detailed evidence of RNG isolation. */
function main() {
  const seed=20261012;
  const baseline=seededRandom(seed);
  const ledger=makeRandomStreamLedger(seed);
  const control=makeRandomStreamLedger(seed);
  const physical=[];
  for(let i=0;i<64;i++) {
    const kind=i%2===0?'arbiter':'dispatch';
    physical.push(ledger.track(kind,()=>ledger.random()));
  }
  assert.deepEqual(physical,Array.from({length:64},()=>baseline()),
    'Game stream must retain exactly the original pinned probe sequence');
  for(let i=0;i<700;i++)
    ledger.track('policy',()=>ledger.random());
  const gameNext=ledger.track('dispatch',()=>ledger.random());
  const controlValues=Array.from({length:65},(_,i)=>
    control.track(i%2===0?'arbiter':'dispatch',()=>control.random()));
  assert.equal(gameNext,controlValues[64],
    '700 policy draws must not move the next physical-game RNG draw');
  const prior=ledger.snapshot();
  assert.equal(prior.calls,765);
  assert.equal(prior.gameCalls,65);
  assert.equal(prior.policyCalls,700);
  assert.equal(prior.bySource.policy,700);
  assert.equal(prior.bySource.arbiter,32);
  assert.equal(prior.bySource.dispatch,33);
  assert.equal(prior.bySource.setup,0);
  const exceptional=makeRandomStreamLedger(7);
  const comparison=makeRandomStreamLedger(7);
  assert.throws(()=>exceptional.track('policy',()=>{
    exceptional.random();throw new Error('deliberate counterfactual exception');
  }),/counterfactual exception/);
  assert.equal(exceptional.track('setup',()=>exceptional.random()),
    comparison.track('setup',()=>comparison.random()),
    'A failed counterfactual must not contaminate the live lane');
  assert.equal(exceptional.snapshot().policyCalls,1);
  assert.throws(()=>exceptional.track('unknown',()=>0),/Unknown RNG source/);
  console.log('[rng-lanes] '+JSON.stringify({
    seed,original_game_draws_preserved:65,policy_draws_isolated:700,
    after_policy_game_draw:gameNext,by_source:prior.bySource,
    failed_policy_restores_game_lane:true
  }));
  console.log('[rng-lanes] PASS: counterfactual simulations cannot consume the live seeded stream');
}
if(require.main===module)main();
module.exports={main};
