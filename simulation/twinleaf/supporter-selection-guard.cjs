'use strict';
const assert = require('node:assert/strict');

/**
 * Research-side guard for pinned SimpleTacticsAi PlaySupporterTactic.
 *
 * The native tactic writes player.supporterTurn = state.turn while deciding
 * which action to return. Boss's Orders and other native Supporter reducers
 * then reject the real dispatch as SUPPORTER_ALREADY_PLAYED. A policy query
 * cannot consume the live player's once-per-turn Supporter entitlement.
 *
 * Restore exactly that uncommitted counter before dispatch; preserve all
 * other State and returned action identities. Version the guard in traces.
 *
 * @returns {{
 *   decode:(bot:{decodeNextAction:(state:object)=>object|undefined},state:object,playerId:number)=>object|undefined,
 *   snapshot:()=>{restored_live_supporter_counters:number}
 * }}
 */
function makeSupporterSelectionGuard() {
  let corrections = 0;

  /**
   * @param {{decodeNextAction:(state:object)=>object|undefined}} bot
   * @param {{players:{id:number,supporterTurn:number}[],turn:number}} state
   * @param {number} playerId Native Player.id
   * @returns {object|undefined} Native action; unaffected by the guard
   */
  function decode(bot, state, playerId) {
    const actor = state.players.find(player => player.id === playerId);
    assert.ok(actor, 'Native bot actor must exist in State');
    const original = actor.supporterTurn;
    try {
      return bot.decodeNextAction(state);
    } finally {
      if (actor.supporterTurn !== original) {
        const speculativeCounter = actor.supporterTurn;
        actor.supporterTurn = original;
        assert.equal(speculativeCounter, state.turn,
          'Unexpected native Supporter counter side effect; re-audit pinned source');
        corrections++;
      }
    }
  }

  return {
    decode,
    snapshot() {
      return {restored_live_supporter_counters: corrections};
    }
  };
}
module.exports = {makeSupporterSelectionGuard};
