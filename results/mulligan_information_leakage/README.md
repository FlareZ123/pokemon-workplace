# Mulligan information leakage before the first turn

## Question

How much information about a deck is exposed by the number and contents of revealed mulligan hands?

The bundled Advanced Player's Rulebook states that a player with no Basic Pokémon reveals that opening hand before shuffling it back and trying again. The human concepts notes also point out that this can reveal or constrain an archetype. This result quantifies that information channel.

Implementation: `tools/mulligan_information_leakage.py`

Reproducer: `results/mulligan_information_leakage/reproduce.py`

## Exact model

For deck size `N`, opening hand size `H`, `B` forced Basics, and `D` non-Basic diagnostic cards:

`P(mulligan) = C(N-B,H) / C(N,H)`.

A mulligan contains exactly `d` diagnostic cards with probability

`C(D,d) C(N-B-D,H-d) / C(N,H)`.

Repeated attempts are independent after reshuffling. If `q` is the probability of a mulligan with zero diagnostics and `r` is the probability of a mulligan with at least one, then

`P(ever reveal a diagnostic before acceptance) = r / (1-q)`.

If exactly `k` mulligans occur before acceptance, their likelihood is

`P(K=k) = P(mulligan)^k (1-P(mulligan))`.

These likelihoods support exact Bayesian updates between candidate deck models.

## Findings

With equal priors on a four-Basic and a twelve-Basic 60-card candidate, observing the exact number of mulligans and then acceptance gives the following posterior for the four-Basic candidate:

| Mulligans | Posterior |
| ---: | ---: |
| 0 | 33.047826979% |
| 1 | 60.857318463% |
| 2 | 83.042748216% |
| 3 | 93.911786801% |
| 5 | 99.350808031% |

Mulligan count alone can therefore be strong setup information.

For a four-copy non-Basic diagnostic card:

| Forced Basics | Diagnostic in one mulligan, conditional | Diagnostic exposed at least once before acceptance |
| ---: | ---: | ---: |
| 1 | 40.516472361% | 75.415936326% |
| 4 | 42.313703068% | 38.876445019% |
| 8 | 44.964447317% | 19.244961978% |
| 12 | 47.954568815% | 10.149436388% |

The conditional probability inside one mulligan rises as Basic density rises, while the full setup-sequence exposure probability falls because mulligans become rarer.

With four forced Basics, a singleton non-Basic diagnostic appears in a revealed mulligan with probability **12.5%**. It is exposed at least once before acceptance with probability **15.817220825%**.

Copy counts also carry information. Compare equal-prior candidates with the same four Basics and either four or two copies of one non-Basic diagnostic:

| Revealed sequence, then acceptance | Posterior for 4-copy candidate |
| --- | ---: |
| one mulligan showing exactly 1 copy | 61.187957689% |
| two mulligans showing exactly 1 copy each | 71.309012361% |
| one mulligan showing exactly 2 copies | 83.138918346% |
| two mulligans showing 0 copies each | 36.332214250% |

Repeated absence is informative as well.

Under this forced-Basic model, ordinary Basic Pokémon never appear in a revealed mulligan hand, because a hand containing one is accepted. Basic density is inferred from mulligan frequency; non-Basic cards can be revealed directly.

## Strategic implication

Matchup-dependent DCI and AMR can change during setup. A simulator that starts its information state at the first normal turn discards public evidence from the mulligan transcript. A richer state should record mulligan count and all revealed rejected-hand identities before selecting matchup-conditioned lines.

## Validation and limits

The implementation uses exact binomial coefficients. The reproducer exhaustively enumerates every labeled opening hand in a small toy deck and matches the closed-form rejected-hand distribution. It also checks the reported 60-card probabilities and posteriors.

This first kernel assumes a stationary forced-Basic keep policy. Optional setup cards and hand-dependent keep choices require integration with `results/setup_mulligan_policy/`. The diagnostic model currently tracks one card class at a time. A future extension should support several card identities and feed the resulting archetype posterior into matchup-conditioned decision models.
