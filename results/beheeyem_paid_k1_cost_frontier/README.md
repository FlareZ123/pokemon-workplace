# Exact willingness-to-pay frontier for early Ultra Ball Prize information

## Research question

The [future-Prize-prior model](../beheeyem_paid_k1_reward_prior/) removes foresight from the opponent's early decision to play Ultra Ball before Beheeyem's Mysterious Noise Item lock. The opponent knows its early physically held source, its own target X count, Judge/Ace counts, and the cost of discarding the Item plus two neutral filler. Its later policy will condition on the subsequent Prize reward, one more draw, public first-packet tutor usage and K1 Prize-X knowledge if Ultra Ball was played.

The prior study sampled several scalar extra opportunity costs `tau`. This extension calculates the **complete exact decision frontier over all nonnegative tau**, using the state-weighted benefit of a paid early source before subtracting that additional cost.

## Finite rational upper-envelope theorem

For each physically payable prelock hand class `s`, write:

```text
b_s = E[optimal later payoff after paid Ultra Ball and K1 | s]
    - E[optimal later payoff without the early source | s]

w_s = P(the early Basic-valid hand belongs to class s).
```

Both are exact rational numbers under the declared physical transition models and any rational future Prize prior `(p0,p1,p2)`. The action can only be bought at additional cost `tau` **before the opponent knows the future Prize outcome or reply draw**, so playing it in class s is optimal exactly when `b_s > tau` (ties broken in favor of retaining the source).

Consequently, the total gain over never using early Ultra Ball and the probability of choosing the source are

```text
G(tau) = sum_{s: b_s > tau} w_s * (b_s - tau)
R(tau) = sum_{s: b_s > tau} w_s.
```

The unique positive `b_s` values are the only possible breakpoints. Between any two successive breakpoints, the chosen hand classes remain unchanged, **G is affine with slope -R**, and the source-usage rate is constant. As tau increases, both G and R weakly decrease.

This is a finite decision-theoretic result that does not require Monte Carlo interpolation or a guessed utility cutoff.

## Exact representative frontiers

Opponent deck: Basic12 / Ultra Ball4 / Ace Trainer4 / Judge4 / X4 / filler32. Seven opening cards conditioned on a Basic, six original Prizes, two prelock natural draws and one locked reply draw. The opponent may buy K1 with a physically held Ultra Ball paid by two disposable fillers. After learning the actual first Beheeyem Prize reward `r` and public first-packet tutor route, it chooses the best available Judge/Ace/no-reset response. Beheeyem side is B4/TAE4/Computer Search1/d1 with three staged Basics. Weight on Beheeyem denial `lambda=10`.

| Future `r=0,1,2` reward prior | Positive critical costs | Highest extra cost permitting any early search | Search chosen at tau=0 | Search chosen at tau=0.01 |
| --- | ---: | ---: | ---: | ---: |
| (1/3,1/3,1/3) | **3** | 0.011593924 | 26.220950% | 12.216193% |
| (1/2,1/2,0) | 2 | 0.009072191 | 26.220950% | **0%** |
| (0,1/2,1/2) | 3 | 0.017390886 | 26.220950% | 12.216193% |
| (1/10,4/5,1/10) | 3 | 0.016179244 | 26.220950% | 12.216193% |

For the uniform prior, the complete optimal early-source purchase probability is a **four-segment staircase**: the three positive source-benefit boundaries divide nonnegative tau into four constant-action regions, and the last region always declines the early purchase.

A subtle distinction: **46.477077%** of early Basic-valid hands can physically pay Ultra Ball, but at tau=0 the optimizer uses it in only **26.220950%**. Hence a majority of physically payable opportunities are not worth taking for this narrow scalar objective. At tau beyond approximately **0.011594**, none of the qualifying hands justifies the added opportunity cost. The cutoff is not a real-world valuation of Ultra Ball; it depends on the hypothetical target X, exogenous r prior and chosen scalar lambda.

The highest buy price changes with the reward prior because Ace Trainer's Prize restriction and Beheeyem's packet risk both depend on r. If reward 2 is impossible, the highest payable source benefit is lower than with r1/r2 having positive probability.

## Exact validation

- [Per-state benefit distribution](../../tools/beheeyem_paid_k1_reward_prior.py) is exposed alongside the previously verified early decision solver, with every class weighted by its actual Basic-conditioned opening probability.
- [Rational piecewise-affine frontier](../../tools/beheeyem_paid_k1_cost_frontier.py) forms the exact set of positive state benefits, partitions the nonnegative tau axis and derives acquisition probability, gross expected benefit and net improvement in each interval.
- [Independent exact-policy regression](reproduce.py) checks four rational future-Prize priors and **41 distinct boundary or interior probes** against the full sequential early-search decision engine. It verifies source-mass conservation, strict decrement of selected source mass at breakpoints, exact agreement at thresholds, and that the tail selects no early source.
- [CI 38135559832 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38135559832).

The prize prior is hypothetical and independent of opponent hand; lambda=10 is a sensitivity parameter and not a win-rate calibration. The opponent's X target is a four-copy abstract card. Prelock Ultra Ball searches for no Pokémon and uses two idealized disposable filler cards; real deck-building and sequencing may make such a choice irrational for additional reasons. Future source benefit also includes three-card physical thinning, which the [decomposition study](../beheeyem_paid_k1_reward_prior/) found much larger than pure K1 Prize knowledge in the uniform-prior example.

## Generalization

Any finite physical game state with a binary early action, exact future-information prior and fixed scalar extra action cost produces the same threshold formula. Rather than assigning a universal DCI or AMR to search, store each state's *net benefit before price* and its probability weight. The optimizer can then recover the entire resource-cost frontier, preserving the underlying state contingencies and public information timing.
