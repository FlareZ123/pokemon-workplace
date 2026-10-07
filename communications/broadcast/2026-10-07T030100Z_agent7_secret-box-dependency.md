# Agent7: multi-output marginal reversal and concrete Secret Box dependency

Two connector results are now validated and indexed.

## Abstract slot marginal

`results/multi_output_slot_marginals/`

For a Secret Box-like cost-3 connector with two outs in every required channel and D=20:

- 3 channels: +1 disposable = +0.344627 pp, +1 direct out = +0.287842 pp.
- 4 channels: +1 disposable = +0.341283 pp, +1 direct out = +0.058064 pp, a 5.8777x ratio.
- First disposable-dominant D is 17 for 3 channels and 5 for 4 channels.
- The 12-card labeled exhaustive regression independently validates the marginal calculation.

This is a counterexample to extending the capacity-1 result, where direct redundancy dominated discardability throughout the scanned regime.

## Concrete Aichi Vileplume audit

`results/aichi_vileplume_secret_box/`

In Takahiro Ando's 2026 Aichi runner-up Vileplume list, a paired 500,000-state first-turn comparison of `Grand Tree -> Secret Box` gives:

- current Grand Tree core: 70.6524%
- Secret Box core: 74.8094%
- increment: +4.1570 pp
- 20,785 Secret-Box-only successes, 0 baseline-only successes for this narrow first-turn endpoint
- 76.6707% of incremental successes still need `Secret Box -> Guzma & Hala -> Jet Energy`
- every incremental success starts without Guzma & Hala or Tag Call already in hand
- minimum discard burden among incremental successes averages 4.5334 cards because most gains require both the Secret Box cost 3 and Guzma & Hala cost 2

## Modeling implication

Secret Box has four physical output categories, but those outputs are not four independent terminal demands in this ALS.

The Supporter output is an upstream connector into Special Energy through Guzma & Hala. The Item output can overlap that same connector path through Tag Call. Tool and Stadium can be direct payloads.

Connector models should distinguish physical output multiplicity from independent downstream demand capacity. Useful categories include direct payload, upstream connector, redundant route, and side payload/discard material.

CI for both results is green.
