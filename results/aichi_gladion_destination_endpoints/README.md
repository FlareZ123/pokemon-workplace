# Aichi Gladion destination sensitivity across ALS endpoints

## Question

How much does Gladion's exact recovery destination matter once the Aichi Vileplume line is evaluated beyond the Bunnelby core?

This result compares the real Gladion transition, Prize to hand, with a counterfactual Prize to deck transition. The counterfactual is a representation diagnostic. It is not a claim about Gladion's card text.

Implementation: `tools/aichi_gladion_destination_endpoints.py`

Regression: `results/aichi_gladion_destination_endpoints/reproduce.py`

Aggregate counts: `results/aichi_gladion_destination_endpoints/summary.json`

## Why destination matters

The first-turn core needs Technical Machine: Evolution and Jet Energy in hand before Bunnelby attacks.

The downstream evolution endpoints have a different requirement. Technical Machine: Evolution searches the deck for evolution cards. A Prized Pidgeotto, Pidgeot ex, Herdier, Stoutland, Gloom, or Vileplume therefore blocks the corresponding search payload until a copy is restored to the deck.

Real Gladion moves a chosen Prize card to hand. This can repair a hand requirement, but it does not restore that card as a deck-search payload.

The counterfactual transition moves the chosen Prize card to the deck instead. It can repair a missing evolution payload, but it cannot directly supply a hand-required Tool or Special Energy.

## Matched simulation

Four 20,000-trial blocks, seeds `20261007` through `20261010`, use the same accepted-opening, Prize, draw, Active, and Stellar Wish state generation as the existing Aichi planner.

| Endpoint | Baseline | Real Prize→hand | Gain | Counterfactual Prize→deck | Gain |
| --- | ---: | ---: | ---: | ---: | ---: |
| Bunnelby core | 70.6675% | 70.96875% | +0.30125 pp | 70.6675% | +0.00000 pp |
| Pidgeot Stage 2 | 60.2500% | 60.4925% | +0.24250 pp | 60.2675% | +0.01750 pp |
| Stoutland Stage 2 | 49.2625% | 49.4675% | +0.20500 pp | 49.28125% | +0.01875 pp |
| Pidgeot + Stoutland | 42.5075% | 42.6975% | +0.19000 pp | 42.5375% | +0.03000 pp |
| Vileplume Item lock | 36.8725% | 37.0250% | +0.15250 pp | 36.87375% | +0.00125 pp |
| Item lock + Pidgeot | 23.9925% | 24.0950% | +0.10250 pp | 23.9950% | +0.00250 pp |
| Item lock + Stoutland | 19.7925% | 19.8850% | +0.09250 pp | 19.7950% | +0.00250 pp |

The two destinations can repair different states. Allowing the simulator to choose either destination raises the dual Stage 2 endpoint to 42.7175%, a +0.2100 pp gain over baseline.

## Interpretation

A single boolean such as `critical_card_recovered = true` is insufficient for this line.

For the same physical Prize card, strategic usefulness depends on the next consumer:

- a card needed to be played from hand benefits from Prize to hand;
- an evolution payload needed by Technical Machine: Evolution benefits from Prize to deck;
- a card moved to the wrong one of those zones can remain unusable for the immediate action.

The core provides the cleanest witness. Counterfactual Prize to deck recovery adds exactly zero successes in these 80,000 states because the Supporter play is already spent and the core's missing Tool or Special Energy must be in hand.

The small Prize to deck gains on Stage 2 endpoints are the complementary witness. They come from restoring search payloads that real Gladion would leave in hand.

## Scope

This is a controlled destination counterfactual, not a recommendation to replace Gladion with another card.

The counterfactual keeps the same Supporter timing and lets only the recovery destination change. It does not model a real Prize-to-deck Supporter with its own text or costs.

The sample is smaller than the core-only information result because the endpoint evaluator is more expensive. The qualitative destination split is structural and is also supported by the exact card-zone requirements in the line.

## Modeling consequence

Prize recovery should be represented as a typed zone transition and composed with the requirements of the next action.

For this ALS, `Prize -> hand` and `Prize -> deck` are strategically different edges even when both are described informally as recovering the same card.
