# Optional discard branch witness

## Finding

Optional discard payment and conditional search use are separate action choices.

Guzma & Hala is the counterexample. Its optional two-card discard unlocks additional Tool and Special Energy search capacity, while the player can pay that discard without filling either added search slot.

Implementation: `tools/trainer_search_transaction.py`  
Regression: `results/optional_discard_branch_witness/reproduce.py`

The regression distinguishes:

- Stadium-only retrieval with no optional discard;
- the same Stadium-only retrieval with the optional discard paid;
- the optional discard paid with zero retrieval.

The first two share the same retrieval witness while producing different hand and discard states. The third has no retrieved card while still changing game state through the discard. A free zero-retrieval action is rejected.

## Consequence

Connector execution needs an explicit branch-choice witness in addition to exact search targets and exact discard-card selection. Conditional-output usage cannot safely stand in for whether an optional state-changing effect was chosen.

This is relevant when discarding particular cards has strategic value. The execution layer represents the choice; later policy evaluation decides whether paying it was good.

## Limits

This result is deterministic and does not assign value to the discarded cards or retrieved side outputs. Those continuation values remain policy questions.
