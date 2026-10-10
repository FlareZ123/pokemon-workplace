# Flexible one-use connectors versus genuinely multi-axis effects

## Question

A single card can have access to multiple resource channels. When computing a draw window's probability of satisfying simultaneous setup requirements, should the card count as satisfying every channel it can reach?

Only if its actual usable effect can deliver those channels **simultaneously**. A card that can be spent to acquire either one Pokémon or one Energy cannot satisfy both channel demands through the same single use.

This is related to the human prior-research warnings about **connector domination**, **Supporter contention** and **multi-axis cards**. In particular, Computer Search can search any one card but cannot independently fulfill several missing material channels with one activation. Genuine multi-axis effects may deliver more than one resource category in a single activation.

## Model

`tools/prize_resource_allocation_exposure.py` represents each distinct physical card-group type by a finite set of **alternative contribution profiles**, each a nonnegative integer vector of resource-channel outputs.

Example with two resource channels (Pokémon access, Energy access):

- `FLEX` has alternatives `(1,0)` or `(0,1)`: it can contribute to either one, at most one per copy.
- `P` has only `(1,0)`.
- `E` has only `(0,1)`.
- A genuinely multi-output `MULTI` could have `(1,1)`, delivering both channels together if the modeled effect warrants it.

Every drawn physical copy can select at most **one** profile, or remain unused. The engine checks whether any allocation of the exposed cards meets the required resource vector.

With a known deck top and ordered suffix prefix, it includes deterministic near-term cards. It then enumerates multivariate hypergeometric group-count outcomes in the exchangeable suffix, grouping types with identical role profiles. For each candidate draw outcome, it runs a bounded dynamic program over feasible resource contributions and weights the outcome by its exact without-replacement draw probability.

This models **direct material accessibility under simplified role options**. A real card-effect compiler must supply accurate profiles and the prerequisites for their use.

## Independent four-card witness

Take physical cards `FLEX, P, E, filler`. The deck order is uniformly random, and the player draws two cards. Success requires one Pokémon channel and one Energy channel.

| Interpretation of FLEX | Probability the two drawn cards can satisfy both channels |
| --- | ---: |
| FLEX selects one output: Pokémon **or** Energy | **1/2** |
| FLEX produces both outputs simultaneously | **2/3** |

The difference is the `FLEX + filler` hand. That hand includes a card *capable* of either role, but cannot serve both independent needs if FLEX is one-use.

A naive "some card can provide P, and some card can provide E" coverage test treats FLEX itself as satisfying both, wrongly awarding success on that hand.

The exact source-independent oracle enumerates all **24 physical card-order permutations**, proving the respective probabilities from pair combinations.

## Two flexible copies: the resource contention becomes extreme

Take a four-card deck with two FLEX copies and two fillers, and draw two.

- If each FLEX can select **one** channel, both copies must be drawn to cover Pokémon and Energy. Probability: **1/6**.
- If each FLEX genuinely outputs both channels, drawing at least one suffices. Probability: **5/6**.

This illustrates how badly graph-connectivity-only scoring can misjudge flexible connectors when it does not model one-use contention.

A known-top state provides a further check: if FLEX is certainly the only card drawn, a single-output FLEX cannot cover both channels, while a true dual-output effect can.

## Validation

`results/prize_resource_allocation_exposure/reproduce.py` tests:

- the 24-deck physical oracle;
- one versus two flexible cards;
- one-card and two-card windows;
- known deck-top identity;
- the ordinary unshuffled and uniformly shuffled cases;
- invalid card group names and malformed resource profiles.

The implementation reuses the prior conserved Prize/deck prefix belief, so it can be applied to states where important cards are Prized or known to occupy specific near-term deck positions.

## Strategic constraints and next work

The illustrative profiles are *abstract roles*, not claims that a particular printed Trainer has these exact effects. For example, applying a profile resembling Computer Search must account for its discard cost and its unique ACE SPEC role. A Guzma & Hala-like multi-output profile must account for its printed category restrictions, activation requirements, discards, and once-per-turn Supporter constraint.

The current model answers whether exposed cards could supply resource-role outputs **under the given profiles**, while omitting those turn-level prerequisites. It is not a complete proof of an executable attack or a tournament win-rate prediction.

The next significant integration is a **resource-conflict-aware action planner** that respects per-turn Supporter limits, discard costs, one-use search connectors, and the card text's actual simultaneous outputs.
