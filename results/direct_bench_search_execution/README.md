# Direct-to-Bench search physical execution

## Question

Can a compiled deck-search effect that puts Basic Pokémon directly onto the Bench be executed against the repository's conserved physical board state without collapsing it into a deck-to-hand search?

Yes, for the literal compiler family in `direct_bench_search_profile_compiler`.

Implementation: `tools/direct_bench_search_execution.py`  
Regression: `results/direct_bench_search_execution/reproduce.py`

## Physical transition

The executor accepts one `StackBoardMaterialState`, the compiled search profile, a typed set of exact Pokémon target classes, and explicit physical placement requests.

For every selected copy it:

1. verifies the represented target count still matches the physical deck count;
2. verifies the target satisfies the compiled `Basic Pokémon` selector;
3. materializes one exchangeable deck copy with a stable instance ID;
4. moves that instance into `in_play` and binds it to a new Pokémon board object;
5. appends a one-card Basic Pokémon stack to the existing board;
6. marks the new Basic as ineligible to evolve immediately;
7. checks whole-ledger card-class conservation through `StackBoardMaterialState`.

The Active Pokémon is unchanged. Every selected target therefore consumes one actual Bench slot and one actual deck copy.

## Bench-capacity rule split

The Advanced Player's Rulebook gives this effect family source-sensitive full-Bench behavior.

The regression encodes that split:

- a direct-Bench Trainer such as Nest Ball is rejected when the Bench is full;
- a Pokémon attack with the same search geometry remains an attack, but its search body stops before searching when the Bench is full;
- when Battle VIP Pass can search for up to two Basic Pokémon but only one Bench slot remains, one exact placement is accepted and two placements are rejected.

This is a concrete example of why destination and action class both belong in connector state.

## Concrete regression

The physical target is Tapu Lele-GX `sm2-60`, loaded through the existing legal Pokémon board metadata index.

The test covers:

- Nest Ball `sv1-181` moving one of two deck copies into one new Bench object;
- Battle VIP Pass `swsh8-225` moving two copies when two slots are open;
- Battle VIP Pass moving one copy when only one slot remains;
- full-Bench Nest Ball rejection;
- full-Bench Pidgey `sv3pt5-16` Call for Family taking the no-search branch;
- rejection of a stale typed target count after physical deck depletion;
- rejection of an Evolution-Pokémon target under the compiled Basic-Pokémon selector.

The target copy's total remains conserved before and after every successful movement.

## Strategic significance

A hand-search result and a direct-Bench result can reach the same Pokémon identity while creating different downstream states.

Direct placement:

- spends Bench capacity immediately;
- bypasses a later hand-to-Bench choice;
- does not represent playing the Pokémon from hand;
- can be prevented by full-Bench Trainer/Ability rules;
- may have different source-specific behavior when the effect comes from an attack.

The executor therefore treats `deck -> Bench` as a physical state transition rather than an annotation on abstract access.

## Boundaries

This module resolves only the direct search/placement body.

It does not yet execute:

- the Trainer card's own hand-to-resolving-to-discard lifecycle;
- Trainer action legality unrelated to Bench capacity, including Battle VIP Pass's first-turn condition;
- Energy payment or attack declaration;
- the attack-ending turn boundary;
- the mandatory deck shuffle after a performed search;
- K1 Prize inference or public information leakage;
- hand-play Ability triggers, which are intentionally absent from a direct placement transition.

Those layers already exist elsewhere in the repository and should be composed rather than reimplemented.

## Next work

The most useful next composition is an atomic Nest Ball transaction that joins Item play legality, this conserved direct placement, shuffle/K1 state, and hand-trigger suppression. A second useful bridge is to expose direct-Bench placements to the existing typed Bench-residency kernel so capacity and downstream release policies share one board truth.
