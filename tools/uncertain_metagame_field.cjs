'use strict';
const assert=require('node:assert/strict');

/**
 * Validate an explicitly assumed opponent-mixture uncertainty set.
 * Feasible fields are probability vectors w with lower<=w<=upper and sum=1.
 * @param {{id:string,lower:number,upper:number}[]} field
 * @returns {{id:string,lower:number,upper:number}[]}
 */
function validateField(field) {
  assert.ok(Array.isArray(field) && field.length>0,'Opponent field required');
  const seen=new Set();
  let sumLow=0,sumHigh=0;
  for(const row of field) {
    assert.ok(row && typeof row.id==='string' && row.id.length>0,
      'Opponent ID required');
    assert.ok(!seen.has(row.id),'Duplicate opponent ID '+row.id);
    seen.add(row.id);
    assert.ok(Number.isFinite(row.lower) && Number.isFinite(row.upper) &&
      row.lower>=0 && row.lower<=row.upper && row.upper<=1,
      'Invalid opponent weight range '+row.id);
    sumLow+=row.lower;sumHigh+=row.upper;
  }
  assert.ok(sumLow<=1+1e-12 && sumHigh>=1-1e-12,
    'Opponent weight ranges cannot sum to one');
  return field;
}

/**
 * Solve a box-constrained probability-simplex linear objective exactly.
 * Exchange argument: given a fixed lower bound on every weight, allocating
 * each remaining unit to the most favorable unsaturated opponent cannot be
 * improved by exchanging it with another opponent of worse objective value.
 * @param {{id:string,lower:number,upper:number}[]} field
 * @param {number[]} values
 * @param {boolean} maximize
 * @returns {{score:number,weights:Record<string,number>}}
 */
function extremalFieldScore(field,values,maximize=false) {
  validateField(field);
  assert.ok(Array.isArray(values) && values.length===field.length &&
    values.every(Number.isFinite),'One finite score per opponent required');
  const weights=field.map(x=>x.lower);
  let remainder=Math.max(0,1-weights.reduce((a,b)=>a+b,0));
  const indices=field.map((_,i)=>i).sort((a,b)=>
    (maximize?values[b]-values[a]:values[a]-values[b])||a-b);
  for(const index of indices) {
    const room=field[index].upper-weights[index];
    const addition=Math.min(remainder,room);
    weights[index]+=addition;
    remainder-=addition;
  }
  assert.ok(Math.abs(remainder)<1e-10,'Field weights failed simplex normalization');
  const score=weights.reduce((sum,w,i)=>sum+w*values[i],0);
  return {score,weights:Object.fromEntries(field.map((row,i)=>[row.id,weights[i]]))};
}

/** @param {object|undefined} interval @returns {{lower:number,upper:number,missing:boolean}} */
function validateMatchup(interval) {
  if(interval==null) return {lower:0,upper:1,missing:true};
  assert.ok(typeof interval==='object' &&
    Number.isFinite(interval.lower) && Number.isFinite(interval.upper) &&
    interval.lower>=0 && interval.lower<=interval.upper && interval.upper<=1,
    'Matchup scores must have bounded [lower,upper] within [0,1]');
  return {lower:interval.lower,upper:interval.upper,missing:false};
}

/**
 * Evaluate candidate score against all mixtures admitted by an explicit field.
 * Missing matchups contribute [0,1], never fabricated 50% results.
 * Inputs are deterministic assumed score bounds, not statistical guarantees.
 * @param {{id:string,lower:number,upper:number}[]} field
 * @param {Record<string,Record<string,{lower:number,upper:number}>>} matchups
 * @param {string} candidate
 */
function evaluateFieldCandidate(field,matchups,candidate) {
  validateField(field);
  const row=matchups[candidate]||{};
  const intervals=field.map(x=>validateMatchup(row[x.id]));
  const lower=extremalFieldScore(field,intervals.map(x=>x.lower),false);
  const upper=extremalFieldScore(field,intervals.map(x=>x.upper),true);
  const unknown=extremalFieldScore(field,intervals.map(x=>Number(x.missing)),true);
  return {
    candidate,score:{lower:lower.score,upper:upper.score},
    lower_witness:lower.weights,upper_witness:upper.weights,
    missing_opponents:field.filter((_,i)=>intervals[i].missing).map(x=>x.id),
    maximum_missing_field_weight:unknown.score
  };
}

/**
 * Strict sufficient test of superiority under a SHARED uncertain field.
 * For each opponent the worst A-B advantage is A.lower-B.upper.
 * Optimizing that difference across one common field is tighter than merely
 * subtracting independently optimized aggregate ranges.
 * @param {{id:string,lower:number,upper:number}[]} field
 * @param {Record<string,Record<string,{lower:number,upper:number}>>} matchups
 * @param {string} candidateA
 * @param {string} candidateB
 */
function compareFieldCandidates(field,matchups,candidateA,candidateB) {
  validateField(field);
  assert.notEqual(candidateA,candidateB,'Compare different candidates');
  const a=field.map(x=>validateMatchup((matchups[candidateA]||{})[x.id]));
  const b=field.map(x=>validateMatchup((matchups[candidateB]||{})[x.id]));
  const lower=extremalFieldScore(field,a.map((x,i)=>x.lower-b[i].upper),false);
  const upper=extremalFieldScore(field,a.map((x,i)=>x.upper-b[i].lower),true);
  return {
    candidate_a:candidateA,candidate_b:candidateB,
    score_difference:{lower:lower.score,upper:upper.score},
    guaranteed_better:lower.score>0?candidateA:upper.score<0?candidateB:null,
    lower_witness:lower.weights,upper_witness:upper.weights,
    interpretation:'Proof is conditional on each input matchup score belonging to its assumed interval, the listed opponent universe being complete and the actual field weights satisfying these bounds. Statistical coverage and paper-game engine fidelity are not established here.'
  };
}

module.exports={
  validateField,extremalFieldScore,validateMatchup,evaluateFieldCandidate,compareFieldCandidates
};
