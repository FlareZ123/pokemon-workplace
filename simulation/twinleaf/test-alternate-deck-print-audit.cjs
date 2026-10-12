'use strict';
const assert=require('node:assert/strict');
const {
  auditAlternativeTournamentLists,SOURCE_DECKS
}=require('./alternate-deck-print-audit.cjs');
const report=auditAlternativeTournamentLists();
assert.equal(report.twinleaf_pin,'3348ebdc898f175a2ed8f999133cd13d1afd01f5');
assert.deepEqual(report.decks.map(x=>x.id),Object.keys(SOURCE_DECKS));
for(const deck of report.decks) {
  assert.equal(deck.total_copies,60);
  assert.ok(deck.total_prints>=20);
  assert.ok(deck.exact_signature_matched_copies>=0 &&
    deck.exact_signature_matched_copies<=60);
  const unresolvedCopies=deck.unresolved.reduce((n,x)=>n+x.copies,0);
  assert.equal(deck.exact_signature_matched_copies+unresolvedCopies,60,
    'Every real source print must be counted exactly once: '+deck.id);
  assert.equal(deck.strict_mapping_possible,unresolvedCopies===0);
  console.log('[alternate-aichi] '+deck.id+': '+
    deck.exact_signature_matched_copies+'/60 copies strictly signature-mapped, '+
    deck.unresolved.length+' unresolved exact prints');
}
console.log('[alternate-aichi] PASS: 3 English 60-card source manifests fully audited without invented print aliases');
