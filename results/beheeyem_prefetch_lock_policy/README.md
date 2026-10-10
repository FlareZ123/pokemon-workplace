# Pre-searching before an expected tutor lock: K1 Beheeyem packet timing

## Research question

A physical Computer Search, Mysterious Treasure, Ultra Ball, or Guzma & Hala can be held to find the missing Beheeyem/Triple Acceleration Energy packet card on turn three. But an opponent may establish a lock before that turn, making the held Trainer unplayable. Is it worthwhile to **prefetch a future packet component on turn two**, even when the first packet is already in hand?

This study extends the [T2 rescue versus T3 deferral result](../beheeyem_tutor_timing/) with a transparent, exogenous probability that the tutor's **play class** will be prohibited on turn three. For Computer Search, Mysterious Treasure and Ultra Ball, that means an Item prohibition. For Guzma & Hala, it means a Supporter prohibition. An Item-only lock does not by itself prohibit Guzma & Hala.

The calculation makes a **K1 information assumption**: the player already knows the remaining deck composition and can infer the six Prize cards when considering the T2 prefetch. It assumes that this future lock probability is independent of the player's play and of the physical cards drawn. Draw budgets themselves remain available by assumption.

## Scope and exact decision

Use the same 60-card conditioned board as the preceding two results: three established Basics, six sampled residual T2 hand cards, six random Prizes, 45 original deck cards, B copies of Beheeyem, T copies of TAE and one physical tutor.

The earlier policy is retained if the T2 hand is missing one packet class: search for that missing class if possible so the first attack can happen, spending the tutor before T3. That T2 rescue branch yields a 47-card T3 deck after Mysterious Noise recycles its B+TAE+Elgyem stack.

If the T2 hand already contains B and TAE, the player may instead:

- **Defer:** keep the physical tutor, attack, shuffle B+TAE+Elgyem into a 48-card T3 deck, then draw d cards. The tutor can be played only if it remains physically available, has sufficient disposable filler payment and its class is not locked on T3.
- **Prefetch B or TAE:** if the tutor is already in hand, the hand has sufficient neutral filler to pay its cost, its target restriction permits the choice and a copy of the selected card is unprized in the original 45-card deck, search that card on T2. The tutor is spent, one searched card enters the hand and the attack recycles its own three-card stack. The T3 deck is now 47 cards. The hand must complete the second packet without any T3 tutor.

Let q be the exogenous probability that playing this tutor type will be denied on T3. For each physically realizable T2 hand and Prize state, calculate the exact hypergeometric packet probabilities of the candidate T2 prefetches and compare them against:

**Expected defer value = (1-q) × unlocked defer success + q × locked defer success.**

Choose a T2 prefetch only if its expectation is greater. This is a narrow finite-horizon **K1 policy optimization**, not an opponent-aware game solver. Card-text search targets, paid discards and physical one-use identity are respected within the simplified model.

## Results: four Beheeyem, four TAE, one Computer Search, one T3 draw

All entries are percentages for the **joint T2-and-T3 packet event**, conditioned on the three Basic board cards.

| Probability of T3 Item-play prohibition | Save tutor / T2 rescue baseline | K1-optimized prefetch policy | Improvement (percentage points) |
| ---: | ---: | ---: | ---: |
| 0% | 0.662553% | 0.662553% | 0 |
| 10% | 0.632415% | **0.646188%** | +0.013773 |
| 25% | 0.587207% | **0.621639%** | +0.034432 |
| 50% | 0.511861% | **0.586179%** | +0.074318 |
| 100% | 0.361169% | **0.562252%** | +0.201083 |

The first T2 packet rate is unchanged at 16.893119% because this decision concerns a hand that already has the first packet. Under certain T3 Item lock, optimal T2 prefetch improves the two-packet event from 0.361169% to 0.562252%. The recovery remains conditional and limited by requiring the tutor already in hand during T2.

In the **no-lock universal-search** case, deferred Computer Search is at least as good as the candidate prefetches throughout all 16 B/TAE copy-count combinations and T3 draw budgets 0–3 tested exhaustively by the regression; a separate scan extended that no-uplift observation to draws 0–5. Universal search can adapt its missing-card target to what was actually drawn, explaining the result in this model. This is a verified finite scan, not a general proof about every possible deck state.

## Category-specific search creates a small no-lock exception

With B=4, TAE=4 and two T3 draws, a single Ultra Ball searching only Pokémon yields:

- **0.911168%** joint packet access under the saved-tutor policy with no future lock.
- **0.913709%** under the K1 policy that can prefetch Beheeyem on T2.

The exact **+0.002541 percentage-point** improvement is small, but it is positive. In some states both first-packet cards are ready, yet Ultra Ball cannot search the missing Special Energy on T3. Searching an extra Beheeyem on T2 removes one card from the deck, changing the T3 blind-draw denominator from 48 to 47 while retaining the same unprized TAE outs. This slightly increases the chance of naturally drawing TAE. The result illustrates that a target-limited connector can have a different optimal action order from a universal connector.

A singleton can have the opposite effect. At B=1/TAE=4, Mysterious Treasure has no extra Beheeyem available in the T2 deck to prefetch once that unique Beheeyem is already in hand for the first attack. Under certain future Item lock and one T3 draw, the K1 prefetch policy cannot improve the **0.014651%** two-packet baseline. The shuffled-back singleton becomes searchable only after the T2 attack has finished, too late to prefetch it.

## Methodology, checks and limitations

- [Exact source](../../tools/beheeyem_prefetch_lock_policy.py) combines the 48-card deferred branch, 47-card T2 rescue branch, and 47-card T2 prefetch branch. For each K1 hand/Prize state, it compares B, T and defer policies using exact rational probabilities.
- [Exact regression](reproduce.py) checks 16 B/TAE copy-count combinations, four tutor modes, d=0–3 and lock probabilities 0 and 1, plus selected intermediate probabilities. It asserts source exchange symmetry, boundedness, exact numerical fractions, universal-search no-lock dominance, and the small category-specific no-lock exception.
- [Physical Monte Carlo](monte_carlo.py) independently samples six-card hands, six Prizes, T2 search removal and discard payment, post-attack reshuffling, Bernoulli future denial and T3 draws in 200,000 trials for each of four fixed-seed scenarios.
- [CI workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-prefetch-lock.yml) runs both validations.

Assumptions are strong: pre-existing mature Elgyem board, unlimited ordinary T3 action bandwidth for the stipulated blind draws, strategically disposable neutral filler, no opponent interaction other than the exogenously imposed tutor-play prohibition, and K1 knowledge before the T2 prefetch decision. The actual opponent may choose a lock in response to visible actions; obtaining the T2 tutor itself may consume a connector; and the attack/evolution/switching line is not simulated. None of these percentages is a deck win-rate forecast.

The most valuable next step is to replace the exogenous lock probability with a two-player response model: what opposing attacker or lock can realistically be established after each observed T2 action, and how does that change the optimal prefetch policy? This would turn the result into a usable example of active-move realism and connector contention under threatened action denial.
