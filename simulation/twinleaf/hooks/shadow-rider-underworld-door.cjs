'use strict';
const path=require('node:path');
const ENGINE=path.resolve(__dirname,'../../../vendor/twinleafgg/ptcg-server/output');
const {ShadowRiderCalyrexVMAX}=require(path.join(ENGINE,'sets/09-sword-and-shield/set-chilling-reign/shadow-rider-calyrex-vmax'));
const {PowerEffect}=require(path.join(ENGINE,'game/store/effects/game-effects'));
const {AttachEnergyPrompt}=require(path.join(ENGINE,'game/store/prompts/attach-energy-prompt'));
const {PlayerType,SlotType}=require(path.join(ENGINE,'game/store/actions/play-card-action'));
const {CardType}=require(path.join(ENGINE,'game/store/card/card-types'));
const {pokemonHasCardType}=require(path.join(ENGINE,'game/store/card/pokemon-card'));
const {GameError}=require(path.join(ENGINE,'game/game-error'));
const {GameMessage}=require(path.join(ENGINE,'game/game-message'));
const MARK=Symbol.for('pokemon-research.shadow-rider-underworld-door-guard');
/** Restrict Underworld Door's targets to actual Benched Psychic Pokemon.
 * Pinned Twinleaf currently checks PokemonCardList instanceof PokemonCard and passes
 * Bench indices through blocked (source cards) instead of blockedTo (targets).
 * This installs a research-side runtime hook without changing vendor files.
 * @returns {boolean} true iff newly installed
 */
function install() {
  const proto=ShadowRiderCalyrexVMAX.prototype;
  if(proto[MARK]) return false;
  const original=proto.reduceEffect;
  proto.reduceEffect=function(store,state,effect) {
    if(!(effect instanceof PowerEffect) || effect.power!==this.powers[0])
      return original.call(this,store,state,effect);
    const owner=effect.player,previous=store.prompt;
    // The pinned source checks only for a nonempty Bench. With no Psychic
    // Bench target the Ability has no possible effect and cannot be used.
    if(!owner.bench.some(slot=>{
      const pokemon=slot.getPokemonCard();
      return pokemon && pokemonHasCardType(pokemon,CardType.PSYCHIC);
    })) throw new GameError(GameMessage.CANNOT_USE_POWER);
    store.prompt=function(s,prompt,continuation) {
      if(prompt instanceof AttachEnergyPrompt && prompt.playerId===owner.id &&
          prompt.cardList===owner.hand && prompt.slots.includes(SlotType.BENCH)) {
        const invalid=[];
        owner.bench.forEach((slot,index)=>{
          const pokemon=slot.getPokemonCard();
          if(!pokemon || !pokemonHasCardType(pokemon,CardType.PSYCHIC)) invalid.push(index);
        });
        const blocked=new Set(invalid);
        prompt.options.blockedTo.push(...invalid.map(index=>({
          player:PlayerType.BOTTOM_PLAYER,slot:SlotType.BENCH,index
        })));
        const validate=prompt.validate.bind(prompt);
        prompt.validate=function(assignments) {
          return validate(assignments) && (assignments===null || assignments.every(a=>
            a.to.player===PlayerType.BOTTOM_PLAYER && a.to.slot===SlotType.BENCH &&
            Number.isInteger(a.to.index) && !blocked.has(a.to.index) &&
            a.to.index>=0 && a.to.index<owner.bench.length));
        };
      }
      return previous.call(this,s,prompt,continuation);
    };
    try { return original.call(this,store,state,effect); }
    finally {store.prompt=previous;}
  };
  Object.defineProperty(proto,MARK,{value:true});
  return true;
}
module.exports={install};
