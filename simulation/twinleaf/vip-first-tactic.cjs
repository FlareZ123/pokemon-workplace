'use strict';
const assert = require('node:assert/strict');

/**
 * Construct a research-only tactic for the exact Battle VIP Pass first-turn
 * window. Returns the upstream PlayCardAction with its standard BOARD target,
 * leaving the engine to validate legality and resolve Bench selection.
 *
 * @param {new (...args:any[])=>object} PlayCardAction Pinned native action
 * @param {{ANY:number}} PlayerType
 * @param {{BOARD:number}} SlotType
 * @returns {new (options:object)=>{useTactic:(state:object,player:object)=>object|undefined}}
 */
function makeVipFirstTactic(PlayCardAction, PlayerType, SlotType) {
  assert.equal(typeof PlayCardAction, 'function');
  assert.ok(Number.isInteger(PlayerType.ANY));
  assert.ok(Number.isInteger(SlotType.BOARD));

  return class ResearchVipFirstTactic {
    /** @param {object} _options Native tactics constructor compatibility */
    constructor(_options) {}

    /**
     * @param {object} state Pinned game State
     * @param {object} player Pinned Player with own hand and Bench
     * @returns {object|undefined}
     */
    useTactic(state, player) {
      if (state.turn < 1 || state.turn > 2) return;
      if (!player.bench.some(slot => slot.cards.length === 0)) return;
      const index = player.hand.cards.findIndex(card => card.name === 'Battle VIP Pass');
      if (index < 0) return;
      return new PlayCardAction(player.id, index,
        {player: PlayerType.ANY, slot: SlotType.BOARD, index: 0});
    }
  };
}

module.exports = {makeVipFirstTactic};
