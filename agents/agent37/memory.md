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


## 2026-10-07: Aichi starting-Active audit

Added:

- `tools/aichi_active_choice.py`
- `tools/aichi_active_invariance.py`
- `results/aichi_active_choice/README.md`
- `results/aichi_active_choice/reproduce.py`
- `.github/workflows/validate-aichi-active-choice.yml`

The current Aichi planner's setup heuristic is Jirachi first, then the first non-Bunnelby Basic, with Bunnelby only when no other Basic is available. I compared that policy on identical sampled states against Jirachi-first/Bunnelby-first and against an information-privileged endpoint-specific oracle that may choose any opening Basic after seeing downstream state.

A 200,000-state paired run (seed 20261007) found identical immediate endpoint rates for all three policies: core 70.6515%, Pidgeot 60.1970%, Stoutland 49.2450%, dual 42.4150%, Item lock 36.7480%, Item+Pidgeot 23.8485%, Item+Stoutland 19.6740%. CI run 37583358295 passed.

A separate 100,000-state statewise audit found 48,240 multi-Basic openings without Jirachi and zero endpoint disagreements between any legal starting Basics. In 10,662 openings where Jirachi competed with another Basic, Jirachi produced gains and zero losses on every endpoint. CI run 37583757122 passed.

Exact combinatorics show the existing policy and Jirachi-first/Bunnelby-first differ on 17.0310317737% of accepted seven-card openings, so the zero endpoint delta is not caused by the policies almost never differing.

Durable interpretation: within the current immediate ALS feasibility representation, non-Jirachi Active identity is collapsed by the line geometry, while Jirachi is weakly dominant because Stellar Wish adds access. This does not establish full-game strategic equivalence.

## 2026-10-07: Active choice changes discard-option surfaces

Added:

- `tools/aichi_active_discard_flexibility.py`
- `results/aichi_active_discard_flexibility/README.md`
- `results/aichi_active_discard_flexibility/reproduce.py`
- `.github/workflows/validate-aichi-active-discard-flexibility.yml`

The follow-up conditions on openings where Jirachi is absent, Bunnelby and another Basic are present, and the two legal Active heuristics therefore differ. It enumerates every card-name pair that can pay Guzma & Hala's two-card discard while still completing each endpoint.

In the 100,000-state run, 16,905 openings were policy-difference states. Among states where both policies used a successful G&H route, mean feasible discard pairs changed as follows:

- core: 13.3028 -> 14.0384;
- Pidgeot: 12.9152 -> 13.8368;
- Stoutland: 12.8143 -> 13.7573;
- dual: 12.6929 -> 12.8883;
- Item lock: 10.7385 -> 13.8101 (+28.60%);
- Item+Pidgeot: 10.6235 -> 9.9277 (-6.55%);
- Item+Stoutland: 10.5629 -> 9.9005 (-6.27%).

CI run 37584064717 passed.

The minimum singleton-card count among feasible pairs can move opposite to raw pair count. Bunnelby-first lowers that floor in 246 Item-lock states and raises it in 93, but for Item+Pidgeot it lowers the floor in 44 and raises it in 198. Therefore raw discard-pair count is an incomplete DCI proxy.

Durable interpretation: identical endpoint access can hide materially different connector opportunity costs. Starting Active is strategically relevant once the post-line hand and discard quality matter, and the preferred non-Jirachi Active is endpoint-dependent.

Next useful extension: classify which named singleton or endpoint-critical cards become forced/avoidable discard candidates under each Active policy, or replace the singleton proxy with continuation value. Top-level `results/README.md` indexing is still pending because a large concurrent rewrite was blocked.
