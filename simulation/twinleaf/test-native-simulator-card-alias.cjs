'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const cp=require('node:child_process');
const root=path.resolve(__dirname,'../../vendor/twinleafgg');
const pin='3348ebdc898f175a2ed8f999133cd13d1afd01f5';
assert.equal(cp.execFileSync('git',['rev-parse','HEAD'],
  {cwd:root,encoding:'utf8'}).trim(),pin);
const engine=p=>require(path.join(root,'ptcg-server/output',p));
const {State,GamePhase}=engine('game/store/state/state');
const {Player}=engine('game/store/state/player');
const {CardList}=engine('game/store/state/card-list');
const {Store}=engine('game/store/store');
const {Simulator}=engine('game/bots/simulator');
const {deepClone}=engine('utils');
const {CardTag,Format}=engine('game/store/card/card-types');
const {CheckTableStateEffect}=engine('game/store/effects/check-effects');
const {RegidragoV}=engine('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {TeamPlasmaBadge}=engine('sets/06-black-and-white/set-plasma-freeze/team-plasma-badge');
const {GrassEnergy}=engine('sets/06-black-and-white/set-black-and-white/basic-energies');
const {makeK0HiddenWorldSampler}=require('./k0-hidden-world-sampler.cjs');
const grass=n=>Array.from({length:n},()=>new GrassEnergy());
const prizes=()=>Array.from({length:6},()=>{
  const slot=new CardList();slot.cards=grass(1);return slot;
});
function fixture(){
  const s=new State();s.phase=GamePhase.PLAYER_TURN;s.turn=2;
  s.activePlayer=0;s.gameSettings.format=Format.EXPANDED;
  const a=new Player();a.id=1;a.name='Actor';
  a.active.cards=[new RegidragoV()];
  a.active.pokemonPlayedTurn=1;
  a.active.tools=[new TeamPlasmaBadge()];
  a.hand.cards=grass(7);a.deck.cards=grass(45);a.prizes=prizes();
  const b=new Player();b.id=2;b.name='Opponent';
  b.active.cards=[new RegidragoV()];b.active.pokemonPlayedTurn=1;
  b.hand.cards=grass(7);b.deck.cards=grass(46);b.prizes=prizes();
  s.players=[a,b];
  for(const p of s.players){
    const n=p.hand.cards.length+p.deck.cards.length+
      p.prizes.reduce((sum,x)=>sum+x.cards.length,0)+
      p.active.cards.length+p.active.tools.length;
    assert.equal(n,60);
  }
  return s;
}
function applyBoardCheck(state){
  const store=new Store({onStateChange:()=>{}});
  store.state=state;
  store.reduceEffect(state,new CheckTableStateEffect([5,5]));
}
const live=fixture();
const card=live.players[0].active.cards[0];
assert.equal(card.hasTag(CardTag.TEAM_PLASMA),false);
const unsafe=new Simulator(live).store.state;
assert.strictEqual(unsafe.players[0].active.cards[0],card);
assert.strictEqual(unsafe.players[0].active.tools[0],live.players[0].active.tools[0]);
applyBoardCheck(unsafe);
assert.equal(card.hasTag(CardTag.TEAM_PLASMA),true,
  'Native speculative CheckTableStateEffect mutated authoritative Pokemon Card');

const protectedLive=fixture();
const protectedCard=protectedLive.players[0].active.cards[0];
const hypothetical=makeK0HiddenWorldSampler(deepClone)(protectedLive,1);
assert.notStrictEqual(hypothetical.players[0].active.cards[0],protectedCard);
assert.notStrictEqual(hypothetical.players[0].active.tools[0],
  protectedLive.players[0].active.tools[0]);
applyBoardCheck(hypothetical);
assert.equal(hypothetical.players[0].active.cards[0].hasTag(CardTag.TEAM_PLASMA),true);
assert.equal(protectedCard.hasTag(CardTag.TEAM_PLASMA),false,
  'Fully cloned Card objects must isolate the research hypothetical effect');
console.log('[native-card-alias] '+JSON.stringify({
  pin,real_print:'Team Plasma Badge PLF 104',
  effect:'CheckTableStateEffect / addRuntimeTag Team Plasma',
  unsafe_simulator_shared_card:true,
  unsafe_live_pokemon_mutated:true,
  research_full_card_clone_isolated:true,
  physical_cards_per_player:60
}));
console.log('[native-card-alias] PASS: concrete pinned Badge reducer leaks speculative Card mutation; research clone isolates it');
