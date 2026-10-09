# Learning an opponent's search policy across games requires labeled evidence

## Question

A player has revealed a specific Pikachu print during a past game. Their opponent wants to infer which K1 target-selection policy they tend to use, so future search reveals can help predict hidden Prize cards.

How much does observing card printings across independent games reveal about that player's policy? And what if a past game's hidden Prize status is learned only after the printing was already observed?

## Exact symmetric policy result

The model uses the same two opposing search rules and 6-card Prize witness in [latent_search_policy_information](../latent_search_policy_information/). Both forward and reverse policies choose each of the two Pikachu prints in exactly 7 of the 15 initial Prize worlds, including 1 world with neither print available and no search. Conditional on a search occurring:

- P(old Pikachu | forward) = 1/2;
- P(old Pikachu | reverse) = 1/2.

Therefore **observing any number of old/new Pikachu print choices alone cannot distinguish these two policies**, even when one fixed policy persists across games. In the regression, 50 successive old-print observations leave the prior exactly 1/2 forward and 1/2 reverse.

The prints are publicly observed, but the strategically important missing label is *whether A was Prized in that past game*.

## Labeled examples and policy confidence

Suppose the observer eventually learns that A was Prized when the player chose the older printing. For this observed joint event:

- P(old and A Prized | forward, successful search) = 2/7;
- P(old and A Prized | reverse, successful search) = 1/14.

The likelihood ratio is 4:1. Starting from equal priors, one such labeled example raises P(forward) to **4/5**, and two independent matching labeled examples raise it to **16/17**.

That belief update changes the practical interpretation of the next printing reveal:

- Initially, knowledge of print identity offers zero gain for the controlled equal-reward Prized/unprized prediction.
- After one labeled example, P(forward)=4/5 remains within the [1/6,5/6] zero-decision-value range.
- After two, P(forward)=16/17 exceeds 5/6 and the next print signal improves the optimal correct-prediction probability by exactly **11/238**, or approximately 4.62 percentage points.

The evidence can be retrospective. A late publicly known Prize status from one game can change the interpretation of that game's earlier printing and improve prediction in a later independent game, assuming the search policy persists.

## Avoiding double counting when the same game's information arrives in stages

There is a separate inference hazard: the print was observed earlier; later learning A's Prize status is an additional observation about **the same event**. The observer must multiply policy odds by

`P(A Prized | previously seen print, policy)`

rather than multiply by the whole joint print-plus-Prize likelihood a second time.

The regression demonstrates this on two asymmetric print preferences, for which print choice already informs policy identity:

1. Prior is 1/2 each for "prefer old" and "prefer new."
2. Seeing old print raises P(prefer old) to **5/7**.
3. Later learning A was Prized, with conditional likelihood, gives posterior **4/5**. This equals observing the full print-plus-Prize outcome once.
4. Incorrectly applying the entire joint event a second time gives **10/11**, an overconfident posterior caused by reusing the same public print evidence.

This is an information-chronology problem closely related to K0/K1 and opponent belief correlation. Information about the same game should have a persistent event identity so a model can compute *incremental* evidence correctly.

## Implementation and validation

- `tools/search_policy_session_learning.py`: exact fractional posterior over persistent policy hypotheses, per-search observations, and optional deferred Prize labels; conditional later-label update avoids recounting a previously observed print.
- `tools/latent_search_policy_belief.py`: exact within-policy search, Prize, and top-card likelihoods.
- `results/sequential_search_policy_learning/reproduce.py`: checks 50 print-only observations, labeled posterior jumps, subsequent decision utility via `observation_policy_envelope.py`, and the asymmetric double-counting counterexample.
- CI: `.github/workflows/validate-sequential-search-policy-learning.yml`.

## Scope

Each game is a fresh independent Prize deal under a fixed policy hypothesis; cards/deck context is deliberately held fixed. The experiment assumes an external source eventually identifies whether a chosen singleton was Prized. This could arise from some game records, opponent reveals, or later public evidence, but is not automatic in every real match.

It is not an empirical model of human consistency, nor a live match predictor. Applying it to Expanded tournaments would require policy hypotheses tied to actual legal game states and a disciplined record of which observations belong to the same match. Its value is a reproducible Bayesian example showing why public behavioral samples can remain uninformative until paired with additional event-specific evidence.
