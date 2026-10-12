'use strict';

/**
 * Research-owned, reversible compatibility hook for pinned Twinleaf's
 * Trevenant & Dusknoir-GX SMP 217 Night Watch.
 *
 * Pinned upstream currently offers the attacking player an arbitrary
 * ChooseCardsPrompt instead of selecting two random opposing hand cards.
 * Preserve upstream's tested MOVE_CARDS / SHOW_CARDS / SHUFFLE_DECK tail by
 * automatically resolving exactly that initial prompt with a seeded,
 * uniformly random without-replacement physical subset.
 *
 * The hook depends on the inspected pinned engine's reducer structure.
 * Reverify before changing Twinleaf's pinned revision.
 */

/**
 * Uniformly sample k distinct *card objects* from an array.
 * The caller's RNG stream controls reproducible stochastic transitions.
 *
 * @template T
 * @param {T[]} cards
 * @param {number} count
 * @param {() => number} random
 * @returns {T[]}
 */
function sampleWithoutReplacement(cards, count, random) {
  const pool = cards.slice();
  if (count < 0 || count > pool.length || !Number.isInteger(count)) {
    throw new RangeError('Invalid draw count');
  }
  for (let i = 0; i < count; i++) {
    const unit = random();
    if (!Number.isFinite(unit) || unit < 0 || unit >= 1) {
      throw new RangeError('RNG must return a float in [0, 1)');
    }
    const j = i + Math.floor(unit * (pool.length - i));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, count);
}

const PATCH_MARKER = Symbol.for('pokemon-workplace.twinleaf.night-watch-random-v1');

/**
 * @param {{
 *   TrevenantDusknoirGX: Function,
 *   AttackEffect: Function,
 *   ChooseCardsPrompt: Function,
 *   random?: () => number
 * }} adapters
 * @returns {() => void} Remove the hook and restore the previous reducer.
 */
function installNightWatchRandomHook(adapters) {
  const { TrevenantDusknoirGX, AttackEffect, ChooseCardsPrompt } = adapters;
  const random = adapters.random ?? Math.random;
  const prototype = TrevenantDusknoirGX.prototype;
  const prior = prototype.reduceEffect;

  if (prior[PATCH_MARKER]) {
    return prior[PATCH_MARKER];
  }

  /** @this {any} */
  function patchedReduceEffect(store, state, effect) {
    if (!(effect instanceof AttackEffect) ||
        effect.attack !== this.attacks[0]) {
      return prior.call(this, store, state, effect);
    }

    const player = effect.player;
    const opponent = state.players.find(p => p.id !== player.id);
    if (!opponent || opponent.hand.cards.length === 0) {
      return prior.call(this, store, state, effect);
    }

    const initialHand = opponent.hand;
    const originalPrompt = store.prompt;
    const hadOwnPrompt = Object.prototype.hasOwnProperty.call(store, 'prompt');
    const n = Math.min(2, initialHand.cards.length);
    let intercepted = false;
    store.prompt = function interceptNightWatch(nextState, prompt, resolve) {
      if (!intercepted && prompt instanceof ChooseCardsPrompt &&
          prompt.playerId === player.id &&
          prompt.cards === initialHand && prompt.options.isSecret === true &&
          prompt.options.min === n && prompt.options.max === n) {
        intercepted = true;
        const selected = sampleWithoutReplacement(
          initialHand.cards, n, random
        );
        // Continue the original card implementation with authentic physical
        // card identities, so it performs its existing move/reveal/shuffle.
        return resolve(selected);
      }
      return originalPrompt.call(store, nextState, prompt, resolve);
    };

    try {
      const result = prior.call(this, store, state, effect);
      if (!intercepted) {
        throw new Error('Night Watch compatibility hook did not find the pinned selection prompt');
      }
      return result;
    } finally {
      if (hadOwnPrompt) {
        store.prompt = originalPrompt;
      } else {
        delete store.prompt;
      }
    }
  }

  /** @returns {void} */
  function uninstall() {
    if (prototype.reduceEffect === patchedReduceEffect) {
      prototype.reduceEffect = prior;
    }
  }

  Object.defineProperty(patchedReduceEffect, PATCH_MARKER, {
    value: uninstall,
  });
  prototype.reduceEffect = patchedReduceEffect;
  return uninstall;
}

module.exports = { sampleWithoutReplacement, installNightWatchRandomHook };
