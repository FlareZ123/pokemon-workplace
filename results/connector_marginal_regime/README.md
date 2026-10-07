# Marginal bottleneck regime scan: direct outs versus discardability

## Question

Across a broad family of two-channel connector states, can one extra disposable card ever provide more realistic same-window joint access than one extra direct out to either required target channel?

Within the exact parameter grid tested here, no.

This is a bounded computational result rather than a general theorem.

Scanner: `tools/connector_marginal_regime.py`  
Reproducer: `results/connector_marginal_regime/reproduce.py`

## Scan definition

Every state uses:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 protected setup starters;
- exactly 1 universal connector;
- at least 1 protected non-starter filler slot reserved for substitution.

The scan varies:

- target-A outs from 1 through 8;
- target-B outs from 1 through 8;
- connector discard cost from 1 through 4;
- disposable non-starters from 0 through the largest value that still leaves a protected filler slot.

For every baseline state, the exact collapsed calculation measures three fixed-size substitutions:

- +1 target-A out;
- +1 target-B out;
- +1 disposable card.

The metric is capacity-aware, discard-gated joint access.

There are **9,728 baseline states** in the grid.

Target counts above four should be interpreted as heterogeneous outs to the same abstract access channel, not as copies of one card name.

## Result

**Disposable-dominant states: 0 / 9,728.**

In every scanned state:

`marginal(+1 disposable) <= marginal(+1 target A)`

and

`marginal(+1 disposable) <= marginal(+1 target B)`

The closest state is:

- discard cost 1;
- target A = 1 out;
- target B = 8 outs;
- disposable pool = 0.

Its realistic one-slot gains are:

| Substitution | Joint-access gain |
| --- | ---: |
| +1 target A | +5.751694 pp |
| +1 target B | +0.517253 pp |
| +1 disposable | +0.470609 pp |

The disposable marginal is **90.982298%** of the weaker direct-out marginal in that state.

## Interpretation

The direct-out result has two mechanisms.

First, an extra direct out raises the chance that its channel is naturally present in the opening hand.

Second, direct redundancy can remove dependence on the one-use connector, freeing that connector for the other channel.

An extra disposable card affects only the connector-payability mechanism in this model. It cannot satisfy a target itself and it cannot increase the connector's one-card output capacity.

That structural asymmetry explains why discardability improvements can be strategically valuable while still having smaller one-slot access marginals than direct redundancy in this scan.

## The closest regime is informative

The near-tie occurs in an intentionally extreme asymmetric state: one target channel already has eight outs, while the other has one.

Adding a ninth out to the saturated eight-out channel has strong diminishing returns. At the same time, moving from zero to one disposable card helps a cost-one connector cross its payment threshold in some opening hands.

Even there, the direct out remains slightly better in the modeled joint-access objective.

This helps bound the result. The scan includes a regime where the disposable intervention is given unusually favorable conditions relative to one of the direct-out choices.

## Relation to the one-slot baseline

The preceding `results/connector_slot_marginals/` example used A=3, B=2, D=20, cost=2.

There, the direct-out marginals were much larger than the disposable marginal:

- +1 A: +1.878295 pp;
- +1 B: +2.744034 pp;
- +1 disposable: +0.139238 pp.

The wider scan shows that this ordering is not peculiar to that one baseline within the tested parameter space.

## Method

The scan uses `two_channel_connector_access_collapsed()`.

That function is exact for this same-window model. It enumerates accepted opening-hand compositions and integrates Prize placement analytically with hypergeometric closed forms.

No Monte Carlo sampling is used.

## Limits of the claim

The zero-violation result applies only to the stated model and grid.

It does not establish that direct redundancy always dominates improved discardability in Pokémon TCG deck construction.

Important excluded mechanisms include:

- discard payloads that are actively beneficial;
- cards serving as both disposable resources and useful game pieces;
- more than one universal connector;
- multi-card connector outputs such as Secret Box;
- multi-turn option value;
- targeted search into the connector;
- attacks and Energy requirements;
- evolution constraints;
- Supporter contention beyond the modeled rescue line;
- lock effects;
- Bench constraints;
- matchup-specific utility.

A future model containing those mechanisms can produce different slot rankings.

## Practical modeling implication

An optimizer should avoid giving generic "consistency" credit to an extra disposable card merely because it raises connector AMR.

The local marginal should be evaluated against direct redundancy and shared-connector capacity in the same state distribution.

For the tested two-channel Computer Search-like abstraction, direct outs consistently provide the larger one-slot access gain.
