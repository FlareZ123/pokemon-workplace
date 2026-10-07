# Zone-exit target branching

## Question

How much search branching can the direct zone-exit target geometries create
before matchup policy or card-specific filters are considered?

Implementation: `tools/zone_exit_branching.py`  
Regression: `results/zone_exit_branching/reproduce.py`

## Full-board target-set upper bounds

Consider a stable board with one Active and five Benched Pokémon on each side.

Ignoring card-specific filters, the target-set counts are:

| Geometry | Target sets |
| --- | ---: |
| self | 1 |
| one of your Pokémon | 6 |
| one of your Benched Pokémon | 5 |
| opponent Active | 1 |
| one opponent Benched Pokémon | 5 |
| one opponent Pokémon | 6 |
| any number of your Pokémon | 64 |
| one opponent Bench plus self | 5 |
| all opponent Benched Pokémon | 1 |
| all opponent Benched except three selected survivors | 10 |
| both Active Pokémon | 1 |

The two AZ printings remain outside this table because the target compiler
preserves their literal unqualified `Put 1 Pokémon into your hand` wording
instead of silently assigning ownership.

## Filters turn these into upper bounds

The `own_one` geometry includes effects with additional restrictions.

Examples include:

- Acerola requiring damage counters;
- Penny requiring a Basic Pokémon;
- Cheren's Care requiring a damaged Colorless Pokémon;
- Corviknight excluding Corviknight.

The geometry count of six is therefore a structural maximum on a full board.
An executable policy must apply the card-specific filter before evaluating the
actual branching factor.

## Virizion-GX: 64 target subsets become 113 mechanical continuations

Virizion-GX `sm8-34` Breeze Away-GX can put any number of your Pokémon in play
and all attached cards into your hand.

With one Active and five Benched Pokémon, target selection alone contains:

`2^6 = 64`

subsets, including the empty subset allowed by attack text using
`any number`.

Target choice is only part of the mechanical branch.

If the Active is kept, every subset of the five Bench Pokémon produces one
continuation:

`2^5 = 32`

If the Active is returned while some Bench Pokémon survive, a replacement
Active must later be chosen. Summed over every removed-Bench subset, those
replacement choices contribute:

`5 * 2^4 = 80`

If all six Pokémon are returned, that is one terminal continuation.

So the full-board mechanical continuation count is:

`32 + 80 + 1 = 113`

The regression enumerates every subset and verifies this formula for Bench sizes
zero through five.

The sequence is:

`2, 4, 9, 21, 49, 113`

for zero through five initial Benched Pokémon.

## Spidops: one target set, 25 ordered replacement pairs

Spidops `sv2-18` Entangling Trap has one deterministic physical target set:
both Active Pokémon.

With five surviving Benched Pokémon on each side, the later visible replacement
choices can form:

`5 * 5 = 25`

ordered promotion pairs.

This branching is sequential information branching. The attacker commits first,
and the opponent can observe that choice before selecting from their five
candidates.

A simulator that counts only target sets would call Entangling Trap a
single-branch effect and miss the 25 later decision continuations.

## Shiftry survivor complement

Shiftry `sv5-5` chooses three opposing Benched Pokémon and shuffles the
opposing Benched Pokémon that were not chosen into the deck.

On a full five-Pokémon Bench, choosing the survivors creates:

`C(5, 3) = 10`

possible survivor sets.

This is a useful example of target semantics being naturally represented as a
complement of a protected set rather than as a direct list of removed objects.

## Search implication

Connector access and card availability are only one part of action-space size.

A single reachable effect can create:

- one deterministic transition;
- several identity-sensitive singleton targets;
- a combinatorial subset choice;
- a survivor-complement choice;
- later sequential replacement decisions.

Search algorithms should therefore separate:

1. card access;
2. target-set generation;
3. physical transition;
4. post-transition decision phases.

Collapsing those layers into one generic `play card` edge can hide large and
state-dependent branching factors.

## Scope

These are mechanical branching counts rather than strategic utility estimates.

Dominated choices, card-specific filters, matchup information, terminal-state
policy, hidden information, and opponent response can reduce or increase the
effective policy-search complexity.

The counts intentionally preserve physical identity: choosing different
Pokémon is a different branch even if the number of Pokémon removed is the same.

## Validation

Run:

`python results/zone_exit_branching/reproduce.py`
