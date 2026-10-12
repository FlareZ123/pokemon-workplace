'use strict';

/**
 * Pinned Twinleaf semantic diagnostic for the 2026 Aichi champion's
 * Trevenant & Dusknoir-GX (SMP 217) Night Watch attack.
 *
 * This SFT witnesses that the live reducer yields an attacker-owned
 * ChooseCardsPrompt accepting every 2-of-3 pair from the opponent's hand.
 * It does not presume that the UI reveals those cards to the attacker.
 * Card text requires two *random* cards, so unconstrained chooser selection
 * is materially different from a uniform random-card outcome.
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const cp = require('node:child_process');

const ROOT = path.resolve(__dirname, '../..');
const SERVER = path.join(ROOT, 'vendor/twinleafgg/ptcg-server');
const VENDOR = path.join(ROOT, 'vendor/twinleafgg');
const PIN = '3348ebdc898f175a2ed8f999133cd13d1afd01f5';

process.env.TS_NODE_PROJECT = path.join(SERVER, 'tsconfig.json');
require(require.resolve('ts-node/register/transpile-only', { paths: [SERVER] }));

/** @param {string} file Source path under pinned ptcg-server/src. */
function engine(file) {
  return require(path.join(SERVER, 'src', file));
}

/** @returns {{status:string,pairs:number,expectedRandomPairProbability:number}} */
function run() {
  const revision = cp.execFileSync('git', ['rev-parse', 'HEAD'],
    { cwd: VENDOR, encoding: 'utf8' }).trim();
  assert.equal(revision, PIN, 'Engine revision changed; review test semantics');

  const { TrevenantDusknoirGX } = engine(
    'sets/08-sun-and-moon/set-sun-and-moon-promos/trevenant-dusknoir-gx.ts'
  );
  const { Player } = engine('game/store/state/player.ts');
  const { AttackEffect } = engine('game/store/effects/game-effects.ts');
  const { ChooseCardsPrompt } = engine(
    'game/store/prompts/choose-cards-prompt.ts'
  );

  const trevenant = new TrevenantDusknoirGX();
  assert.equal(trevenant.set, 'SMP');
  assert.equal(trevenant.setNumber, '217');
  assert.equal(trevenant.attacks[0].name, 'Night Watch');
  assert.match(trevenant.attacks[0].text, /2 random cards/);

  const attacker = new Player();
  attacker.id = 1;
  const defender = new Player();
  defender.id = 2;
  const hidden = Array.from({ length: 3 }, (_, i) => {
    const card = new TrevenantDusknoirGX();
    card.id = 100 + i;
    return card;
  });
  defender.hand.cards.push(...hidden);

  const state = { players: [attacker, defender] };
  /** @type {import('../../vendor/twinleafgg/ptcg-server/src/game/store/prompts/choose-cards-prompt').ChooseCardsPrompt | null} */
  let observed = null;
  const store = {
    prompt(_state, prompt, _callback) {
      assert.equal(observed, null);
      observed = prompt;
      return _state;
    },
  };
  const effect = new AttackEffect(attacker, defender, trevenant.attacks[0]);
  trevenant.reduceEffect(store, state, effect);

  assert.ok(observed instanceof ChooseCardsPrompt);
  assert.equal(observed.playerId, attacker.id);
  assert.equal(observed.cards, defender.hand);
  assert.equal(observed.options.isSecret, true);
  assert.equal(observed.options.min, 2);
  assert.equal(observed.options.max, 2);

  const allowedPairs = [[0, 1], [0, 2], [1, 2]];
  for (const pair of allowedPairs) {
    const decoded = observed.decode(pair);
    assert.ok(observed.validate(decoded), 'unexpected illegal pair ' + pair);
    assert.deepEqual(decoded.map(card => card.id),
      pair.map(index => 100 + index));
  }

  const evidence = {
    status: 'random-card-selection-not-enforced',
    attack: 'Night Watch',
    printed: 'SMP 217',
    promptOwner: 'attacking player',
    opponentHandCount: 3,
    legalChoicePairs: allowedPairs.length,
    expectedUniformProbabilityPerPair: 1 / allowedPairs.length,
    engineRevision: PIN,
  };
  console.log(JSON.stringify(evidence, null, 2));
  console.log('Night Watch random-versus-choice SFT passed');
  return {
    status: evidence.status,
    pairs: allowedPairs.length,
    expectedRandomPairProbability: 1 / allowedPairs.length,
  };
}

if (require.main === module) {
  run();
}

module.exports = { run };
