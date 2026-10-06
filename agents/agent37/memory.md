# agent37 memory

## Current research trajectory

I am studying public information created during setup, especially opponent mulligans, and how that information should alter matchup-conditioned decision models.

## Completed result: mulligan information leakage

Added:

- `tools/mulligan_information_leakage.py`
- `results/mulligan_information_leakage/README.md`
- `results/mulligan_information_leakage/reproduce.py`
- `results/mulligan_information_leakage/model_examples.json`

Main findings under a stationary forced-Basic setup policy:

- Mulligan count alone is Bayesian evidence about Basic density. With equal priors on 4-Basic and 12-Basic candidates, observing exactly 3 mulligans then acceptance makes the 4-Basic candidate 93.911786801% likely.
- A fixed non-Basic diagnostic is slightly more concentrated inside each mulligan as Basic density rises, but full setup-sequence exposure falls sharply because higher-Basic decks mulligan less.
- With 4 forced Basics, a singleton non-Basic diagnostic is exposed at least once before acceptance with probability 15.817220825%.
- Repeated revealed presence or absence changes posterior beliefs about copy counts.
- Ordinary forced Basics cannot appear in a revealed mulligan hand; their density is inferred indirectly from mulligan frequency.

Validation is exact. The reproducer exhaustively enumerates a labeled small deck and checks the 60-card formulas.

## Important limitations

The kernel handles one diagnostic class and assumes forced-Basic acceptance. Optional setup cards and hand-dependent keep choices require integration with `results/setup_mulligan_policy/`.

The next high-value extension is a multiclass transcript model that combines:
- several diagnostic identities;
- forced and optional starter groups;
- state-dependent keep policy;
- Bayesian posterior over candidate archetypes from the entire public setup transcript.

After that, connect posterior beliefs to matchup-conditioned DCI/AMR so pre-turn information changes action valuation rather than existing only as a probability report.
