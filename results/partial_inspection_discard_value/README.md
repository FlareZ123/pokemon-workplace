# Partial deck inspection and discard-policy information value

## Question

A full deck search can establish K1, while effects such as Jirachi's Stellar Wish expose only part of the deck.

How much can a partial deck inspection improve an endpoint-critical discard choice without revealing exact Prize composition?

Implementation: `tools/partial_inspection_discard_value.py`  
Reproducer: `results/partial_inspection_discard_value/reproduce.py`

## Exact model

Start with `U` unknown own cards. Exactly `P` are hidden as Prize cards. There are `m` endpoint-critical discard candidates, each with one replacement copy among those unknown cards.

Then the player observes `q` cards from the non-Prize deck.

For each candidate replacement, the observation can establish one of two visible facts:

- it appeared in the inspected deck cards, so it is definitely live;
- it did not appear, so it remains uncertain between the unobserved deck and the Prize cards.

The policy may condition its choice of `d` critical discards on the observed candidate set. It may not condition on the hidden location of unobserved candidates.

The exact sample space chooses the Prize set and then the observed deck subset. Hidden worlds are grouped by the observation before policy optimization.

## First-turn 52-card benchmark

Use `U=52`, `P=6`, two singleton replacement candidates, and one required critical discard.

| Observed deck cards | Best policy success | Full K1 success | Residual K1 advantage |
| ---: | ---: | ---: | ---: |
| 0 | 88.461538% | 98.868778% | 10.407240 pp |
| 1 | 88.687783% | 98.868778% | 10.180995 pp |
| 5 | 89.592760% | 98.868778% | **9.276018 pp** |
| 10 | 90.723982% | 98.868778% | 8.144796 pp |
| 20 | 92.986425% | 98.868778% | 5.882353 pp |
| 40 | 97.511312% | 98.868778% | 1.357466 pp |
| 46 | 98.868778% | 98.868778% | 0.000000 pp |

A five-card inspection recovers about 1.131222 percentage points of success relative to no inspection, while most of the full-information advantage remains unresolved.

## Three-candidate examples

With three singleton candidates and one required discard, a five-card inspection improves success from 88.461538% to 90.633484%; full K1 reaches 99.909502%.

With three singleton candidates and two required discards, the same five-card inspection improves success from 78.054299% to 79.162896%; full K1 reaches 96.787330%.

The information value of a partial reveal depends strongly on how many candidates must jointly remain recoverable.

## Strategic interpretation

K0 and K1 are useful endpoints, while real gameplay contains intermediate information states.

A top-five look can prove that a replacement is in the deck, which can make that candidate immediately safer to discard. Failure to see a candidate also changes its posterior Prize risk because the remaining uncertainty is concentrated into a smaller unseen pool.

The second effect is important. Partial inspection can increase certainty in both directions without identifying exact Prize composition.

## Relation to Stellar Wish

Jirachi's Stellar Wish looks at the top five cards of the deck. That creates a five-card private observation before later decisions.

This result models the information geometry of such a top-five inspection. It does not claim to be a full Stellar Wish simulator because Stellar Wish can also move one Trainer card into the hand and then shuffles the other cards back into the deck.

For a discard policy, the reusable lesson is that a five-card inspection should update the actor's belief state even when it falls far short of K1.

## Modeling consequence

A binary `K0/K1` flag cannot represent this state faithfully.

A stronger simulator should retain observer-specific evidence such as:

- known cards seen in the deck;
- known cards removed from the deck;
- posterior candidate-location probabilities;
- whether the deck was later randomized;
- whether a full inspection subsequently collapsed the Prize uncertainty.

This aligns the discard-policy problem with the repository's broader observer-belief work.
