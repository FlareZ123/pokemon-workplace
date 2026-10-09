# Unknown hand composition must stay correlated with the Prize-origin card

## Research question

Previous E-31 Prize-origin hand models assumed the other hand cards were known by class. In actual games, the opponent often knows the size of a hand while remaining uncertain about its composition. Can Bayesian updates from publicly discarded random cards retain that additional uncertainty?

Yes. A latent joint belief can represent (deck top, remaining Prize slots, tagged Prize-derived card class, counts of other hidden hand groups). Each hidden world has a conditional likelihood for a random public discard, and a known physical card instance still moves to discard in the canonical ledger.

Implementation: `tools/prize_unknown_hand_composition.py`  
Regression: `results/prize_unknown_hand_composition/reproduce.py`

## Exact two-card hand example

An E-31 face-down Prize containing Chansey is taken and Lucky Bonus declined. The opponent's prior after that decision is P(tagged Prize card C)=2/7 and P(deck top S)=13/35. The affected player's two-card hand now holds this tagged card and one other card whose class the opponent does not know.

Suppose the opponent believes:

| Tagged Prize class | P(other card C) | P(other card O) |
| --- | ---: | ---: |
| C | 1/4 | 3/4 |
| O | 3/4 | 1/4 |

The affected player knows their exact hand; the opponent's beliefs preserve the conditional correlation with the tagged Prize.

If one of the two hand cards is selected uniformly at random and publicly discarded as C, the correct posterior is:

- P(tagged Prize card C) = **2/5 = 40%**;
- P(deck top S) = **11/25 = 44%**;
- P(tagged physical Prize card survived) = **17/25 = 68%**.

An incorrect model that first averages the other-hand composition to P(other C)=17/28, then treats it as independent of the tagged card, gives P(tag C)=**18/35 = 51.43%**, over eleven percentage points above the correct value.

The independent exact Fraction oracle enumerates all combinations of hidden tag class, other-card class, and which of the two physical cards was discarded, weighting by the initially observed Lucky Bonus decline.

## Physical provenance and continued play

The regression uses the physical truth where the tagged card is Chansey and the other card is also Chansey. Both possible physical discard choices are tested:

1. Discard the other Chansey, retaining the tagged card in hand.
2. Discard the tagged Chansey itself.

The same publicly discarded group C yields the same opponent posterior, while the affected hand owner knows the exact origin. Card instances and total counts are conserved.

The returned posterior is compatible with the existing sequential-discard model. When the other Chansey is discarded first and the remaining tagged Chansey is discarded second, the opponent learns the tagged class was necessarily C and the tagged card has left the hand.

## Limits

The expansion function represents a conditional distribution of other-hand counts given the tagged card group. An unrestricted joint distribution could additionally condition on deck top and remaining Prize configuration, while card-level knowledge may constrain these distributions through finite card-copy counts. This model assumes an externally supplied plausible hand hypothesis and a uniformly random discard.

Mars (`sm5-128`, Expanded-legal in the bundled English database) is a concrete source of a random opponent-hand discard after successfully drawing two cards. Its Supporter and draw requirements are upstream. The numerical witness itself is a hypothetical game-state distribution and is not a claim about Mars deck frequencies.
