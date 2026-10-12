'use strict';
const assert = require('node:assert/strict');
const {makeTacticOrder, MODES} = require('./tactic-order-policy.cjs');
class EvolveTactic {}
class UseAbilityTactic {}
class RetreatTactic {}
class AttackTactic {}
const native = [EvolveTactic, UseAbilityTactic, RetreatTactic, AttackTactic];
assert.deepEqual(MODES, ['native', 'attack_before_retreat']);
const untouched = makeTacticOrder('native', native);
const alternate = makeTacticOrder('attack_before_retreat', native);
assert.deepEqual(untouched, native);
assert.notEqual(untouched, native, 'Native setting must not mutate upstream tactics');
assert.deepEqual(alternate, [EvolveTactic, UseAbilityTactic, AttackTactic, RetreatTactic]);
assert.deepEqual(native, [EvolveTactic, UseAbilityTactic, RetreatTactic, AttackTactic]);
assert.deepEqual(makeTacticOrder('attack_before_retreat', native), alternate);
assert.throws(() => makeTacticOrder('novel', native), /Unknown research tactic order/);
assert.throws(() => makeTacticOrder('attack_before_retreat', [EvolveTactic, AttackTactic]), /Expected pinned/);
assert.throws(() => makeTacticOrder('attack_before_retreat', [AttackTactic, RetreatTactic]), /ordering changed/);
console.log('[tactic-order] PASS: copy-only, idempotent reorder, exact pinned tactic guards and invalid mode rejection');
