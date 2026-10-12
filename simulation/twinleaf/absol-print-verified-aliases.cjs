'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {verifyBattleCompressorLabel}=require('./baseline-deck-loader.cjs');

const ROOT=path.resolve(__dirname,'../..');
/**
 * Exact-print scoped name-equivalence evidence for Tapu Koko Prism Star TEU 51.
 * The paper snapshot encodes the Prisma symbol ◇, whereas pinned Twinleaf
 * renders the same print's descriptive suffix as "Prism Star".
 * This makes no claim about behavioral parity beyond the printed signatures.
 * @param {{print_id:string,name:string,status:string,engine_candidates?:Array<{fullName:string}>,source_attacks?:string[],engine_attacks?:string[],source_abilities?:string[],engine_powers?:string[]}} entry
 * @param {Map<string,object>} engines
 * @returns {string|null}
 */
function verifyTapuKokoPrismLabel(entry,engines) {
  if(entry.print_id!=='sm9-51' || entry.name!=='Tapu Koko ◇' ||
    entry.status!=='name_mismatch_review' ||
    entry.engine_candidates?.length!==1 ||
    entry.engine_candidates[0].fullName!=='Tapu Koko Prism Star TEU') return null;
  const paper=JSON.parse(fs.readFileSync(path.join(ROOT,'resources/cards/en/sm9.json'),'utf8'))
    .find(c=>c.id===entry.print_id);
  const engine=engines.get('Tapu Koko Prism Star TEU');
  assert.ok(paper&&engine,'Both exact Tapu Koko print records must exist');
  assert.equal(paper.supertype,'Pokémon');
  assert.ok(paper.subtypes.includes('Basic')&&paper.subtypes.includes('Prism Star'));
  assert.equal(paper.name,entry.name);
  assert.ok(paper.rules.some(r=>r.includes('◇ (Prism Star) Rule:')));
  assert.equal(engine.name,'Tapu Koko Prism Star');
  assert.equal(engine.set,'TEU');
  assert.equal(String(engine.setNumber),'51');
  assert.ok(engine.tags.includes('Prism Star'),'Engine must retain restrictive Prism Star rule');
  assert.equal(engine.hp,130);
  assert.deepEqual(engine.attacks.map(a=>a.name),paper.attacks.map(a=>a.name));
  assert.deepEqual(paper.abilities.map(a=>a.name),engine.powers.map(p=>p.name));
  return engine.fullName;
}

/**
 * Checked literal or reviewed display-name mapping for the fifth tournament 60.
 * @param {Array<object>} audited
 * @param {Map<string,object>} engines
 * @returns {{resolved:Array<object>,names:string[],blocked:Array<object>}}
 */
function resolveAbsolPrints(audited,engines) {
  const resolved=audited.map(entry=>{
    let name=entry.twinleaf_full_name||null;
    if(!name && entry.print_id==='xy4-92') {
      name=verifyBattleCompressorLabel({
        printId:entry.print_id,name:entry.name,status:entry.status,
        matches:entry.engine_candidates||[],
      },engines);
    }
    if(!name && entry.print_id==='sm9-51')
      name=verifyTapuKokoPrismLabel(entry,engines);
    return {...entry,resolved_full_name:name,resolution:
      entry.twinleaf_full_name?'exact_signature':
      name?'verified_print_name_alias':'blocked'};
  });
  const blocked=resolved.filter(c=>!c.resolved_full_name);
  const names=resolved.flatMap(c=>c.resolved_full_name?
    Array(c.quantity).fill(c.resolved_full_name):[]);
  return {resolved,names,blocked};
}
module.exports={verifyTapuKokoPrismLabel,resolveAbsolPrints};
