'use strict';
const assert = require('node:assert/strict');
const {parseProbeSettings, MAX_SEED_PAIRS} = require('./tournament-probe-settings.cjs');
const ids = ['vileplume', 'shadow_rider', 'regidrago', 'mew_genesect', 'mew_genesect_vip4', 'regidrago_dragapult_2'];
const original = parseProbeSettings({}, ids);
assert.deepEqual(original, {deckAId: 'vileplume', deckBId: 'mew_genesect', seeds: [20261012], tacticOrder: 'native'});
const swapped = parseProbeSettings({
  TWINLEAF_DECK_A: 'shadow_rider',
  TWINLEAF_DECK_B: 'regidrago',
  TWINLEAF_SEEDS: ' 0, 20261012, 4294967295 '
}, ids);
assert.deepEqual(swapped, {
  deckAId: 'shadow_rider', deckBId: 'regidrago', seeds: [0, 20261012, 4294967295], tacticOrder: 'native'
});
assert.deepEqual(parseProbeSettings({
  TWINLEAF_DECK_A:'mew_genesect',
  TWINLEAF_DECK_B:'mew_genesect_vip4',
  TWINLEAF_SEEDS:'20261012'
},ids), {
  deckAId:'mew_genesect', deckBId:'mew_genesect_vip4', seeds:[20261012], tacticOrder:'native'
});
assert.deepEqual(parseProbeSettings({
  TWINLEAF_DECK_A:'regidrago',
  TWINLEAF_DECK_B:'regidrago_dragapult_2',
  TWINLEAF_SEEDS:'20261012'
},ids), {
  deckAId:'regidrago', deckBId:'regidrago_dragapult_2', seeds:[20261012], tacticOrder:'native'
});
assert.equal(MAX_SEED_PAIRS, 3);
assert.equal(parseProbeSettings({TWINLEAF_TACTIC_ORDER:'attack_before_retreat'},ids).tacticOrder,
  'attack_before_retreat');
for (const env of [
  {TWINLEAF_DECK_A: 'invalid'},
  {TWINLEAF_DECK_B: 'invalid'},
  {TWINLEAF_DECK_B: 'vileplume'},
  {TWINLEAF_SEEDS: '1,2,3,4'},
  {TWINLEAF_SEEDS: '5,5'},
  {TWINLEAF_SEEDS: '5,'},
  {TWINLEAF_SEEDS: '-1'},
  {TWINLEAF_SEEDS: '2.4'},
  {TWINLEAF_SEEDS: '4e2'},
  {TWINLEAF_SEEDS: '4294967296'},
  {TWINLEAF_TACTIC_ORDER: 'skip_all_actions'},
]) assert.throws(() => parseProbeSettings(env, ids), undefined, JSON.stringify(env));
console.log('[tournament-settings] PASS: verified defaults, four source decks, distinct uint32 seed pairs and CI workload ceiling');
