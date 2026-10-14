# Observation-consistent K0 physical search selection

## Research question

A player holding a search Item has not necessarily examined their deck or identified the six face-down Prize cards. Can a planner choose to spend a discard cost according to the actual hidden location of its target even though the player has not yet gained that information?

The source of the problem is the distinction between K0 (before first deck inspection) and K1 (after inspection). A pure physical-state optimizer sees exactly which cards are in the deck and Prizes and can leak that information into a pre-search decision. The correct first decision must be the same in states with identical observed hand, public zones, card population, and action channels.

## New model

tools/k0_physical_search_policy.py accepts multiple physical world states with exact Fraction weights. It verifies agreement on all zones other than the still-hidden deck and Prize zones, on full per-class totals, and on shared turn resources.

A first-search family fixes the played card and discard-choice menu for every indistinguishable world. After that common payment, the deck inspection is allowed to reveal which targets can be retrieved. The family can therefore contain several contingent legal search-target choices. It uses the canonical exact Trainer transaction to enforce physical availability and card-class conservation in each world.

The planner scores a declared acquisition goal with explicit, hypothetical success rewards and discard penalties. It compares:

- best observation-consistent first search, including the choice to do nothing;
- a deliberately clairvoyant upper bound where the first search decision can vary by hidden world.

The difference is a value-of-hidden-information diagnostic *within the supplied action family and utility assumptions*.

## Source-checked Radiant Eternatus illustration

Mysterious Treasure (sm6-113) physically discards one card to search a Psychic or Dragon Pokémon. Radiant Eternatus (swsh12pt5-105) is a Basic Dragon Pokémon.

The reproducer conservatively models only the Dragon/Radiant branch of Treasure. Every physical state is a conserved 60-card toy composition, with one opening Basic already Active, seven cards remaining in hand after one natural draw, six face-down Prizes and 46 deck cards. The visible hand includes Treasure and a Psychic Energy card selected as the only permitted discard witness. Radiant is unseen.

Conditional on that eight-card exposure, Radiant is uniformly among the 52 unseen physical cards. The exact probabilities are:

| Hidden state | Probability |
| --- | ---: |
| Radiant in the searchable 46-card deck | 46/52 = 88.461538% |
| Radiant among the six Prizes | 6/52 = 11.538462% |

For a hypothetical reward of 3 utility units when Radiant reaches hand and cost of 1 unit for discarding the Psychic Energy, a legal K0 policy plays Treasure in both worlds. It retrieves Radiant when present and may select zero restricted-search targets in the Prized world, having still paid the cost. Its expected utility is **43/26**, while the clairvoyant policy's is **23/13**, a gap of **3/26**.

When acquisition reward is only 21/20 units and discard costs 1 unit, the K0 policy preserves Treasure and Energy. The clairvoyant policy still searches only in the deck-resident world, creating a **23/520** utility gap. These utility units are intentionally hypothetical and make no assertion about card values or match win rates.

## Why this is relevant

The earlier exact search planner is mechanically correct for a known complete physical state, but its strongest scoring policy could make an illegal information-dependent pre-search choice if deployed directly as a game-playing agent. This belief wrapper enforces the player's observation boundary and permits target choice only after the information-generating action resolves.

This also clarifies the difference between the physical truth needed by a simulator and the information available to a real decision policy. The same approach can be extended to sequential first-turn lines, including Search -> K1 -> conditional search target -> pay later cost.

## Limits and validation

This is one first search, with caller-supplied trusted retrieval variants and explicit heuristic utility. The 60-card world uses abstract neutral card classes, rather than a reconstructed playable tournament list, and holds a specific visible hand fixed. It omits Prize recovery, future hand utility, Basic Bench occupancy, other Mysterious Treasure targets, opponent disruption, and full-game outcomes.

The reproducer asserts that both worlds retain the same observable state and each physical card total, tests the conditional target choices and exact rational expected utilities, and rejects different visible states or unnormalized beliefs.

Reproduce with results/k0_physical_search_policy/reproduce.py or manually dispatch .github/workflows/validate-k0-physical-search-policy.yml.
