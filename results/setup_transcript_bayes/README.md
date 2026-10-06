# Optional-starter policy censors the public mulligan transcript

## Question

How should setup information models handle optional starter cards when players can keep some Basic-less hands and mulligan others?

A revealed mulligan is a selected sample. The player's setup policy determines which Basic-less hands ever become public.

Implementation: `tools/setup_transcript_bayes.py`

Reproducer: `results/setup_transcript_bayes/reproduce.py`

Preserved examples: `results/setup_transcript_bayes/model_examples.json`

## Model

The model tracks forced Basics plus any number of non-Basic groups. Some tracked groups may be optional setup starters, while others can be ordinary diagnostic cards.

For every no-forced-Basic hand composition `x`, a stationary policy supplies a keep probability `k(x)`. The probability that a particular composition becomes a revealed mulligan is its exact hypergeometric hand probability multiplied by `1-k(x)`.

A transcript likelihood is the product of each observed rejected-hand composition followed by the probability that the final opening is accepted. Candidate deck constructions or candidate setup policies can then be compared with Bayes' rule.

## Example

Consider a 60-card deck with:

- 4 forced Basics;
- 2 Manectric optional starters;
- 2 Snorlax Doll optional starters;
- 4 unrelated non-Basic cards in diagnostic class X.

Three policies are compared.

| Policy | Mulligan probability | Manectric in a revealed mulligan | Doll in a revealed mulligan | X in a revealed mulligan | X exposed before setup succeeds |
| --- | ---: | ---: | ---: | ---: | ---: |
| decline every optional-only hand | 60.050037426% | 23.636363636% | 23.636363636% | 42.313703068% | 38.876445019% |
| keep optional-only iff Doll is present | 45.856392216% | 24.458420685% | 0% | 43.600178339% | 26.968245460% |
| keep every optional-only hand | 34.640642897% | 0% | 0% | 44.964447317% | 19.244961978% |

## Finding 1: keep policy can create zero-probability observations

If every Basic-less hand containing Manectric or Snorlax Doll is kept, neither optional starter can appear in a revealed mulligan.

A revealed mulligan containing exactly one Manectric has positive probability under the decline-all policy and zero probability under the accept-any-optional policy. With equal priors between those two policy models, observing that transcript gives posterior probability 1 to the decline-all model.

This means a public setup transcript contains information about player policy as well as deck composition.

## Finding 2: censoring can enrich unrelated cards in each revealed hand

Diagnostic X is unrelated to the keep decision. Its conditional visibility within a revealed mulligan still changes:

- decline all optional-only hands: 42.313703068%;
- keep Doll-only hands: 43.600178339%;
- keep every optional-only hand: 44.964447317%.

Hands containing optional starters are selectively removed from the public sample. The remaining mulligans therefore have a different composition distribution.

## Finding 3: per-hand enrichment can coexist with lower match-level exposure

Although X becomes more concentrated inside each revealed mulligan, its probability of being exposed at least once before setup succeeds falls from 38.876445019% to 19.244961978% between the decline-all and accept-any policies.

The policy produces fewer mulligans overall. Per-reveal composition and full-setup exposure are separate quantities.

## Strategic consequence

An archetype classifier should not treat revealed mulligan cards as an unbiased sample from the deck's non-Basic cards. When optional setup cards exist, inference should model the keep policy that generated the public transcript.

This extends `results/setup_mulligan_policy/`, which showed that optional setup decisions change opening and Prize priors. The same choices also change what the opponent can learn before the first normal turn.

## Validation and limits

The reproducer exhaustively enumerates every labeled opening hand in a small deck with several tracked groups and a selective keep policy. Every rejected composition probability matches the closed-form model.

The current implementation assumes a stationary policy based on tracked group counts. Real players may use the entire hand, turn order, revealed opponent information, and matchup knowledge. Extending the policy state to those variables is the next step toward a realistic setup belief model.
