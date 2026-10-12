'use strict';
/** @param {new (...args: any[]) => object} BaseArbiter */
function makeUniformShuffleArbiter(BaseArbiter) {
  return class UniformShuffleArbiter extends BaseArbiter {
    /** @param {{cards: object[]}} cards @returns {number[]} */
    shuffle(cards) {
      const order=Array.from({length:cards.cards.length},(_,i)=>i);
      for(let i=order.length-1;i>0;i--) {
        const j=Math.floor(Math.random()*(i+1));
        [order[i],order[j]]=[order[j],order[i]];
      }
      return order;
    }
  };
}
module.exports={makeUniformShuffleArbiter};
