'use strict';
const assert = require('node:assert/strict');

/**
 * Lightweight reporting boundary for the pinned Twinleaf Store.
 * Capture the inputs before dispatch because the engine mutates a State in
 * place. Neither capture nor observation changes decisions or uses RNG.
 */
function makeMatchActionTelemetry() {
  const activity = [
    {attacks: {}, abilities: {}, cards_played: {}, retreats: 0, passes: 0},
    {attacks: {}, abilities: {}, cards_played: {}, retreats: 0, passes: 0}
  ];
  const prizeEvents = [];

  /** @param {Record<string, number>} counts @param {string} label */
  function record(counts, label) {
    counts[label] = (counts[label] || 0) + 1;
  }

  /**
   * @param {object} action Native Twinleaf action
   * @param {object} state Native Twinleaf State, before dispatch
   * @returns {{turn:number,seat:number,prizes:number[],played_card:string|null}}
   */
  function capture(action, state) {
    assert.equal(state.players.length, 2, 'Game must have two players');
    const playerId = action.clientId ?? (action.type === 'PLAY_CARD_ACTION' ? action.id : undefined);
    const seat = state.players.findIndex(player => player.id === playerId);
    let playedCard = null;
    if (seat >= 0 && action.type === 'PLAY_CARD_ACTION') {
      const card = state.players[seat].hand.cards[action.handIndex];
      assert.ok(card && typeof card.name === 'string', 'Played card must originate in hand');
      playedCard = card.name;
    }
    return {turn: state.turn, seat, prizes: state.players.map(p => p.getPrizeLeft()),
      played_card: playedCard};
  }

  /**
   * Called only after the Store accepts the action.
   * @param {object} action Native Twinleaf action
   * @param {{turn:number,seat:number,prizes:number[],played_card:string|null}} before
   * @param {object} after Native Twinleaf State after dispatch
   * @param {number} step Zero-based action index
   */
  function observe(action, before, after, step) {
    assert.ok(Number.isSafeInteger(step) && step >= 0);
    assert.equal(after.players.length, 2);
    const row = activity[before.seat];

    if (row) {
      if (action.type === 'ATTACK_ACTION') {
        assert.ok(typeof action.name === 'string' && action.name.length > 0);
        record(row.attacks, action.name);
      } else if (action.type === 'USE_ABILITY_ACTION' ||
        action.type === 'USE_TRAINER_ABILITY_ACTION' ||
        action.type === 'USE_ENERGY_ABILITY_ACTION') {
        assert.ok(typeof action.name === 'string' && action.name.length > 0);
        record(row.abilities, action.name);
      } else if (action.type === 'PLAY_CARD_ACTION') {
        record(row.cards_played, before.played_card);
      } else if (action.type === 'RETREAT_ACTION') {
        row.retreats++;
      } else if (action.type === 'PASS_TURN') {
        row.passes++;
      }
    }

    // Prize setup is over before the first player turn. A single resolution
    // can take multiple Prizes, so record counts for each player separately.
    if (before.turn >= 1) {
      for (let i = 0; i < 2; i++) {
        const next = after.players[i].getPrizeLeft();
        if (next !== before.prizes[i]) {
          prizeEvents.push({step, turn: before.turn, seat: i + 1,
            prizes_before: before.prizes[i], prizes_after: next});
        }
      }
    }
  }

  return {
    capture, observe,
    /** @returns {{by_seat:object[],prize_events:object[]}} */
    snapshot() {
      return {
        by_seat: activity.map(row => ({
          attacks: {...row.attacks},
          abilities: {...row.abilities},
          cards_played: {...row.cards_played},
          retreats: row.retreats, passes: row.passes
        })),
        prize_events: prizeEvents.map(event => ({...event}))
      };
    }
  };
}

module.exports = {makeMatchActionTelemetry};
