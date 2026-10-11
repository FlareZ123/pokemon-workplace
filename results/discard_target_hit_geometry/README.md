# A discard can increase target hit probability even while lowering target density

## Question

The [paid Ultra Ball K1 research](../beheeyem_paid_k1_reward_prior/) found that much of the benefit of a prior deck search came from physically removing three non-target cards before a future Judge/Ace Trainer full-deck shuffle. An important adjacent question for deck-optimization and discardability heuristics is how this benefit changes if the player discards a desired target card as part of that cost.

Can target density alone decide whether a discard improves the probability of seeing a target within the next fixed number of draws?

## Exact without-replacement geometry

Let an N-card draw population contain K copies of a strategically required target, and draw n cards uniformly without replacement. The probability of finding at least one target is

```text
P_hit(N,K,n) = 1 - C(N-K,n)/C(N,n).
```

Suppose a prior action removes m physical cards from the eventual draw population, including t copies of the target. The change is

```text
Delta = P_hit(N-m,K-t,n) - P_hit(N,K,n).
```

All quantities are exact rational combinatorial probabilities. The allowed physical state obeys `0<=t<=K`, `0<=m-t<=N-K` and `n<=N-m`.

### A sufficient condition

If the remaining target *density* is at least the original density,

```text
(K-t)/(N-m) >= K/N,
```

then **P_hit after discarding is at least P_hit before** for any permitted n.

Proof: the no-hit probability is the product of miss hazards

```text
P_miss(N,K,n) = product_{i=0}^{n-1} (1 - K/(N-i)).
```

The density assumption is `Km >= Nt`. At every draw position i, compare the after-discard and before-discard target hazards:

```text
(K-t)/(N-m-i) >= K/(N-i)

iff   (K-t)(N-i) - K(N-m-i) = Km - Nt + ti >= 0.
```

Each after-discard miss factor is therefore no larger, and their product is no larger. This establishes the sufficient condition. Removing only non-target filler (`t=0`) is consequently always weakly helpful for the hit event, provided draw quota remains feasible.

### The surprising converse fails

**Target density can decrease while the target-hit probability still increases.** Consider an exact seven-card deck with two X targets, choosing three draws:

| Event | Original deck | Remove three cards, including one X |
| --- | ---: | ---: |
| N | 7 | 4 |
| K | 2 | 1 |
| Target density | 2/7 = 28.571429% | 1/4 = 25% |
| Chance next three draws contain X | 5/7 = **71.428571%** | 3/4 = **75%** |

Despite lowering X's density, reducing the deck to four cards means a three-card draw reaches a larger fraction of the remaining population. The target hit probability rises by 3.571429 percentage points.

In an independent exhaustive census of **21,980** legal configurations with N=2..22, m=1..5 and n=1..6 where possible, **528** configurations lowered target density but increased the chance of at least one target. Thus density nondecrease is a useful guarantee; density decrease is insufficient to conclude that the draw became worse.

## Practical-scale counterpoint: opponent X redraw from a 53-card population

For the previous Beheeyem opponent hypothetical target X, take N=53 before an early Ultra Ball discard, K=4 unprized target copies, and either Judge's four-card redraw or Ace Trainer's six-card redraw. Removing exactly three cards has different consequences depending on how many X copies are discarded.

| Draw quota | Baseline P(X) | Remove three filler, 0 X lost | Remove two filler and 1 X | Remove one filler and 2 X |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 27.644156% | **29.142423%** | 22.551020% | 15.510204% |
| 6 | 39.088193% | **41.054711%** | 32.428571% | 22.775510% |

At N=53, K=4 and n=6, discarding three genuine filler cards improves the next X hit by **1.966519 percentage points**. If one of the three discards is an X, the hit chance instead falls by **6.659621 percentage points** below baseline. That is an 8.626140-percentage-point difference between two literal three-card discard payments.

This quantifies the state-dependent DCI/UDP warning from the human-developed concepts: a discard action cannot be evaluated solely by its card count or by abstract draw depth. Which cards are consumed can dominate the favorable deck-thinning effect. The tiny-seven-card density counterexample does not imply that discarding a critical target is generally advantageous.

## Verification

- [Exact probability kernel](../../tools/discard_target_hit_probability.py) retains full rational combinatorics and checks the target-density sufficient condition.
- [Exhaustive independent census](reproduce.py) tests 21,980 physically legal (N,K,n,m,t) cases, asserts the sufficient condition and monotonic non-target thinning, and identifies the density-decreasing but hit-improving counterexample.
- [Independent random physical card arrays](monte_carlo.py) shuffle a 53-card or seven-card deck after removing the specified target/filler mix and check the next n draws. Three seeded 200,000-trial simulations agree with exact target-hit rates within six standard errors.
- [GitHub Actions run 38135051295 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38135051295).

This is an isolated one-category hit event. A real deck's success may require multiple distinct pieces (e.g., Beheeyem plus TAE), a sequence of legal actions, Supporter contention, bench positions and Prize information. The theorem is a reusable component of those larger models; it is not a claim that removing non-target cards is always strategically desirable when the removed cards have their own later functions.
