'use strict';

const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const manifest = require('../../results/verified_card_metadata_boundary/overrides.json');
const {
  normalizeVerifiedCardMetadata,
  AUDITED_CARD_METADATA_IDS,
} = require('./verified-card-metadata.cjs');

const ROOT = path.resolve(__dirname, '..', '..');
const SETS = ['me5', 'me2pt5', 'me3', 'sv5', 'sv6', 'sv8pt5'];

/** @type {Map<string, Record<string, unknown>>} */
const cards = new Map();
for (const setId of SETS) {
  const input = readFileSync(path.join(ROOT, 'resources', 'cards', 'en', setId + '.json'), 'utf8');
  for (const card of JSON.parse(input)) cards.set(card.id, card);
}

assert.equal(AUDITED_CARD_METADATA_IDS.length, 72);
assert.deepEqual(AUDITED_CARD_METADATA_IDS, Object.keys(manifest.patches));
/** @type {Record<string, number>} */
const countBySet = {};

for (const id of AUDITED_CARD_METADATA_IDS) {
  assert.ok(cards.has(id), 'Missing source print: ' + id);
  const raw = cards.get(id);
  const oldSource = structuredClone(raw);
  const corrected = normalizeVerifiedCardMetadata(raw);
  for (const [field, patch] of Object.entries(manifest.patches[id])) {
    assert.deepEqual(raw[field] ?? null, patch.before, id + ' before.' + field);
    assert.deepEqual(corrected[field], patch.after, id + ' after.' + field);
  }
  assert.deepEqual(raw, oldSource, id + ' source immutability');
  assert.strictEqual(normalizeVerifiedCardMetadata(corrected), corrected, id + ' idempotence');
  const setId = id.split('-')[0];
  countBySet[setId] = (countBySet[setId] || 0) + 1;
}

const unaffected = cards.get('me2pt5-11');
assert.ok(unaffected);
assert.strictEqual(normalizeVerifiedCardMetadata(unaffected), unaffected);

const corrupted = structuredClone(cards.get('me2pt5-89'));
corrupted.rules[0] = 'Unexpected changed Rule Box';
assert.throws(() => normalizeVerifiedCardMetadata(corrupted), /source text changed/);

console.log('verified print metadata CJS parity: PASS');
console.log('Audited print count:', AUDITED_CARD_METADATA_IDS.length);
console.log('Patch distribution:', JSON.stringify(countBySet));
console.log('Corruption guard and original-source immutability: PASS');
