# Prize conditioning changes the value of state-dependent Bench-restoration outs

## Question

If two card classes can both restore Bench capacity in some states, does Prizing one copy of either class have the same strategic effect?

No. Prize impact depends on whether that card class is mechanically live in the current board state.

This result connects the Bench-restoration out model to the repository's grouped Prize-belief kernel.

Implementation: `tools/bench_restore_prize_conditioning.py`  
Regression: `results/bench_restore_prize_conditioning/reproduce.py`

## Example prior

Before six Prize cards are set, the unknown 46-card pool contains:

- 2 direct restorative Stadiums;
- 2 Bench-triggered Stadium removers;
- 42 other cards.

After six random Prizes, 40 cards remain in deck. The model then asks for the probability of seeing at least one live unlocker in five random cards.

At zero Bench slack, only unprized direct restorers are live. At one slack, unprized copies of both classes are live.

## K0: uncertainty over live-out count

A grouped hypergeometric Prize prior gives:

| State | K0 expected five-card unlock access |
| --- | ---: |
| zero slack | **20.772947%** |
| one slack | **37.941600%** |

The zero-slack live-out distribution is:

- 0 live direct outs: 1.449275%;
- 1 live direct out: 23.188406%;
- 2 live direct outs: 75.362319%.

At one slack, all four relevant copies can become live. The probability all four are Prized is only 0.009192%, while 56.003922% of Prize states leave all four live.

The exact expectations independently match the repository's `PrizeBelief.from_hypergeometric` state masses.

## K1: realized Prize identity changes impact

When no relevant copies are Prized, zero-slack five-card unlock access is 23.717949%.

If exactly one direct restorer is known Prized:

- live unlockers = 1;
- access falls to **12.500000%**.

If instead exactly one remover is known Prized:

- live direct unlockers remain 2;
- access stays **23.717949%**.

The remover Prize has zero current unlock penalty because remover copies were already mechanically dead at zero slack.

At one slack, one direct restorer Prized and one remover Prized are symmetric in this toy model:

- either case leaves 3 live unlockers;
- five-card unlock access is **33.755061%**.

The Prize penalty therefore changes when the board gains a single Bench slot.

## Strategic interpretation

Prize risk should attach to **state-conditioned role value**, not simply card identity.

A Prized card can be:

- catastrophic because it removes the only live route;
- partially harmful because redundant live routes remain;
- currently irrelevant because the card's route is mechanically unavailable anyway;
- newly important after another state variable changes.

This result gives a small exact example of the last two categories. One unit of Bench slack turns remover copies from dead identities into live recovery outs, which simultaneously turns their Prize status from irrelevant into strategically meaningful.

## Evidence class

The board-state distinction is inherited from the deterministic `bench_capacity_restoration_bootstrap` result. Prize masses are exact hypergeometric calculations and are cross-validated against the repository's grouped `PrizeBelief` implementation.

## Limitations

The model evaluates only immediate random draw access after Prize placement. It does not include search effects, Gladion or other Prize recovery, Stadium search, K0-to-K1 inspection costs, or a decision between competing strategic policies.

The direct and remover classes are symmetric once live. Real cards differ in searchability, action cost, lock vulnerability, and secondary value.

## Relation to prior work

`bench_restoration_out_marginals` showed that remover-copy marginal value is zero at zero slack and positive at one slack. This result shows the same state change also alters Prize sensitivity.

## Next useful work

A natural extension is to compute the **value of K1 information** for a decision between two recovery policies. When the board has zero slack, exact knowledge that direct restorers are Prized should push the player toward a different plan more often than exact knowledge about remover copies; with one slack, the policy boundary should change.
