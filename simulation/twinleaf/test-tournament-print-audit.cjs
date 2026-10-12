'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {ROOT,parseDecks,loadDecks}=require('./tournament-baselines.cjs');
const {audit}=require('./tournament-print-audit.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
/** @returns {Array<object>} Twinleaf engine print objects from pinned compiled sets. */
function implementedCards() {
  const sets=require('../../vendor/twinleafgg/ptcg-server/output/sets'),seen=new Map();
  for(const [name,cards] of Object.entries(sets)) {
    if(!name.startsWith('set') || !Array.isArray(cards)) continue;
    for(const c of cards) {
      if(!c || typeof c.fullName!=='string') continue;
      if(seen.has(c.fullName) && seen.get(c.fullName)!==c) throw Error('Twinleaf duplicate fullName '+c.fullName);
      seen.set(c.fullName,c);
    }
  }
  if(seen.size===0) throw Error('No Twinleaf compiled cards');
  return [...seen.values()];
}
/** Write machine-readable CI diagnostics atomically under an exclusive lock. @param {string} target @param {object} report */
function save(target,report) {
  const lock=target+'.lock',temp=target+'.'+process.pid+'.tmp',fd=fs.openSync(lock,'wx');
  try {fs.writeFileSync(temp,JSON.stringify(report,null,2)+'\n');fs.renameSync(temp,target);}
  finally {fs.closeSync(fd);fs.rmSync(lock);if(fs.existsSync(temp))fs.rmSync(temp);}
}
function main() {
  assert.throws(()=>parseDecks('## No decks\n'),/Expected 4/);
  const decks=loadDecks();
  assert.deepEqual(decks.map(d=>d.id),['vileplume','shadow_rider','regidrago','mew_genesect']);
  const dummy=[{set:'CRE',setNumber:'75',name:'Shadow Rider Calyrex VMAX',fullName:'Shadow Rider Calyrex VMAX CRE',attacks:[{name:'Max Geist'}],powers:[{name:'Underworld Door'}]}];
  const mock=audit([{id:'test',cards:[{quantity:1,name:'Shadow Rider Calyrex VMAX',print_id:'swsh6-75'}]}],
    [{id:'swsh6',ptcgoCode:'CRE'}],dummy,()=>[{id:'swsh6-75',name:'Shadow Rider Calyrex VMAX',attacks:[{name:'Max Geist'}],abilities:[{name:'Underworld Door'}]}]);
  assert.equal(mock[0].matching_copies,1);
  const missing=audit([{id:'test',cards:[{quantity:1,name:'Shadow Rider Calyrex VMAX',print_id:'swsh6-75'}]}],
    [{id:'swsh6',ptcgoCode:'CRE'}],[],()=>[{id:'swsh6-75',name:'Shadow Rider Calyrex VMAX'}]);
  assert.equal(missing[0].cards[0].status,'missing_print');
  const implemented=implementedCards();
  const report={twinleaf_pin:'3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    scope:'Exact print availability and attack/Ability names only; no behavioral parity or win rates',
    engine_card_count:implemented.length,
    decks:audit(decks,read(path.join(ROOT,'resources/sets/en.json')),implemented,
      id=>read(path.join(ROOT,'resources/cards/en',id+'.json')))};
  for(const d of report.decks) {
    console.log('[Twinleaf '+d.id+'] '+d.matching_prints+'/'+d.total_prints+' prints; '+d.matching_copies+'/60 copies');
    for(const c of d.cards.filter(c=>c.status!=='signature_match'))
      console.log('  '+c.print_id+' '+c.name+': '+c.status);
  }
  if(process.argv[2]) save(path.resolve(process.argv[2]),report);
  console.log('[Twinleaf] PASS: source decks and exact-print diagnostics generated');
}
try {main();} catch(err) {console.error('[Twinleaf] FAIL',err);process.exitCode=1;}
