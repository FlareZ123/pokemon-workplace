# Typed condition payloads now execute through the Checkup board kernel

## Question

Can the separate Special Condition, modifier, scheduling, and deferred-KO
kernels be composed into one executable Checkup transition without losing the
distinctions they were created to preserve?

Implementation: `tools/typed_checkup_execution.py`  
Regression: `results/typed_checkup_execution/reproduce.py`

## Concrete witness

The regression reads three Expanded-era card records from the supplied database:

- Galarian Weezing `swsh2-113`, **Severe Poison**: Poison uses 4 counters
  instead of 1.
- Toxicroak `swsh1-124`, **More Poison**: add 2 more counters to the
  opponent's Poisoned Pokémon.
- Garganacl `sv2-123`, **Blessed Salt**: heal 20 during Pokémon Checkup.

The target is also Burned.

Its typed condition block therefore compiles to:

- Severe Poison base 4 + More Poison 2 = 6 counters;
- ordinary Burn = 2 counters.

The target begins at 20 damage on 100 HP.

## Execution trace

The chosen legal schedule is:

`Special Condition block -> Blessed Salt`.

After the condition block:

- 2 existing damage counters;
- +6 Poison counters;
- +2 Burn counters;
- 10 total counters;
- 0 remaining HP.

The Checkup executor keeps the Pokémon in play because KO selection is deferred
until the Checkup effect phase is complete.

Blessed Salt then heals 2 counters:

- 8 counters remain;
- 20 remaining HP;
- the final Knock Out batch is empty.

This composes three earlier findings in one transition:

1. irregular condition payload matters;
2. additive condition modifiers remain separate from the payload;
3. zero HP inside Checkup is intermediate state until the final KO boundary.

## Representation

`compile_condition_block()` accepts one timed condition state per Checkup board
object, resolves deterministic recovery using explicit coin outcomes, and emits
ordered `CounterMutation` objects.

Damage-counter mutations are ordered by the manual's Special Condition order,
then deterministically by object ID within each condition family.

`execute_static_typed_checkup()` inserts that compiled block into the existing
Checkup schedule and delegates board mutation plus deferred-KO selection to
`checkup_execution_kernel.py`.

## Static-effect boundary

This integration deliberately accepts only non-condition Checkup effects that
mutate damage counters.

That restriction makes one-time compilation sound: those effects cannot change
which conditions exist or which condition modifiers are active before the
condition block resolves.

Effects that can move Pokémon, remove an Ability source, suppress Abilities,
change a Stadium, or otherwise alter modifier eligibility require a dynamic
scheduler that recomputes eligibility at each step.

## Validation

The regression checks:

- exact source card text for all three card anchors;
- compiled Poison mutation = 6 counters;
- compiled Burn mutation = 2 counters;
- target reaches zero HP after the condition block;
- target remains present for Blessed Salt;
- healing returns it to 20 remaining HP;
- final KO batch is empty;
- Poison and Burn remain because the Burn coin is tails and neither condition is
  cleared by the represented healing effect.

## Next useful work

The remaining architectural gap is dynamic eligibility. A future executor should
resolve one schedule token at a time while recomputing continuous effects and
available Checkup effects after every state-changing token.
