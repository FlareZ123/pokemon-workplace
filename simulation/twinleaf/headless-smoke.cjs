'use strict';

/**
 * Research-owned Twinleaf headless smoke pinned to an inspected upstream commit.
 * In-memory Store, live state transitions, real simple bot decisions.
 * The two minimalist 60-card decks are engine smoke fixtures, not optimized.
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const cp = require('node:child_process');

const vendor = path.resolve(__dirname, '../../vendor/twinleafgg');
const server = path.join(vendor, 'ptcg-server');
const expectedRevision = '3348ebdc898f175a2ed8f999133cd13d1afd01f5';
process.env.TS_NODE_PROJECT = path.join(server, 'tsconfig.json');
require(require.resolve('ts-node/register/transpile-only', { paths: [server] }));

/** @param {string} name @returns {any} */
function engine(name) {
  return require(path.join(server, 'src', name));
}

const { CardManager } = engine('game/cards/card-manager.ts');
const { Store } = engine('game/store/store.ts');
const { Format } = engine('game/store/card/card-types.ts');
const { AddPlayerAction } = engine('game/store/actions/add-player-action.ts');
const { GamePhase } = engine('game/store/state/state.ts');
const { SimpleTacticsAi } = engine('simple-bot/simple-tactics-ai.ts');
const {
  allSimpleTactics, allPromptResolvers, defaultStateScores, defaultArbiterOptions
} = engine('simple-bot/simple-bot-definitions.ts');
const { BotArbiter, BotFlipMode, BotShuffleMode } =
  engine('game/bots/bot-arbiter.ts');
const { RegidragoV } =
  engine('sets/09-sword-and-shield/set-silver-tempest/regidrago-v.ts');
const { GrassEnergy, FireEnergy } =
  engine('sets/06-black-and-white/set-black-and-white/basic-energies.ts');

/** @param {number} seed @returns {() => number} */
function makeRandom(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6D2B79F5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** @returns {string[]} */
function smokeDeck() {
  return [
    ...Array(4).fill('Regidrago V SIT'),
    ...Array(28).fill('Grass Energy BLW'),
    ...Array(28).fill('Fire Energy BLW'),
  ];
}

/**
 * @param {number} seed
 * @param {number} maxActions
 * @returns {{status:string,seed:number,actions:number,turn:number,
 *   winner:number,phases:number[],attacks:number,revision:string}}
 */
function run(seed = 20261012, maxActions = 1000) {
  const revision = cp.execFileSync('git', ['rev-parse', 'HEAD'],
    { cwd: vendor, encoding: 'utf8' }).trim();
  assert.equal(revision, expectedRevision, 'Twinleaf pin changed without review');
  const originalRandom = Math.random;
  Math.random = makeRandom(seed);

  try {
    const manager = CardManager.getInstance();
    const instances = [new RegidragoV(), new GrassEnergy(), new FireEnergy()];
    for (const card of instances) {
      if (!manager.isCardDefined(card.fullName)) {
        manager.defineCard(card);
      }
    }

    const deck = smokeDeck();
    assert.equal(deck.length, 60);
    const store = new Store({ onStateChange: () => {} });
    store.state.gameSettings.format = Format.EXPANDED;
    store.state.gameSettings.recordingEnabled = false;

    const opts = {
      tactics: allSimpleTactics,
      promptResolvers: allPromptResolvers,
      scores: defaultStateScores,
      arbiter: defaultArbiterOptions,
    };
    const bots = new Map([1, 2].map(id => [
      id, new SimpleTacticsAi(
        { id, name: 'SmokeBot' + id }, opts, deck
      )
    ]));
    const arbiter = new BotArbiter({
      flipMode: BotFlipMode.RANDOM,
      shuffleMode: BotShuffleMode.RANDOM,
    });

    store.dispatch(new AddPlayerAction(1, 'SmokeBot1', deck));
    store.dispatch(new AddPlayerAction(2, 'SmokeBot2', deck));
    assert.equal(store.state.players.length, 2);
    assert.notEqual(store.state.phase, GamePhase.FINISHED);

    const phases = new Set([store.state.phase]);
    let attacks = 0;
    let actions = 0;

    for (; actions < maxActions; actions++) {
      const state = store.state;
      phases.add(state.phase);
      if (state.phase === GamePhase.FINISHED) {
        break;
      }

      const prompt = state.prompts.find(p => p.result === undefined);
      const playerId = prompt
        ? prompt.playerId : state.players[state.activePlayer]?.id;
      const bot = bots.get(playerId);
      assert.ok(bot, 'unhandled actor ' + playerId + ' on turn ' + state.turn);

      const action = prompt
        ? (arbiter.resolvePrompt(state, prompt) || bot.decodeNextAction(state))
        : bot.decodeNextAction(state);

      assert.ok(action, 'missing action on turn ' + state.turn +
        ' phase ' + state.phase + ' prompt ' +
        (prompt ? prompt.constructor.name : 'none'));
      try {
        store.dispatch(action);
      } catch (error) {
        const cause = error instanceof Error ? error.message : String(error);
        throw new Error('dispatch failed step ' + actions + ' turn ' +
          state.turn + ' phase ' + state.phase + ' action ' +
          action.constructor.name + ' prompt ' +
          (prompt ? prompt.constructor.name : 'none') + ': ' + cause,
          { cause: error });
      }
      if (action.type === 'ATTACK_ACTION') {
        attacks++;
      }
    }

    const state = store.state;
    assert.ok(state.turn >= 2, 'Twinleaf never completed an initial turn');
    assert.ok(phases.has(GamePhase.PLAYER_TURN),
      'Twinleaf never entered a player turn');
    return {
      status: state.phase === GamePhase.FINISHED ? 'finished' : 'action_limit',
      seed, actions, turn: state.turn, winner: state.winner,
      phases: [...phases].sort((a, b) => a - b), attacks, revision,
    };
  } finally {
    Math.random = originalRandom;
  }
}

if (require.main === module) {
  process.stdout.write(JSON.stringify({
    runner: 'research-owned-store-headless-smoke', ...run()
  }, null, 2) + '\n');
}

module.exports = { run, smokeDeck };
