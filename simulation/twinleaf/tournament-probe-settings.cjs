'use strict';
const assert = require('node:assert/strict');

const MAX_SEED_PAIRS = 3;

/**
 * A manual-only configuration surface for bounded Twinleaf diagnostics.
 * Prevents malformed seeds and open-ended shared-CI match workloads.
 * @param {Record<string, string|undefined>} env
 * @param {string[]} availableIds Exact, validated engine-mappable tournament list IDs
 * @returns {{deckAId:string,deckBId:string,seeds:number[]}}
 */
function parseProbeSettings(env, availableIds) {
  const deckAId = env.TWINLEAF_DECK_A || 'vileplume';
  const deckBId = env.TWINLEAF_DECK_B || 'mew_genesect';
  assert.ok(availableIds.includes(deckAId), 'Unknown or unmapped deck A: ' + deckAId);
  assert.ok(availableIds.includes(deckBId), 'Unknown or unmapped deck B: ' + deckBId);
  assert.notEqual(deckAId, deckBId, 'Select two different decks for seat-paired comparison');

  const fields = (env.TWINLEAF_SEEDS || '20261012').split(',');
  assert.ok(fields.length > 0 && fields.length <= MAX_SEED_PAIRS,
    'Manual diagnostic may run at most ' + MAX_SEED_PAIRS + ' seed pairs');
  const seeds = fields.map(field => {
    const token = field.trim();
    assert.match(token, /^\d+$/, 'Seed must be an unsigned decimal integer');
    const seed = Number(token);
    assert.ok(Number.isSafeInteger(seed) && seed <= 0xffffffff, 'Seed must fit unsigned 32 bits');
    return seed;
  });
  assert.equal(new Set(seeds).size, seeds.length, 'Seed pairs must be distinct');
  return {deckAId, deckBId, seeds};
}

module.exports = {MAX_SEED_PAIRS, parseProbeSettings};
