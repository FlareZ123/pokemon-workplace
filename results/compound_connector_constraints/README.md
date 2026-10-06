# Compound connector constraints: one-use capacity plus discard payability

## Question

What happens when a shared search connector is overcredited in two ways at once?

A naive access graph can:

1. reuse the same physical connector across two required target channels;
2. assume the connector is usable whenever it is present, even when its discard cost cannot be paid.

This result measures both errors in the same exact setup-conditioned states.

Implementation: `tools/compound_connector_constraints.py`  
Independent reproducer: `results/compound_connector_constraints/reproduce.py`

## Model

The deck contains:

- target A;
- target B;
- shared connectors that may search either target, one target per connector use;
- disposable non-starters;
- protected setup starters;
- protected filler.

The opening hand is conditioned on containing a setup-eligible starter. Prize cards are then sampled, followed by an optional number of random non-Prize draws.

Both target channels are required at the access check.

Each connector use:

- can search one missing target from the remaining deck;
- consumes one physical connector copy;
- requires `discard_cost` disposable cards from hand.

Targets, connectors, and disposable cards are non-starters in this baseline.

## Four evaluations of the same state

**Naive joint access** checks target A and target B independently. The same connector can therefore count as an out to both targets, and discard cost is ignored.

**Capacity-only access** enforces one-use connector capacity. If both targets are missing from hand, two physical connector copies are required. Discard cost is ignored.

**Discard-only naive access** checks the discard gate but still lets the same payable connector count independently for both target channels.

**Full joint access** enforces both physical connector capacity and discard payability.

This decomposition lets us identify capacity error, discard error, their union, and the probability mass where both errors occur in the same state.

## Illustrative baseline

Use:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 protected setup starters;
- 2 copies of target A;
- 2 copies of target B;
- 1 shared connector;
- no later random draws.

### Varying disposable density at discard cost two

| Disposable non-starters | Naive joint | Capacity-only | Discard-only naive | Full joint | Combined overstatement |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 14.286842% | 7.121909% | 6.265670% | 4.384240% | 9.902602% |
| 15 | 14.286842% | 7.121909% | 8.413299% | 4.959448% | 9.327394% |
| 20 | 14.286842% | 7.121909% | 10.431440% | 5.564306% | 8.722535% |
| 25 | 14.286842% | 7.121909% | 12.052213% | 6.115275% | 8.171567% |
| 30 | 14.286842% | 7.121909% | 13.180575% | 6.557295% | 7.729547% |
| 35 | 14.286842% | 7.121909% | 13.847377% | 6.863784% | 7.423058% |

The capacity-only column is constant because disposable density does not affect physical connector count. The discard-only and full columns improve as more hands can pay the connector cost.

With 20 disposable non-starters, the naive graph reports 14.29% joint access while the full model reports only 5.56%.

## Constraint overlap

For the 20-disposable baseline:

| Discard cost | Naive joint | Capacity-only | Discard-only naive | Full joint | States failing both constraints |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 14.286842% | 7.121909% | 14.286842% | 7.121909% | 0.000000% |
| 2 | 14.286842% | 7.121909% | 10.431440% | 5.564306% | 2.297799% |
| 3 | 14.286842% | 7.121909% | 6.655194% | 4.375070% | 4.884809% |

The overlap column is the probability that a naive-joint-success state simultaneously has insufficient connector capacity and insufficient discard payability.

This matters because the two error corrections are not additive.

At discard cost two:

- capacity error: 7.164933 percentage points;
- discard error: 3.855402 points;
- their simple sum: 11.020335 points;
- actual combined error: 8.722535 points;
- overlap: 2.297799 points.

The identity is the ordinary inclusion-exclusion relation:

`combined error = capacity error + discard error - overlap`.

A model that independently subtracts average penalties for connector contention and discard AMR can double-count the same bad states.

## Strategic interpretation

### Reachability does not compose across shared resources

A target can be individually reachable while the full line is impossible. One Computer Search-like connector cannot search both a missing attacker and a missing rescue Supporter.

The error is a resource-allocation problem, not a failure of either individual edge.

### Payability and capacity interact state by state

A connector can fail because:

- it is being asked to serve too many channels;
- its discard cost is unpayable;
- both are true simultaneously.

The third category creates overlap. Aggregate correction factors lose that dependence.

### Optimizers need joint state

A deck optimizer that scores:

- target A access;
- target B access;
- connector presence;
- discard density;

as independent marginal features can still substantially overrate the state.

The minimum useful representation must preserve the shared identity of the connector and enough hand state to evaluate its cost.

## Relation to Computer Search and connector domination

Computer Search is a natural interpretation of the one-use, any-card connector in this baseline.

Suppose the current line needs both:

- a Gladion-like Prize-rescue Supporter;
- another required card such as an attacker or Energy-enabling piece.

If both are absent, one Computer Search can choose either target. It cannot satisfy both independently.

If its two-card discard cost is also unpayable, even the chosen edge disappears.

This is a concrete quantitative form of connector domination. The connector's value depends on which competing use receives it and whether that use can actually be paid.

The model still does not decide which target is strategically more valuable. It only tests whether the two-target requirement can be jointly satisfied.

## Validation

The calculations are exact.

The reproducer independently exhausts a labeled 10-card case over:

- every accepted opening-hand subset;
- every disjoint Prize subset;
- every disjoint later-draw subset.

It computes all four access evaluations plus capacity failure, discard failure, combined failure, and overlap directly from labeled cards.

Every quantity matches the category model to floating-point precision. Total state mass is asserted to be one.

## Limits

The baseline has two required target channels and one connector class.

It omits:

- target priorities;
- multiple connector types;
- multi-axis connectors that genuinely satisfy several channels per play;
- Supporter timing;
- Bench requirements;
- Ability or Item lock;
- stochastic search;
- graded DCI;
- targeted access to the connector itself;
- ordinary Prize-taking;
- full gameplay policy.

The disposable pool is binary and state-fixed.

## Next useful work

A stronger representation should generalize the two-target test to a connector-allocation problem.

Useful capabilities include:

- arbitrary target requirement vectors;
- multiple connector classes;
- one-shot any-card connectors;
- connectors restricted to subsets of targets;
- genuine multi-axis actions such as Stadium plus Special Energy plus Tool;
- per-use costs;
- state-dependent availability;
- target-specific downstream value.

That moves the research from pairwise reachability correction toward a reusable resource-allocation engine for real deck lines.
