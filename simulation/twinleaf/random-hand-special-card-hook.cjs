'use strict';

/**
 * Research-owned exact-print repairs for three random-hand attack reducers
 * whose original control flow is incompatible with a simple prompt interceptor.
 * All three are pinned to Twinleaf 3348ebdc898f175a2ed8f999133cd13d1afd01f5.
 */

const MARKER=Symbol.for('pokemon-workplace.twinleaf.random-hand-special-v1');

/**
 * @template T
 * @param {T[]} hand
 * @param {()=>number} random
 * @returns {T|null}
 */
function drawUniform(hand,random) {
  if(hand.length===0)return null;
  const n=random();
  if(!Number.isFinite(n)||n<0||n>=1)
    throw new RangeError('Expected uniform game RNG float in [0,1)');
  return hand[Math.floor(n*hand.length)];
}

/**
 * @param {{
 *   Wimpod:Function,Honchkrow:Function,Dusclops:Function,
 *   AttackEffect:Function,CoinFlipEffect:Function,MoveCardsEffect:Function,
 *   ChoosePokemonPrompt:Function,ShowCardsPrompt:Function,ShuffleDeckPrompt:Function,
 *   GameMessage:any,PlayerType:any,SlotType:any,
 *   random?:()=>number
 * }} adapters
 * @returns {string[]} Source-guarded print names.
 */
function installRandomHandSpecialHooks(adapters) {
  const {
    Wimpod,Honchkrow,Dusclops,AttackEffect,CoinFlipEffect,MoveCardsEffect,
    ChoosePokemonPrompt,ShowCardsPrompt,ShuffleDeckPrompt,
    GameMessage,PlayerType,SlotType
  }=adapters;
  const random=adapters.random ?? (()=>Math.random());

  /** @param {Function} CardClass
   * @param {(store:any,state:any,effect:any)=>any} replacement
   */
  function patch(CardClass,replacement) {
    const prototype=CardClass.prototype;
    const previous=prototype.reduceEffect;
    if(previous[MARKER])return;
    /** @this {any} @param {any} store @param {any} state @param {any} effect */
    function wrappedReduce(store,state,effect) {
      if(!(effect instanceof AttackEffect) || effect.attack!==this.attacks[0])
        return previous.call(this,store,state,effect);
      return replacement.call(this,store,state,effect);
    }
    /** @returns {void} */
    function uninstall() {
      if(prototype.reduceEffect===wrappedReduce)
        prototype.reduceEffect=previous;
    }
    Object.defineProperty(wrappedReduce,MARKER,{value:uninstall});
    prototype.reduceEffect=wrappedReduce;
  }

  // In pinned Wimpod PAR48, the original reducer creates a coin prompt and
  // an unrelated discard choice even after tails. The replacement creates
  // the discard effect only from the actual heads-resolution callback.
  patch(Wimpod,function repairWimpod(store,state,effect) {
    const actor=effect.player;
    const opponent=state.players.find(p=>p.id!==actor.id);
    if(opponent.hand.cards.length===0)return state;
    return store.reduceEffect(state,new CoinFlipEffect(actor,heads=>{
      if(heads!==true || opponent.hand.cards.length===0)return;
      const chosen=drawUniform(opponent.hand.cards,random);
      store.reduceEffect(state,new MoveCardsEffect(
        opponent.hand,opponent.discard,{cards:[chosen],sourceCard:this}
      ));
    }));
  });

  // The pinned Honchkrow UPR72 incorrectly requests a one-card choice when
  // the opponent's hand is EMPTY, and never discards with a nonempty hand.
  // Preserve the source's optional Bench switch in the same attack.
  patch(Honchkrow,function repairHonchkrow(store,state,effect) {
    const actor=effect.player;
    const opponent=state.players.find(p=>p.id!==actor.id);
    const chosen=drawUniform(opponent.hand.cards,random);
    if(chosen!==null) {
      store.reduceEffect(state,new MoveCardsEffect(
        opponent.hand,opponent.discard,{cards:[chosen],sourceCard:this}
      ));
    }
    if(!actor.bench.some(slot=>slot.cards.length>0))return state;
    return store.prompt(state,new ChoosePokemonPrompt(
      actor.id,GameMessage.CHOOSE_POKEMON_TO_SWITCH,
      PlayerType.BOTTOM_PLAYER,[SlotType.BENCH],{allowCancel:false}
    ),result=>{
      actor.switchPokemon(result[0]);
    });
  });

  // Dusclops BCR62's original Astonish generator yields a queued card-choice
  // prompt and later resumes it with callback-driven generator.next(). Calling
  // that callback synchronously would reenter the already-running generator.
  // Reproduce its move->reveal->shuffle sequence without the random chooser.
  patch(Dusclops,function repairDusclops(store,state,effect) {
    const actor=effect.player;
    const opponent=state.players.find(p=>p.id!==actor.id);
    const chosen=drawUniform(opponent.hand.cards,random);
    if(chosen===null)return state;
    const cards=[chosen];
    store.reduceEffect(state,new MoveCardsEffect(
      opponent.hand,opponent.deck,{
        cards,sourceCard:this,sourceEffect:this.attacks[0]
      }
    ));
    return store.prompt(state,new ShowCardsPrompt(
      actor.id,GameMessage.CARDS_SHOWED_BY_THE_OPPONENT,cards
    ),()=>{
      return store.prompt(state,new ShuffleDeckPrompt(opponent.id),order=>{
        opponent.deck.applyOrder(order);
      });
    });
  });

  return ['Wimpod PAR48 Sneaky Snacking','Honchkrow UPR72 Rip and Run',
    'Dusclops BCR62 Astonish'];
}

module.exports={MARKER,drawUniform,installRandomHandSpecialHooks};
