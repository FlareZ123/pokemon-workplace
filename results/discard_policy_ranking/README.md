# DCI-style scores rank legal Pokémon TCG discard witnesses

## Question

If scalar discardability scores cannot define the full legal discard set, can they still be useful?

Yes.

This result gives scalar DCI-style values a precise role:

1. joint constraints define which exact discard witnesses are strategically legal;
2. scalar values rank those legal witnesses.

Implementation: `tools/discard_policy_ranking.py`  
Regression: `results/discard_policy_ranking/reproduce.py`

## Example

The hand contains A, B, and C.

Discard desirability scores are:

| TCG resource | Score |
| --- | ---: |
| A | 1.0 |
| B | 0.9 |
| C | 0.1 |

The effect requires discarding two resources.

Without any joint rule, the highest additive score is:

`A + B = 1.9`

Now add the strategic requirement that at least one of A or B must remain:

`discard(A) + discard(B) <= 1`

The A+B witness is removed before ranking.

The remaining witnesses rank as:

1. A+C, score 1.1;
2. B+C, score 1.0.

## Result

The scalar values remain useful as an objective function.

They are insufficient as a feasibility representation.

This separation resolves the tension between two observations:

- DCI-style scores can express which resources are more attractive to discard;
- joint strategic dependencies can make the highest-scoring combination illegal.

## Architecture

`rank_discard_selections()` receives:

- the exact hand state;
- card-class candidates;
- discard cost;
- joint group constraints;
- one score in `[0, 1]` for each candidate class.

It first asks `joint_discard_constraints` for exact legal witnesses.

Only those witnesses are scored and sorted.

The scoring layer therefore cannot accidentally restore a witness rejected by a strategic retention rule.

## Relation to DCI

The human-developed DCI concept proposes a state-dependent scalar from 0 to 1, with higher values representing greater desire or acceptability to discard.

This result supports retaining such a scalar as a heuristic or optimization coefficient.

A stronger representation is:

`state -> legal witness family -> DCI ranking -> exact transition`

The DCI values can change after each exact transition.

## Relation to adjacent results

- `discard_cost_amr/` measures whether a discard cost is mechanically reachable from a frozen disposable pool.
- `discard_cost_witness/` preserves exact TCG hand selections.
- `joint_discard_constraints/` adds relational feasibility.
- `discard_capacity_nonfungibility/` shows that the scalar capacity must sometimes be recomputed after an exact selection.
- `temporal_discard_replenishment/` shows that new candidate resources can enter the hand between discard decisions.

Together these results turn DCI from a standalone scalar representation into one component of a state-aware discard policy.

## Limits

The current score is additive across selected copies.

Real continuation value can have interactions that are not additive even after feasibility filtering. The group constraints capture some hard interactions, while softer pairwise or future-value interactions may require a richer objective.

The result does not estimate DCI values automatically. It specifies how externally supplied state-dependent scores can be used safely within this constrained layer.

## Next useful work

A future policy can derive scores and constraints from concrete deck state:

- intended attack line;
- known Prize state;
- matchup;
- already-used once-per-game effects;
- redundant copies;
- recovery options;
- downstream search requirements.

The exact witness can then be executed and the policy recomputed from the resulting state.
