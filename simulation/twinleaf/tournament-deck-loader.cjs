'use strict';
const fs=require('node:fs');
const path=require('node:path');
const {ROOT,loadDecks}=require('./tournament-baselines.cjs');
const {audit}=require('./tournament-print-audit.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
/** Resolve source-verified English print IDs into pinned Twinleaf fullNames.
 * Return a blocking diagnostic rather than substituting missing or ambiguous cards.
 * @returns {Array<{id:string,status:string,engine_names:string[],blocked_prints:Array<object>}>}
 */
function loadTournamentDecks() {
  const baseline=loadDecks(),implemented=loadImplementedCards();
  const checked=audit(baseline,read(path.join(ROOT,'resources/sets/en.json')),implemented,
    id=>read(path.join(ROOT,'resources/cards/en',id+'.json')));
  return checked.map(d=>{
    const blocked=d.cards.filter(c=>c.status!=='signature_match');
    const names=d.cards.flatMap(c=>c.status==='signature_match'
      ? Array(c.quantity).fill(c.twinleaf_full_name) : []);
    if(blocked.length===0 && names.length!==60) throw Error('Internal deck expansion mismatch '+d.id);
    return {id:d.id,status:blocked.length===0?'strictly_mappable':'blocked',
      engine_names:names,blocked_prints:blocked,total_selected_copies:60};
  });
}
module.exports={loadTournamentDecks};
