'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const engine=p=>require(path.join(ROOT,p));
const {Simulator}=engine('game/bots/simulator');
const {State,GamePhase}=engine('game/store/state/state');
const {Player}=engine('game/store/state/player');
const {PokemonCardList}=engine('game/store/state/pokemon-card-list');
const {CardList}=engine('game/store/state/card-list');
const {PlayCardAction,PlayerType,SlotType}=engine('game/store/actions/play-card-action');
const {ResolvePromptAction}=engine('game/store/actions/resolve-prompt-action');
const {ChoosePokemonPrompt}=engine('game/store/prompts/choose-pokemon-prompt');
const {WaitPrompt}=engine('game/store/prompts/wait-prompt');
const {CoinFlipPrompt}=engine('game/store/prompts/coin-flip-prompt');
const {BotArbiter,BotFlipMode,BotShuffleMode}=engine('game/bots/bot-arbiter');
const {PokemonCatcher}=engine('sets/10-scarlet-and-violet/set-scarlet-and-violet/pokemon-catcher');
const {RegidragoV}=engine('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');

/** A source-card-grounded active/bench board with one usable Pokémon Catcher.
 * @returns {any} Native Twinleaf State in the active player's own turn.
 */
function scenario() {
  const state=new State();
  state.phase=GamePhase.PLAYER_TURN;
  state.turn=4;
  state.activePlayer=0;
  const players=[new Player(),new Player()];
  players.forEach((p,i)=>{
    p.id=i+1;
    p.name='Coin audit '+(i+1);
    const card=new RegidragoV();
    card.id=100+i;
    p.active.cards.push(card);
    p.active.hp=card.hp;
    p.deck.cards.push(new RegidragoV());
    p.prizes=Array.from({length:6},()=>{
      const slot=new CardList();slot.cards.push(new RegidragoV());return slot;
    });
  });
  const bench=new PokemonCardList();
  const pokemon=new RegidragoV();pokemon.id=102;
  bench.cards.push(pokemon);
  bench.hp=pokemon.hp;
  players[1].bench.push(bench);
  players[0].hand.cards.push(new PokemonCatcher());
  state.players=players;
  return state;
}

/** @param {{flipMode?:number,shuffleMode?:number}} options
 * @param {number} randomValue
 */
function replay(options,randomValue) {
  const prior=Math.random;
  let randomCalls=0;
  Math.random=()=>{randomCalls++;return randomValue;};
  try {
    const sim=new Simulator(scenario(),options);
    const action=new PlayCardAction(1,0,{player:PlayerType.ANY,slot:SlotType.BOARD,index:0});
    sim.dispatch(action);
    let choiceCount=0,waitCount=0;
    for(let step=0;step<12;step++) {
      const prompt=sim.store.state.prompts.find(p=>p.result===undefined);
      if(!prompt)break;
      if(prompt instanceof WaitPrompt) {
        waitCount++;
        sim.dispatch(new ResolvePromptAction(prompt.id,null));
      } else if(prompt instanceof ChoosePokemonPrompt) {
        choiceCount++;
        sim.dispatch(new ResolvePromptAction(prompt.id,[sim.store.state.players[1].bench[0]]));
      } else {
        throw Error('Unexpected unresolved prompt '+prompt.constructor.name);
      }
    }
    const state=sim.store.state;
    assert.ok(state.prompts.every(p=>p.result!==undefined),'Unresolved native prompts remain');
    return {active_id:state.players[1].active.getPokemonCard()?.id,
      random_calls:randomCalls,had_pokemon_choice:choiceCount>0,wait_prompts:waitCount,
      phase:GamePhase[state.phase]};
  } finally {Math.random=prior;}
}

function main() {
  const defaultLow=replay({},0.1),defaultHigh=replay({},0.9);
  const randomLow=replay({flipMode:BotFlipMode.RANDOM,shuffleMode:BotShuffleMode.NO_SHUFFLE},0.1);
  const randomHigh=replay({flipMode:BotFlipMode.RANDOM,shuffleMode:BotShuffleMode.NO_SHUFFLE},0.9);
  assert.deepEqual([defaultLow.active_id,defaultHigh.active_id],[102,101],
    'Modern CoinFlipEffect samples RNG even under all-heads arbiter defaults');
  assert.deepEqual([randomLow.active_id,randomHigh.active_id],[102,101],
    'Stochastic hypothetical simulator must preserve both paper Catcher outcomes');
  assert.deepEqual([defaultLow.had_pokemon_choice,defaultHigh.had_pokemon_choice,
    randomLow.had_pokemon_choice,randomHigh.had_pokemon_choice],[true,false,true,false]);
  /** Legacy CoinFlipPrompt arbitration still obeys the default ALL_HEADS policy. */
  function resolveLegacy(options,value) {
    const previous=Math.random;
    Math.random=()=>value;
    try {
      const arbiter=new BotArbiter(options);
      const action=arbiter.resolvePrompt(scenario(),new CoinFlipPrompt(1,0));
      assert.ok(action,'Legacy prompt must be arbitrated');
      return action.result;
    } finally {Math.random=previous;}
  }
  const legacy={defaultLow:resolveLegacy({},0.1),defaultHigh:resolveLegacy({},0.9),
    randomLow:resolveLegacy({flipMode:BotFlipMode.RANDOM},0.1),
    randomHigh:resolveLegacy({flipMode:BotFlipMode.RANDOM},0.9)};
  assert.deepEqual(legacy,{defaultLow:true,defaultHigh:true,randomLow:true,randomHigh:false},
    'Legacy arbiter prompt and modern CoinFlipEffect follow different chance policies');
  console.log('[counterfactual-coin] '+JSON.stringify({
    pin:'3348ebdc898f175a2ed8f999133cd13d1afd01f5',
    card:'Pokémon Catcher SVI 187',
    default_low:defaultLow,default_high:defaultHigh,
    random_low:randomLow,random_high:randomHigh,legacy_prompt:legacy
  }));
  console.log('[counterfactual-coin] PASS: modern CoinFlipEffect uses RNG; legacy arbiter CoinFlipPrompt defaults to heads');
}
if(require.main===module)main();
module.exports={scenario,replay,main};
