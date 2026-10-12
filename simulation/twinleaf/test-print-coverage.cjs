'use strict';

const assert = require('node:assert/strict');
const {
  parseBaselineDecks, matchPaperPrint, auditAichiBaselines, makePaperSetCodes
} = require('./print-coverage.cjs');

/** @returns {void} */
function run() {
  const sample = [
    '## 2026 Aichi champion: Shadow Rider Calyrex',
    ...Array.from({ length: 20 }, (_, i) => `| 3 | Test ${i} | sm5-${i + 1} |`),
    '## Some other heading'
  ].join('\n');
  assert.throws(() => parseBaselineDecks(sample), /Incomplete vileplume baseline/);

  const paperSets = new Map([['swsh6', 'CRE']]);
  const examples = [
    { set: 'CRE', setNumber: '074', name: 'Shadow Rider Calyrex V', fullName: 'Shadow Rider Calyrex V CRE' },
    { set: 'CRE', setNumber: '75', name: 'Shadow Rider Calyrex VMAX', fullName: 'Shadow Rider Calyrex VMAX CRE' }
  ];
  const valid = matchPaperPrint({ qty: 3, name: 'Shadow Rider Calyrex V', printId: 'swsh6-74' }, paperSets, examples);
  assert.equal(valid.status, 'exact');
  assert.equal(valid.matches[0].fullName, examples[0].fullName);
  const resolvedPromoSets = makePaperSetCodes([
    { id: 'xyp', ptcgoCode: 'PR-XY' },
    { id: 'smp', ptcgoCode: 'PR-SM' },
    { id: 'swsh6', ptcgoCode: 'CRE' },
  ]);
  assert.equal(resolvedPromoSets.get('xyp'), 'XYP');
  assert.equal(resolvedPromoSets.get('smp'), 'SMP');
  assert.equal(resolvedPromoSets.get('swsh6'), 'CRE');
  assert.equal(makePaperSetCodes([
    { id: 'xyp', ptcgoCode: 'UNKNOWN' }
  ]).get('xyp'), 'UNKNOWN');
  const promoSets = resolvedPromoSets;
  const promoCards = [
    { set: 'XYP', setNumber: '177', name: 'Karen', fullName: 'Karen XYP' },
    { set: 'SMP', setNumber: '217', name: 'Trevenant & Dusknoir-GX',
      fullName: 'Trevenant & Dusknoir-GX SMP' }
  ];
  assert.equal(matchPaperPrint(
    { qty: 1, name: 'Karen', printId: 'xyp-XY177' }, promoSets, promoCards
  ).status, 'exact');
  assert.equal(matchPaperPrint(
    { qty: 1, name: 'Trevenant & Dusknoir-GX', printId: 'smp-SM217' },
    promoSets, promoCards
  ).status, 'exact');
  assert.equal(matchPaperPrint(
    { qty: 1, name: 'Karen', printId: 'xyp-XY178' }, promoSets, promoCards
  ).status, 'missing_print');
  assert.equal(matchPaperPrint(
    { qty: 1, name: 'Karen', printId: 'xyp-XY177' },
    new Map([['xyp', 'ABC']]), promoCards
  ).status, 'missing_print');

  const wrongName = matchPaperPrint({ qty: 3, name: 'Mewtwo', printId: 'swsh6-74' }, paperSets, examples);
  assert.equal(wrongName.status, 'name_mismatch_review');
  const unknown = matchPaperPrint({ qty: 1, name: 'Unknown', printId: 'foo-74' }, paperSets, examples);
  assert.equal(unknown.status, 'unmapped_set');
  const copycat = [{
    set: 'GRI', setNumber: '58', name: 'Mimikyu', fullName: 'Mimikyu GRI',
    attacks: [{ name: 'Copycat' }]
  }];
  assert.equal(matchPaperPrint({
    qty: 1, name: 'Mimikyu (Copycat)', printId: 'sm2-58'
  }, new Map([['sm2', 'GRI']]), copycat).status, 'qualified_exact');
  const basic = [{
    set: 'BLW', setNumber: '109', name: 'Psychic Energy', fullName: 'Psychic Energy BLW',
    energyType: 0
  }];
  assert.equal(matchPaperPrint({
    qty: 11, name: 'Basic Psychic Energy', printId: 'bw1-109'
  }, new Map([['bw1', 'BLW']]), basic).status, 'qualified_exact');

  const fusionMew=[{set:'FST',setNumber:'113',name:'Mew V',fullName:'Mew V FST',
    tags:['V','Fusion Strike'],attacks:[{name:'Energy Mix'},{name:'Psychic Leap'}]}];
  assert.equal(matchPaperPrint({qty:4,name:'Mew V (Fusion Strike)',printId:'swsh8-113'},
    new Map([['swsh8','FST']]),fusionMew).status,'qualified_exact');
  console.log('[print-coverage] Synthetic collision and set-resolution checks passed');

  const decks = auditAichiBaselines();
  for (const [name, entries] of Object.entries(decks)) {
    assert.equal(entries.reduce((sum, item) => sum + item.qty, 0), 60);
    const counts = {};
    for (const entry of entries) {
      counts[entry.status] = (counts[entry.status] ?? 0) + entry.qty;
    }
    console.log(`[print-coverage] ${name}: ${JSON.stringify(counts)}`);
    for (const entry of entries) {
      if (entry.status !== 'exact') {
        console.log(`[print-coverage] REVIEW ${name} ${entry.qty}x ${entry.printId} ${entry.name}: ${entry.status} ${JSON.stringify(entry.matches)}`);
      }
    }
  }

  const shadow = decks.shadow_rider;
  const v = shadow.find(entry => entry.printId === 'swsh6-74');
  const karen = decks.vileplume.find(entry => entry.printId === 'xyp-XY177');
  const trevenant = shadow.find(entry => entry.printId === 'smp-SM217');
  assert.equal(karen.status, 'exact');
  assert.equal(karen.matches[0].fullName, 'Karen XYP');
  assert.equal(trevenant.status, 'exact');
  assert.equal(trevenant.matches[0].fullName, 'Trevenant & Dusknoir-GX SMP');
  const vmax = shadow.find(entry => entry.printId === 'swsh6-75');
  assert.equal(v.status, 'exact');
  assert.equal(v.matches[0].fullName, 'Shadow Rider Calyrex V CRE');
  assert.equal(vmax.status, 'exact');
  assert.equal(vmax.matches[0].fullName, 'Shadow Rider Calyrex VMAX CRE');
  console.log('[print-coverage] PASS: pinned source semantics and conservative Aichi print coverage classified');
}

try {
  run();
} catch (error) {
  console.error('[print-coverage] FAIL:', error);
  process.exitCode = 1;
}
