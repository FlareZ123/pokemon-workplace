# Source-aware environment Retreat modifiers

## Question

Can three important non-attached-card sources of Retreat Cost modifiers be
derived from two exact Pokémon boards and an explicitly identified active
Stadium, rather than being inserted as unexplained numeric values?

## Card-text scope

The bundled paper Expanded card pool supplies three exact, legal-scope prints:

- Galar Mine `swsh2-160`: both Active Pokémon have Retreat Cost 2 higher.
- Ariados `sv6-5`, **Big Net**: the opponent's Active Evolution Pokémon
  has Retreat Cost 1 higher while Ariados's Ability is active.
- Hisuian Sneasler `swsh10-93`, **Carry and Climb**: while on its
  controller's Bench, its controller's Active Pokémon has Retreat Cost 2 lower.

`tools/retreat_environment_modifiers.py` encodes these three predicates.
`tools/board_derived_retreat.py` now composes the resulting instances with
existing Special Energy, Tool, and external modifier sources before calling
the canonical Retreat payment and destination transaction.

This is a narrow exact-print compiler. It does not claim to enumerate every
Expanded Retreat modifier.

## Mechanical results

1. A qualifying opponent's Ariados can affect the retreating player's Active
   Evolution Pokémon from either Active or Bench. Two such Ariados contribute
   two independent +1 instances.
2. A qualifying own Hisuian Sneasler contributes -2 only while Benched.
   An opponent's Sneasler or an own Active Sneasler does not reduce the
   retreating Active's cost.
3. Ability suppression on a source removes its contribution. The source
   flags must already reflect relevant Ability-lock semantics.
4. An enabled Galar Mine contributes +2 independently of Ability suppression.
   The caller supplies the current exact Stadium print ID and whether its
   effect applies. Stadium-zone continuity and Stadium cancellation are not
   inferred here.
5. D-11 and D-12 effects add before floor-at-zero. D-13 effects such as
   Float Stone's no-Retreat-Cost condition take precedence.

An exact mixed witness has base Retreat Cost 2, two Benched Sneasler,
two opposing Ariados, and Galar Mine. Its deltas are
`[-2,-2,+1,+1,+2]`, giving an effective cost of 2.

## Transaction-level significance

The reproducible scenario begins with one Double Colorless Energy on an
Active Stage 1 Pokémon, one friendly Benched Hisuian Sneasler, an opposing
Ariados, and Galar Mine. Base cost 1 changes to 2; the DCE can pay and
a conserved Retreat commits. Removing Sneasler while keeping the same
attacking Pokémon, DCE, Stadium, and Ariados increases cost to 4 and makes
that requested payment illegal.

A separate Float Stone witness shows that a no-cost effect permits a
zero-Energy Retreat even with two Ariados and Galar Mine applying increases.

## Reproduce and boundaries

Run `python results/retreat_environment_modifiers/reproduce.py`.
The GitHub Actions workflow `validate-retreat-environment-modifiers.yml`
also runs the existing board-derived Retreat regression.

Remaining gaps include other sources such as attack-applied timed effects,
effectively active Stadium resolution, source suppression derived from a
full lock graph, and complete legality-aware source compilation. Tests prove
the supported local semantic cases, not a general-purpose game simulator.
