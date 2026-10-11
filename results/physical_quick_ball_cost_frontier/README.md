# Exact opportunity-cost frontier for a physically paid Quick Ball inspection

## Question

[The earlier physical Quick Ball model](../physical_quick_ball_search_option/) makes the source physically accessible and pays the printed Quick Ball plus one inert filler. But how much **additional future-use opportunity cost** can the player tolerate before the source becomes worse than keeping it for later?

Introduce a hypothetical nonnegative scalar cost τ charged every time the player chooses Quick Ball in addition to its already-modeled immediate physical discard. The cost is expressed in the same scalar utility units as the one-step target-access reward, which itself optionally subtracts λ times opponent next-turn target readiness. This cost is **not** inferred from actual card strength.

## General exact frontier

For each observed valid-opening hand h, calculate the postpayment K1-optimal continuation payoff and the no-search K0-optimal continuation payoff. Let their difference be δ(h). The source can only be used in hands with both a Quick Ball (Q) and a disposable filler (F). The payment is committed **before observing the deck**.

With normalized hand probability p(h), the exact optimal improvement over never playing Quick Ball is

G(τ) = sum_h p(h) max(0, δ(h) - τ).

Its exact selected-source probability is

S(τ) = sum_{h : δ(h) > τ} p(h).

Both are stepwise/linear functions of τ determined by the finitely many positive δ(h). On an interval without a threshold crossing, the slope of G is exactly -S. At equality a zero-increment source is declined.

These formulas model the choice to skip a bad search, incorporate printed two-card payment, and avoid attributing physical deck-thinning gains to an information-only bonus.

## Constructed deck and exact results

Reuse the physically dealt first-turn hypothetical 60-card deck B12/I4/N4/Research4/T4/filler28/QuickBall4. Condition on a Basic-valid seven-card opener, select one Basic Active, set six Prizes and draw one card going second. The opponent's Prize uncertainty is integrated out as in the preceding result.

Quick Ball plus inert filler is physically payable in **42.391235%** of these hands.

| Opponent denial weight λ | Distinct positive source-cost thresholds | Source-use probability at τ=0 | Gain at τ=0 |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 4.015584% | +0.049289939 pp |
| 0.1 | 3 | 10.781919% | +0.051818963 pp |
| 0.2 | 1 | 6.746318% | +0.082808768 pp |
| 2 | 6 | 12.483465% | +0.135648714 pp |

At **λ=0**, all 33 profitable hand-category compositions share precisely one positive willingness-to-pay threshold:

δ = **1353050739/110231206540 ≈ 0.012274661427** target-access probability units, or **1.227466 percentage points** conditional on such a hand.

Its combined probability mass is exactly **83155856/2070828243**, or 4.015584%. In every such hand the player holds Q and F, has at least one N, has no Iono or Research, and has no target in hand. With no target held, Iono/Research missing, and N available, spending Q and F before playing N increases useful-out density in the shuffled-back pool. Elsewhere either the search is unpayable or a no-search action already meets or exceeds the paid alternative at λ=0.

Consequently a uniform additional cost τ at or above 1.227466 percentage points of the conditional scalar target-access reward makes playing zero-output Quick Ball unprofitable for **every** modeled hand when λ=0, even though its original physical source payment was available in many hands.

At **λ=0.1**, there are exactly three positive thresholds, approximately 0.0000635092, 0.0005837043 and 0.0122746614 probability units. Their probability masses are 2.730733%, 4.035601% and 4.015584%, respectively. A hypothetical additional source cost of 0.001 probability units (0.1 percentage points) leaves only the highest-value 4.015584% of hands using Quick Ball. The optimal source decision is therefore sensitive to even small unmodeled opportunity costs.

At λ=2 there are six thresholds; the largest is **677809/50896300 ≈ 0.013317451367** probability units.

## Independent validation

- [Rational physical frontier](../../tools/physical_quick_ball_cost_frontier.py) computes hand-specific exact source benefits, merges identical threshold values, and evaluates G and S at arbitrary rational τ.
- [Labeled physical reproducer](reproduce.py) independently enumerates actual opening and Prize cards, the natural draw, Q+F payment and without-replacement Supporter redraw subsets across **18 small physical parameter settings**. It reconstructs the complete cost threshold/mass distribution, checks thresholds and intermediate values, and validates the λ0/0.1/2 exact 60-card witnesses.
- [Windows CI](../../.github/workflows/validate-agent2-physical-quick-ball-cost.yml) runs the reproduction with Python 3.13.

The costs τ are hypothetical future opportunity costs and are **not** estimates of the actual utility of Quick Ball or discarded cards. The result evaluates a one-step access outcome and deliberately gives Quick Ball zero searched Basic output. Real deck choices may derive more value from fetching a Basic or preserving the Item. The cost frontier exposes the fragility of a small numerical source advantage to missing future utility and is not a deck recommendation or game win-rate model.
