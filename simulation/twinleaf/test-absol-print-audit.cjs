'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {audit}=require('./tournament-print-audit.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');

const ROOT=path.resolve(__dirname,'../..');
/** @param {string} file @returns {any} */
const read=file=>JSON.parse(fs.readFileSync(file,'utf8'));

/** Write atomically under an exclusive sidecar lock. @param {string} target @param {object} value */
function save(target,value) {
  const lock=target+'.lock',temp=target+'.'+process.pid+'.tmp';
  const fd=fs.openSync(lock,'wx');
  try {
    fs.writeFileSync(temp,JSON.stringify(value,null,2)+'\n');
    fs.renameSync(temp,target);
  } finally {
    fs.closeSync(fd);fs.rmSync(lock);
    if(fs.existsSync(temp))fs.rmSync(temp);
  }
}
/** @returns {void} */
function main() {
  const source=read(path.join(ROOT,'results/competitive_deck_baselines/absol_garbodor_kobayashi_2026.json'));
  assert.equal(source.source.date,'2026-05-10');
  assert.equal(source.source.place,8);
  assert.equal(source.cards.length,37);
  assert.equal(source.cards.reduce((n,c)=>n+c.quantity,0),60);
  assert.equal(new Set(source.cards.map(c=>c.print_id)).size,37);
  const byId=new Map(source.cards.map(c=>[c.print_id,c]));
  assert.equal(byId.get('me1-86').quantity,2);
  assert.equal(byId.get('swsh3-104').quantity,1);
  assert.equal(byId.get('bw11-68').quantity,2);
  assert.equal(byId.get('swsh12-156').quantity,1);

  const engine=loadImplementedCards();
  const deck={id:'absol_garbodor',cards:source.cards.map(c=>({
    quantity:c.quantity,name:c.name,print_id:c.print_id
  }))};
  const report=audit(
    [deck],
    read(path.join(ROOT,'resources/sets/en.json')),
    engine,
    id=>read(path.join(ROOT,'resources/cards/en',id+'.json'))
  )[0];
  assert.equal(report.total_copies,60);
  assert.equal(report.total_prints,37);
  assert.equal(report.cards.length,37);
  assert.equal(report.cards.reduce((n,c)=>n+c.quantity,0),60);
  const failures=report.cards.filter(c=>c.status!=='signature_match');
  console.log('[Aichi Absol/Garbodor] '+report.matching_prints+'/37 exact-print signatures; '+report.matching_copies+'/60 physical copies');
  for(const c of failures) {
    console.log('[print blocker] '+c.print_id+' '+c.name+' x'+c.quantity+' -> '+c.status);
  }
  const output={
    engine_pin:'3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    deck_source:source.source,
    scope:'Paper print/engine signature audit only, not gameplay semantics or winning',
    engine_card_count:engine.length,
    summary:{
      matching_copies:report.matching_copies,
      total_copies:report.total_copies,
      matching_prints:report.matching_prints,
      total_prints:report.total_prints,
      blocked_prints:failures.length
    },
    report
  };
  if(process.argv[2])save(path.resolve(process.argv[2]),output);
  console.log('[Aichi Absol/Garbodor] PASS: full published 60 audited without replacement aliases');
}
try{main();}catch(error){console.error('[Aichi Absol/Garbodor] FAIL',error);process.exitCode=1;}
