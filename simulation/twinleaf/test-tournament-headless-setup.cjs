'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const engineRoot=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const engine=p=>require(path.join(engineRoot,p));
const {loadTournamentDecks}=require('./tournament-deck-loader.cjs');
const {loadImplementedCards}=require('./print-coverage.cjs');
const {CardManager}=engine('game/cards/card-manager');
const {Store}=engine('game/store/store');
const {Format}=engine('game/store/card/card-types');
const {GamePhase}=engine('game/store/state/state');
const {AddPlayerAction}=engine('game/store/actions/add-player-action');
const {SimpleTacticsAi}=engine('simple-bot/simple-tactics-ai');
const {BotArbiter,BotFlipMode,BotShuffleMode}=engine('game/bots/bot-arbiter');
const {allSimpleTactics,allPromptResolvers,defaultStateScores,defaultArbiterOptions}=engine('simple-bot/simple-bot-definitions');
const {makeUniformShuffleArbiter}=require('./hooks/uniform-random-shuffle.cjs');
const UniformBotArbiter=makeUniformShuffleArbiter(BotArbiter);
/** @param {number} seed @returns {()=>number} */
function random(seed) {
  let n=seed>>>0;
  return ()=>{n=(n+0x6D2B79F5)>>>0;let x=n;
    x=Math.imul(x^(x>>>15),x|1);x^=x+Math.imul(x^(x>>>7),x|61);
    return ((x^(x>>>14))>>>0)/4294967296;};
}
/** @param {string[]} left @param {string[]} right @param {number} seed */
function checkOpening(left,right,seed) {
  const old=Math.random;Math.random=random(seed);
  try {
    const store=new Store({onStateChange:()=>{}});
    store.state.gameSettings.format=Format.EXPANDED;
    store.state.gameSettings.recordingEnabled=false;
    const opts={tactics:allSimpleTactics,promptResolvers:allPromptResolvers,
      scores:defaultStateScores,arbiter:defaultArbiterOptions};
    const bots=new Map([[1,new SimpleTacticsAi({id:1,name:'Aichi A'},opts,left)],
      [2,new SimpleTacticsAi({id:2,name:'Aichi B'},opts,right)]]);
    const arbiter=new BotArbiter({flipMode:BotFlipMode.RANDOM,shuffleMode:BotShuffleMode.RANDOM});
    store.dispatch(new AddPlayerAction(1,'Aichi A',left));
    store.dispatch(new AddPlayerAction(2,'Aichi B',right));
    let actions=0;
    while(actions<300 && store.state.phase!==GamePhase.PLAYER_TURN &&
       store.state.phase!==GamePhase.FINISHED) {
      const state=store.state,prompt=state.prompts.find(p=>p.result===undefined);
      const id=prompt?prompt.playerId:state.players[state.activePlayer]?.id;
      const bot=bots.get(id);assert.ok(bot,'Unrecognized actor '+id);
      const action=(prompt?arbiter.resolvePrompt(state,prompt):undefined)||bot.decodeNextAction(state);
      assert.ok(action,'No action during setup at '+actions);
      store.dispatch(action);actions++;
    }
    assert.equal(store.state.phase,GamePhase.PLAYER_TURN,'Failed to reach real first turn');
    assert.equal(store.state.players.length,2);
    for(const p of store.state.players) assert.equal(p.getPrizeLeft(),6);
    return {seed,setup_actions:actions,turn:store.state.turn,phase:GamePhase[store.state.phase],
      actives:store.state.players.map(p=>p.active.getPokemonCard()?.name)};
  } finally {Math.random=old;}
}
function main() {
  const mapped=loadTournamentDecks();
  const vileplume=mapped.find(d=>d.id==='vileplume'),mew=mapped.find(d=>d.id==='mew_genesect');
  assert.equal(vileplume.status,'strictly_mappable');assert.equal(mew.status,'strictly_mappable');
  const prototypes=new Map(loadImplementedCards().map(c=>[c.fullName,c]));
  const manager=CardManager.getInstance();
  for(const name of new Set([...vileplume.engine_names,...mew.engine_names])) {
    assert.ok(prototypes.has(name));
    if(!manager.isCardDefined(name)) manager.defineCard(prototypes.get(name));
  }
  const a=checkOpening(vileplume.engine_names,mew.engine_names,20261012);
  const b=checkOpening(mew.engine_names,vileplume.engine_names,20261013);
  console.log('[tournament-setup] '+JSON.stringify({games:[a,b],pin:'3348ebdc898f175a2ed8f999133cd13d1afd01f5'}));
  console.log('[tournament-setup] PASS: two exact Aichi 60-card references enter a real first turn from both seats');
}
try {main();} catch(error) {console.error('[tournament-setup] FAIL',error);process.exitCode=1;}
