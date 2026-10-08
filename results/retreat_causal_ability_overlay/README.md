# Causal Ability suppression changes Retreat execution

## Question

Can a single Retreat attempt consume the repository's existing verified
continuous Ability-lock resolution rather than asking an independent caller
to manually set every source's `abilities_enabled` flag?

## Composition

`tools/retreat_ability_lock_bridge.py` projects the verified
`AbilityLockCausalState` onto temporary immutable copies of the two
`BoardState` objects. Pokémon suppressed by the causal graph receive
`abilities_enabled=False` for the purpose of evaluating subsequent
Retreat source effects. Existing false flags remain false.

`tools/board_derived_retreat.py` accepts optional `ability_lock_state`
and applies the projected boards to:

- fixed Ability modifiers such as Big Net Ariados and Carry and Climb;
- opponent continuous Retreat denials such as Block and Poison Barrier;
- destination-affecting Scoop-Up Block sources.

The projected flags do not mutate the physical, conserved Energy board.
The transaction operates on the original prepared physical state after
its legal preconditions are established.

If a supplied causal state is **unresolved**, the result records
`unresolved_ability_lock=True` and cannot commit a Retreat transaction.
The reported numeric cost and source lists in that branch are provisional;
they were evaluated without a resolved suppression overlay.

When `ability_lock_state` is absent, the prior caller-resolved
`abilities_enabled` flags remain authoritative, preserving the earlier
adapter behavior.

## Four distinguishing witnesses

1. An opposing Active Snorlax `pgo-55` forbids the Float Stone holder's
   otherwise free Retreat. Our Benched Alolan Muk `sm1-58` suppresses
   that Basic Snorlax's Ability; the same free Retreat becomes legal.
   Removing Muk restores the prohibition.
2. An opposing Cradily `sm12-11` bars our Poisoned holder from
   Retreating, even with Float Stone. Friendly Tool-attached Garbodor
   `xy9-57` suppresses that source and allows the normal Retreat.
3. An opposing Active Galarian Weezing `swsh2-113` suppresses a
   friendly Benched Hisuian Sneasler's Retreat Cost reduction. With
   base Retreat Cost 2, a previously free Retreat becomes a legal
   two-Energy physical payment requiring one Double Colorless Energy.
4. Reciprocal Active Wobbuffet `xy4-36` and opposing Active
   Galarian Weezing produce an unresolved suppression cycle in the
   snapshot dependency graph. The transaction is withheld rather than
   arbitrarily selecting a winner.

## Boundaries

This bridge assumes the causal Ability-lock state has been initialized or
advanced on the current event-complete board history. It does not derive
causal precedence from sparse snapshots and does not resolve previously
unsupported mutual-suppression cycles.

Its source compilation remains the exact-print islands already supported
by the previous Retreat cost and prohibition modules. Additional global
effects, source condition predicates, and all possible Ability interactions
remain outside the claimed complete coverage.

Run `python results/retreat_causal_ability_overlay/reproduce.py`.
