# Pokémon Checkup ordering has concrete state value

## Question

Does the Advanced Player's Rulebook rule that the next-turn player orders
Pokémon Checkup effects matter to actual board state, or can simultaneous
Checkup effects be treated as commuting arithmetic?

Implementation: `tools/checkup_order_value.py`  
Regression: `results/checkup_order_value/reproduce.py`

## Concrete card pair

The supplied card database contains these post-Black & White cards:

- Garganacl `sv2-123`, Ability **Blessed Salt**: during Pokémon Checkup,
  heal 20 damage from each of your Pokémon.
- Froslass `svp-117`, Ability **Freezing Shroud**: during Pokémon Checkup,
  put 1 damage counter on every Pokémon with an Ability, on both sides,
  except Froslass.

The regression reads those exact records from `resources/cards/en/` rather
than hard-coding only the card names.

## Counterexample

Consider one of Garganacl's player's other Pokémon that:

- has an Ability;
- is Poisoned;
- begins Pokémon Checkup with zero damage counters;
- is affected by both Blessed Salt and Freezing Shroud.

For this target, the three relevant operations are:

- ordinary Poisoned condition block: +1 damage counter;
- Freezing Shroud: +1 damage counter;
- Blessed Salt: heal 2 damage counters, floored at zero.

The condition sequence is an atomic block relative to Checkup Trainer/Ability
effects, so with two distinct effects the rulebook permits six abstract
schedules.

The regression finds three distinct final states:

| Final damage counters | Number of schedules |
| ---: | ---: |
| 0 | 2 |
| 1 | 2 |
| 2 | 2 |

Examples:

- `Poison -> Freezing Shroud -> Blessed Salt` ends at 0.
- `Poison -> Blessed Salt -> Freezing Shroud` ends at 1.
- `Blessed Salt -> Poison -> Freezing Shroud` ends at 2.

The operations therefore do not commute. Healing's floor at zero turns timing
authority into measurable state value.

## Turn-parity consequence

The Advanced Player's Rulebook assigns ordering authority for several Pokémon
Checkup effects to the player whose turn would be next.

The same board can therefore give different control over these six schedules at
the two alternating Checkups:

- after Player A's turn, Player B chooses the ordering;
- after Player B's turn, Player A chooses it.

If the players value damage on the target oppositely, the rational extrema in
this example differ by 2 damage counters, or 20 damage.

This is a temporal-control variable. Ownership of the effects does not by itself
identify who controls their order.

## Architectural consequence

A simulator should keep these layers separate:

1. which Checkup effects are eligible;
2. the atomic Special Condition block;
3. who owns ordering authority at this Checkup;
4. the chosen legal schedule;
5. sequential state mutation under that schedule;
6. the later Knock Out check.

Sorting Checkup effects into a fixed engine order can produce the wrong state.
Summing all damage and healing as one net delta also fails because healing is
bounded by the damage actually present when it resolves.

## Validation

The reproducer:

- verifies the exact Garganacl and Froslass card texts in the supplied database;
- enumerates all six legal schedules from the Special Condition kernel;
- evaluates each schedule from a full-HP Poisoned target;
- obtains exactly the reachable totals `{0, 1, 2}`;
- checks that each total has two schedule witnesses;
- composes the existing `effect_order_authority.py` rule and confirms the
  chooser flips with the next-turn player.

## Scope and limits

The scalar evaluator studies one target's damage counters. It does not attempt
to resolve every target of either Ability, status recovery coin flips, dynamic
effect eligibility, trigger creation, or Knock Outs.

The target state is a mechanically valid local witness. A deck-level strategic
claim about whether a player should construct this exact board would require
separate deck and matchup analysis.

The card database is used here to verify card text and print identity. Broader
legality assumptions remain subject to the repository's paper-Expanded
legality methodology.

## Next useful work

The next step is an executable Checkup kernel that applies one chosen schedule to
multi-Pokémon board state while keeping Knock Out checking deferred until the
rulebook's final Checkup step. That would make it possible to test healing,
damage, and trigger interactions without collapsing intermediate state.
