'use strict';
const assert = require('node:assert/strict');

/**
 * Lightweight reporting boundary for the pinned Twinleaf Store.
 * All events are read from dispatched actions and real game state; evaluation
 * does not alter decisions or consume any random numbers.
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
   * @param {object} action Pinned live-engine action
   * @param {object} before State before successful Store dispatch
   * @param {object} after State after successful Store dispatch
   * @param {number} step Zero-based action index
   */
  function observe(action, before, after, step) {
    assert.ok(Number.isSafeInteger(step) && step >= 0);
    assert.equal(before.players.length, 2);
    assert.equal(after.players.length, 2);

    const playerId = action.clientId ?? (action.type === 'PLAY_CARD_ACTION' ? action.id : undefined);
    const seat = before.players.findIndex(player => player.id === playerId);
    const row = activity[seat];

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
        const card = before.players[seat].hand.cards[action.handIndex];
        assert.ok(card && typeof card.name === 'string', 'Played card must originate in hand');
        record(row.cards_played, card.name);
      } else if (action.type === 'RETREAT_ACTION') {
        row.retreats++;
      } else if (action.type === 'PASS_TURN') {
        row.passes++;
      }
    }

    // A single resolution may take several Prizes; record one transition per
    // affected player, preserving the before and after counts. Initial setup
    // places the six Prizes and is deliberately excluded.
    if (before.turn >= 1 && before.phase !== 1 && after.phase !== 1) {
      for (let i = 0; i < 2; i++) {
        const prior = before.players[i].getPrizeLeft();
        const next = after.players[i].getPrizeLeft();
        if (next !== prior) {
          prizeEvents.push({step, turn: before.turn, seat: i + 1,
            prizes_before: prior, prizes_after: next});
        }
      }
    }
  }

  return {
    observe,
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
