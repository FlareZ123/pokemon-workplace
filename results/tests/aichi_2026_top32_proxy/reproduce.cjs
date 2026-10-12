'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {
  validateField,extremalFieldScore
}=require('../../../tools/uncertain_metagame_field.cjs');

const source=JSON.parse(fs.readFileSync(path.join(__dirname,'data.json'),'utf8'));
assert.equal(source.date,'2026-05-10');
assert.equal(source.participants,926);
assert.equal(source.counts.length,13);
assert.equal(source.source_statistics,
  'https://limitlesstcg.com/tournaments/566/statistics');
assert.equal(new Set(source.counts.map(r=>r.id)).size,source.counts.length);
assert.ok(source.counts.every(r=>Number.isInteger(r.count)&&r.count>0));
assert.equal(source.counts.reduce((n,r)=>n+r.count,0),32);
assert.equal(source.counts[0].id,'regidrago');
assert.equal(source.counts[0].count,11);

const field=source.counts.map(r=>({
  id:r.id,lower:r.count/32,upper:r.count/32
}));
validateField(field);
const selectable=source.counts.map(r=>Number(r.manual_matchup_selectable));
const curated=source.counts.map(r=>Number(r.curated_reference));
const selectMass=extremalFieldScore(field,selectable,false);
const curatedMass=extremalFieldScore(field,curated,true);
assert.equal(selectMass.score,14/32);
assert.equal(curatedMass.score,27/32);
assert.deepEqual(source.counts.filter(r=>!r.manual_matchup_selectable)
  .map(r=>r.count).reduce((n,c)=>n+c,0),18);
assert.equal(source.counts.filter(r=>!r.curated_reference).length,5);
assert.equal(source.counts.filter(r=>!r.curated_reference)
  .reduce((n,r)=>n+r.count,0),5);

const result={
  event:source.event,
  event_participants:source.participants,
  reported_ranked_decks:32,
  archetypes:source.counts.length,
  top32_share:{
    regidrago:11/32,mega_absol_box:5/32,
    iron_thorns:3/32,raichu_electrode:3/32
  },
  headless_selectable_archetype_mass:selectMass.score,
  headless_unselectable_archetype_mass:1-selectMass.score,
  curated_archetype_mass:curatedMass.score,
  curated_missing_archetype_mass:1-curatedMass.score,
  interpretation:'Shares are among thirty-two published high finishes in a 926-player Japanese event; they are not deck usage frequencies for all entrants and are not matchup win rates.'
};
console.log('[aichi-top32-proxy] '+JSON.stringify(result,null,2));
console.log('[aichi-top32-proxy] PASS: source counts, universe, reproducible mixture and present tooling coverage');
