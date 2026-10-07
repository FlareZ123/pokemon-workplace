# Pokémon Checkup has a deferred Knock Out boundary

## Question

If a Pokémon reaches zero remaining HP partway through Pokémon Checkup, should a
simulator remove it immediately, or can later Checkup effects still modify it
before the Knock Out batch is formed?

Implementation: `tools/checkup_execution_kernel.py`  
Regression: `results/checkup_deferred_ko/reproduce.py`

## Rules evidence

The bundled Advanced Player's Rulebook gives Pokémon Checkup three phases:

1. Special Conditions;
2. Checkup Trainer/Ability effects, with the rulebook-defined ordering freedom;
3. Check for Knock Outs.

An official Pokémon Asia attack/Knock Out flow chart states the boundary even
more explicitly: for a Knock Out during Pokémon Checkup, both players first
resolve all effects, and only then are all Pokémon at zero or less remaining HP
Knocked Out.

Official flow-chart source:
https://asia.pokemon-card.com/sg/wp-content/uploads/sites/6/2022/08/attack_flow_chart_EN.pdf

This is the Checkup-specific interpretation of the general Knock Out timing
rules. A zero-HP intermediate state during Checkup is not itself a disposal
boundary.

## Counterexample to immediate deletion

The regression creates two 100-HP targets at 90 damage.

Freezing Shroud puts one damage counter on both targets. Immediately after that
effect, both targets have zero remaining HP.

Blessed Salt then heals 20 damage from one target but not the other.

Intermediate state:

- `a-target`: 100 damage, 0 remaining HP;
- `b-target`: 100 damage, 0 remaining HP.

After Blessed Salt:

- `a-target`: 80 damage, 20 remaining HP;
- `b-target`: 100 damage, 0 remaining HP.

At the final Checkup KO boundary, only `b-target` belongs to the Knock Out
batch.

An engine that deleted both targets immediately after Freezing Shroud would
produce the wrong final board and would prevent a legal later Checkup heal from
affecting `a-target`.

## Representation

`CheckupBoard` stores immutable per-Pokémon HP and damage-counter state.

`CounterMutation` represents a narrow deterministic Checkup mutation:

- put counters;
- heal counters.

`execute_checkup_schedule()` applies a caller-supplied legal schedule without
removing any Pokémon. After every token it records a snapshot, including which
Pokémon currently have zero remaining HP.

Only after the full schedule is exhausted does it populate
`knocked_out_ids`. Physical disposal, Prize taking, and promotion remain
delegated to the repository's existing Knock Out machinery.

## Finding

**Zero HP is observable intermediate state during Pokémon Checkup, while Knock
Out disposal is a later phase boundary.**

That distinction matters for state-machine architecture:

- effect eligibility and targets must use the still-present board during the
  Checkup effect phase;
- zero-HP membership can change before the final KO batch is formed;
- the KO subsystem should receive the final simultaneous batch rather than
  deleting objects after each Checkup mutation.

This mirrors the repository's broader simultaneous-KO work: batch boundaries
must be represented explicitly rather than inferred from local mutation order.

## Validation

The reproducer checks:

- both targets reach zero HP after the first Checkup effect;
- one of those targets is healed back above zero by a later effect;
- all board objects remain present during the whole Checkup schedule;
- the final KO batch contains only the target still at zero HP.

## Scope and limits

This kernel intentionally covers only deterministic damage-counter mutation and
the Checkup KO boundary. It does not perform actual KO disposal, Prize
resolution, status-recovery coin flips, trigger scheduling, or dynamic
eligibility.

Outside Pokémon Checkup, other effects can have different Knock Out timing. The
result should not be generalized into a rule that zero-HP Pokémon always remain
in play until some generic end phase.

## Next useful work

Compose this executor with:

- `special_condition_state.py` for typed condition payloads;
- `effect_order_authority.py` for the player choosing the schedule;
- `trigger_deferral_kernel.py` for effects generated while another effect is
  resolving;
- the existing simultaneous-KO disposal kernel for the final batch.

A particularly useful next regression is to distinguish Checkup-wide deferred
KO from ordinary during-turn immediate KO using the same physical board
objects.
