'use strict';
const assert=require('node:assert/strict');

/**
 * K0 exchangeable-pool probability that the next k unrevealed deck positions
 * contain at least one eligible print. The pool comprises deck plus face-down
 * Prizes; its combined multiset is inferable from a known decklist and public
 * removals even when their current allocation is unknown.
 * This is not a K1 posterior or a prediction after tracked deck-order effects.
 * @param {number} poolSize
 * @param {number} hits
 * @param {number} draws
 * @returns {number}
 */
function atLeastOne(poolSize,hits,draws) {
  assert.ok([poolSize,hits,draws].every(Number.isSafeInteger));
  assert.ok(poolSize>=0 && hits>=0 && hits<=poolSize && draws>=0 && draws<=poolSize);
  let miss=1;
  for(let i=0;i<draws;i++) {
    if(i>=poolSize-hits)return 1;
    miss*= (poolSize-hits-i)/(poolSize-i);
  }
  return 1-miss;
}

/**
 * Research-only surrogate for the two specific printed top-k Items whose
 * pinned native lookahead was proven to inspect secret deck order.
 * Other Items still use native evaluation and may have independent leakage.
 *
 * Native benchmark (results/tests/twinleaf_hidden_topdeck_oracle) measures
 * +4 / -2 bot score for hit/miss in its controlled fixture. The constant
 * -2+6p is therefore a deliberately provisional heuristic elsewhere.
 * Neither this narrow patch nor the native tactic is a competitive policy.
 *
 * @param {Function} NativeTactic
 * @param {{TrainerCard:Function,TrainerType:object,PlayCardAction:Function,PlayerType:object,SlotType:object}} engine
 * @returns {Function}
 */
function makeBlindTopdeckTrainerTactic(NativeTactic,engine) {
  const {TrainerCard,TrainerType,PlayCardAction,PlayerType,SlotType}=engine;
  assert.equal(typeof NativeTactic,'function');
  const targets={
    'Pokegear SVI':{window:7,eligible:c=>
      c instanceof TrainerCard && c.trainerType===TrainerType.SUPPORTER},
    "Trainers' Mail ROS":{window:4,eligible:c=>
      c instanceof TrainerCard && c.name!=="Trainers' Mail"}
  };
  return class BlindTopdeckTrainerTactic extends NativeTactic {
    useTactic(state,player) {
      const items=player.hand.cards.filter(c=>
        c instanceof TrainerCard && c.trainerType===TrainerType.ITEM);
      if(items.length===0)return;
      const target={player:PlayerType.ANY,slot:SlotType.BOARD,index:0};
      const baseline=this.getStateScore(state,player.id);
      const unseen=[...player.deck.cards,...player.prizes.flatMap(slot=>slot.cards)];
      let bestScore=baseline;
      let best;
      for(const item of items) {
        const index=player.hand.cards.indexOf(item);
        const action=new PlayCardAction(player.id,index,target);
        const spec=targets[item.fullName];
        let score;
        if(spec) {
          if(player.deck.cards.length===0)continue;
          const count=unseen.filter(spec.eligible).length;
          const probability=atLeastOne(unseen.length,count,
            Math.min(player.deck.cards.length,spec.window));
          score=baseline-2+6*probability;
        } else {
          score=this.evaluateAction(state,player.id,action);
        }
        if(score!==undefined && score>bestScore) {
          bestScore=score;
          best=action;
        }
      }
      return best;
    }
  };
}
module.exports={atLeastOne,makeBlindTopdeckTrainerTactic};
