'use strict';
const assert = require('node:assert/strict');
const {makeMatchActionTelemetry} = require('./match-action-telemetry.cjs');

/**
 * A small mutable stand-in for the real two-player Store: separate physical
 * card identifiers are unnecessary to check pre-dispatch snapshots.
 * @returns {object}
 */
function state() {
  return {turn: 3, players: [1, 2].map((id, i) => ({
    id,
    prizeLeft: 6,
    hand: {cards: [{name: i ? 'Energy Search' : 'Ultra Ball'}]},
    getPrizeLeft() {return this.prizeLeft;}
  }))};
}
const game = state();
const telemetry = makeMatchActionTelemetry();
const play = {type: 'PLAY_CARD_ACTION', id: 1, handIndex: 0};
const beforePlay = telemetry.capture(play, game);
game.players[0].hand.cards.shift();
telemetry.observe(play, beforePlay, game, 0);
assert.deepEqual(telemetry.snapshot().by_seat[0].cards_played, {'Ultra Ball': 1});
assert.deepEqual(telemetry.snapshot().by_seat[1].cards_played, {});
assert.deepEqual(telemetry.snapshot().prize_events, []);
console.log('[match-telemetry] pre-dispatch hand card identity survives Store mutation');

const attack = {type: 'ATTACK_ACTION', clientId: 2, name: 'Apex Dragon'};
const beforeAttack = telemetry.capture(attack, game);
game.players[1].prizeLeft = 4;
telemetry.observe(attack, beforeAttack, game, 1);
assert.deepEqual(telemetry.snapshot().by_seat[1].attacks, {'Apex Dragon': 1});
assert.deepEqual(telemetry.snapshot().prize_events,
  [{step: 1, turn: 3, seat: 2, prizes_before: 6, prizes_after: 4}]);

const ability = {type: 'USE_ABILITY_ACTION', clientId: 1, name: 'Underworld Door'};
telemetry.observe(ability, telemetry.capture(ability, game), game, 2);
const retreat = {type: 'RETREAT_ACTION', clientId: 1};
telemetry.observe(retreat, telemetry.capture(retreat, game), game, 3);
const pass = {type: 'PASS_TURN', clientId: 2};
telemetry.observe(pass, telemetry.capture(pass, game), game, 4);
const prompt = {type: 'RESOLVE_PROMPT_ACTION', id: 42};
telemetry.observe(prompt, telemetry.capture(prompt, game), game, 5);
const snapshot = telemetry.snapshot();
assert.deepEqual(snapshot.by_seat[0].abilities, {'Underworld Door': 1});
assert.equal(snapshot.by_seat[0].retreats, 1);
assert.equal(snapshot.by_seat[1].passes, 1);
assert.equal(snapshot.prize_events.length, 1);
assert.deepEqual(snapshot.by_seat[1].cards_played, {});

const setup = state();
setup.turn = 0;
const fresh = makeMatchActionTelemetry();
const setupAction = {type: 'SOME_SETUP_ACTION'};
const setupBefore = fresh.capture(setupAction, setup);
setup.players[0].prizeLeft = 0;
fresh.observe(setupAction, setupBefore, setup, 0);
assert.deepEqual(fresh.snapshot().prize_events, [], 'Setup Prize placement must not be counted');
assert.throws(() => fresh.capture({type:'PLAY_CARD_ACTION', id:1, handIndex:9}, setup),
  /Played card must originate in hand/);
console.log('[match-telemetry] PASS: seat attribution, attack/ability history, multi-Prize delta, setup exclusion, and missing card guard');
