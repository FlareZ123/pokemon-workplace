# Regidrago: initial Dragon attack payload Prize coverage

## Source and question

The published 2026 Aichi 10th-place Regidrago VSTAR 60-card list in `results/competitive_deck_baselines/regidrago_haruku_2026.json` contains five one-copy Dragon attack payloads: Basic Dialga-GX (`sm5-100`), Koraidon ex (`sv5-120`), Kyurem (`sv6pt5-47`); Stage 2 Dragapult ex (`sv6-130`); and Hisuian Goodra VSTAR (`swsh11-136`). It also contains 12 other Basics (15 total) and one Hisuian Heavy Ball (`swsh10-146`). The bundled print text confirms Dragon typing and that Heavy Ball exchanges for a **Basic Pokémon** in the initial Prize cards; it cannot directly rescue either Evolution payload.

Question: How frequently are all five attack-source **card identities** outside initial Prizes, how much can a naturally observed Heavy Ball repair missing Basics, and what inventory coverage does one extra source copy buy?

## Exact model and reproducibility

Uniform 60-card deck, valid seven-card starting hand containing at least one Basic, six initial Prizes, followed by the first natural draw. All five named payload types, the single Heavy Ball, 12 unnamed Basics, and 42 unnamed non-Basic cards are partitioned exactly. A payload type is *covered* when at least one physical copy is outside the initial Prizes, or when all copies are Prized but that payload is a Basic and Heavy Ball is observed in the first eight cards. One Heavy Ball can recover **one** missing Basic payload type, so a five-type simultaneous objective cannot use it to fill two absent types.

Compute exact multivariate hypergeometric mass for every Prize composition, conditioning on valid openings. Reversing the dealing order is distribution-preserving: after six Prizes, if S Basics remain, there are `C(54,7)-C(54-S,7)` accepted opening hands. If Heavy Ball is unprized, its first-eight-card visible numerator over the 47 equiprobable natural draws is `47*[C(53,6)-C(53-S,6)] + [C(53,7)-C(53-S,7)]`. Composition multiplicities are products of binomial coefficients. The implementation uses exact Python integers and `Fraction`, with no Monte Carlo approximation.

- Reusable solver: `tools/prize_payload_frontier.py`.
- Independent physical-card oracle: `results/regidrago_payload_prize_coverage/reproduce.py`. This enumerates individually labeled opening hands, Prizes, and natural draws for three twelve-card toy configurations and matches every reported output exactly, then checks 60-card identities.

## Published-list results

| Inventory event, conditional on a valid starter | Probability |
| --- | ---: |
| All five attack types have at least one copy outside initial Prizes | **58.186828992%** |
| All five types are covered allowing one naturally observed Heavy Ball rescue | **60.840563509%** |
| Timeless-GX and Phantom Dive are jointly covered allowing Heavy Ball | **82.121695037%** |
| Heavy Ball is in the opening hand or the first natural draw | **12.825314878%** |
| A particular single-copy Basic Dragon is initially Prized | **9.824147458%** |
| A particular single-copy Evolution Dragon is initially Prized | **10.058617514%** |
| A particular Basic singleton is Prized and Heavy Ball is naturally available to rescue it | **1.277520770%** |

The 60.84% figure describes an unusually demanding *five-source inventory* endpoint; games need different attacks in different matchups. Heavy Ball is credited optimistically when it is visible and can be played, but physical discard access and attack execution are outside this model. No information here establishes a setup completion probability or tournament win rate.

## One-slot structural duplication sensitivity

Each variant adds one copy of the named payload by replacing an **unspecified non-Basic filler**. These remain 60-card category models, not fully proposed playable replacements. Duplicating a Basic changes total starter count from 15 to 16, and therefore changes the accepted-opening prior.

| Extra copy | Five-type coverage | Delta from published | Timeless-GX + Phantom Dive coverage | Delta |
| --- | ---: | ---: | ---: | ---: |
| None | 60.840564% | baseline | 82.121695% | baseline |
| Dialga-GX | 66.404852% | +5.564288 pp | 89.284196% | +7.162501 pp |
| Koraidon ex | 66.404852% | +5.564288 pp | 82.107600% | -0.014095 pp |
| Kyurem | 66.404852% | +5.564288 pp | 82.107600% | -0.014095 pp |
| Dragapult ex | **67.466769%** | **+6.626205 pp** | **90.646307%** | **+8.524612 pp** |
| Hisuian Goodra VSTAR | **67.466769%** | **+6.626205 pp** | 82.121695% | 0 pp |

The tiny loss in paired-source coverage when adding an unrelated Basic arises entirely from the changed valid-start conditioning. It does not show that the added card is worse strategically. Adding a second Dragapult improves the pair chiefly because the original Stage 2 singleton has no Heavy Ball rescue. Yet the cost of replacing a specific Trainer could exceed this availability benefit. Draw, Battle Compressor loading, Energy attachments, opponent locks, prize-taking, and matchup need remain unmodeled.

## Next decision test

Select a specific proposed 60-card substitution, then compare real resource costs and play lines. In particular test second Dragapult versus the removed Item, tracking whether Phantom Dive is required in the matchup, whether the attack source actually reaches discard, and whether Apex Dragon is powered on time. Treat the current result as an exact inventory ceiling for those deeper experiments.
