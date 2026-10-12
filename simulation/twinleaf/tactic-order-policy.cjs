'use strict';
const assert = require('node:assert/strict');

const MODES = Object.freeze(['native', 'attack_before_retreat']);

/**
 * Research-owned alternative to the pinned upstream SimpleTacticsAi tactic
 * priority. Both modes reuse the exact same upstream tactic implementations.
 * @template T
 * @param {'native'|'attack_before_retreat'} mode
 * @param {T[]} tactics Native array of tactic constructors
 * @returns {T[]} Copy safe to hand to SimpleTacticsAi
 */
function makeTacticOrder(mode, tactics) {
  assert.ok(MODES.includes(mode), 'Unknown research tactic order: ' + mode);
  assert.ok(Array.isArray(tactics) && tactics.length > 1);
  const ordered = [...tactics];
  if (mode === 'native') return ordered;

  const attackIndex = ordered.findIndex(Tactic => Tactic.name === 'AttackTactic');
  const retreatIndex = ordered.findIndex(Tactic => Tactic.name === 'RetreatTactic');
  assert.ok(attackIndex >= 0 && retreatIndex >= 0,
    'Expected pinned AttackTactic and RetreatTactic implementations');
  assert.ok(retreatIndex < attackIndex,
    'Pinned native tactic ordering changed; inspect before changing priority');
  const [attack] = ordered.splice(attackIndex, 1);
  ordered.splice(retreatIndex, 0, attack);
  return ordered;
}

module.exports = {MODES, makeTacticOrder};
