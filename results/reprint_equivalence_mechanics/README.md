# Operational-equivalence proof patterns for historical Trainers

## Purpose

This synthesis relates three bounded, tested historical-print comparisons.
A positive functional-reprint argument needs to preserve the effects of
a card on the game and its available decisions. It must also preserve
information and event semantics. Text resemblance by itself cannot do
this reliably.

## Three positive proof patterns

### 1. Equality of scalar expressions: Copycat

The original Copycat clause "draw a number ... equal to the number
of cards in your opponent's hand" and its handbook-certified
historical counterpart "count ... and draw that many" evaluate
the same integer. The same shuffle, draw, and Supporter clauses
remain. A guarded current-semantic normalizer now links two more
historical prints through the explicitly certified source print.

Evidence and regression:
[Copycat count equivalence](../copycat_count_equivalence/).

### 2. Redundant observation in a public zone: Energy Recycle System

The EX-era card says to search the public discard pile and *show*
one or three Basic Energy. The current card gives the same
two branches in "Choose 1" form. If the selected physical IDs,
destination zones, and mandatory counts coincide, explicitly
showing cards that are already public adds no private information.
Both branches obey the same shortage and playability rules.

The independent text interpretations produced the same labeled-card
action-frontier outcomes in 108 configurations, including conditional
post-shuffle deck order. This is evidence of modeled material
equivalence, while event-trigger questions and present-day tournament
policy remain open.

Evidence and regression:
[Energy Recycle System](../energy_recycle_equivalence/).

### 3. Intermediate insertion erased by a final shuffle: Pokémon Communication

Let `H` be the hand, `D` the deck, `p` a returned Pokémon
from `H`, and `q` a searched Pokémon from `D + {p}` (or
no selection, where the limited deck-search rule allows it).

After returning `p`, selecting `q`, and shuffling, the
final hand is `H - {p} + {q}`, the final deck multiset is
`D + {p} - {q}`, and its order is uniformly randomized.

Whether `p` was first placed *on top* of the deck or simply
*into* it does not alter these final consequences under the
assumption that no intervening effect observes insertion position.
Each version reveals the same returned and selected IDs. The
bounded regression compares 54 configurations and 1,854
conditional outcome rows with exact permutation probabilities.

Evidence and regression:
[Pokémon Communication](../pokemon_communication_equivalence/).

## Conditions required before generalization

These arguments are conditional on card-category identity, target
selection legality, public/private observation equivalence, available
resource counts, exact zone changes, timing, and absence of
intervening trigger effects. For instance:

- Pokédex's historical "up to 5" creates different private
  observation choices from the mandatory current top-five text,
  even when some final deck arrangements coincide.
- Rainbow Energy's damage versus damage-counter text has
  different event semantics despite superficially similar
  numerical effects.
- A reusable general-purpose normalizer must not silently treat
  differently timed or differently scoped effects as equivalent.

The first Copycat family already has a tournament-handbook
certification anchor; the other two presently remain model-level
evidence and retain `semantic_review` in the central resolver.
These proofs do not themselves establish tournament legality.

## Research direction

An evidence-aware reprint system can preserve separate labels
for source-text equality, rules-derived execution equivalence,
and official tournament-policy endorsement. Future work should
enumerate and search for counterexample states against each
equivalence class before admitting broader normalization rules.

Primary rules: the bundled Advanced Player's Rulebook, especially
I-B-01, I-H, II-A and II-D; and the official public-discard
definition in the [Pokémon TCG glossary](https://www.pokemon.com/us/play-pokemon/about/pokemon-tcg-glossary).
