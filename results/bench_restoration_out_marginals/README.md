# Bench-restoration outs have state-conditioned marginal value

## Question

Should every card that can answer a Bench restriction count as a live out whenever it is accessible?

No. A Bench-triggered Stadium remover is an out only when enough Bench slack already exists for the remover to enter play. Direct restorative Stadiums stay live at zero slack.

This result quantifies that state dependence with exact without-replacement probabilities.

Implementation: `tools/bench_restoration_out_marginals.py`  
Regression: `results/bench_restoration_out_marginals/reproduce.py`

## Example state

The illustrative deck state has:

- 40 cards remaining;
- 5 random cards seen;
- 2 direct restorative Stadium outs;
- 2 Bench-triggered Stadium-remover outs;
- 4 required-entrant outs.

At **zero Bench slack**, the remover cards are accessible but mechanically unusable for the unlock objective. Only the two direct restorers count as live unlockers.

At **one Bench slack**, the two remover copies become live because they can legally enter and remove the restriction.

## Exact unlock access

| State | Live direct outs | Live remover outs | Total live unlockers | Unlock access |
| --- | ---: | ---: | ---: | ---: |
| zero slack | 2 | 0 | 2 | **23.717949%** |
| one slack | 2 | 2 | 4 | **42.707080%** |

The difference is 18.989131 percentage points, caused only by the state making two already-present card identities executable.

The same distinction persists when success requires both an unlocker and one of four required entrants in the five-card sample:

| State | Joint unlock + entrant access |
| --- | ---: |
| zero slack | **8.712660%** |
| one slack | **16.018042%** |

## Single-copy marginal reversal

Starting from the 2-direct / 2-remover example:

| Added copy | Zero-slack unlock marginal | One-slack unlock marginal |
| --- | ---: | ---: |
| +1 direct restorer | **+10.037112 pp** | **+7.957350 pp** |
| +1 Bench-triggered remover | **+0.000000 pp** | **+7.957350 pp** |

At zero slack, an additional remover copy increases nominal card access but adds no executable unlock route. At one slack, the same copy has the same simple draw-access marginal as an additional direct restorer under the symmetric assumptions of this toy model.

This is a concrete example of a card's marginal value changing discontinuously when one unit of a board resource becomes available.

## Mathematical basis

For `N` remaining cards, `L` live unlockers, and `k` random cards seen:

`P(unlock) = 1 - C(N-L,k) / C(N,k)`

For disjoint live-unlocker and required-entrant classes of sizes `L` and `E`:

`P(unlock and entrant) = 1 - P(no unlocker) - P(no entrant) + P(neither)`

The calculation is exact for the stated random-sample model.

## Strategic interpretation

An out count should be conditioned on the current execution state.

A card can be:

- present in the deck;
- drawable or searchable;
- textually capable of solving a problem;
- mechanically dead because a prerequisite resource is missing.

Bench-triggered Stadium removers at zero slack occupy that last category.

This sharpens the repository's broader connector-realism synthesis. Nominal redundancy does not imply executable redundancy. Two classes of cards that solve the same abstract problem can have different marginal values because their entry costs consume different resources.

## Evidence class

The zero-slack legality distinction comes from the deterministic `bench_capacity_restoration_bootstrap` result and card text. The access values are exact combinatorial derivations under the stated toy composition.

## Limitations

The five seen cards are treated as an unordered random sample. Search effects, Prize information, Supporter costs, Stadium access connectors, and card-specific draw sequencing are excluded.

The direct restorers and remover copies are treated as equally accessible once mechanically live. Real cards differ in searchability, action costs, lock vulnerability, and secondary value.

## Next useful work

The next useful extension is to add Prize conditioning. A Prized direct restorer should be much more damaging at zero slack than a Prized remover, while the distinction narrows once one slack makes both classes live. This would connect Bench-state-conditioned outs to the repository's K0/K1 and belief-state research.
