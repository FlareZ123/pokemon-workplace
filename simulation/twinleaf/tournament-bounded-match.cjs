'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const engine=p=>require(path.join(base,p));
const {loadCandidateDecks}=require('./candidate-deck-loader.cjs');
const {makeSeatPairs,deckDigest}=require('./paired-seat-plan.cjs');
const {summarizePairedTraces}=require('./paired-result-summary.cjs');
const {parseProbeSettings}=require('./tournament-probe-settings.cjs');
const {makeMatchActionTelemetry}=require('./match-action-telemetry.cjs');
const {makeTacticOrder}=require('./tactic-order-policy.cjs');
const {makeVipFirstTactic}=require('./vip-first-tactic.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');
const {CardManager}=engine('game/cards/card-manager');
const {Store}=engine('game/store/store');
const {Format}=engine('game/store/card/card-types');
const {GamePhase}=engine('game/store/state/state');
const {AddPlayerAction}=engine('game/store/actions/add-player-action');
const {PlayCardAction,PlayerType,SlotType}=engine('game/store/actions/play-card-action');
const {SimpleTacticsAi}=engine('simple-bot/simple-tactics-ai');
const {BotArbiter,BotFlipMode,BotShuffleMode}=engine('game/bots/bot-arbiter');
const {allSimpleTactics,allPromptResolvers,defaultStateScores,defaultArbiterOptions}=engine('simple-bot/simple-bot-definitions');
const {makeUniformShuffleArbiter}=require('./hooks/uniform-random-shuffle.cjs');
const {makeRandomStreamLedger}=require('./random-stream-ledger.cjs');
const UniformBotArbiter=makeUniformShuffleArbiter(BotArbiter);
const ResearchVipTactic=makeVipFirstTactic(PlayCardAction,PlayerType,SlotType);
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
 * @param {'native'|'attack_before_retreat'|'vip_first'|'vip_attack_before_retreat'} tacticOrder
 */
function runOne(deckA,deckB,seed,maxActions=350,wallMilliseconds=25000,tacticOrder='native') {
  const prior=Math.random;
  const ledger=makeRandomStreamLedger(seed);
  Math.random=ledger.random;
  const trackRandom=ledger.track;
  const started=Date.now();
  const telemetry=makeMatchActionTelemetry();
  try {
    const store=new Store({onStateChange:()=>{}});
    store.state.gameSettings.format=Format.EXPANDED;
    store.state.gameSettings.recordingEnabled=false;
    const settings={tactics:makeTacticOrder(tacticOrder,allSimpleTactics,ResearchVipTactic),
      promptResolvers:allPromptResolvers,
      scores:defaultStateScores,arbiter:defaultArbiterOptions};
    const players=new Map([[1,new SimpleTacticsAi({id:1,name:'Aichi A'},settings,deckA)],
      [2,new SimpleTacticsAi({id:2,name:'Aichi B'},settings,deckB)]]);
    const arbiter=new UniformBotArbiter({flipMode:BotFlipMode.RANDOM,shuffleMode:BotShuffleMode.RANDOM});
    trackRandom('setup',()=>store.dispatch(new AddPlayerAction(1,'Aichi A',deckA)));
    trackRandom('setup',()=>store.dispatch(new AddPlayerAction(2,'Aichi B',deckB)));
    let actions=0,attacks=0,status='action_cap',error=null,firstActor=null;
    const openingHands=[null,null];
    while(actions<maxActions) {
      if(Date.now()-started>wallMilliseconds){status='wall_cap';break;}
      const state=store.state;
      if(state.phase===GamePhase.PLAYER_TURN && state.turn<=2 &&
        openingHands[state.activePlayer]===null)
        openingHands[state.activePlayer]=state.players[state.activePlayer].hand.cards.map(card=>card.name);
      if(firstActor===null && state.phase===GamePhase.PLAYER_TURN)
        firstActor=state.players[state.activePlayer]?.id ?? null;
      if(state.phase===GamePhase.FINISHED){status='finished';break;}
      const prompt=state.prompts.find(p=>p.result===undefined);
      const id=prompt?prompt.playerId:state.players[state.activePlayer]?.id;
      const bot=players.get(id);
      if(!bot){status='unknown_actor';error=String(id);break;}
      let move;
      try {
        move=prompt?trackRandom('arbiter',()=>arbiter.resolvePrompt(state,prompt)):undefined;
        if(!move)move=trackRandom('policy',()=>bot.decodeNextAction(state));
      }
      catch(e){status='policy_error';error=String(e);break;}
      if(!move){status='no_action';break;}
      try {
        const before=telemetry.capture(move,store.state);
        trackRandom('dispatch',()=>store.dispatch(move));
        telemetry.observe(move,before,store.state,actions);
      } catch(e) {
        status='dispatch_error';
        error='step '+actions+' '+move.constructor.name+': '+String(e);
        break;
      }
      if(move.type==='ATTACK_ACTION')attacks++;
      actions++;
    }
    const state=store.state;
    if(state.phase===GamePhase.FINISHED && (status==='action_cap' || status==='wall_cap'))
      status='finished';
    const rng=ledger.snapshot();
    return {seed,status,actions,attacks,first_actor:firstActor,
      first_turn_hands:openingHands,random_calls:rng.calls,
      game_random_calls:rng.gameCalls,policy_random_calls:rng.policyCalls,
      random_sources:rng.bySource,turn:state.turn,phase:GamePhase[state.phase],
      winner:state.winner,prizes:state.players.map(p=>p.getPrizeLeft()),
      end_board:state.players.map(p=>({
        deck_left:p.deck.cards.length,
        hand_count:p.hand.cards.length,
        discard_count:p.discard.cards.length,
        active:p.active.getPokemonCard()?.name||null,
        bench:p.bench.map(slot=>slot.getPokemonCard()?.name).filter(Boolean)
      })),
      terminal_log:state.logs.slice(-6).map(log=>({
        code:log.message,client:log.client,params:{...log.params}
      })),
      elapsed_ms:Date.now()-started,error,telemetry:telemetry.snapshot()};
  } finally {Math.random=prior;}
}
function main() {
  const decks=loadCandidateDecks();
  const config=parseProbeSettings(process.env,
    decks.filter(d=>d.status==='strictly_mappable').map(d=>d.id));
  const a=decks.find(d=>d.id===config.deckAId),b=decks.find(d=>d.id===config.deckBId);
  assert.equal(a.status,'strictly_mappable');assert.equal(b.status,'strictly_mappable');
  registerLists([a.engine_names,b.engine_names]);
  const seatPairs=makeSeatPairs(a,b,config.seeds);
  const traces=seatPairs.map(p=>runOne(p.seat1.engine_names,p.seat2.engine_names,p.seed,
    350,25000,config.tacticOrder));
  const pairedResults=summarizePairedTraces(seatPairs,traces);
  const report={scope:'bounded engine self-play diagnostics only, SimpleTacticsAi policy unvalidated',
    twinleaf_pin:'3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    shuffle_policy:'research_uniform_fisher_yates_v1',
    random_stream_policy:'separated_live_game_and_counterfactual_policy_v1',
    ci_budget_policy:'max_three_seed_pairs_350_actions_25000ms_per_game',
    tactic_order:config.tacticOrder,
    decks:[a.id,b.id],deck_sha256:[deckDigest(a),deckDigest(b)],
    deck_sources:[a.source||'aichi_reference',b.source||'aichi_reference'],
    seat_assignments:seatPairs.map(p=>[p.pair_id,p.seed,p.seat1.id,p.seat2.id]),
    max_actions:350,wall_ms:25000,paired_results:pairedResults,traces};
  console.log('[tournament-probe] '+JSON.stringify(report));
  assert.ok(traces.every(t=>t.turn>=1),'Both games must enter actual turn one');
  assert.equal(pairedResults.error_games,0,'Engine or bot error must not silently pass as a match');
  assert.equal(pairedResults.terminal_unresolved_games,0,'Uninterpretable terminal winner requires engine investigation');
  console.log('[tournament-probe] PASS: paired bounded headless traces emitted with explicit limitations');
}
if(require.main===module){try{main();}catch(error){console.error('[tournament-probe] FAIL',error);process.exitCode=1;}}
module.exports={registerLists,runOne};
