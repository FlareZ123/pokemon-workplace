'use strict';
const assert=require('node:assert/strict');
const {loadTournamentDecks}=require('./tournament-deck-loader.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');
const {CardManager}=require('../../vendor/twinleafgg/ptcg-server/output/game/cards/card-manager');
function run() {
  const decks=loadTournamentDecks();
  assert.deepEqual(decks.map(d=>d.id),['vileplume','shadow_rider','regidrago','mew_genesect']);
  const runnable=decks.filter(d=>d.status==='strictly_mappable');
  assert.deepEqual(runnable.map(d=>d.id),['vileplume','shadow_rider','regidrago','mew_genesect']);
  for(const d of decks) {
    assert.deepEqual(d.blocked_prints,[]);
    assert.deepEqual(d.verified_text_aliases,
      ['shadow_rider','regidrago'].includes(d.id)?['xy4-92']:[]);
  }
  const manager=CardManager.getInstance();
  const byName=new Map(loadImplementedCards().map(c=>[c.fullName,c]));
  for(const d of runnable) {
    assert.equal(d.engine_names.length,60);
    for(const name of d.engine_names) {
      const original=byName.get(name);
      assert.ok(original,'Missing compiled prototype '+name);
      if(!manager.isCardDefined(name)) manager.defineCard(original);
      assert.equal(manager.getCardByName(name).fullName,name);
    }
    console.log('[tournament-loader] '+d.id+': 60 exact verified engine cards registered');
  }
  console.log('[tournament-loader] Battle Compressor source text alias independently verified for Shadow Rider and Regidrago');
  console.log('[tournament-loader] PASS: four complete verified 60-card engine lists without silent print substitution');
}
try {run();} catch(error) {console.error('[tournament-loader] FAIL',error);process.exitCode=1;}
