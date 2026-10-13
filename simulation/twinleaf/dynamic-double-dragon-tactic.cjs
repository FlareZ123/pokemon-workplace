'use strict';
/**
 * Explicit experimental policy: the native EnergyScore ignores dynamic
 * Special Energy such as Double Dragon (whose static provides array is []).
 * This tactic supplies a legal Dragon-only attachment choice before that
 * static-score tactic. It is a heuristic, not an optimized opponent policy.
 */
const path=require('node:path');
const base=path.resolve(__dirname,'../../vendor/twinleafgg/ptcg-server/output');
const load=p=>require(path.join(base,p));
const {PlayCardAction,PlayerType}=load('game/store/actions/play-card-action');
const {CardType}=load('game/store/card/card-types');
const {pokemonHasCardType}=load('game/store/card/pokemon-card');

class DynamicDoubleDragonTactic {
  /** @param {object} options */
  constructor(options){this.options=options;}
  /** @param {object} state @param {object} player */
  useTactic(state,player){
    if(player.energyPlayedTurn>=state.turn)return;
    const index=player.hand.cards.findIndex(c=>c.fullName==='Double Dragon Energy ROS');
    if(index<0)return;
    const choices=[];
    player.forEachPokemon(PlayerType.BOTTOM_PLAYER,(cards,pokemon,target)=>{
      if(!pokemonHasCardType(pokemon,CardType.DRAGON))return;
      if(!pokemon.attacks.some(attack=>attack.cost.length>0))return;
      const used=cards.cards.filter(c=>c.fullName==='Double Dragon Energy ROS').length;
      if(used>=2)return;
      const isActive=cards===player.active;
      const score=(pokemon.name==='Regidrago VSTAR'?30:0)+(isActive?20:0)-used*10;
      choices.push({score,target});
    });
    if(choices.length===0)return;
    choices.sort((a,b)=>b.score-a.score);
    return new PlayCardAction(player.id,index,choices[0].target);
  }
}
module.exports={DynamicDoubleDragonTactic};
