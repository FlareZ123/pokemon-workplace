'use strict';
const assert = require('node:assert/strict');
const {summarizePairedTraces} = require('./paired-result-summary.cjs');
const {summarizeScoreBounds} = require('./paired-score-bounds.cjs');

/**
 * Canonical experimental identity for merger. A new code revision or engine
 * hook changes the experiment even if the two decks stay unchanged.
 * @param {object} report Output from tournament-bounded-match.cjs
 * @returns {string}
 */
function experimentIdentity(report) {
  assert.ok(report && typeof report === 'object', 'Experiment report required');
  assert.ok(Array.isArray(report.decks) && report.decks.length === 2,
    'Exactly two deck IDs required');
  assert.ok(Array.isArray(report.deck_sha256) && report.deck_sha256.length === 2,
    'Exactly two physical deck hashes required');
  assert.notEqual(report.decks[0], report.decks[1], 'Deck IDs must differ');
  const entries = report.decks.map((name, index) => {
    assert.match(name, /^[a-zA-Z0-9_-]+$/, 'Invalid deck ID');
    const sha = report.deck_sha256[index];
    assert.match(sha, /^[0-9a-f]{64}$/, 'Missing or invalid deck SHA-256');
    return [name, sha];
  }).sort((a,b) => a[0].localeCompare(b[0]));
  assert.match(report.twinleaf_pin, /^[0-9a-f]{40}$/, 'Engine pin required');
  assert.match(report.research_revision, /^[0-9a-f]{40}$/,
    'Research code revision required');
  assert.ok(Array.isArray(report.engine_hooks) &&
    report.engine_hooks.every(x => typeof x === 'string' && x.length > 0),
    'Explicit engine hook manifest required');
  for (const key of ['shuffle_policy','random_stream_policy','tactic_order']) {
    assert.ok(typeof report[key] === 'string' && report[key].length > 0,
      'Missing model field: ' + key);
  }
  assert.ok(Number.isSafeInteger(report.max_actions) && report.max_actions > 0,
    'Action budget required');
  assert.ok(Number.isSafeInteger(report.wall_ms) && report.wall_ms > 0,
    'Wall budget required');
  return JSON.stringify({
    decks:entries,
    pin:report.twinleaf_pin,
    research:report.research_revision,
    hooks:[...report.engine_hooks].sort(),
    shuffle:report.shuffle_policy,
    random_stream:report.random_stream_policy,
    tactics:report.tactic_order,
    action_cap:report.max_actions,
    wall_cap_ms:report.wall_ms
  });
}

/**
 * Merge independent seat-paired *diagnostics* without pooling incompatible
 * engine, policy, deck or code revisions. Recompute winner attribution from
 * raw traces and accompanying pair seats; do not trust stale summaries.
 *
 * @param {object[]} reports Full JSON reports from bounded runner
 * @param {string} [deckA] Deck identity to score first
 * @returns {object}
 */
function mergeTournamentReports(reports, deckA) {
  assert.ok(Array.isArray(reports) && reports.length > 0,
    'At least one complete report required');
  const signature=experimentIdentity(reports[0]);
  const names=[...reports[0].decks];
  const chosen=deckA || names[0];
  assert.ok(names.includes(chosen),'Scoring deck is absent');
  const seeds=new Set();
  const assignments=[],traces=[];
  let newPairId=0;

  for (const report of reports) {
    assert.equal(experimentIdentity(report),signature,
      'Cannot pool different engine, code, hooks, decklists, policies or budgets');
    assert.ok(report.paired_results &&
      Array.isArray(report.paired_results.games) &&
      Array.isArray(report.traces) &&
      report.paired_results.games.length === report.traces.length,
      'Raw traces and annotated game rows must correspond');
    const gameRows=report.paired_results.games;
    const perPair=new Map();
    for (let i=0;i<gameRows.length;i++) {
      const row=gameRows[i],trace=report.traces[i];
      assert.equal(row.seed,trace.seed,'Raw and attributed seed mismatch');
      assert.equal(row.status,trace.status,'Raw and attributed status mismatch');
      assert.equal(row.raw_winner_index,trace.winner,
        'Raw and attributed winner mismatch');
      assert.deepEqual(row.error,trace.error || null,
        'Raw and attributed error mismatch');
      assert.ok(names.includes(row.seat1) && names.includes(row.seat2) &&
        row.seat1 !== row.seat2,'Unexpected deck seat mapping');
      if (!perPair.has(row.pair_id)) perPair.set(row.pair_id,[]);
      perPair.get(row.pair_id).push({row,trace});
    }
    assert.equal(perPair.size,report.paired_results.paired_seed_count,
      'Pair census differs from raw games');

    for (const slots of perPair.values()) {
      assert.equal(slots.length,2,'Each seed must have both seat orientations');
      const seed=slots[0].row.seed;
      assert.ok(Number.isSafeInteger(seed) && seed>=0 && seed<=0xffffffff,
        'Invalid seed identity');
      assert.ok(!seeds.has(seed),
        'Repeated seed label across reports cannot count as independent evidence');
      seeds.add(seed);
      for (const {row,trace} of slots) {
        assignments.push({
          pair_id:newPairId,seed:row.seed,orientation:row.orientation,
          seat1:{id:row.seat1},seat2:{id:row.seat2}
        });
        traces.push(trace);
      }
      newPairId++;
    }
  }

  const merged=summarizePairedTraces(assignments,traces);
  const bounds=summarizeScoreBounds(merged,chosen);
  return {
    experiment:JSON.parse(signature),
    reports:reports.length,
    distinct_seed_pairs:seeds.size,
    raw_games:traces.length,
    merged_results:merged,
    score_bounds:bounds,
    interpretation:'Only compatible fixed-policy engine experiments were pooled. Identically numbered seeds across reports were rejected. Bounds describe model outcomes and depend on genuinely independent sampled paired seeds; no claim of human paper Expanded matchup accuracy.'
  };
}

module.exports={experimentIdentity,mergeTournamentReports};
