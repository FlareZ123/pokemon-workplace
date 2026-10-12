'use strict';
const assert=require('node:assert/strict');
const {loadAbsolTwinleaf}=require('./absol-twinleaf-deck.cjs');
const {verifyTapuKokoPrismLabel}=require('./absol-print-verified-aliases.cjs');
const {registerLists,runOne}=require('./tournament-bounded-match.cjs');
const {deckDigest}=require('./paired-seat-plan.cjs');
/** @returns {void} */
function main() {
  // A name resemblance without the same exact print and engine Prism tag
  // must never authorize an unsupported physical card alias.
  assert.equal(verifyTapuKokoPrismLabel({
    print_id:'sm9-51',name:'Tapu Koko ◇',status:'missing_print',
    engine_candidates:[{fullName:'Tapu Koko Prism Star TEU'}]
  },new Map()),null);
  const deck=loadAbsolTwinleaf();
  assert.equal(deck.status,'verified_full_print_mapping');
  assert.deepEqual(deck.verified_aliases.sort(),['sm9-51','xy4-92']);
  assert.equal(deck.engine_names.length,60);
  assert.equal(deck.blocked_prints.length,0);
  registerLists([deck.engine_names]);
  const trace=runOne(deck.engine_names,deck.engine_names,20261012,350,20000);
  const report={
    id:deck.id,
    pinned_engine:'3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    scope:'source-verified print-name mapping and one bounded SimpleTacticsAi self-play diagnostic; no validated matchup strength',
    deck_digest:deckDigest(deck),
    verified_name_aliases:deck.verified_aliases,
    cards:deck.engine_names.length,
    trace
  };
  assert.ok(trace.turn>=1,'Must reach an actual Twinleaf player turn');
  console.log('[Aichi Absol headless] '+JSON.stringify(report));
  console.log('[Aichi Absol headless] PASS: all exact source-printed names map with two independently verified same-print aliases');
}
try{main();}catch(e){console.error('[Aichi Absol headless] FAIL',e);process.exitCode=1;}
