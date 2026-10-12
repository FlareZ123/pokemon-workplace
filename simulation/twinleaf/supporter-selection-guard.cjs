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
 *   wrapTactic:(NativeTactic:Function)=>Function,
 *   snapshot:()=>{restored_live_supporter_counters:number}
 * }}
 */
function makeSupporterSelectionGuard() {
  let corrections = 0;

  /**
   * Undo only the known native PlaySupporterTactic preplay side effect.
   * @param {{supporterTurn:number}} actor
   * @param {number} original
   * @param {number} turn
   */
  function restore(actor, original, turn) {
    if (actor.supporterTurn !== original) {
      const speculativeCounter = actor.supporterTurn;
      actor.supporterTurn = original;
      assert.equal(speculativeCounter, turn,
        'Unexpected native Supporter counter side effect; re-audit pinned source');
      corrections++;
    }
  }

  /**
   * Restore immediately after the native tactic, BEFORE SimpleTacticsAi
   * validates its proposed action by cloning the current State.
   * @param {Function} NativeTactic Pinned PlaySupporterTactic class
   * @returns {Function} Drop-in native tactic constructor
   */
  function wrapTactic(NativeTactic) {
    assert.equal(typeof NativeTactic, 'function');
    return class ResearchSafeSupporterTactic extends NativeTactic {
      useTactic(state, actor) {
        const previous = actor.supporterTurn;
        try {
          return super.useTactic(state, actor);
        } finally {
          restore(actor, previous, state.turn);
        }
      }
    };
  }

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
      restore(actor, original, state.turn);
    }
  }

  return {
    decode,
    wrapTactic,
    snapshot() {
      return {restored_live_supporter_counters: corrections};
    }
  };
}
module.exports = {makeSupporterSelectionGuard};
