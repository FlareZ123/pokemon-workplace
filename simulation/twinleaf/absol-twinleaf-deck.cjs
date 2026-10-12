'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {audit}=require('./tournament-print-audit.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');
const {resolveAbsolPrints}=require('./absol-print-verified-aliases.cjs');

const ROOT=path.resolve(__dirname,'../..');
/** @param {string} file @returns {any} */
const read=file=>JSON.parse(fs.readFileSync(file,'utf8'));
/**
 * Read the published source's exact paper prints, verify mapped Twinleaf
 * signatures and two individually audited same-print label aliases.
 * @returns {{id:string,status:string,engine_names:string[],blocked_prints:Array<object>,verified_aliases:string[]}}
 */
function loadAbsolTwinleaf() {
  const source=read(path.join(ROOT,'results/competitive_deck_baselines/absol_garbodor_kobayashi_2026.json'));
  assert.equal(source.cards.length,37);
  assert.equal(source.cards.reduce((n,c)=>n+c.quantity,0),60);
  const engines=loadImplementedCards(),byName=new Map(engines.map(c=>[c.fullName,c]));
  const checked=audit([{
    id:'absol_garbodor',cards:source.cards.map(c=>({
      quantity:c.quantity,name:c.name,print_id:c.print_id
    }))
  }],read(path.join(ROOT,'resources/sets/en.json')),engines,
  id=>read(path.join(ROOT,'resources/cards/en',id+'.json')))[0];
  const output=resolveAbsolPrints(checked.cards,byName);
  if(output.blocked.length===0)assert.equal(output.names.length,60);
  return {
    id:'absol_garbodor',
    status:output.blocked.length===0?'verified_full_print_mapping':'blocked',
    engine_names:output.names,
    blocked_prints:output.blocked,
    verified_aliases:output.resolved
      .filter(c=>c.resolution==='verified_print_name_alias')
      .map(c=>c.print_id)
  };
}
module.exports={loadAbsolTwinleaf};
