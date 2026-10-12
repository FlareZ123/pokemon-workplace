'use strict';
const assert = require('node:assert/strict');
const {summarizePairedTraces}=require('./paired-result-summary.cjs');
const {summarizeScoreBounds}=require('./paired-score-bounds.cjs');

const deckA={id:'shadow_rider'},deckB={id:'regidrago'};
/** @param {number[]} ids @returns {object[]} */
function plan(ids) {
  return ids.flatMap((seed,pair_id)=>[
    {pair_id,seed,orientation:'AB',seat1:deckA,seat2:deckB},
    {pair_id,seed,orientation:'BA',seat1:deckB,seat2:deckA}
  ]);
}
/** @param {number} seed @param {number} winner @param {string} [status] */
function trace(seed,winner,status='finished') {
  return {seed,winner,status,phase:status==='finished'?'FINISHED':'PLAYER_TURN',error:null};
}
/** @param {number[]} seeds @param {object[]} traces */
function evaluate(seeds,traces) {
  const summary=summarizePairedTraces(plan(seeds),traces);
  return summarizeScoreBounds(summary,deckA.id);
}
/** @param {number} actual @param {number} expected */
function close(actual,expected) {
  assert.ok(Math.abs(actual-expected)<1e-12,actual+' differs from '+expected);
}

const sweeping=evaluate([77],[trace(77,0),trace(77,1)]);
assert.deepEqual(sweeping.sample_score_bounds.shadow_rider,{lower:1,upper:1});
assert.deepEqual(sweeping.sample_score_bounds.regidrago,{lower:0,upper:0});
assert.deepEqual(sweeping.sample_score_bounds.first_seat,{lower:0.5,upper:0.5});
console.log('[paired-score] Both seat orientations won by deck A: 100% observed, 50% first-seat score.');

const seatOnly=evaluate([77],[trace(77,0),trace(77,0)]);
assert.deepEqual(seatOnly.sample_score_bounds.shadow_rider,{lower:0.5,upper:0.5});
assert.deepEqual(seatOnly.sample_score_bounds.first_seat,{lower:1,upper:1});
console.log('[paired-score] Both games won by player 1: equal deck scores, 100% first-seat score.');

const censored=evaluate([77],[trace(77,0),trace(77,-1,'action_cap')]);
assert.deepEqual(censored.sample_score_bounds.shadow_rider,{lower:0.5,upper:1});
assert.deepEqual(censored.sample_score_bounds.regidrago,{lower:0,upper:0.5});
assert.equal(censored.complete_pairs,0);
console.log('[paired-score] A censored orientation remains a zero-to-one unknown.');

const drawError=evaluate([77],[trace(77,3),trace(77,-1,'dispatch_error')]);
assert.deepEqual(drawError.sample_score_bounds.shadow_rider,{lower:0.25,upper:0.75});
assert.deepEqual(drawError.sample_score_bounds.regidrago,{lower:0.25,upper:0.75});
console.log('[paired-score] True draws have half-score and engine errors have unknown score.');

const many=evaluate([77,78,79],[
  trace(77,0),trace(77,1),
  trace(78,0),trace(78,1),
  trace(79,0),trace(79,1)
]);
assert.equal(many.paired_seed_count,3);
assert.equal(many.complete_pairs,3);
const radius=Math.sqrt(Math.log(40)/6);
close(many.conditional_hoeffding.radius_per_endpoint,radius);
close(many.conditional_hoeffding.shadow_rider.lower,1-radius);
assert.equal(many.conditional_hoeffding.shadow_rider.upper,1);
assert.equal(many.conditional_hoeffding.regidrago.lower,0);
close(many.conditional_hoeffding.regidrago.upper,radius);
console.log('[paired-score] Six games in three paired seeds count as three iid units, with wide 95% bounds.');

assert.throws(()=>summarizeScoreBounds(summarizePairedTraces(plan([77]),[
  trace(77,0),trace(77,1)]),'missing'),/Deck A missing/);
assert.throws(()=>summarizeScoreBounds(summarizePairedTraces(plan([77]),[
  trace(77,0),trace(77,1)]),deckA.id,1),/Confidence/);
assert.throws(()=>evaluate([77,77],[
  trace(77,0),trace(77,1),trace(77,0),trace(77,1)
]),/Seed labels must be unique/);
console.log('[paired-score] Repeated seed labels cannot be counted as independent evidence.');
console.log('[paired-score] PASS: seat attribution, draws, adversarial censoring, dependence and small-sample uncertainty');
