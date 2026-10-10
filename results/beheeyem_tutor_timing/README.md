# A one-copy tutor can rescue T2 or be held for T3: exact packet timing

## Question

The [physical tutor frontier](../beheeyem_physical_tutor/) assumed that the turn-two Beheeyem + Triple Acceleration Energy packet was already directly in hand. It then evaluated a physical search card saved for the next turn. That excludes a natural alternative: use the same one-copy tutor **on turn two to fetch the missing first-packet card** and give up its availability on turn three.

This investigation tests a specific, transparent policy:

- If both B and TAE are already in the T2 hand, attack directly and **save** the tutor for T3.
- If exactly one category is in hand, spend the tutor on T2 to search the other, provided the tutor is physically in hand, its search category applies, the missing card is unprized in the 45-card deck, and enough hand filler can be discarded.
- If neither category is in hand, one tutor cannot construct both. No first attack occurs under this policy.
- A tutor spent on T2 is gone. No additional tutor exists on T3.

This is a controlled physical-acquisition policy, not a solution to the full turn-sequencing optimization problem.

## Physical transitions and exact method

The initial conditioning is the same as the previous experiment: three Basic Pokémon already on board by T1, including two old-enough-to-evolve Elgyem and one anchor; six other T2 hand cards from 57 residual cards containing B Beheeyem, T Triple Acceleration Energy, one tutor and neutral filler; six uniform Prizes from the remaining 51, leaving 45 in deck. The tutor modes and their payment/search restrictions are unchanged: Computer Search (any type, two discards), Mysterious Treasure (Psychic Beheeyem, one discard), Ultra Ball (Beheeyem, two discards), and Guzma & Hala (Special Energy, two discards).

There are two **disjoint** physical event families.

**Direct first packet:** B and T are in hand. The first attack recycles Beheeyem, TAE and Elgyem into the 45-card deck, making a 48-card T3 deck. The tutor may be held or drawn during T3 and used if one packet category is missing. This is computed by the established physical-tutor exact engine.

**Tutor-rescued first packet:** exactly one packet category is in the T2 hand, and a physically held tutor finds the other in the unprized 45-card deck after paying its discard cost from neutral filler. The search removes one card from deck (45 to 44); the attack then returns the two packet cards and underlying Elgyem (44 to **47**). The T3 d-card blind draw is therefore sampled from **47** rather than 48. Because the one tutor was consumed, the second packet must already be in hand or entirely obtained by that draw.

For each T2 hand and six-Prize composition, the code evaluates legal first-packet search availability and then uses exact hypergeometric inclusion-exclusion to calculate the second-packet event. The final probabilities sum the disjoint families. These are exact rational outcomes.

The stage/TAE attack and evolutionary readiness, physical positioning, Energy attaching, all other draw/search actions, opponent reactions and real discardability remain externally guaranteed or ignored, as explained in the parent result. The opponent-facing Mysterious Noise lock is not simulated.

## Main results

Every number is a percentage of conditioned random configurations of the **57 residual cards**, before conditioning on the first packet.

| B / TAE | Tutor | T3 draws | First packet direct | First packet after T2 rescue | Both packets if tutor saved for T3 only | Both packets under rescue-if-needed policy |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 4 / 4 | Computer Search | 1 | 12.006938% | **16.893119%** | 0.617735% | **0.662553%** |
| 4 / 4 | Mysterious Treasure | 3 | 12.006938% | **14.450161%** | 1.299912% | **1.435276%** |
| 1 / 4 | Mysterious Treasure | 1 | 3.364328% | **6.111209%** | 0.053147% | **0.059878%** |
| 1 / 1 | Computer Search | 2 | 0.939850% | **2.477785%** | 0.007771% | **0.009194%** |

The column named first packet after T2 rescue includes both the direct and rescued first-packet families.

For B=T=4 with Computer Search and one T3 draw, rescuing the missing first-packet category adds **4.886181 percentage points** to first-attack access. Yet it adds only **0.044818 percentage points** to joint two-attack access, because the tutor is no longer there to solve missing T3 resources and the one natural draw rarely assembles two categories. Relative to the saved-tutor-only event, two-packet access increases by **7.26%**.

A similar asymmetry occurs at B=1/T=4 with Mysterious Treasure: first-packet access goes from 3.364328% to 6.111209%, while two-packet access goes from 0.053147% to 0.059878%. Improving the probability of the *first attack* is an insufficient proxy for maintaining the subsequent control loop.

At zero T3 draws, the T2-rescued family never produces a second packet because at least one card category is absent from its remaining hand. At d=47, every T2-rescued first packet produces the necessary second packet because its entire 47-card deck is drawn; this edge case is a mathematical invariant, not a realistic play scenario.

## Implications and boundaries

**Tutor opportunity cost is temporal.** On T2, a search may preserve immediate tempo. On T3, that same copy may be the only way to rebuild a mixed Stage 1/Special Energy packet. A deck optimizer must specify the horizon and prize-taking or locking objective before rewarding an early search.

**Exact physical accounting matters.** The T2 search produces a 47-card post-attack deck, while the saved tutor and direct first packet produce a 48-card deck. Using the same denominator in both branches would be wrong.

This result evaluates a fixed policy and does not yet formally compare every possible prefetch decision when a direct first packet already exists. A richer optimizer should include turn-specific Supporter/Item lock, remaining Prize requirements, discard protection and other tutor targets.

## Reproduction

- [Exact timing engine](../../tools/beheeyem_tutor_timing.py) composes the original 48-card physical tutor branch with the new 47-card T2-rescue branch.
- [Deterministic regression](reproduce.py) checks 16 B/TAE copy-count pairs, four tutor modes, T3 draw counts 0–5, exact rational reference values, symmetry of two-discard category-specific tutors, the one-discard dominance, and exhaustive d=47 rescue certainty.
- [Independent physical simulation](monte_carlo.py) models shuffled physical hand/Prize/deck partitions, removes the searched card on T2, discards the tutor and its payment, returns the attack packet, reshuffles, and samples T3. Four configurations each use 200,000 seeded random trials.
- [CI workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-tutor-timing.yml) reproduces both validations.

The most useful next extension is to compare this policy to T2 prefetch strategies when both initial packet categories are present, then add explicit contingent opponent Item/Supporter lock and protected-discard feasibility.
