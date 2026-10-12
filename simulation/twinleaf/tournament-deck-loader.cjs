'use strict';
const fs=require('node:fs');
const path=require('node:path');
const {ROOT,loadDecks}=require('./tournament-baselines.cjs');
const {audit}=require('./tournament-print-audit.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');
const {verifyBattleCompressorLabel}=require('./baseline-deck-loader.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
/** Translate source print IDs into pinned Twinleaf names with exact identity checks.
 * A unique Battle Compressor display alias is admitted only after independent
 * source-print type and full printed effect-text verification.
 * @returns {Array<object>}
 */
function loadTournamentDecks() {
  const baseline=loadDecks(),implemented=loadImplementedCards();
  const byFullName=new Map(implemented.map(c=>[c.fullName,c]));
  const checked=audit(baseline,read(path.join(ROOT,'resources/sets/en.json')),implemented,
    id=>read(path.join(ROOT,'resources/cards/en',id+'.json')));
  return checked.map(d=>{
    const resolved=d.cards.map(c=>{
      if(c.status==='signature_match')return c;
      const alias=verifyBattleCompressorLabel({printId:c.print_id,name:c.name,
        status:c.status,matches:c.engine_candidates||[]},byFullName);
      return alias?{...c,status:'verified_text_alias',twinleaf_full_name:alias}:c;
    });
    const blocked=resolved.filter(c=>!['signature_match','verified_text_alias'].includes(c.status));
    const names=resolved.flatMap(c=>c.twinleaf_full_name?Array(c.quantity).fill(c.twinleaf_full_name):[]);
    if(blocked.length===0 && names.length!==60)throw Error('Internal deck expansion mismatch '+d.id);
    return {id:d.id,status:blocked.length===0?'strictly_mappable':'blocked',
      engine_names:names,blocked_prints:blocked,
      verified_text_aliases:resolved.filter(c=>c.status==='verified_text_alias').map(c=>c.print_id),
      total_selected_copies:60};
  });
}
module.exports={loadTournamentDecks};
