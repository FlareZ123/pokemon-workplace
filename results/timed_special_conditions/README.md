# Special Conditions require temporal state

## Question

Is a typed Special Condition identity and payload sufficient to determine the
next Pokémon Checkup transition?

No. Paralysis requires age relative to the owner's turns.

Implementation: `tools/timed_special_conditions.py`  
Regression: `results/timed_special_conditions/reproduce.py`

## Rules evidence

Official Pokémon TCG basic rules distinguish the Checkup behavior:

- Poisoned places one damage counter during each Pokémon Checkup.
- Burned places two damage counters during Pokémon Checkup, then the owner flips
  a coin; on heads the Burn is removed.
- Asleep flips during every Pokémon Checkup; on heads it is removed, including
  the Checkup immediately after the attack that inflicted it.
- Paralyzed prevents attacking and retreating and recovers after its owner's
  next turn, during Pokémon Checkup.
- Confused is resolved when the Pokémon tries to attack, rather than as a
  Pokémon Checkup transition.

Official sources:
- https://asia.pokemon-card.com/sg/rules/search/
- https://asia.pokemon-card.com/sg/rules/search/?pageNo=10
- https://assets.pokemon.com/assets/cms2-en-uk/pdf/trading-card-game/rulebook/par_rulebook_en.pdf

## Finding 1: `Paralyzed` has hidden temporal state

Consider owner A's Active Pokémon after player B inflicts Paralyzed during turn
10.

At the immediate Checkup after B's turn, A's Pokémon must still be Paralyzed so
that the condition can constrain A's incoming turn.

After A then completes turn 11, the next Checkup removes that same Paralyzed
instance.

Both moments project to the same untimed label `{"Paralyzed"}`, yet their next
transitions differ. Condition identity alone therefore aliases mechanically
different states.

The kernel attaches `applied_turn_serial` to each condition instance. A
Paralyzed instance recovers only when:

- the completed turn belongs to that Pokémon's owner; and
- the completed turn serial is later than the serial on which the current
  Paralyzed instance was applied.

This also prevents a self-inflicted Paralysis created during an owner's current
turn from being incorrectly cleared at the Checkup immediately following that
same turn.

## Finding 2: status conditions have different temporal families

The regression exposes three families:

1. **Every-Checkup counter conditions**: Poisoned and Burned.
2. **Every-Checkup recovery test**: Asleep, and Burned after its counter
   placement.
3. **Owner-turn-aged recovery**: Paralyzed.
4. **Attack-attempt timing**: Confused.

A simulator that stores all five conditions as equivalent booleans cannot
implement these timing differences correctly.

## Deterministic kernel boundary

`resolve_basic_checkup()` takes coin outcomes as explicit inputs. This is
intentional.

The base rules determine what a heads or tails means, while cards such as
Slumbering Forest, Centiskorch, or Wela Volcano Park can change coin count or
recovery consequences. Randomness and coin-modifying effects therefore belong
in a separate outcome-generation layer.

The Checkup resolver consumes the resulting outcome and performs deterministic
state mutation.

## Validation

The regression checks:

- Paralysis inflicted during player B's turn survives the immediate Checkup;
- it clears after owner A completes the following turn;
- a Paralyzed instance created during A's own turn does not clear at the same
  turn's Checkup merely because A was the completed-turn player;
- Poisoned + Burned + Asleep coexist legally;
- the first Checkup immediately applies 1 Poison counter and 2 Burn counters;
- heads removes Burned and Asleep while Poisoned remains;
- Confused does not mutate during the Checkup block.

## Architectural consequence

Special Condition state now has three distinct information layers:

- identity and coexistence;
- condition-local payload, such as Severe Poison's counter base;
- temporal provenance, where required, such as Paralysis application age.

This is another instance of the repository's recurring principle that visible
card labels are weaker than executable state.

## Limits

The kernel does not generate coin flips and does not yet model cards that alter
the number of coins or override recovery on heads.

The `applied_turn_serial` abstraction assumes the game engine exposes a
monotonic turn serial. Extra-turn handling should increment that serial in the
same way as ordinary turns; composing this with `turn_sequence_kernel.py` is
the next useful validation.

The result also leaves actual damage-counter placement on board objects to the
Checkup execution layer and final KO disposal to the KO layer.
