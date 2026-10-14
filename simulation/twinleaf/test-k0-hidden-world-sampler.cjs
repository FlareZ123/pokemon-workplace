'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const cp=require('node:child_process');
const vendor=path.resolve(__dirname,'../../vendor/twinleafgg');
const pin='3348ebdc898f175a2ed8f999133cd13d1afd01f5';
assert.equal(cp.execFileSync('git',['rev-parse','HEAD'],
  {cwd:vendor,encoding:'utf8'}).trim(),pin);
const load=p=>require(path.join(vendor,'ptcg-server/output',p));
const {Simulator}=load('game/bots/simulator');
const {deepClone}=load('utils');
const {State,GamePhase}=load('game/store/state/state');
const {Player}=load('game/store/state/player');
const {CardList}=load('game/store/state/card-list');
const {CardManager}=load('game/cards/card-manager');
const {Format,CardTag}=load('game/store/card/card-types');
const {PlayTrainerTactic}=load('simple-bot/simple-tactics/play-trainer-tactic');
const {SimpleTacticsAi}=load('simple-bot/simple-tactics-ai');
const {defaultStateScores,defaultArbiterOptions,allPromptResolvers}=
  load('simple-bot/simple-bot-definitions');
const {Pokegear30}=load('sets/10-scarlet-and-violet/set-scarlet-and-violet/pokegear-30');
const {BossOrders}=load('sets/10-scarlet-and-violet/set-paldea-evolved/boss-orders');
const {RegidragoV}=load('sets/09-sword-and-shield/set-silver-tempest/regidrago-v');
const {GrassEnergy}=load('sets/06-black-and-white/set-black-and-white/basic-energies');
const {makeK0HiddenWorldSampler,publicKey,permute}=require('./k0-hidden-world-sampler.cjs');
const sample=makeK0HiddenWorldSampler(deepClone);
const duplicates=Array.from({length:7},(_,i)=>({fullName:'Grass Energy BRS',id:i+1}));
assert.deepEqual(permute(duplicates,'same-known-public-state').map(c=>c.id),
  permute([...duplicates].reverse(),'same-known-public-state').map(c=>c.id),
  'Equal-print original position must not leak into deterministic sampled identity order');
for(const obj of [new Pokegear30(),new BossOrders(),new RegidragoV(),new GrassEnergy()]){
  const manager=CardManager.getInstance();
  if(!manager.isCardDefined(obj.fullName))manager.defineCard(obj);
}
const grass=n=>Array.from({length:n},()=>new GrassEnergy());
const prizes=()=>Array.from({length:6},()=>{
  const slot=new CardList();slot.cards=grass(1);return slot;
});

/** @param {number} position @param {boolean} ownPrized @param {boolean} opponentHand */
function world(position,ownPrized=false,opponentHand=false){
  const s=new State();s.phase=GamePhase.PLAYER_TURN;s.turn=2;s.activePlayer=0;
  s.gameSettings.format=Format.EXPANDED;
  const me=new Player();me.id=1;me.name='Actor';
  me.active.cards=[new RegidragoV()];me.active.pokemonPlayedTurn=1;
  me.hand.cards=[new Pokegear30(),...grass(6)];me.deck.cards=grass(46);
  me.prizes=prizes();
  if(ownPrized)me.prizes[0].cards[0]=new BossOrders();
  else me.deck.cards[position]=new BossOrders();
  const them=new Player();them.id=2;them.name='Opponent';
  them.active.cards=[new RegidragoV()];them.active.pokemonPlayedTurn=1;
  them.hand.cards=grass(7);them.deck.cards=grass(46);them.prizes=prizes();
  if(opponentHand)them.hand.cards[0]=new BossOrders();
  else them.deck.cards[20]=new BossOrders();
  s.players=[me,them];
  for(const p of s.players){
    const count=p.active.cards.length+p.hand.cards.length+p.deck.cards.length+
      p.prizes.reduce((n,slot)=>n+slot.cards.length,0);
    assert.equal(count,60);
  }
  return s;
}
const publicView=w=>publicKey(w,1);
const privateNames=w=>w.players.map((p,i)=>({
  hand:i===0?null:p.hand.cards.map(c=>c.fullName),
  deck:p.deck.cards.map(c=>c.fullName),
  prizes:p.prizes.map(x=>x.cards.map(c=>c.fullName))
}));
const source=[world(0),world(12),world(1,true),world(12,false,true)];
assert.ok(source.every(s=>publicView(s)===publicView(source[0])));
const opts={scores:defaultStateScores,arbiter:defaultArbiterOptions,
  promptResolvers:allPromptResolvers};
const native=new PlayTrainerTactic(opts);
assert.equal(native.useTactic(source[0],source[0].players[0])?.type,'PLAY_CARD_ACTION');
assert.equal(native.useTactic(source[1],source[1].players[0]),undefined);
// Pinned Simulator's ignored Card class gives both states the same mutable
// card objects. A policy clone must provide a stronger isolation boundary.
const unsafe=new Simulator(source[0]).store.state;
assert.strictEqual(unsafe.players[0].hand.cards[0],source[0].players[0].hand.cards[0],
  'Pinned Simulator must expose the documented mutable-card alias');
const original=source.map(s=>privateNames(s));
const hypothetical=source.map(s=>sample(s,1));
for(let i=1;i<hypothetical.length;i++){
  assert.deepEqual(privateNames(hypothetical[i]),privateNames(hypothetical[0]),
    'Indistinguishable worlds must yield identical canonical sampled names');
}
for(let i=0;i<source.length;i++){
  assert.notStrictEqual(hypothetical[i].players[0].hand.cards[0],
    source[i].players[0].hand.cards[0],
    'Hypothetical card mutations must never reach the authoritative state');
  assert.notStrictEqual(hypothetical[i].players[0].hand.cards[0].marker,
    source[i].players[0].hand.cards[0].marker,
    'Attached card markers must also be isolated');
  assert.deepEqual(privateNames(source[i]),original[i],
    'Sampling must never change the authoritative physical State');
  assert.equal(publicView(hypothetical[i]),publicView(source[i]),
    'Sampling must preserve every field of the declared public projection');
  assert.deepEqual(hypothetical[i].players[0].hand.cards.map(c=>c.fullName),
    source[i].players[0].hand.cards.map(c=>c.fullName));
}
const actorCard=source[0].players[0].hand.cards[0];
const mockCard=hypothetical[0].players[0].hand.cards[0];
assert.equal(actorCard.hasTag(CardTag.FUTURE),false);
mockCard.addRuntimeTag(CardTag.FUTURE);
assert.equal(mockCard.hasTag(CardTag.FUTURE),true);
assert.equal(actorCard.hasTag(CardTag.FUTURE),false,
  'Native hypothetical card effect must not alter live card runtime tags');
mockCard.removeRuntimeTag(CardTag.FUTURE);
const tdecisions=hypothetical.map(s=>native.useTactic(s,s.players[0])?.type||null);
assert.ok(tdecisions.every(x=>x===tdecisions[0]));
const bdecisions=hypothetical.map(s=>{
  const bot=new SimpleTacticsAi({id:1,name:'Sampled'},
    {...opts,tactics:[PlayTrainerTactic]},null);
  return bot.decodeNextAction(s)?.constructor.name;
});
assert.ok(bdecisions.every(x=>x===bdecisions[0]));
console.log('[k0-world-sampler] '+JSON.stringify({pin,worlds:source.length,
  native_oracle_before:['PLAY_CARD_ACTION',null],
  sampled_native_decision:tdecisions[0],
  sampled_bot_decision:bdecisions[0],
  observation_equal:true,secret_original_unmodified:true}));
console.log('[k0-world-sampler] PASS: identical hypothetical worlds for equal observable states and hidden inventory');
