'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=p=>require(path.join(base,p));
const {MegaAbsolex}=load('sets/11-mega-evolution/set-mega-evolution/mega-absol-ex');
const {Player}=load('game/store/state/player');
const {State}=load('game/store/state/state');
const {AttackEffect}=load('game/store/effects/game-effects');
const {KnockOutOpponentEffect}=load('game/store/effects/attack-effects');
const {install}=require('./hooks/mega-absol-terminal-period.cjs');
function fixture(count){const state=new State(),p=new Player(),o=new Player();p.id=1;o.id=2;state.players=[p,o];const a=new MegaAbsolex();p.active.cards=[a];o.active.cards=[new MegaAbsolex()];o.active.damage=count*10;const effects=[];const store={reduceEffect(s,e){effects.push(e);return s;}};a.reduceEffect(store,state,new AttackEffect(p,o,a.attacks[0]));return {o,effects};}
function main(){assert.equal(fixture(6).o.active.damage,1059);assert.equal(install(),true);assert.equal(install(),false);const a=fixture(6);assert.equal(a.o.active.damage,60);assert.equal(a.effects.length,1);assert.ok(a.effects[0] instanceof KnockOutOpponentEffect);for(const c of [0,5,7]){const f=fixture(c);assert.equal(f.o.active.damage,c*10);assert.equal(f.effects.length,0);}console.log('[Mega Absol] PASS: non-damage KO effect and exact-six gate');}
try{main();}catch(e){console.error(e);process.exitCode=1;}
