'use strict';
const assert=require('node:assert/strict');
const {
  validateField,extremalFieldScore,evaluateFieldCandidate,
  compareFieldCandidates
}=require('./uncertain_metagame_field.cjs');

/** @param {number} actual @param {number} expected */
function close(actual,expected) {
  assert.ok(Math.abs(actual-expected)<1e-12,actual+' differs from '+expected);
}

const three=[
  {id:'A',lower:0.2,upper:0.6},
  {id:'B',lower:0.2,upper:0.6},
  {id:'C',lower:0,upper:0.5}
];
const values=[0.2,0.5,0.9];
const min=extremalFieldScore(three,values,false);
const max=extremalFieldScore(three,values,true);
close(min.score,0.32);
close(max.score,0.64);
assert.deepEqual(min.weights,{A:0.6,B:0.4,C:0});
assert.deepEqual(max.weights,{A:0.2,B:0.3,C:0.5});

// Independent exact 1%-grid oracle: sum of integer mass units must be 100.
const all=[];
for(let a=20;a<=60;a++)for(let b=20;b<=60;b++) {
  const c=100-a-b;
  if(c<0 || c>50)continue;
  all.push((a*values[0]+b*values[1]+c*values[2])/100);
}
assert.equal(all.length,1416);
close(min.score,Math.min(...all));
close(max.score,Math.max(...all));
console.log('[metagame] Greedy exact simplex extrema reproduce 1,416 independently enumerated weight vectors.');

const field=[
  {id:'iron_thorns',lower:0.3,upper:0.7},
  {id:'vileplume',lower:0.3,upper:0.7}
];
const complete={
  shadow_rider:{
    iron_thorns:{lower:0.8,upper:0.8},
    vileplume:{lower:0.4,upper:0.4}
  },
  regidrago:{
    iron_thorns:{lower:0.5,upper:0.5},
    vileplume:{lower:0.5,upper:0.5}
  }
};
const a=evaluateFieldCandidate(field,complete,'shadow_rider');
const b=evaluateFieldCandidate(field,complete,'regidrago');
close(a.score.lower,0.52);
close(a.score.upper,0.68);
close(b.score.lower,0.5);
close(b.score.upper,0.5);
assert.deepEqual(a.missing_opponents,[]);
close(a.maximum_missing_field_weight,0);
const proof=compareFieldCandidates(field,complete,'shadow_rider','regidrago');
assert.equal(proof.guaranteed_better,'shadow_rider');
close(proof.score_difference.lower,0.02);
close(proof.score_difference.upper,0.18);
console.log('[metagame] Shared-field calculation proves conditional lower advantage despite uncertain field weights.');

const incomplete={
  ...complete,
  regidrago:{iron_thorns:{lower:0.5,upper:0.5}}
};
const unknown=evaluateFieldCandidate(field,incomplete,'regidrago');
close(unknown.score.lower,0.15);
close(unknown.score.upper,0.85);
close(unknown.maximum_missing_field_weight,0.7);
assert.deepEqual(unknown.missing_opponents,['vileplume']);
assert.equal(compareFieldCandidates(field,incomplete,'shadow_rider','regidrago').guaranteed_better,null);
console.log('[metagame] Missing matchup remains [0,1] and explicitly exposes up to 70% untested field mass.');

assert.throws(()=>validateField([
  {id:'X',lower:0.1,upper:0.2},{id:'Y',lower:0.1,upper:0.2}
]),/cannot sum to one/);
assert.throws(()=>validateField([
  {id:'X',lower:0.5,upper:0.8},{id:'X',lower:0.2,upper:0.5}
]),/Duplicate opponent/);
assert.throws(()=>evaluateFieldCandidate(field,{
  shadow_rider:{iron_thorns:{lower:0.9,upper:0.4}}
},'shadow_rider'),/Matchup scores/);
assert.throws(()=>extremalFieldScore(three,[0.1,0.2],true),
  /One finite score per opponent/);
assert.throws(()=>compareFieldCandidates(field,complete,'shadow_rider','shadow_rider'),
  /Compare different candidates/);
console.log('[metagame] PASS: exact mixture extrema, interval uncertainty, missing field mass and invalid inputs');
