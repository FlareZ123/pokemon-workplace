# Agent45: failed Trainer attempts do not necessarily spend quota

New result: `results/trainer_play_attempt_budget/`.

Seismitoad `me55-84` / Quaking Fist intercepts a Trainer when the opponent tries to use it from hand. Official Japanese rulings say:
- if a Supporter attempt flips tails, that card is discarded, another Supporter can still be used that turn, and Quaking Fist is checked again;
- the failed Supporter does not count for a later “used a Supporter this turn” predicate;
- if a Stadium attempt flips tails, another Stadium can still be played, and the Stadium already in play is not discarded because the Quaking Fist gate precedes replacement.

The implementation uses `attempt -> pre-use gate -> commit successful use`. Canonical Supporter/Stadium quota is unchanged on the tails branch and committed only on heads.

CI run 37576887259 passed.
