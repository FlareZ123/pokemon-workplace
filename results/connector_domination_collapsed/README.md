# Collapsing Prize enumeration in the connector-domination model

## Question

Can the exact two-channel connector-domination calculation avoid explicit Prize-state enumeration without changing its result?

Yes.

The same-window model only needs to know whether each missing target class retains at least one searchable copy after the six Prize cards are set. Conditional on an opening-hand composition, those events have direct hypergeometric closed forms.

The collapsed implementation is `two_channel_connector_access_collapsed()` in `tools/connector_domination.py`.

Validation and a lightweight timing check are in `results/connector_domination_collapsed/reproduce.py`.

## Closed-form Prize integration

After fixing an accepted opening hand, let:

- `R` be the number of cards remaining before Prize placement;
- `P` be the number of Prize cards;
- `k` be the remaining copies of a missing target class.

The probability that **every** copy of that target is Prized is:

`C(R-k, P-k) / C(R, P)`

when `k <= P`, and zero otherwise.

So the probability that at least one copy remains searchable is one minus that value.

When both target classes are missing, let their remaining copy counts be `a` and `b`. The probability that both retain at least one searchable copy follows inclusion-exclusion:

`1 - P(all A Prized) - P(all B Prized) + P(all A and B Prized)`

That is all the Prize information required by this same-window access model.

## Exact equivalence

The reproducer compares the original explicit Prize-composition enumerator against the collapsed calculation across 20 parameter combinations:

- discard costs 0 through 3;
- target-count pairs from singleton/singleton through 4/3;
- disposable pools from 5 through 25.

Every field of `ConnectorDominationResult` is checked.

In the local development calculation, the largest absolute difference was about (1.2 × 10^{-13}), consistent with floating-point summation order.

## Computational value

For the representative 60-card A=3, B=2, disposable=20, cost=2 state, the development benchmark observed roughly a 239× median speed ratio in favor of the collapsed calculation.

The reproducer prints its own local timing rather than asserting a fixed speedup because runtime depends on hardware and interpreter conditions.

The structural improvement is deterministic: explicit enumeration loops over opening-hand compositions and Prize compositions, while the collapsed version loops over opening-hand compositions only.

## Why this matters

The original exact calculation is already fast for one deck state.

Parameter sweeps multiply that cost quickly. Deck-construction studies may vary:

- target counts;
- discard cost;
- disposable-card density;
- opening-hand size;
- starter density.

Analytically removing the Prize loop makes broad exact sweeps practical without replacing the model with Monte Carlo sampling.

## Limitations

This reduction is specific to the information the same-window connector model asks of Prize placement.

More detailed models may need the full Prize composition, for example when:

- several distinct critical cards can be rescued separately;
- Gladion-like actions change Prize contents over time;
- ordinary Prize-taking is modeled;
- the identity of multiple Prized resources changes policy.

Those models should retain richer Prize-state representations.

## Next use

Use the collapsed calculation for a broad slot-marginal regime scan. The goal is to identify where direct redundancy, discard payability, or connector capacity is the active bottleneck.
