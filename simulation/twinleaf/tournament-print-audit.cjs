'use strict';
const {makePaperSetCodes,matchPaperPrint}=require('./print-coverage.cjs');
/** Match signed physical prints using the shared normalization for promos, Energy and role-qualified labels. */
function audit(decks,metadata,engineCards,getSourceSet) {
  const codes=makePaperSetCodes(metadata);
  const byFullName=new Map(engineCards.map(c=>[c.fullName,c]));
  const source=new Map();
  for(const setId of new Set(decks.flatMap(d=>d.cards.map(c=>c.print_id.slice(0,c.print_id.lastIndexOf('-')))))) {
    for(const c of getSourceSet(setId)) source.set(c.id,c);
  }
  return decks.map(deck=>{
    const cards=deck.cards.map(c=>{
      const print=source.get(c.print_id);
      if(!print) throw Error('Missing exact source print '+c.print_id);
      const found=matchPaperPrint({qty:c.quantity,name:c.name,printId:c.print_id},codes,engineCards);
      if(!['exact','qualified_exact'].includes(found.status))
        return {...c,status:found.status,engine_candidates:found.matches};
      const impl=byFullName.get(found.matches[0].fullName);
      if(!impl) throw Error('Engine mapping inconsistency '+found.matches[0].fullName);
      const srcAttacks=(print.attacks||[]).map(a=>a.name), engineAttacks=(impl.attacks||[]).map(a=>a.name),
        srcAbilities=(print.abilities||[]).map(a=>a.name), enginePowers=(impl.powers||[]).map(a=>a.name);
      const attacksMatch=srcAttacks.length===engineAttacks.length && srcAttacks.every((a,i)=>a===engineAttacks[i]);
      const abilitiesMatch=srcAbilities.every(a=>enginePowers.includes(a));
      return {...c,status:attacksMatch&&abilitiesMatch?'signature_match':'signature_mismatch',
        twinleaf_full_name:impl.fullName,paper_print_status:found.status,source_attacks:srcAttacks,
        engine_attacks:engineAttacks,source_abilities:srcAbilities,engine_powers:enginePowers};
    });
    const matched=cards.filter(c=>c.status==='signature_match');
    return {id:deck.id,total_copies:60,total_prints:cards.length,
      matching_copies:matched.reduce((n,c)=>n+c.quantity,0),matching_prints:matched.length,
      fully_mapped:matched.length===cards.length,cards};
  });
}
module.exports={audit};
