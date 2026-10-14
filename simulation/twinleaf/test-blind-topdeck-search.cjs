'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const cp=require('node:child_process');

const vendor=path.resolve(__dirname,'../../vendor/twinleafgg');
const pin='3348ebdc898f175a2ed8f999133cd13d1afd01f5';
assert.equal(cp.execFileSync('git',['rev-parse','HEAD'],
  {cwd:vendor,encoding:'utf8'}).trim(),pin);
const out=path.join(vendor,'ptcg-server/output');
const load=p=>require(path.join(out,p));
const {State,GamePhase}=load('game/store/state/state');
const {Player}=load('game/store/state/player');
const {CardList}=load('game/store/state/card-list');
const {CardManager}=load('game/cards/card-manager');
const {Format,TrainerType}=load('game/store/card/card-types');
const {PlayCardAction,PlayerType,SlotType}=load('game/store/actions/play-card-action');
const {TrainerCard}=load('game/store/card/trainer-card');
const {SimpleTacticsAi}=load('simple-bot/simple-tactics-ai');
const {PlayTrainerTactic}=load('simple-bot/simple-tactics/play-trainer-tactic');
const {defaultStateScores,defaultArbiterOptions,allPromptResolvers}=
  load('simple-bot/simple-bot-definitions');
const {Pokegear30}=load('sets/10-scarlet-and-violet/set-scarlet-and-violet/pokegear-30');
const {TrainersMail}=load('sets/07-x-and-y/set-roaring-skies/trainers-mail');
const {BossOrders}=load('sets/10-scarlet-and-violet/set-paldea-evolved/boss-orders');
const {RegidragoV}=load('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {GrassEnergy}=load('sets/06-black-and-white/set-black-and-white/basic-energies');
const {atLeastOne,makeBlindTopdeckTrainerTactic}=
  require('./blind-topdeck-trainer-tactic.cjs');
const BlindTactic=makeBlindTopdeckTrainerTactic(PlayTrainerTactic,{
  TrainerCard,TrainerType,PlayCardAction,PlayerType,SlotType});
const opts={scores:defaultStateScores,arbiter:defaultArbiterOptions,
  promptResolvers:allPromptResolvers};
const grass=n=>Array.from({length:n},()=>new GrassEnergy());
const prizes=()=>Array.from({length:6},()=>{
  const x=new CardList();x.cards=grass(1);return x;
});
for(const obj of [new Pokegear30(),new TrainersMail(),new BossOrders(),
  new RegidragoV(),new GrassEnergy()]) {
  const manager=CardManager.getInstance();
  if(!manager.isCardDefined(obj.fullName))manager.defineCard(obj);
}

/**
 * 60 physical cards per player. Worlds with the same case preserve the full
 * known inventory, hand and public board, but change private deck positions.
 * @param {'pokegear'|'mail'} item
 * @param {number[]} bossPositions
 * @param {number[]} extraTrainerPositions
 * @param {boolean} bossPrized
 */
function world(item,bossPositions,extraTrainerPositions=[],bossPrized=false) {
  const state=new State();state.phase=GamePhase.PLAYER_TURN;
  state.turn=2;state.activePlayer=0;state.gameSettings.format=Format.EXPANDED;
  const me=new Player();me.id=1;me.name='Actor';
  me.active.cards=[new RegidragoV()];me.active.pokemonPlayedTurn=1;
  me.hand.cards=[item==='pokegear'?new Pokegear30():new TrainersMail(),...grass(6)];
  me.deck.cards=grass(46);me.prizes=prizes();
  for(const i of bossPositions)me.deck.cards[i]=new BossOrders();
  for(const i of extraTrainerPositions)me.deck.cards[i]=new Pokegear30();
  if(bossPrized)me.prizes[0].cards[0]=new BossOrders();
  const them=new Player();them.id=2;them.name='Opponent';
  them.active.cards=[new RegidragoV()];them.active.pokemonPlayedTurn=1;
  them.hand.cards=grass(7);them.deck.cards=grass(46);them.prizes=prizes();
  state.players=[me,them];
  for(const p of state.players) {
    const total=p.hand.cards.length+p.deck.cards.length+p.prizes.reduce(
      (sum,slot)=>sum+slot.cards.length,0)+p.active.cards.length;
    assert.equal(total,60);
  }
  return state;
}
function decision(w) {
  const tactic=new BlindTactic(opts);
  const action=tactic.useTactic(w,w.players[0]);
  const bot=new SimpleTacticsAi({id:1,name:'Blind'},
    {...opts,tactics:[BlindTactic]},null);
  const actual=bot.decodeNextAction(w);
  return {direct:action?.type||null,bot:actual?.constructor.name||null};
}
function checkInvariance(label,a,b,expected) {
  const da=decision(a),db=decision(b);
  assert.deepEqual(da,db,'Different hidden topdeck changed a blind decision: '+label);
  assert.equal(da.direct,expected,label);
  assert.equal(da.bot,expected?'PlayCardAction':'PassTurnAction',label);
  console.log('[blind-topdeck] '+JSON.stringify({case:label,decision:da}));
}
const scarceHit=world('pokegear',[0]);
const scarceMiss=world('pokegear',[10]);
const native=new PlayTrainerTactic(opts);
assert.equal(native.useTactic(scarceHit,scarceHit.players[0])?.type,'PLAY_CARD_ACTION');
assert.equal(native.useTactic(scarceMiss,scarceMiss.players[0]),undefined);
checkInvariance('pokegear_one_unseen',scarceHit,scarceMiss,null);
checkInvariance('pokegear_prized_vs_deck',scarceMiss,
  world('pokegear',[],[],true),null);
checkInvariance('mail_one_unseen',world('mail',[0]),world('mail',[10]),null);
checkInvariance('pokegear_four_unseen',
  world('pokegear',[0,10,18,23]),world('pokegear',[10,18,23,33]),
  'PLAY_CARD_ACTION');
checkInvariance('mail_eight_unseen',
  world('mail',[0,10,18,23],[1,11,19,24]),
  world('mail',[10,18,23,33],[11,19,24,34]),'PLAY_CARD_ACTION');
assert.ok(Math.abs(atLeastOne(52,1,7)-7/52)<1e-12);
assert.ok(Math.abs(atLeastOne(52,4,7)-0.4496444731738849)<1e-12);
assert.ok(Math.abs(atLeastOne(52,8,4)-0.49856496444731735)<1e-12);
console.log('[blind-topdeck] PASS: K0-decision invariance for five paired physical worlds; native oracle reproduced');
