# Exact dynamic-programming Retreat payment counts for multi-unit Energy

## Why extend the model

The previous Retreat payment-count formula specialized to physical Energy
cards providing one or two units. Expanded can include Energy cards that
supply three or four units under specified game-state conditions, such as
Reversal Energy, Ignition Energy or Super Boost Energy Prism Star.

Exact counting without enumerating all physical subsets is useful for
deciding when a simulator should invoke complete payment generation.

## DP representation and correctness

For each group of certifiably interchangeable attached physical Energy
copies, supply the exact current Energy units per card and number of
available copies. The dynamic program iterates over these groups,
tracking three sufficient statistics:

1. Number of selected physical cards.
2. Total supplied Energy units.
3. Smallest unit count of any selected card.

The coefficient for choosing j physical cards out of m copies in the
next group is C(m,j). Identical states from different selection
histories are merged by adding exact integer multiplicities.

For a positive effective Retreat Cost c, accepted payments require
1 <= selected-card count <= c and supplied units >= c.

An accepted payment is inclusion-minimal exactly when
supplied units minus the smallest selected unit is less than c.
Removing any single card is then insufficient; conversely, if the
smallest selected card could be removed, the payment is nonminimal.
For cost zero there is one empty payment.

This computes the full physical payment count and its
inclusion-minimal subset count with integer arithmetic. Its runtime
depends on reachable DP summary states rather than the number of
labeled physical subsets.

## Independent finite verification

The reproducible test constructs literal EnergyAttachment objects,
using groups with one, two, three and four units. It enumerates
all physical payment subsets through the canonical board kernel,
independently classifies inclusion-minimal payments, and checks the
sum of explicit payment-orbit multiplicities.

The test covers 729 mixed-unit configurations with zero to two
cards of each of the four unit sizes, at Retreat Costs 0 through 8.
It also checks 343 one/two-unit cases against the earlier closed-form
binomial count.

As an illustrative large mixed-unit state, 8 one-unit, 4 two-unit,
4 three-unit and 1 four-unit Energy cards attached at cost 4 yield
**3,081 legal physical payments**, of which **243** are
inclusion-minimal.

## Source and limitations

Implementation: `tools/retreat_payment_polynomial_dp.py`.
Reproduce: `python results/retreat_payment_polynomial_dp/reproduce.py`.

The supplied card pool and existing
`tools/retreat_dynamic_energy_units.py` establish which provider
families can supply multi-unit Energy in specific states. A caller must
resolve the actual current unit count, including Prize dependence and
holder eligibility, before using it as a deterministic DP input.

As in the physical board kernel, this study adopts the conservative
selection rule that a positive-cost Retreat may select at most c
physical Energy cards. It counts payment subsets only. Bench position,
Retreat prohibition, destination replacement, turn-budget restrictions,
future strategic value and private card information are separate.

The DP is a counting engine and does not itself prune any legal
physical action or establish tournament win-rate claims.
