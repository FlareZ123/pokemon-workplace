'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {audit}=require('./tournament-print-audit.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');
const {writeReportAtomic}=require('./report-atomic.cjs');

const ROOT=path.resolve(__dirname,'../..');
const SOURCE_DECKS={
  raichu_electrode:'results/decks/raichu-electrode-aichi-2026/manifest.json',
  iron_thorns_english:'results/decks/iron_thorns_aichi_english/manifest.json',
  snorlax_stall_english:'results/decks/snorlax-stall-aichi-2026-english/manifest.json'
};
/** @param {string} filename */
function read(filename) {
  return JSON.parse(fs.readFileSync(path.join(ROOT,filename),'utf8'));
}

/**
 * Audit only truly supplied paper prints and actual pinned engine signatures.
 * This is a coverage census, not permission to alias any same-name print.
 * @returns {object}
 */
function auditAlternativeTournamentLists() {
  const names=Object.entries(SOURCE_DECKS).map(([id,filename])=>{
    const manifest=read(filename);
    assert.ok(Array.isArray(manifest.cards),id+' must have a card manifest');
    assert.equal(manifest.cards.reduce((n,c)=>n+c.quantity,0),60,
      id+' must preserve sixty physical source prints');
    assert.equal(new Set(manifest.cards.map(c=>c.print_id)).size,
      manifest.cards.length,id+' has duplicate print rows');
    return {
      id,cards:manifest.cards.map(c=>({
        name:c.name,quantity:c.quantity,print_id:c.print_id
      }))
    };
  });
  const implemented=loadImplementedCards();
  const full=audit(names,read('resources/sets/en.json'),
    implemented,setId=>read('resources/cards/en/'+setId+'.json'));
  const decks=full.map(x=>({
    id:x.id,total_prints:x.total_prints,
    exact_signature_matched_copies:x.matching_copies,
    total_copies:60,
    strict_mapping_possible:x.fully_mapped,
    unresolved:x.cards.filter(c=>c.status!=='signature_match').map(c=>({
      name:c.name,print_id:c.print_id,copies:c.quantity,
      status:c.status,candidates:c.engine_candidates||[],
      source_attacks:c.source_attacks||[],
      engine_attacks:c.engine_attacks||[]
    }))
  }));
  return {
    research_scope:'source English paper 60s checked against pinned Twinleaf; strict signature matching only',
    twinleaf_pin:'3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    decks
  };
}

if(require.main===module){
  try{
    const report=auditAlternativeTournamentLists();
    if(process.env.TWINLEAF_ALTERNATE_COVERAGE_PATH)
      writeReportAtomic(process.env.TWINLEAF_ALTERNATE_COVERAGE_PATH,report);
    console.log('[alternate-paper-print-audit] '+JSON.stringify(report));
    console.log('[alternate-paper-print-audit] PASS: all source 60-card manifest compositions checked without guesswork');
  }catch(error){console.error('[alternate-paper-print-audit] FAIL',error);process.exitCode=1;}
}
module.exports={auditAlternativeTournamentLists,SOURCE_DECKS};
