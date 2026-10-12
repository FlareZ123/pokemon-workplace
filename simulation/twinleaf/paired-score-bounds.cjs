'use strict';
const assert = require('node:assert/strict');

/**
 * Map a seat-attributed game to lower/upper possible deck and first-seat
 * scores. A draw awards half a point; every unfinished or unclassified game
 * is left genuinely unidentified. No censoring is imputed as a loss.
 * @param {object} game Row from summarizePairedTraces().games
 * @param {string} deckId
 * @returns {{low:number,high:number,seatLow:number,seatHigh:number}}
 */
function scoreBounds(game, deckId) {
  if (game.outcome === 'decided') {
    const point = Number(game.winner_deck === deckId);
    const seat = Number(game.winner_deck === game.seat1);
    return {low:point,high:point,seatLow:seat,seatHigh:seat};
  }
  if (game.outcome === 'draw')
    return {low:0.5,high:0.5,seatLow:0.5,seatHigh:0.5};
  return {low:0,high:1,seatLow:0,seatHigh:1};
}

/**
 * Pair-seed-aware bounds for games from the SAME immutable engine, policies,
 * and decklists. Without independent random seeds and model fidelity these
 * are diagnostics and must not be labeled competitive match probabilities.
 *
 * Each paired seed is one independent sampling unit, even though it yields
 * two dependent seat-swapped games. Lower/upper sample bounds allocate every
 * censored, errored or terminal-unresolved game adversarially. Optional
 * Hoeffding bounds apply to independent identically distributed PAIR SEEDS,
 * with a simultaneous one-sided union bound for lower/upper endpoints.
 *
 * @param {ReturnType<import('./paired-result-summary.cjs').summarizePairedTraces>} summary
 * @param {string} deckA
 * @param {number} confidence Defaults to 0.95
 * @returns {object}
 */
function summarizeScoreBounds(summary, deckA, confidence = 0.95) {
  assert.ok(confidence > 0 && confidence < 1, 'Confidence must be between zero and one');
  const names = Object.keys(summary.by_deck);
  assert.equal(names.length, 2, 'Expected exactly two deck identities');
  assert.ok(names.includes(deckA), 'Deck A missing from paired report');
  const deckB = names.find(name => name !== deckA);
  assert.equal(summary.games.length, summary.paired_seed_count * 2,
    'Every paired seed requires two games');

  const byPair = new Map();
  for (const game of summary.games) {
    if (!byPair.has(game.pair_id)) byPair.set(game.pair_id, []);
    byPair.get(game.pair_id).push(game);
  }
  const seeds = [...byPair].sort((a,b) => a[0]-b[0]).map(([pairId, games]) => {
    assert.equal(games.length, 2, 'Pair has missing orientation');
    assert.deepEqual(games.map(g => g.orientation).sort(), ['AB','BA'],
      'Pair must have both orientations');
    assert.equal(games[0].seed, games[1].seed, 'Orientations must share seed');
    const values = games.map(g => scoreBounds(g,deckA));
    return {
      pair_id: pairId,seed:games[0].seed,
      complete: games.every(g => g.outcome === 'decided' || g.outcome === 'draw'),
      deck_a_lower: (values[0].low+values[1].low)/2,
      deck_a_upper: (values[0].high+values[1].high)/2,
      first_seat_lower: (values[0].seatLow+values[1].seatLow)/2,
      first_seat_upper: (values[0].seatHigh+values[1].seatHigh)/2
    };
  });
  assert.ok(seeds.length > 0, 'No seed pairs');
  assert.equal(new Set(seeds.map(row => row.seed)).size,seeds.length,
    'Seed labels must be unique across independent pairs');
  const average = key => seeds.reduce((total,row) => total+row[key],0)/seeds.length;
  const low=average('deck_a_lower'),high=average('deck_a_upper');
  const firstLow=average('first_seat_lower'),firstHigh=average('first_seat_upper');
  const radius=Math.sqrt(Math.log(2/(1-confidence))/(2*seeds.length));
  return {
    deck_a:deckA,deck_b:deckB,
    independent_units:'seed pairs, not individual games',
    paired_seed_count:seeds.length,
    complete_pairs:seeds.filter(s=>s.complete).length,
    sample_score_bounds:{
      [deckA]:{lower:low,upper:high},
      [deckB]:{lower:1-high,upper:1-low},
      first_seat:{lower:firstLow,upper:firstHigh}
    },
    conditional_hoeffding:{
      confidence,unit:'independently sampled paired seeds',
      radius_per_endpoint:radius,
      [deckA]:{lower:Math.max(0,low-radius),upper:Math.min(1,high+radius)},
      [deckB]:{lower:Math.max(0,1-high-radius),upper:Math.min(1,1-low+radius)}
    },
    seed_pairs:seeds,
    interpretation:'Sample bounds give every unresolved game a possible score from 0 to 1. Hoeffding bounds require iid seed pairs, immutable policy and engine, and still describe only the simulator. Neither supplies a paper Expanded win rate.'
  };
}

module.exports={scoreBounds,summarizeScoreBounds};
