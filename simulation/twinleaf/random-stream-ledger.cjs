'use strict';
const assert=require('node:assert/strict');

/** Mulberry32, matching the original pinned tournament probe stream. @param {number} seed */
function seededRandom(seed) {
  let n=seed>>>0;
  return ()=>{n=(n+0x6D2B79F5)>>>0;let t=n;
    t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);
    return ((t^(t>>>14))>>>0)/4294967296;};
}

/**
 * Two independent seeded RNG streams. Live Store actions and random-arbiter
 * prompts share the physical-game stream; counterfactual bot simulations
 * receive a separate policy stream so speculative exploration cannot advance
 * future game coin flips or shuffle randomness.
 *
 * Run methods synchronously. The caller installs random() as Math.random
 * for the duration of the headless match and restores it in finally.
 * @param {number} seed
 */
function makeRandomStreamLedger(seed) {
  assert.ok(Number.isSafeInteger(seed) && seed>=0 && seed<=0xffffffff,'uint32 seed required');
  const game=seededRandom(seed);
  const policy=seededRandom((seed^0x9e3779b9)>>>0);
  const sources={setup:0,arbiter:0,policy:0,dispatch:0};
  let lane='game',calls=0,gameCalls=0,policyCalls=0;

  function random() {
    calls++;
    if(lane==='policy'){policyCalls++;return policy();}
    gameCalls++;return game();
  }

  /** @template T @param {'setup'|'arbiter'|'policy'|'dispatch'} source
   * @param {()=>T} operation @returns {T}
   */
  function track(source,operation) {
    assert.ok(Object.hasOwn(sources,source),'Unknown RNG source '+source);
    const before=calls,previous=lane;
    lane=source==='policy'?'policy':'game';
    try{return operation();}
    finally{sources[source]+=calls-before;lane=previous;}
  }

  function snapshot() {
    assert.equal(Object.values(sources).reduce((a,b)=>a+b,0),calls,
      'All RNG draws must occur in an attributed operation');
    assert.equal(sources.policy,policyCalls,'Policy draws must use the policy stream');
    assert.equal(sources.setup+sources.arbiter+sources.dispatch,gameCalls,
      'Only game operations may consume live RNG');
    return {calls,gameCalls,policyCalls,bySource:{...sources}};
  }

  return {random,track,snapshot};
}
module.exports={seededRandom,makeRandomStreamLedger};
