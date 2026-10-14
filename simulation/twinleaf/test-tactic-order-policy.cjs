'use strict';
const assert = require('node:assert/strict');
const {makeTacticOrder, MODES} = require('./tactic-order-policy.cjs');
class EvolveTactic {}
class UseAbilityTactic {}
class RetreatTactic {}
class AttackTactic {}
class ResearchVipFirstTactic {}
class DynamicDoubleDragonTactic {}
const native = [EvolveTactic, UseAbilityTactic, RetreatTactic, AttackTactic];
assert.deepEqual(MODES, ['native', 'attack_before_retreat', 'vip_first', 'vip_attack_before_retreat', 'double_dragon_first','blind_topdeck','sampled_k0']);
const untouched = makeTacticOrder('native', native);
const alternate = makeTacticOrder('attack_before_retreat', native);
assert.deepEqual(untouched, native);
assert.deepEqual(makeTacticOrder('blind_topdeck',native),native,
  'Blind search changes only the chosen Trainer tactic, not constructor order');
assert.deepEqual(makeTacticOrder('sampled_k0',native),native,
  'Sampled hypothetical state changes only the policy observation, not tactic priority');
assert.notEqual(untouched, native, 'Native setting must not mutate upstream tactics');
assert.deepEqual(alternate, [EvolveTactic, UseAbilityTactic, AttackTactic, RetreatTactic]);
assert.deepEqual(native, [EvolveTactic, UseAbilityTactic, RetreatTactic, AttackTactic]);
assert.deepEqual(makeTacticOrder('vip_first',native,ResearchVipFirstTactic),
  [ResearchVipFirstTactic,EvolveTactic,UseAbilityTactic,RetreatTactic,AttackTactic]);
assert.deepEqual(makeTacticOrder('vip_attack_before_retreat',native,ResearchVipFirstTactic),
  [ResearchVipFirstTactic,EvolveTactic,UseAbilityTactic,AttackTactic,RetreatTactic]);
assert.throws(()=>makeTacticOrder('vip_first',native),/require the research tactic/);
assert.deepEqual(makeTacticOrder('attack_before_retreat', native), alternate);
assert.throws(() => makeTacticOrder('novel', native), /Unknown research tactic order/);
assert.throws(() => makeTacticOrder('attack_before_retreat', [EvolveTactic, AttackTactic]), /Expected pinned/);
assert.throws(() => makeTacticOrder('attack_before_retreat', [AttackTactic, RetreatTactic]), /ordering changed/);
console.log('[tactic-order] PASS: native, attack-priority, VIP-priority and combined modes are copy-only and pinned-guarded');
