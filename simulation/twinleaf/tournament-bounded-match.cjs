'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const engine=p=>require(path.join(base,p));
const {loadTournamentDecks}=require('./tournament-deck-loader.cjs');
const {makeSeatPairs,deckDigest}=require('./paired-seat-plan.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');
const {CardManager}=engine('game/cards/card-manager');
const {Store}=engine('game/store/store');
const {Format}=engine('game/store/card/card-types');
const {GamePhase}=engine('game/store/state/state');
const {AddPlayerAction}=engine('game/store/actions/add-player-action');
const {SimpleTacticsAi}=engine('simple-bot/simple-tactics-ai');
const {BotArbiter,BotFlipMode,BotShuffleMode}=engine('game/bots/bot-arbiter');
const {allSimpleTactics,allPromptResolvers,defaultStateScores,defaultArbiterOptions}=engine('simple-bot/simple-bot-definitions');
/** Deterministic draw for a bounded execution trace. @param {number} seed */
function seededRandom(seed) {
  let n=seed>>>0;
  return ()=>{n=(n+0x6D2B79F5)>>>0;let t=n;
    t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);
    return ((t^(t>>>14))>>>0)/4294967296;};
}
/** Register every exact implementation used by the two source lists once. @param {string[][]} lists */
function registerLists(lists) {
  const manager=CardManager.getInstance();
  const instances=new Map(loadImplementedCards().map(c=>[c.fullName,c]));
  for(const name of new Set(lists.flat())) {
    const card=instances.get(name);
    assert.ok(card,'Missing pinned source instance '+name);
    if(!manager.isCardDefined(name))manager.defineCard(card);
  }
}
/** Run a capped native Store trace. Results are engine/policy diagnostics, not win-rate samples.
 * @param {string[]} deckA @param {string[]} deckB @param {number} seed
 * @param {number} maxActions @param {number} wallMilliseconds
 */
function runOne(deckA,deckB,seed,maxActions=1000,wallMilliseconds=12000) {
  const prior=Math.random;Math.random=seededRandom(seed);
  const started=Date.now();
  try {
    const store=new Store({onStateChange:()=>{}});
    store.state.gameSettings.format=Format.EXPANDED;
    store.state.gameSettings.recordingEnabled=false;
    const settings={tactics:allSimpleTactics,promptResolvers:allPromptResolvers,
      scores:defaultStateScores,arbiter:defaultArbiterOptions};
    const players=new Map([[1,new SimpleTacticsAi({id:1,name:'Aichi A'},settings,deckA)],
      [2,new SimpleTacticsAi({id:2,name:'Aichi B'},settings,deckB)]]);
    const arbiter=new BotArbiter({flipMode:BotFlipMode.RANDOM,shuffleMode:BotShuffleMode.RANDOM});
    store.dispatch(new AddPlayerAction(1,'Aichi A',deckA));
    store.dispatch(new AddPlayerAction(2,'Aichi B',deckB));
    let actions=0,attacks=0,status='action_cap',error=null;
    while(actions<maxActions) {
      if(Date.now()-started>wallMilliseconds){status='wall_cap';break;}
      const state=store.state;
      if(state.phase===GamePhase.FINISHED){status='finished';break;}
      const prompt=state.prompts.find(p=>p.result===undefined);
      const id=prompt?prompt.playerId:state.players[state.activePlayer]?.id;
      const bot=players.get(id);
      if(!bot){status='unknown_actor';error=String(id);break;}
      let move;
      try {move=(prompt?arbiter.resolvePrompt(state,prompt):undefined)||bot.decodeNextAction(state);}
      catch(e){status='policy_error';error=String(e);break;}
      if(!move){status='no_action';break;}
      try {store.dispatch(move);}
      catch(e){status='dispatch_error';error='step '+actions+' '+move.constructor.name+': '+String(e);break;}
      if(move.type==='ATTACK_ACTION')attacks++;
      actions++;
    }
    const state=store.state;
    return {seed,status,actions,attacks,turn:state.turn,phase:GamePhase[state.phase],
      winner:state.winner,prizes:state.players.map(p=>p.getPrizeLeft()),
      elapsed_ms:Date.now()-started,error};
  } finally {Math.random=prior;}
}
function main() {
  const decks=loadTournamentDecks();
  const a=decks.find(d=>d.id==='vileplume'),b=decks.find(d=>d.id==='mew_genesect');
  assert.equal(a.status,'strictly_mappable');assert.equal(b.status,'strictly_mappable');
  registerLists([a.engine_names,b.engine_names]);
  const seatPairs=makeSeatPairs(a,b,[20261012]);
  const traces=seatPairs.map(p=>runOne(p.seat1.engine_names,p.seat2.engine_names,p.seed));
  const report={scope:'bounded engine self-play diagnostics only, SimpleTacticsAi policy unvalidated',
    twinleaf_pin:'3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    decks:[a.id,b.id],deck_sha256:[deckDigest(a),deckDigest(b)],
    seat_assignments:seatPairs.map(p=>[p.pair_id,p.seed,p.seat1.id,p.seat2.id]),
    max_actions:1000,wall_ms:12000,traces};
  console.log('[tournament-probe] '+JSON.stringify(report));
  assert.ok(traces.every(t=>t.turn>=1),'Both games must enter actual turn one');
  console.log('[tournament-probe] PASS: paired bounded headless traces emitted with explicit limitations');
}
if(require.main===module){try{main();}catch(error){console.error('[tournament-probe] FAIL',error);process.exitCode=1;}}
module.exports={registerLists,runOne};
