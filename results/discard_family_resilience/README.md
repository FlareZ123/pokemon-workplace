# Structural resilience of discard-witness families

This result studies families of endpoint-preserving discard choices. Several states can have the same number of feasible discard pairs while differing substantially in how much redundancy those pairs provide.

Implementation: `tools/discard_family_resilience.py`  
Regression: `results/discard_family_resilience/reproduce.py`

## Core metric

The tool measures the smallest number of card names whose future preservation would intersect every currently feasible discard witness. A value of one means every witness shares at least one common name. Larger values indicate that the witness family remains feasible under more independent preservation requirements.

For three families with the same three-witness count:

| Witness family | Common name in every witness | Structural threshold |
| --- | --- | ---: |
| `AB, AC, AD` | A | 1 |
| `AB, AC, BC` | none | 2 |
| `AB, CD, EF` | none | 3 |

Using a shared six-name candidate universe and choosing preserved names uniformly, the exact probability that at least one witness remains feasible is:

| Preserved names | Family 1 | Family 2 | Family 3 |
| ---: | ---: | ---: | ---: |
| 1 | 83.3333% | 100.0000% | 100.0000% |
| 2 | 66.6667% | 80.0000% | 100.0000% |
| 3 | 45.0000% | 50.0000% | 60.0000% |

Raw witness count therefore does not determine robustness.

## Relation to Aichi Vileplume

The recent `aichi_active_discard_flexibility/` result measures feasible-pair count, and `aichi_active_forced_singletons/` measures names appearing in every pair. This result provides an intermediate structural measure for states where no single name is mandatory but several future preservation requirements together can eliminate all feasible pairs.

## Validation

The implementation exactly enumerates the relevant subsets. The regression verifies the three families and the exact probabilities above.

## Next work

Apply the structural metric to the sampled Aichi Guzma & Hala witness families and compare it with raw pair count under the two Active-choice policies.
