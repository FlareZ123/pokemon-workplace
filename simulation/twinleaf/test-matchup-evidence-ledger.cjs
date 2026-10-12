'use strict';
const assert=require('node:assert/strict');
const {summarizePairedTraces}=require('./paired-result-summary.cjs');
const {mergeTournamentReports,experimentIdentity}=require('./matchup-evidence-ledger.cjs');

const ONE='1'.repeat(64),TWO='2'.repeat(64),PIN='a'.repeat(40),CODE='b'.repeat(40);
const ids=['shadow_rider','regidrago'];
/** @param {number} seed @param {number[]} winners @param {string[]} [statuses] @param {boolean} [reverse] */
function makeReport(seed,winners,statuses=['finished','finished'],reverse=false) {
  const [a,b]=reverse?[ids[1],ids[0]]:ids;
  const assignments=[
    {pair_id:0,seed,orientation:'AB',seat1:{id:a},seat2:{id:b}},
    {pair_id:0,seed,orientation:'BA',seat1:{id:b},seat2:{id:a}}
  ];
  const traces=winners.map((winner,i)=>({
    seed,winner,status:statuses[i],
    phase:statuses[i]==='finished'?'FINISHED':'PLAYER_TURN',error:null
  }));
  const paired_results=summarizePairedTraces(assignments,traces);
  return {
    decks:[a,b],
    deck_sha256:reverse?[TWO,ONE]:[ONE,TWO],
    twinleaf_pin:PIN,research_revision:CODE,
    engine_hooks:['underworld-door-guard-v1'],
    shuffle_policy:'uniform-v1',random_stream_policy:'split-v1',
    tactic_order:'native',
    max_actions:350,wall_ms:25000,paired_results,traces
  };
}
const winBoth=makeReport(11,[0,1]);
const seatOne=makeReport(12,[0,0]);
const evidence=mergeTournamentReports([winBoth,seatOne],ids[0]);
assert.equal(evidence.reports,2);
assert.equal(evidence.distinct_seed_pairs,2);
assert.equal(evidence.raw_games,4);
assert.equal(evidence.merged_results.completed_decisions,4);
assert.deepEqual(evidence.score_bounds.sample_score_bounds.shadow_rider,{lower:0.75,upper:0.75});
assert.deepEqual(evidence.score_bounds.sample_score_bounds.regidrago,{lower:0.25,upper:0.25});
assert.deepEqual(evidence.score_bounds.sample_score_bounds.first_seat,{lower:0.75,upper:0.75});
console.log('[matchup-ledger] Two separately completed paired runs merge with correct seat attribution.');

const reversed=makeReport(13,[1,1],undefined,true);
assert.equal(experimentIdentity(winBoth),experimentIdentity(reversed));
const reversedMerged=mergeTournamentReports([winBoth,reversed],ids[0]);
assert.equal(reversedMerged.distinct_seed_pairs,2);
assert.equal(reversedMerged.merged_results.completed_decisions,4);
console.log('[matchup-ledger] Reversing deck order with matching physical hashes preserves the experiment.');

const censored=makeReport(14,[0,-1],['finished','action_cap']);
const bounded=mergeTournamentReports([winBoth,censored],ids[0]);
assert.deepEqual(bounded.score_bounds.sample_score_bounds.shadow_rider,{lower:0.75,upper:1});
assert.deepEqual(bounded.score_bounds.sample_score_bounds.regidrago,{lower:0,upper:0.25});
assert.equal(bounded.merged_results.censored_games,1);
console.log('[matchup-ledger] Censored orientations contribute honest unknown score intervals.');

assert.throws(()=>mergeTournamentReports([winBoth,winBoth]),
  /Repeated seed label/);
const differentRevision=makeReport(15,[0,1]);
differentRevision.research_revision='c'.repeat(40);
assert.throws(()=>mergeTournamentReports([winBoth,differentRevision]),
  /Cannot pool different/);
const differentHook=makeReport(15,[0,1]);
differentHook.engine_hooks=[];
assert.throws(()=>mergeTournamentReports([winBoth,differentHook]),
  /Cannot pool different/);
const differentPolicy=makeReport(15,[0,1]);
differentPolicy.tactic_order='vip_first';
assert.throws(()=>mergeTournamentReports([winBoth,differentPolicy]),
  /Cannot pool different/);
const differentDeck=makeReport(15,[0,1]);
differentDeck.deck_sha256=['9'.repeat(64),TWO];
assert.throws(()=>mergeTournamentReports([winBoth,differentDeck]),
  /Cannot pool different/);
console.log('[matchup-ledger] Duplicate seeds and mismatched deck, engine hooks, code or policies cannot silently pool.');

const falsified=makeReport(16,[0,1]);
falsified.paired_results.games[0].raw_winner_index=1;
assert.throws(()=>mergeTournamentReports([falsified]),
  /Raw and attributed winner mismatch/);
const malformed=makeReport(16,[0,1]);
malformed.traces.pop();
assert.throws(()=>mergeTournamentReports([malformed]),
  /Raw traces and annotated game rows/);
const noRevision=makeReport(16,[0,1]);
delete noRevision.research_revision;
assert.throws(()=>mergeTournamentReports([noRevision]),
  /Research code revision required/);
console.log('[matchup-ledger] Source trace integrity and explicit research pin are mandatory.');
console.log('[matchup-ledger] PASS: pooled seed pairs, censoring, comparability, and trace consistency');
