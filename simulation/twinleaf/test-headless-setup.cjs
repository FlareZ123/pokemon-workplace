'use strict';

const assert = require('node:assert/strict');
const { ExpandedResearchBot } = require('./expanded-research-bot.cjs');
const { CardManager } = require('../../vendor/twinleafgg/ptcg-server/output/game/cards/card-manager');
const { Game } = require('../../vendor/twinleafgg/ptcg-server/output/game/core/game');
const { GameSettings } = require('../../vendor/twinleafgg/ptcg-server/output/game/core/game-settings');
const { AddPlayerAction } = require('../../vendor/twinleafgg/ptcg-server/output/game/store/actions/add-player-action');
const { Format } = require('../../vendor/twinleafgg/ptcg-server/output/game/store/card/card-types');
const { GamePhase } = require('../../vendor/twinleafgg/ptcg-server/output/game/store/state/state');
const { config } = require('../../vendor/twinleafgg/ptcg-server/output/config');
const sets = require('../../vendor/twinleafgg/ptcg-server/output/sets');

/** @returns {Promise<void>} */
async function main() {
  const manager = CardManager.getInstance();
  manager.defineSet(sets.setChillingReign);
  manager.defineSet(sets.setScarletAndVioletEnergy);

  const basic = 'Shadow Rider Calyrex V CRE';
  const energy = 'Psychic Energy SVE';
  assert.equal(manager.isCardDefined(basic), true);
  assert.equal(manager.isCardDefined(energy), true);
  const deck = [...Array(4).fill(basic), ...Array(56).fill(energy)];
  const a = new ExpandedResearchBot('Smoke A', deck);
  const b = new ExpandedResearchBot('Smoke B', deck);
  a.id = 1;
  b.id = 2;
  a.user.id = 101;
  b.user.id = 102;

  const originalDelay = config.bots.actionDelay;
  config.bots.actionDelay = 0;
  let deleted = false;
  const clients = [a, b];
  const core = {
    emit(fn) { clients.forEach(fn); },
    deleteGame() { deleted = true; }
  };

  const settings = new GameSettings();
  settings.format = Format.EXPANDED;
  settings.recordingEnabled = false;
  settings.timeLimit = 60;
  const game = new Game(core, 1, settings);

  try {
    game.dispatch(a, new AddPlayerAction(a.id, a.name, deck));
    game.dispatch(a, new AddPlayerAction(b.id, b.name, deck));
    game.clients.push(a, b);
    a.onGameJoin(game, a);
    b.onGameJoin(game, b);

    const deadline = Date.now() + 12000;
    let turn = game.state.turn;
    while (Date.now() < deadline && turn < 2 && game.state.phase !== GamePhase.FINISHED) {
      await new Promise(resolve => setTimeout(resolve, 20));
      turn = game.state.turn;
    }

    console.log('[headless-setup] state:', JSON.stringify({
      turn: game.state.turn,
      phase: GamePhase[game.state.phase],
      players: game.state.players.length,
      unresolvedPrompts: game.state.prompts.filter(prompt => prompt.result === undefined)
        .map(prompt => ({ type: prompt.type, playerId: prompt.playerId })),
      deleted
    }));
    assert.equal(game.state.players.length, 2);
    assert.ok(game.state.turn >= 2 || game.state.phase === GamePhase.FINISHED,
      'Two fixed-deck bots must progress through setup into turn 2');
    console.log('[headless-setup] PASS: independent fixed-deck bots advanced a real Twinleaf game');
  } finally {
    a.onGameLeave(game, a);
    b.onGameLeave(game, b);
    // Pinned Game.cleanup() omits stopPeriodicSync(); avoid an orphaned
    // 15-second timer keeping the Node headless test process alive forever.
    game.stopPeriodicSync();
    game.cleanup();
    config.bots.actionDelay = originalDelay;
  }
}

main().catch(error => {
  console.error('[headless-setup] FAIL:', error);
  process.exitCode = 1;
});
