# Multi-copy zone-state representation

## Question

Can a state model treat `card name -> one zone` as a canonical representation of physical card location in a 60-card Pokémon TCG deck?

No. Ordinary legal decks contain repeated cards, and repeated copies can occupy different zones simultaneously. A one-value-per-name map therefore collapses valid game states.

Implementation: `tools/multicopy_zone_state.py`  
Regression: `results/multicopy_zone_state/reproduce.py`

## Concrete counterexample

Suppose a deck contains two copies of Quick Ball.

At some point in a game:

- one Quick Ball is in hand;
- one Quick Ball remains in the deck.

A Python mapping with two `"Quick Ball"` keys cannot preserve both facts. The later key replaces the earlier one.

The reproducer contrasts that failure with `ZoneCountState`, which records:

```text
Quick Ball, hand -> 1
Quick Ball, deck -> 1
```

After playing the hand copy, a single transition produces:

```text
Quick Ball, deck -> 1
Quick Ball, discard -> 1
```

The total number of Quick Ball copies remains exactly two.

## Combinatorial size of the missing state

If `n` gameplay-equivalent copies are exchangeable and can occupy `z` zones, the number of distinct zone-count vectors is the stars-and-bars quantity:

`C(n + z - 1, z - 1)`.

This is the state space before assigning persistent identity to individual copies.

Examples checked by the reproducer:

- four copies across deck, hand, Prize, and discard: `C(7,3) = 35` count states;
- ten copies across five zones: `C(14,4) = 1001` count states.

A single `card -> zone` value distinguishes only `z` alternatives and cannot encode mixed-zone occupancy.

## Representation hierarchy

This result suggests three identity layers should stay separate:

1. **Card-class identity.** Choose the semantic key appropriate to the question: exact print ID, a conservative gameplay variant, an authoritative functional-reprint class, or another explicitly defined equivalence class. Use `card_class_namespace.py` when a string token crosses subsystem boundaries so the selected relation remains explicit. Existing `card_identity.py` and the reprint-equivalence audit show why deck-building name and conservative fingerprint cannot be treated as universal identities.
2. **Exchangeable-copy multiplicity.** While copies of the same card class have no strategically relevant individual history, store counts by zone. This preserves all mixed-zone distributions without creating arbitrary instance labels.
3. **Materialized board-object identity.** When topology or history differentiates copies, assign object identity. Examples include a Tool attached to one specific Pokémon, Energy attached to different attackers, damage/evolution state, temporary attack effects, or a Pokémon moving between Active and Bench.

The third layer is where the unified state kernel still needs stronger per-Pokémon board objects.

## Why count state is preferable before materialization

Always labeling every physical copy would represent all states, but it introduces symmetric duplicates. If four interchangeable copies are split two in the deck and two in the discard pile, swapping the arbitrary labels of the two deck copies does not create a strategically different state.

Zone counts preserve the strategically relevant multiplicity while avoiding that permutation explosion.

Instance identity should therefore be introduced when an effect, board relation, hidden-information distinction, or persistent history makes two copies non-exchangeable.

## Relationship to the unified state kernel

`unified_state_kernel.py` currently uses a tuple derived from a mapping of string keys to one zone. Its targeted examples remain valid because every modeled key is unique in those regressions.

The representation should be understood as a labeled-card scaffold, rather than a complete canonical deck-zone model.

A stronger unified state can replace its current location map with a count-preserving zone ledger for exchangeable cards, then materialize board objects for cards whose topology matters.

## Evidence type and limits

The duplicate-key counterexample is a representation fact.

The distribution formula is a mathematical derivation for exchangeable copies across unrestricted abstract zones. Actual card types cannot legally occupy every zone in every state, so the formula is an upper-level representation count, not a claim that every counted Pokémon TCG state is mechanically reachable.

This result does not yet implement board-object materialization or migrate the existing unified kernel. It establishes the state contract that such a migration should preserve.
