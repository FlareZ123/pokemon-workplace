# The value of a Prize pickup versus an extra deck draw depends on known Prize composition

## Research question

For a Beheeyem lock deck that has already executed its first Mysterious Noise attack, how much is **one additional face-down Prize card entering hand** worth relative to **drawing one extra card from the post-attack deck**?

These are controlled counterfactual resource-supply comparisons, not necessarily actions the player can substitute in the same real game. Taking Prizes requires earning an appropriate Knock Out, whereas drawing from the deck requires access to an additional draw effect. The two cards come from physically different random populations.

The prior [Prize-award calculation](../beheeyem_prize_packet/) gives the full unconditional incidence of additional Prize awards. This study retains that exact model and decomposes it across states in which the player knows the six-Prize **composition** (K1), while individual face-down Prize positions remain unknown.

## Model and conditional value

Start with the same fixed three-Basic board and 57-card residual population: B Beheeyem, T Triple Acceleration Energy, one physical paid tutor and neutral filler. Six cards form the T2 hand, six are set as Prizes and 45 begin in the deck. The first attack is possible if B+TAE are directly held, or when a legal physical tutor searches exactly one missing category and discards its required number of neutral filler cards.

- A direct first attack returns Beheeyem, TAE and underlying Elgyem into the deck, yielding **48** T3 deck cards.
- A T2 tutor rescue removes a searched packet card first, yielding **47** T3 deck cards after the return.
- On turn three, both experiments draw d ordinary cards from the same shuffled deck.
- **Prize option:** one additional random physical card among the six original face-down Prizes is put into hand before those d deck draws.
- **Draw option:** no Prize is taken, and the player instead draws d+1 cards from the T3 deck.

The second packet event succeeds if at least one Beheeyem and one TAE are available in hand, either directly or by playing an available one-copy tutor with sufficient discard payment. The model optimistically treats all neutral filler, including the returned Elgyem if drawn, as disposable for this test. It retains the tutor's search-class restriction.

For each physically realizable T2 hand and six-Prize composition, the study calculates exact rational conditional probabilities P(Prize option succeeds) and P(draw option succeeds). It partitions K1 states according to which option has the higher probability, weighting each by the exact chance of that state occurring. It then sums the positive and negative advantage contributions separately.

## Headline finding: known-state majority versus aggregate expectation

Four Beheeyem, four TAE, one Computer Search, and d=1 ordinary T3 draw:

| Statistic | Result |
| --- | ---: |
| First packet can attack on T2 | 16.893119% |
| Two packets with one Prize pickup + one deck draw | **1.125764%** |
| Two packets with two deck draws and no Prize pickup | **1.214069%** |
| First-packet-capable mass in states where a Prize pickup is better | 9.451318 percentage points |
| Prize-favored fraction of first-packet-capable states, probability weighted | **55.947740%** |
| First-packet-capable mass in states where an extra deck draw is better | 7.169371 percentage points |
| Exact ties, as mass of all shuffled configurations | 0.272430 percentage points |

**A random Prize pickup is better in more than half of the physically weighted first-packet-capable K1 states, yet an extra deck draw has the higher ex ante average success rate.**

This happens because the *magnitude* of each state's advantage matters. The Prize-favored states contribute +0.221069 percentage points to the unconditional joint packet probability relative to an extra draw. Draw-favored states contribute -0.309374 percentage points. Their net is **-0.088304 percentage points**, which matches 1.125764% - 1.214069%.

The finite census finds the same aggregate ordering (one extra deck draw at least as effective as one random Prize pickup) in **all 384 tested copy-count/tutor/draw configurations**: B and T each 1–4, all four tutor modes, d=0–5. This is a verified finite grid, **not** a mathematical theorem for other deck structures or hand-selection policies.

## Strong, fully specified K1 witnesses

Both witnesses below have the same exact T2 hand composition of **one Beheeyem, one TAE, one Computer Search and three neutral filler cards**. After attacking, the hand retains Computer Search plus three filler, and the post-attack deck is reshuffled.

**Prize-rich witness**

- Six original Prizes: **3 Beheeyem and 3 TAE**.
- T3 deck: **1 Beheeyem, 1 TAE and 46 filler** (48 cards).
- If one random Prize is taken, it must be B or T. Computer Search can retrieve the other type from the deck. Packet success after the original d=1 draw is **100%**.
- If the player instead draws two cards from the T3 deck, success is only **31/376 = 8.244681%**, requiring a B or T among those two deck draws to complement Computer Search.
- In this state, the Prize option has a **91.755319 percentage-point** advantage.

**Prize-empty witness**

- Six original Prizes: **six neutral filler**.
- T3 deck: **4 Beheeyem, 4 TAE and 40 filler**.
- A Prize pickup yields neutral filler, so the original one deck draw plus tutor succeeds with probability **1/6 = 16.666667%**.
- Two deck draws give probability **29/94 = 30.851064%**, allowing one drawn resource plus Computer Search.
- The deck-draw option leads by **20/141 = 14.184397 percentage points**.

K1 information provides a principled explanation for these reversals. Without the deck inspection, the player cannot distinguish the Prize-rich and Prize-empty states by Prize location alone. Even in K1, knowing which *cards* are Prized does not normally identify their face-down positions; every Prize pickup is evaluated as an unbiased selection from the known six-card multiset.

## Copy-count sensitivity

| B / TAE and tutor | d | Prize option | Extra-draw option | Prize-favored fraction of first-attack-capable mass |
| --- | ---: | ---: | ---: | ---: |
| 4 / 4, Computer Search | 1 | 1.125764% | 1.214069% | 55.947740% |
| 4 / 4, Ultra Ball | 2 | 1.338937% | 1.435248% | 39.457941% |
| 1 / 4, Mysterious Treasure | 1 | 0.093157% | 0.121750% | 32.984721% |
| 1 / 1, Computer Search | 1 | 0.003560% | 0.009194% | 4.137931% |

When both packet categories are singletons, almost every first-attack-capable state is better served by an extra draw from the deck, which contains the two returned packet identities. Prize pickups can still recover the physical tutor when that card was originally Prized, accounting for the small positive fraction.

## Reproducibility and assumptions

- [Exact K1 comparison engine](../../tools/beheeyem_prize_vs_draw.py) fully enumerates all physical T2 hand and six-Prize compositions, computes both conditional resource paths using the existing exact packet probability engine, and identifies maximum-difference witnesses.
- [Deterministic regression](reproduce.py) cross-validates the integrated rates against the existing zero- and one-Prize exact results in 384 configurations, verifies the positive/negative decomposition, source-exchange symmetry and exact reference fractions.
- [Independent shuffled-card Monte Carlo](monte_carlo.py) samples four configurations with 200,000 trials each. It checks the first-attack event, each resource-source success rate, and the mass of K1 states where a Prize pickup is better.
- [GitHub Actions workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-prize-vs-draw.yml) runs the exact and physical validations.

The entire experiment is conditional on an already prepared, mature three-Basic board and favorable attack legality, available T3 draws, neutral filler discardability, and no additional opponent effects. It does not measure real Knock Out rates or the actual opportunity cost of earning a Prize versus adding an extra draw action. The hand/deck/prize geometry is isolated precisely to test **information-sensitive source value**.

## Follow-on research

Integrate a realistic KO target and hand-disruption model. A T2 Prize award is a particularly exposed source of future packet cards if the opponent can use a hand-shuffling or discarding Supporter before T3. That would test whether prize-rich K1 states remain favorable after a real opponent reply. A future optimizer should retain the entire K1 belief about Prize composition and card identities instead of collapsing all future accessible cards into one uniform pool.
