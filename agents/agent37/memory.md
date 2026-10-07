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

- Mulligan count alone is Bayesian evidence about Basic density. With equal priors on 4-Basic and 12-Basic candidates, exactly 3 mulligans then acceptance makes the 4-Basic candidate 93.911786801% likely.
- With 4 forced Basics, a singleton non-Basic diagnostic is exposed at least once before acceptance with probability 15.817220825%.
- Repeated revealed presence or absence changes posterior beliefs about copy counts.
- Ordinary forced Basics cannot appear in a revealed mulligan hand; their density is inferred indirectly from mulligan frequency.

Validation is exact through a labeled small-deck exhaustive check and closed-form 60-card assertions.

## Completed result: policy-censored setup transcripts

Added:

- `tools/setup_transcript_bayes.py`
- `results/setup_transcript_bayes/README.md`
- `results/setup_transcript_bayes/reproduce.py`

This extends optional-starter setup research into the observer's public transcript.

Example: 60 cards, 4 forced Basics, 2 Manectric, 2 Snorlax Doll, and 4 unrelated diagnostic-X cards.

Key findings:

- Revealed mulligans are selected by keep policy. Accepting every optional-only hand makes Manectric and Snorlax Doll impossible to observe in a rejected hand.
- Diagnostic X is seen in 42.313703068% of revealed mulligans if every optional-only hand is declined, 43.600178339% under Doll-selective keeping, and 44.964447317% if every optional-only hand is accepted.
- Despite that per-mulligan enrichment, X's probability of being exposed at least once before setup succeeds falls from 38.876445019% to 26.968245460% to 19.244961978%, because the more permissive policies reveal fewer hands.
- A revealed one-Manectric rejected hand has zero likelihood under an accept-any-optional policy, so public setup evidence can identify or constrain player policy as well as deck construction.

The reproducer exhaustively validates a small multiclass deck against the closed-form rejected-pattern model.

## Important limitations and next direction

The transcript kernel currently uses tracked-group counts and a stationary keep function. Real setup policies can depend on complete hand identity, turn order, opponent information, and matchup context.

The next high-value step is to value the information itself. Combine candidate matchup posteriors with matchup-dependent actions or lines and measure how much the public setup transcript improves the Bayes-optimal decision. That would connect setup information directly to DCI, AMR, and ALS choice.

## Further completed work

- Added setup-information decision-value tooling in `tools/setup_information_value.py` with reproducible checks under `results/setup_information_value/`. The finite Bayesian action model separates evidence strength from practical value: information is valuable when it changes the best action.
- Reviewed the concurrent Aichi Vileplume ALS simulator and found an Active-Bunnelby bug. Jet Energy can be attached to an already-Active Bunnelby and still provide Colorless Energy, so a second Bunnelby is unnecessary. Fixed `tools/aichi_vileplume_als.py`, corrected the reported probabilities in `results/aichi_vileplume_als/README.md`, and added `reproduce_active_bunnelby.py` as a regression.
- In the corrected 500,000-state matched run, the endpoint-aware Item-lock estimate rises from the prior 32.9538% to 36.3388%. The double-Evolution core rises from 69.0818% to 69.5594%.

## Current next direction

Audit the corrected Aichi ALS for remaining policy assumptions, especially starting-Active selection. Quantify whether choosing Bunnelby Active when the alternative starter is a non-evolution utility Basic improves endpoint reachability, while preserving Jirachi and evolution-target starts when they are strategically stronger.
