'use strict';
/** Verify exact Big Parasol's attack-effect protection after the Mega Absol hook. */
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=p=>require(path.join(base,p));
const {MegaAbsolex}=load('sets/11-mega-evolution/set-mega-evolution/mega-absol-ex');
const {BigParasol}=load('sets/09-sword-and-shield/set-darkness-ablaze/big-parasol');
const {Player}=load('game/store/state/player');
const {State}=load('game/store/state/state');
const {AttackEffect}=load('game/store/effects/game-effects');
const {KnockOutOpponentEffect}=load('game/store/effects/attack-effects');
const {install}=require('./hooks/mega-absol-terminal-period.cjs');
function main(){
  const state=new State(),a=new Player(),b=new Player();
  a.id=1;b.id=2;state.players=[a,b];
  const absol=new MegaAbsolex(),tool=new BigParasol();
  a.active.cards=[absol];b.active.cards=[new MegaAbsolex()];
  b.active.damage=60;b.active.tools.push(tool);
  install();
  let found=null;
  const store={reduceEffect(s,e){
    if(e instanceof KnockOutOpponentEffect){
      found=e;tool.reduceEffect(store,s,e);
    }
    return s;
  }};
  absol.reduceEffect(store,state,new AttackEffect(a,b,absol.attacks[0]));
  assert.ok(found,'Terminal Period must generate actual attack-effect dispatch');
  assert.equal(found.preventDefault,true,'Big Parasol must prevent direct KO');
  assert.equal(b.active.damage,60,'No artificial damage counters may be added');
  console.log('[Mega Absol + Big Parasol] PASS: protected target retains six counters');
}
try{main();}catch(e){console.error('[Mega Absol + Big Parasol] FAIL',e);process.exitCode=1;}
