# Beheeyem's returned resources versus disposable search capacity

## Question

The [ideal recycling construction](../beheeyem_lock_recycling/) reuses Beheeyem \`sm11-91\` and Triple Acceleration Energy \`sm10-190\` across consecutive attacks. What does one legal **actual access packet** cost in Trainer resources and discard-capable cards?

## One concrete return-trip line

Assume a previously played Elgyem A, Beheeyem, and Triple Acceleration Energy are all back in the deck following last turn's Mysterious Noise. A second Elgyem B has been on the Bench since at least the preceding turn. A prepared lock anchor with Float Stone is Active, and the player has an unused Supporter and Energy attachment.

Starting with the following five cards in hand suffices:

- \`Nest Ball\` \`sv1-181\`;
- \`Evolution Incense\` \`swsh1-163\`;
- \`Guzma & Hala\` \`sm12-193\`;
- two independently disposable hand cards.

Sequencing:

1. Nest Ball searches for A and puts it directly onto the Bench. A must wait until a later turn to evolve.
2. Evolution Incense searches for Beheeyem. Retain it for the mature B.
3. Use Guzma & Hala as the turn's Supporter, discarding the two genuinely disposable hand cards to enable the optional Special Energy and Tool search. Select Triple Acceleration Energy as the Special Energy; the ordinary Stadium search can be declined if the rules allow fewer targets, and no additional Stadium is required by this witness.
4. Evolve B into Beheeyem, attach Triple Acceleration Energy to it, retreat the anchor with Float Stone, then attack with Mysterious Noise. The anchor is promoted again after Beheeyem shuffles away.

The card text for Guzma & Hala explicitly makes the two-card discard a prerequisite to searching a Special Energy. The otherwise attractive card access can be unavailable if no two acceptable discards remain. Protecting Beheeyem in hand is essential. More efficient or different access routes may exist; this is a concrete feasible witness.

## Exact synthetic hand-packet model

Consider an abstract uniformly random hand of seven or nine cards from a hypothetical 60-card deck with four each of Nest Ball, Evolution Incense and Guzma & Hala; F specifically discardable filler cards; and 48-F other cards treated as strategically protected. Require at least one each of the three connectors and at least two filler cards.

This is a controlled **hand-composition sensitivity experiment**. It is not a literal turn-three distribution: the actual board, Prize cards, previously consumed searches, and hand history change the reservoir substantially.

| Hand size | Disposable copies F | Complete packet probability | Payment succeeds given one of each connector already held |
| ---: | ---: | ---: | ---: |
| 7 | 8 | 0.492420% | 9.048379% |
| 7 | 16 | 1.660954% | 31.184021% |
| 7 | 24 | 2.932894% | 56.491228% |
| 7 | 32 | 3.939161% | 78.165110% |
| 9 | 8 | 2.110336% | 19.426023% |
| 9 | 16 | 5.708268% | 54.567236% |
| 9 | 24 | 8.190979% | 81.251144% |
| 9 | 32 | 9.276409% | 94.826811% |

The first probability is an exact multivariate hypergeometric event over the five disjoint categories. For the second, condition on exactly one of each required connector already being held, then sample the remaining \`h-3\` cards from 57, of which F are designated discardable. The conditional payment event counts at least two of those F cards.

The conditional percentages are deliberately distinct from the unconditional packet event and should not be multiplied with the full-packet percentages.

## Resource-conservation consequence

One execution permanently moves Nest Ball, Evolution Incense, and Guzma & Hala to the discard pile under ordinary Trainer rules, while Beheeyem, Elgyem and Triple Acceleration Energy cycle back into the deck. With four copies of each specific connector and no recovery, **at most four later-turn repetitions** can use this exact three-connector package. The two disposable hand cards are also spent each cycle.

This is a second resource bottleneck beyond the two-Elgyem evolution cadence. Renewable attacker and Energy cards do not themselves create an indefinitely renewable access engine. Recovering search Items and Supporters, using alternative connectors, or drawing the recycled pieces naturally changes the limit.

## Reproduce and interpret

\`reproduce.py\` exactly enumerates the hand compositions and verifies that their counts sum to \`C(60,h)\` for each scenario. The conditional payment calculation uses an independent two-class hypergeometric count. It asserts several expected results and increasing access as the declared discardable stock or hand size rises.

Run \`python results/beheeyem_recycle_access_packet/reproduce.py\`.

This deliberately simplified experiment provides concrete examples of the human-developed **DCI, AMR, connector domination, and Supporter contention** ideas. A full optimizer needs hand-state-dependent discard choices, real retrieval sequences, turn budgets, and eventual recursion through recovery effects before it can compare this packet to other Beheeyem builds.
