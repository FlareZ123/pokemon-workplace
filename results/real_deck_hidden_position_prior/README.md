# Exact hidden-position prior from a published Regidrago 60-card deck

## Research question

A group-copy feasibility filter removes impossible hidden card assignments, but does it recover probabilities produced by a finite shuffled 60-card deck? It generally does not. The remaining joint hypotheses must be weighted by sampling **without replacement**.

We use the exact playable [2026 Aichi tenth-place Regidrago list](../regidrago_aichi_top10_playable/), including the published count of three Quick Ball and one Prime Catcher. The other 56 cards are grouped as O. This groups exact card-name counts from the machine-readable 60-card manifest.

## Exact three-position experiment

We consider three prespecified distinct positions of an otherwise uniformly shuffled 60: one deck-top card, one tagged card that later enters hand (such as a previously Prized card), and one other hand card. The two hand cards are then subject to a uniform random public discard, with the observed discard being **Quick Ball** (group Q).

This deliberately excludes opening-Basic conditioning, six-Prize selection, how the Prize was taken, known previous searches, discard effects' legality, and the opponent's real action policy. It is an isolated finite-population geometry, not an estimated match win rate.

The independent oracle enumerates every ordered triple of distinct physical indices: 60 × 59 × 58 = **205,320** triples and both random discard choices. It matches the exact-rational grouped distribution at every possible (top, tag, other) class triple.

| Quantity | Actual finite-deck sampling | Independent-with-replacement, then copy-feasibility pruning |
| --- | ---: | ---: |
| P(top is Quick Ball | public discard Q) | **2/59 = 3.3898%** | **180/3599 = 5.0014%** |
| P(top is Prime Catcher | public discard Q) | **1/59 = 1.6949%** | **1/61 = 1.6393%** |

Both priors obey the physical group-copy ceilings, yet their conditional probability assignments disagree. The wrong Quick Ball posterior exaggerates that draw by approximately 1.61 percentage points.

## Implementation and proof

- `tools/exact_three_position_group_prior.py` builds a joint, exact Fraction-valued distribution using sequential depletion of physical copies.
- `exact_three_position_hand_belief` converts it to the established `LatentHandCompositionBelief` interface for observer-relative hidden-zone kernels.
- `results/real_deck_hidden_position_prior/reproduce.py` loads the actual published 60-card JSON manifest, runs full labeled enumeration, checks every group triple, verifies that the copy-budget filter leaves exact worlds unchanged, and compares the capacity-pruned independent baseline.

This is evidence that copy feasibility is a necessary prerequisite and correct finite-population *weights* are an additional requirement. Follow-on experiments should condition these beliefs on real K0/K1 card access, initial hand and Prize outcomes, and game-specific actions before they are used to optimize a competitive deck.
