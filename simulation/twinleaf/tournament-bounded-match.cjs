'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const cp=require('node:child_process');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const engine=p=>require(path.join(base,p));
const {loadCandidateDecks}=require('./candidate-deck-loader.cjs');
const {makeSeatPairs,deckDigest}=require('./paired-seat-plan.cjs');
const {summarizePairedTraces}=require('./paired-result-summary.cjs');
const {summarizeScoreBounds}=require('./paired-score-bounds.cjs');
const {parseProbeSettings}=require('./tournament-probe-settings.cjs');
const {makeMatchActionTelemetry}=require('./match-action-telemetry.cjs');
const {makeSupporterSelectionGuard}=require('./supporter-selection-guard.cjs');
const {writeReportAtomic}=require('./report-atomic.cjs');
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
const {PlaySupporterTactic}=engine('simple-bot/simple-tactics/play-supporter-tactic');
const {BotArbiter,BotFlipMode,BotShuffleMode}=engine('game/bots/bot-arbiter');
const {allSimpleTactics,allPromptResolvers,defaultStateScores,defaultArbiterOptions}=engine('simple-bot/simple-bot-definitions');
const {makeUniformShuffleArbiter}=require('./hooks/uniform-random-shuffle.cjs');
const {makeRandomStreamLedger}=require('./random-stream-ledger.cjs');
const {install:installUnderworldDoorGuard}=require('./hooks/shadow-rider-underworld-door.cjs');
const {install:installCelestialRoarGuard}=require('./hooks/regidrago-celestial-roar.cjs');
const {install:installStoutlandWildTackleGuard}=require('./hooks/stoutland-wild-tackle.cjs');
const UniformBotArbiter=makeUniformShuffleArbiter(BotArbiter);
const ResearchVipTactic=makeVipFirstTactic(PlayCardAction,PlayerType,SlotType);
/** Install verified rules-correctness hooks for every live match, including direct runOne callers.
 * @returns {readonly string[]}
 */
function ensureResearchEngineHooks() {
  installUnderworldDoorGuard();
  installCelestialRoarGuard();
  installStoutlandWildTackleGuard();
  return ['shadow_rider_underworld_door_guard_v1','regidrago_celestial_roar_any_energy_v1',
    'stoutland_wild_tackle_self20_v1'];
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
 * @param {'native'|'attack_before_retreat'|'vip_first'|'vip_attack_before_retreat'} tacticOrder
 */
function runOne(deckA,deckB,seed,maxActions=350,wallMilliseconds=25000,tacticOrder='native') {
  const engineHooks=ensureResearchEngineHooks();
  const prior=Math.random;
  const ledger=makeRandomStreamLedger(seed);
  Math.random=ledger.random;
  const trackRandom=ledger.track;
  const started=Date.now();
  const telemetry=makeMatchActionTelemetry();
  const supporterSelectionGuard=makeSupporterSelectionGuard();
  try {
    const store=new Store({onStateChange:()=>{}});
    store.state.gameSettings.format=Format.EXPANDED;
    store.state.gameSettings.recordingEnabled=false;
    const SafeSupporterTactic=supporterSelectionGuard.wrapTactic(PlaySupporterTactic);
    const safeTactics=allSimpleTactics.map(Tactic=>
      Tactic===PlaySupporterTactic?SafeSupporterTactic:Tactic);
    assert.equal(safeTactics.filter(Tactic=>Tactic===SafeSupporterTactic).length,1,
      'Pinned policy tactic roster changed: inspect before applying Supporter guard');
    const settings={tactics:makeTacticOrder(tacticOrder,safeTactics,ResearchVipTactic),
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
        if(!move)move=trackRandom('policy',()=>supporterSelectionGuard.decode(bot,state,id));
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
    return {seed,status,actions,attacks,engine_hooks:engineHooks,first_actor:firstActor,
      first_turn_hands:openingHands,
      policy_hidden_information:'unmasked_native_SimpleTacticsAi_order_oracle',
      policy_hooks:['supporter_prevalidation_and_dispatch_counter_restore_v2'],
      policy_repair_stats:supporterSelectionGuard.snapshot(),
      random_calls:rng.calls,
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
  const pairedScoreBounds=summarizeScoreBounds(pairedResults,a.id);
  const report={scope:'bounded engine self-play diagnostics only, SimpleTacticsAi policy unvalidated',
    twinleaf_pin:'3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    research_revision:cp.execFileSync('git',['rev-parse','HEAD'],
      {cwd:path.resolve(__dirname,'../..'),encoding:'utf8'}).trim(),
    shuffle_policy:'research_uniform_fisher_yates_v1',
    random_stream_policy:'separated_live_game_and_counterfactual_policy_v1',
    policy_hidden_information:'unmasked_native_SimpleTacticsAi_order_oracle',
    policy_hidden_information_evidence:'results/tests/twinleaf_hidden_topdeck_oracle/README.md',
    policy_hooks:['supporter_prevalidation_and_dispatch_counter_restore_v2'],
    ci_budget_policy:'max_three_seed_pairs_350_actions_25000ms_per_game',
    tactic_order:config.tacticOrder,
    engine_hooks:['shadow_rider_underworld_door_guard_v1','regidrago_celestial_roar_any_energy_v1',
      'stoutland_wild_tackle_self20_v1'],
    decks:[a.id,b.id],deck_sha256:[deckDigest(a),deckDigest(b)],
    deck_sources:[a.source||'aichi_reference',b.source||'aichi_reference'],
    seat_assignments:seatPairs.map(p=>[p.pair_id,p.seed,p.seat1.id,p.seat2.id]),
    max_actions:350,wall_ms:25000,paired_results:pairedResults,
    paired_score_bounds:pairedScoreBounds,traces};
  if(process.env.TWINLEAF_REPORT_PATH)
    writeReportAtomic(process.env.TWINLEAF_REPORT_PATH,report);
  console.log('[tournament-probe] '+JSON.stringify(report));
  assert.ok(traces.every(t=>t.turn>=1),'Both games must enter actual turn one');
  assert.equal(pairedResults.error_games,0,'Engine or bot error must not silently pass as a match');
  assert.equal(pairedResults.terminal_unresolved_games,0,'Uninterpretable terminal winner requires engine investigation');
  console.log('[tournament-probe] PASS: paired bounded headless traces emitted with explicit limitations');
}
if(require.main===module){try{main();}catch(error){console.error('[tournament-probe] FAIL',error);process.exitCode=1;}}
module.exports={registerLists,runOne,ensureResearchEngineHooks};
