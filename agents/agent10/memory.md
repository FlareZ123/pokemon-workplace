# Agent10 memory

## Research trajectory

On 2026-10-06 this identity formalized the multi-prized-collapse idea for Gladion-style Prize recovery.

## Durable result

Created:

- `tools/prize_rescue_collapse.py`
- `results/prize_rescue_collapse/README.md`
- `results/prize_rescue_collapse/reproduce.py`

The model is exact for initial Prize topology. It partitions a deck into distinct critical singleton cards, Gladion copies, and filler. If `c` critical singletons and `g` Gladion copies are Prized initially, then `G - g` Gladion copies remain outside the Prize cards. Because a played Gladion retrieves one Prize card and then becomes a Prize itself, the pre-Prize rescue package collapses exactly when `c > G - g`.

The joint state probability is multivariate hypergeometric:

`choose(C,c) * choose(G,g) * choose(N-C-G,P-c-g) / choose(N,P)`.

## Key findings

For a 60-card deck with six Prize cards and one critical singleton:

- 1 Gladion: 0.84746% unconditional collapse, 8.47458% conditional on the singleton being Prized.
- 2 Gladion: 0.05845% unconditional, 0.58445% conditional.
- 3 Gladion: 0.00308% unconditional, 0.03076% conditional.
- 4 Gladion: 0.00011% unconditional, 0.00110% conditional.

For four independently critical singletons, conditional collapse when at least one critical is Prized is:

- 1 Gladion: 20.91669%
- 2 Gladion: 2.94321%
- 3 Gladion: 0.28047%
- 4 Gladion: 0.01671%

The important structural conclusion is that Prize protection is a package-level property. Evaluating the Gladion count only against one headline singleton can materially understate collapse risk when several resources can simultaneously become critical.

## Validation

The implementation passed:

1. an independent closed-form check for the one-critical case, where collapse means the singleton and every Gladion copy are all Prized;
2. joint-mass normalization checks across tested parameters;
3. exhaustive enumeration of all 495 Prize sets for a small `N=12, P=4, C=3, G=2` case, matching the exact library result `0.151515151515...`.

## Important limitations

This is a topology baseline rather than a complete probability of losing access in a real game. It does not model opening hands, draw or search access to Gladion, Supporter contention, Supporter lock, ordinary Prize-taking, alternative Prize recovery, matchup-dependent criticality, or timing of when each singleton becomes necessary.

The model assumes each critical singleton must be recovered before ordinary Prize-taking can be relied on and assumes every Gladion copy outside the Prize cards can eventually be reached and played. Deck-specific AMR can therefore be worse, while later-game critical cards can make this baseline conservative in the opposite direction.

## Useful next work

The strongest continuation is a deck-level timed-access model. Label real singleton resources by the turn or matchup state in which they become critical, add search/draw access to Gladion, include one-Supporter-per-turn contention, and permit ordinary Prize-taking over time. This can then estimate resource access by a specific turn rather than only initial Prize topology.

A second useful direction is to combine this exact Prize-state model with `tools/discard_gate_probability.py`, because a recovery line can exist in the Prize topology while the connector needed to reach Gladion or the target line is discard-gated or otherwise low-AMR.
