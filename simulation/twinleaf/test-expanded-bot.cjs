'use strict';

const assert = require('node:assert/strict');
const { ExpandedResearchBot } = require('./expanded-research-bot.cjs');
const { Format } = require('../../vendor/twinleafgg/ptcg-server/output/game/store/card/card-types');

/**
 * SFT: validate the fixed-deck Expanded research adapter without a database or
 * simulated game. Card labels are synthetic and intentionally never dispatched
 * to the Twinleaf game engine.
 *
 * @returns {Promise<void>}
 */
async function main() {
  const fixed = Array.from({ length: 60 }, (_, i) => `test-card-${i}`);
  const bot = new ExpandedResearchBot('Expanded SFT', fixed);
  console.log('[expanded-bot] Created bot using synthetic 60-card fixture');

  assert.deepEqual(bot.getAllowedFormats(), [Format.EXPANDED]);
  assert.equal(bot.isFormatAllowed(Format.EXPANDED), true);
  assert.equal(bot.isFormatAllowed(Format.STANDARD), false);
  console.log('[expanded-bot] Format restriction enforced');

  fixed[0] = 'mutated-after-creation';
  const first = await bot.loadDeck();
  assert.equal(first.length, 60);
  assert.equal(first[0], 'test-card-0');
  first[1] = 'mutated-returned-deck';
  const second = await bot.loadDeck();
  assert.equal(second[1], 'test-card-1');
  assert.deepEqual(second, await bot.getDeck(Format.EXPANDED));
  console.log('[expanded-bot] Deck selected deterministically and copied');

  assert.throws(() => new ExpandedResearchBot('short', fixed.slice(0, 59)), TypeError);
  assert.throws(() => new ExpandedResearchBot('null', [...fixed.slice(0, 59), null]), TypeError);
  assert.throws(() => new ExpandedResearchBot('blank', [...fixed.slice(0, 59), '']), TypeError);
  console.log('[expanded-bot] Invalid length and identifiers rejected');

  const custom = new ExpandedResearchBot('custom', second, {});
  assert.equal((await custom.loadDeck()).length, 60);
  assert.equal(custom.isFormatAllowed(Format.EXPANDED), true);
  console.log('[expanded-bot] PASS: fixed deck boundary verified');
}

main().catch(error => {
  console.error('[expanded-bot] FAIL:', error);
  process.exitCode = 1;
});
