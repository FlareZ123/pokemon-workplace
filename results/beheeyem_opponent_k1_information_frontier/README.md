# Exact maximum of free K1 own-Prize information value over all denial weights

## Research question

The [opponent K1 target study](../beheeyem_opponent_k1_target/) showed that knowing how many copies of its own four-copy target X are still Prized can improve the opponent's choice between leaving the hand intact, Judge and Ace Trainer. Under a tradeoff between finding X and denying a second Beheeyem packet, the incremental value is extremely sensitive to the chosen relative importance weight `lambda`.

Can we calculate **the maximum information advantage over all possible nonnegative lambda** exactly, rather than sampling a handful of intuitive weights?

## Finite rational proof method

For every physically possible opposing hand, remaining X Prize count, Supporter availability, public Prize totals and optionally observed Beheeyem first-tutor route, each action has utility

```text
P(own X after response) - lambda × P(Beheeyem second packet | first packet).
```

Both coefficients are exact Fractions determined by the physical models, so each action is an affine line in lambda. The optimal action is its upper envelope. Thus K0 and K1 policy utilities are continuous piecewise affine, and their difference is also piecewise affine.

All interior maxima of a nonconstant affine segment are impossible. Therefore the maximum of the K1-minus-K0 utility difference over lambda≥0 must occur at lambda=0, a rational pairwise action-intersection threshold of either information policy, or the tail value at infinity. The tail here reaches zero, since packet-denial dominates and X-Prize information cannot change which action minimizes the opponent packet risk.

The implementation enumerates all physically reachable hand presence states (Judge/Ace), held-X counts, remaining-Prized-X counts, direct/tutor first-packet routes, and legal response pairs. It collects all positive rational pairwise crossings, including transitions where one branch is ultimately never optimal, plus K0 policy crossings, and evaluates the exact information gap at each candidate. This supplies a global finite-model maximum without numerical grid-search error.

## Results: physical 60-card opponent deck, B4/TAE4/C1/d1 Beheeyem

Opponent's illustrative deck: Basic12, Ace Trainer4, Judge4, X4, filler36; Basic-valid seven-card opener, two subsequent draws, and exogenous opponent Prize awards. The Beheeyem side remains conditioned on three mature Basics, an initial attack packet, and r externally awarded Prize cards.

| Beheeyem Prizes r | Opponent Prizes remaining q | First tutor route observed? | Critical lambda at maximum | Maximum K1 utility gain |
| ---: | ---: | :---: | ---: | ---: |
| 0 | 6 | No | 3.367994 | 0.004703788 |
| 0 | 6 | Yes | 3.556751 | 0.003343260 |
| 1 | 6 | No | **81.677800** | **0.006253694** |
| 1 | 6 | Yes | 98.731704 | 0.002776303 |
| 2 | 6 | No | 22.160244 | 0.004880427 |
| 2 | 6 | Yes | 14.862875 | 0.002776786 |
| 2 | 5 | Yes | 14.894053 | 0.002931110 |
| 2 | 4 | Yes | 285.062009 | 0.002613037 |

The entries are absolute increases in the chosen dimensionless scalar utility (`P(X ready) - lambda × P(Beheeyem packet | first attack)`), rather than direct changes in win rate or percentage points of either individual outcome. Since lambda is unconstrained, a larger maximum at a different lambda does **not** mean the information has greater practical value in an actual deck.

The r=1/q=6 case is a particularly clear information-interaction example:

- With no observation of whether Beheeyem consumed its tutor, the **maximum** K1 improvement reaches 0.006253694 at lambda≈81.6778.
- With the tutor route already observed, the **maximum** K1 improvement drops to 0.002776303 at lambda≈98.7317.
- At the particular weight lambda=10, the relationship reverses: route-hidden K1 improvement is only **0.000000681**, whereas route-visible K1 improvement is **0.000472574**.

Thus public information about a prior **tutor play** and private information about own **Prized target copies** can be strategically **substitutes at some relative weights and complements at others**. The upper envelope and exact state weights explain why a single global information-value coefficient is generally unsafe.

## Verification

- [Exact global maximum enumerator](../../tools/beheeyem_opponent_k1_information_frontier.py) obtains all K0 and K1 action-crossing candidate lambdas as exact rational values, then compares K1 and K0 expected policy values at every candidate.
- [Regression](reproduce.py) checks eight Prize/visibility scenarios, verifies the purported global maximizer exactly and compares against a dense set of additional independent rational probe weights, including 0,1,2,5,10,20,50,100,1000,1e6, half the optimizer, twice it and nearby values.
- [GitHub Actions run 38134055377 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38134055377). Underlying physical X/Prize state kernels have independent shuffle-validation in [CI 38133827205](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133827205).

### Boundaries

This is a **free-information upper bound** within a deliberately hypothetical opponent deck. The K1 Prize knowledge presupposes an earlier lawful deck search but does not include its card, tempo or Supporter/Item cost. The player's X target is abstract and may or may not correspond to an attack-enabling card in any real deck. The Beheeyem outcome is resource packet availability conditional on a staged board and exogenous first attack/Prize rewards; no actual KO, opponent response timing, realistic gameplay or win rate is modeled.

Next: model explicit search-source cost and physical action feasibility to turn this calculated ceiling into an achievable value-of-information tradeoff. An exact search-source access model can ask how often observing the remaining deck actually occurs before the relevant opponent response.
