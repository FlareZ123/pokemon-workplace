'use strict';
const fs = require('node:fs');
const path = require('node:path');
const {ROOT,loadDecks} = require('./tournament-baselines.cjs');
const PROMOS = {'PR-SM':'SMP','PR-XY':'XYP','PR-BW':'BWP'};
/** Index exact engine print identity, retaining collisions for explicit audit. @param {Array<object>} cards */
function indexEngine(cards) {
  const index = new Map();
  for (const card of cards) {
    const key = [card.set,card.setNumber,card.name].join('|');
    index.set(key,[...(index.get(key)||[]),card]);
  }
  return index;
}
/** Audit exact print coverage and attack/Ability names. No behavioral or match strength certification. */
function audit(decks, metadata, engineCards, getSourceSet) {
  const codes=new Map(metadata.map(s=>[s.id,s.ptcgoCode]));
  const engine=indexEngine(engineCards), source=new Map();
  for(const id of new Set(decks.flatMap(d=>d.cards.map(c=>c.print_id.slice(0,c.print_id.lastIndexOf('-')))))) {
    for (const card of getSourceSet(id)) source.set(card.id,card);
  }
  return decks.map(deck=>{
    const cards=deck.cards.map(c=>{
      const cut=c.print_id.lastIndexOf('-'),setId=c.print_id.slice(0,cut),number=c.print_id.slice(cut+1);
      const printed=source.get(c.print_id);
      if(!printed || printed.name!==c.name) throw Error('Print/name mismatch: '+c.print_id);
      const raw=codes.get(setId), set=PROMOS[raw]||raw;
      if(!set) return {...c,status:'missing_set_code'};
      const exact=engine.get([set,number,c.name].join('|'))||[];
      if(exact.length!==1) return {...c,status:exact.length?'ambiguous_print':'missing_engine_print',engine_set:set};
      const imp=exact[0],expectedAttacks=(printed.attacks||[]).map(a=>a.name),actualAttacks=(imp.attacks||[]).map(a=>a.name),
        expectedAbilities=(printed.abilities||[]).map(a=>a.name),actualPowers=(imp.powers||[]).map(p=>p.name);
      const attacksMatch=expectedAttacks.length===actualAttacks.length && expectedAttacks.every((a,i)=>a===actualAttacks[i]);
      const abilitiesMatch=expectedAbilities.every(a=>actualPowers.includes(a));
      return {...c,status:attacksMatch&&abilitiesMatch?'signature_match':'signature_mismatch',
        twinleaf_full_name:imp.fullName,source_attacks:expectedAttacks,engine_attacks:actualAttacks,
        source_abilities:expectedAbilities,engine_powers:actualPowers};
    });
    const matches=cards.filter(c=>c.status==='signature_match');
    return {id:deck.id,total_copies:60,total_prints:cards.length,
      matching_copies:matches.reduce((n,c)=>n+c.quantity,0),matching_prints:matches.length,
      fully_mapped:matches.length===cards.length,cards};
  });
}
module.exports={audit,indexEngine};
