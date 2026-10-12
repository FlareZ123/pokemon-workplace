'use strict';

const { isDeepStrictEqual } = require('node:util');
const manifest = require('../../results/verified_card_metadata_boundary/overrides.json');

/**
 * Apply audited English-card archive field corrections to one source card.
 * Source records and static manifest entries are never mutated.
 *
 * @param {{ id: string, [key: string]: unknown }} card
 * @returns {{ id: string, [key: string]: unknown }}
 */
function normalizeVerifiedCardMetadata(card) {
  const changes = manifest.patches[card.id];
  if (!changes) return card;

  let corrected = card;
  for (const [field, patch] of Object.entries(changes)) {
    const actual = card[field] === undefined ? null : card[field];
    if (isDeepStrictEqual(actual, patch.after)) continue;
    if (!isDeepStrictEqual(actual, patch.before)) {
      throw new Error('Audited card source text changed: ' + card.id + ' (' + field + ')');
    }
    if (corrected === card) corrected = { ...card };
    corrected[field] = Array.isArray(patch.after) ? patch.after.slice() : patch.after;
  }
  return corrected;
}

module.exports = {
  normalizeVerifiedCardMetadata,
  AUDITED_CARD_METADATA_IDS: Object.freeze(Object.keys(manifest.patches)),
};
