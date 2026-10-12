'use strict';
const assert = require('node:assert/strict');

const CAPPED = new Set(['action_cap', 'wall_cap']);
const BLOCKED = new Set(['unknown_actor', 'policy_error', 'dispatch_error', 'no_action']);

/**
 * Interpret raw Twinleaf winner indices using the seat assignment for each
 * actual game. An unfinished or anomalous terminal game cannot count as a win.
 * This is reporting only; small sample counts are not competitive estimates.
 *
 * @param {Array<{pair_id:number,seed:number,orientation:string,seat1:{id:string},seat2:{id:string}}>} pairs
 * @param {Array<{seed:number,status:string,phase:string,winner:number,error:string|null}>} traces
 * @returns {object}
 */
function summarizePairedTraces(pairs, traces) {
  assert.ok(Array.isArray(pairs) && pairs.length > 0, 'At least one seat assignment required');
  assert.ok(Array.isArray(traces) && traces.length === pairs.length, 'Exactly one trace per seat assignment required');
  const ids = [...new Set(pairs.flatMap(p => [p.seat1.id, p.seat2.id]))];
  assert.equal(ids.length, 2, 'Expected exactly two distinct deck identities');
  const byDeck = Object.fromEntries(ids.map(id => [id, {wins: 0, losses: 0, draws: 0, unresolved: 0}]));
  const byPair = new Map();

  const games = pairs.map((pair, index) => {
    const trace = traces[index];
    assert.ok(trace && typeof trace === 'object', 'Missing trace for game ' + index);
    assert.equal(trace.seed, pair.seed, 'Trace and assignment seeds differ at game ' + index);
    assert.ok(pair.seat1.id !== pair.seat2.id, 'Seat decks must be different');
    assert.ok(ids.includes(pair.seat1.id) && ids.includes(pair.seat2.id), 'Unexpected deck identity');
    assert.ok(['AB', 'BA'].includes(pair.orientation), 'Unexpected seat orientation');
    assert.ok(trace.status === 'finished' || CAPPED.has(trace.status) || BLOCKED.has(trace.status),
      'Unknown engine trace status: ' + trace.status);
    const completed = trace.status === 'finished' && trace.phase === 'FINISHED';
    const blocked = BLOCKED.has(trace.status) ||
      trace.status === 'finished' && trace.phase !== 'FINISHED';
    let outcome = blocked ? 'error' : completed ? 'terminal_unresolved' : 'censored';
    let winnerDeck = null;
    if (completed && (trace.winner === 0 || trace.winner === 1)) {
      outcome = 'decided';
      winnerDeck = trace.winner === 0 ? pair.seat1.id : pair.seat2.id;
      const loserDeck = trace.winner === 0 ? pair.seat2.id : pair.seat1.id;
      byDeck[winnerDeck].wins++;
      byDeck[loserDeck].losses++;
    } else if (completed && trace.winner === 3) {
      outcome = 'draw';
      byDeck[pair.seat1.id].draws++;
      byDeck[pair.seat2.id].draws++;
    } else {
      byDeck[pair.seat1.id].unresolved++;
      byDeck[pair.seat2.id].unresolved++;
    }
    assert.ok(trace.first_actor == null || trace.first_actor === 1 || trace.first_actor === 2,
      'First-turn actor must be player ID 1 or 2 when supplied');
    const row = {pair_id: pair.pair_id, seed: pair.seed, orientation: pair.orientation,
      seat1: pair.seat1.id, seat2: pair.seat2.id, status: trace.status,
      raw_winner_index: trace.winner, outcome, winner_deck: winnerDeck,
      first_actor: trace.first_actor ?? null,
      error: trace.error || null};
    if (!byPair.has(pair.pair_id)) byPair.set(pair.pair_id, []);
    byPair.get(pair.pair_id).push(row);
    return row;
  });

  const pairsSummary = [...byPair].sort((a,b) => a[0]-b[0]).map(([pairId, rows]) => {
    assert.equal(rows.length, 2, 'Each pair must contain exactly two orientations');
    assert.deepEqual(rows.map(row => row.orientation).sort(), ['AB', 'BA'], 'Pair must have two orientations');
    assert.equal(rows[0].seed, rows[1].seed, 'Pair orientations must share a seed');
    assert.equal(rows[0].seat1, rows[1].seat2, 'Both decks must swap seats');
    assert.equal(rows[0].seat2, rows[1].seat1, 'Both decks must swap seats');
    return {pair_id: pairId, seed: rows[0].seed,
      both_decided: rows.every(row => row.outcome === 'decided'),
      winner_decks: rows.map(row => row.winner_deck)};
  });
  const count = outcome => games.filter(game => game.outcome === outcome).length;
  return {games, by_deck: byDeck, paired_seed_count: pairsSummary.length,
    fully_decided_pairs: pairsSummary.filter(p => p.both_decided).length,
    completed_decisions: count('decided'), drawn_games: count('draw'), censored_games: count('censored'),
    error_games: count('error'), terminal_unresolved_games: count('terminal_unresolved'),
    pairs: pairsSummary,
    interpretation: 'Pinned Twinleaf GameWinner enum: 0 is seat 1, 1 is seat 2, 3 is DRAW. Censored, unresolved and errored games are not wins. Counts are diagnostics, not win-rate estimates.'};
}

module.exports = {summarizePairedTraces};
