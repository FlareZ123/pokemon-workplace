'use strict';
const assert=require('node:assert/strict');
const {loadTournamentDecks}=require('./tournament-deck-loader.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');
const {CardManager}=require('../../vendor/twinleafgg/ptcg-server/output/game/cards/card-manager');
function run() {
  const decks=loadTournamentDecks();
  assert.deepEqual(decks.map(d=>d.id),['vileplume','shadow_rider','regidrago','mew_genesect']);
  const runnable=decks.filter(d=>d.status==='strictly_mappable');
  assert.deepEqual(runnable.map(d=>d.id),['vileplume','mew_genesect']);
  for(const d of decks.filter(d=>d.status==='blocked')) {
    assert.equal(d.blocked_prints.length,1);
    assert.equal(d.blocked_prints[0].print_id,'xy4-92');
    assert.equal(d.blocked_prints[0].status,'name_mismatch_review');
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
  console.log('[tournament-loader] Unresolved printed-name aliases correctly block Shadow Rider and Regidrago');
  console.log('[tournament-loader] PASS: no silent tournament print substitution');
}
try {run();} catch(error) {console.error('[tournament-loader] FAIL',error);process.exitCode=1;}
