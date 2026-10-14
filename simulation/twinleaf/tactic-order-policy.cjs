'use strict';
const assert = require('node:assert/strict');

const MODES = Object.freeze(['native','attack_before_retreat','vip_first','vip_attack_before_retreat','double_dragon_first','blind_topdeck','sampled_k0']);

/**
 * Research-owned alternatives to the pinned upstream SimpleTacticsAi priority.
 * Implementations remain upstream except for the independently constructed
 * first-turn VIP tactic. Original constructors and arrays are never mutated.
 * @template T
 * @param {string} mode One of MODES; blind_topdeck selects a tactic in the runner
 * @param {T[]} tactics Native pinned tactic constructors
 * @param {T} [vipTactic] Research VIP constructor, required for VIP modes
 * @param {T} [doubleDragonTactic] Explicit dynamic Special Energy tactic
 * @returns {T[]} New constructor array
 */
function makeTacticOrder(mode, tactics, vipTactic, doubleDragonTactic) {
  assert.ok(MODES.includes(mode), 'Unknown research tactic order: ' + mode);
  assert.ok(Array.isArray(tactics) && tactics.length > 1);
  const ordered = [...tactics];

  if (mode === 'attack_before_retreat' || mode === 'vip_attack_before_retreat') {
    const attackIndex = ordered.findIndex(Tactic => Tactic.name === 'AttackTactic');
    const retreatIndex = ordered.findIndex(Tactic => Tactic.name === 'RetreatTactic');
    assert.ok(attackIndex >= 0 && retreatIndex >= 0,
      'Expected pinned AttackTactic and RetreatTactic implementations');
    assert.ok(retreatIndex < attackIndex,
      'Pinned native tactic ordering changed; inspect before changing priority');
    const [attack] = ordered.splice(attackIndex, 1);
    ordered.splice(retreatIndex, 0, attack);
  }

  if (mode === 'vip_first' || mode === 'vip_attack_before_retreat') {
    assert.equal(typeof vipTactic, 'function', 'VIP modes require the research tactic constructor');
    ordered.unshift(vipTactic);
  }
  if(mode==='double_dragon_first'){
    assert.equal(typeof doubleDragonTactic,'function','Double Dragon mode requires an explicit research tactic');
    ordered.unshift(doubleDragonTactic);
  }
  return ordered;
}

module.exports = {MODES, makeTacticOrder};
