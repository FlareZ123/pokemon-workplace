# The same N-replacement deck can have opposite Iono value depending on card zones

## Question

The preceding [opposing Supporter comparison](../beheeyem_supporter_reset/) found that, averaged over physical hands and six-Prize configurations, N tends to reduce next-turn Beheeyem packet access more than Iono. Both Supporters draw based on remaining Prize cards, but N shuffles the hand **into** the deck whereas Iono shuffles it onto the **bottom**.

Does the population-average result describe every individual known-state configuration? It does not. An exact finite census identifies and quantifies **K1 states where N is more favorable to Beheeyem than Iono**, despite the opposite aggregate ranking.

Here K1 means the Beheeyem player has already searched the deck and can infer the multiset of six original face-down Prizes. The player also knows their own hand. An opponent choosing N or Iono normally does **not** know these hidden cards. State-specific comparisons serve as omniscient analytic witnesses, **not** strategies the opponent can select without additional information.

## Exact physical model

The setup matches the parent result: a mature two-Elgyem-plus-one-anchor board, six residual T2 hand cards from 57 unknown cards containing B Beheeyem, T Triple Acceleration Energy (TAE), one tutor and neutral filler, plus six uniformly distributed Prize cards.

The first Mysterious Noise attack requires a Beheeyem and TAE directly in hand, or a tutor to search one missing category with its actual target restriction and discard payment. The attack recycles the Beheeyem, attached TAE and underlying Elgyem into a randomized 48-card deck (47 if the T2 tutor searched first).

After the first attack is conditionally awarded r=0,1,2 random original face-down Prize cards, the opponent may play **N** or **Iono**. Either redraws 6-r cards, then the player obtains d additional blind T3 cards. N reshuffles the newly awarded Prize cards and the surviving hand throughout the entire deck. Iono places that hand on the bottom, preserving the distribution of the original 48-/47-card top deck for the short draw sequence.

For each complete T2 hand and six-Prize multiset, the solver calculates the exact chance of assembling the T3 B+TAE packet under each opposing Supporter, including a newly drawn and payable tutor. It averages over random Prize awards within that fixed K1 state, then partitions all first-packet-capable physical states into N-favored, Iono-favored and tied categories.

## Result: opposite rankings within the same deck composition

With four Beheeyem, four TAE, one Computer Search, d=1 T3 extra draw and r=1 Prize awarded on the first attack:

| Measure | Value |
| --- | ---: |
| First-packet-capable configuration incidence | 16.893119% |
| Mean next-packet access after opposing N | **2.647861%** |
| Mean next-packet access after opposing Iono | **2.820953%** |
| Fraction of first-packet-capable configurations where N gives more access | **26.640302%** |
| Fraction where Iono gives more access | **73.359698%** |
| Exact state ties | 0% |

Thus N is the lower-access opposing play on average, yet in more than one quarter of the possible first-packet-capable K1 mass it would actually give Beheeyem **more** access than Iono. The distribution of the old hand across zones matters after conditioning, and cannot be reconstructed from the final aggregate deck composition alone.

## Two particularly revealing witnesses

In both examples the six original Prizes are **all neutral filler**, exactly one original packet is used for the first attack, and the future Prize award is likewise filler. Their **fully shuffled N draw pools are identical in composition**: 4 Beheeyem, 4 TAE, 1 Computer Search and 43 filler cards, a 52-card pool.

<text>Witness A: N is favorable to Beheeyem</text>

- T2 hand before first attack: **B1, TAE4, Computer Search1, filler0**.
- After the first attack, hand: **TAE3, Computer Search1**; 48-card deck: **B4, TAE1, no Computer Search, filler43**.
- **Iono:** bottoms the three held TAE and Computer Search, then draws six cards from a top deck with only one TAE out. Next-packet access is **4.655832%**.
- **N:** shuffles those TAE and Computer Search into the full 52-card deck, restoring TAE/tutor density in the draw pool. Next-packet access is **19.111035%**.
- N improves Beheeyem's next-packet chance by **14.455203 percentage points** in this K1 configuration.

<text>Witness B: Iono is favorable to Beheeyem</text>

- T2 hand before first attack: **B1, TAE1, Computer Search0, filler4**.
- After the first attack, hand: **four filler**; 48-card deck: **B4, TAE4, Computer Search1, filler39**.
- **Iono:** bottoms four held filler, leaving a comparatively resource-rich top deck. Next-packet access is **22.535055%**.
- **N:** reshuffles that filler into the deck, diluting the packet-card and tutor density to precisely the same 52-card final pool as Witness A. Next-packet access is **19.111035%**.
- Iono improves Beheeyem's next-packet chance by **3.424020 percentage points** in this configuration.

The paired witnesses are structurally informative because the N outcomes are **identical** while the Iono outcomes differ sharply. The reason is an information-and-zone partition: Iono's draw distribution depends on **which** categories were in hand versus already in the deck, while N erases that distinction by fully reshuffling both zones.

## Finite census

The exact solver covers B=1–4, T=1–4, four tutor modes, d=0–5 and r=0–2, totaling **1,152 configurations**. For every configuration in this grid, N gives **lower aggregate** packet access than Iono, yet **both types of K1 state reversal are present**. The N-favored mass is especially small for two singleton packet categories and larger when multiple spare TAE/Pokémon copies can accumulate in the held hand.

Examples of N-favored fractions among first-attack-capable states at d=1/r=1:

| B / TAE | Tutor | N-favored state mass | Iono-favored state mass |
| --- | --- | ---: | ---: |
| 4 / 4 | Computer Search | **26.640302%** | 73.359698% |
| 1 / 4 | Mysterious Treasure | **15.359089%** | 84.640911% |
| 1 / 1 | Computer Search | **6.896552%** | 93.103448% |

All percentages are **probability-weighted** across physically possible T2 hand and six-Prize states conditioned on first packet availability. They do not treat rare K1 states as equally common.

## Validation

- [Exact K1 decomposition](../../tools/beheeyem_reset_state_value.py): enumerates all complete hand/Prize configurations and evaluates exact N/Iono conditional packet probabilities, both directions of advantage and maximum-difference witnesses.
- [Regression](reproduce.py): cross-validates each aggregate result against the independently authored [Supporter reset engine](../../tools/beheeyem_supporter_reset.py) across all 1,152 parameter settings, confirms exact rational moment identities and reproduces the opposing-witness details.
- [Independent shuffled-card sampling](monte_carlo.py): four 200,000-trial physical experiments separately shuffle an old hand into N's draw pool or bottom it under Iono. It checks both packet rates and the weighted incidence of N-favored K1 states.
- [CI workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-reset-state-value.yml) runs both checks.

## Interpretation and limits

These are exact conditional card-access results with a guaranteed mature board and first-attack legality, an externally awarded Prize count, an opposing hand-reset Supporter assumed playable, a stipulated draw budget, and every neutral filler treated as potentially disposable. They exclude opposing tactical choices, return-card disruption, attack costs, and actual win rates.

The opponent typically has **incomplete information** about the Beheeyem player's hand and face-down Prize composition. An adversarial model must therefore optimize against the opponent's belief state and available public observations rather than selecting the best Supporter separately in each hidden K1 state. The paired N/Iono witnesses demonstrate exactly why that information constraint changes the available policy.

A useful next step is to formalize this as a finite Bayesian decision problem: public observations, an opponent belief over hidden T2 hands, and the resulting expected value of N, Iono or Marnie. The present exact state enumeration supplies the necessary conditional payoff kernel.
