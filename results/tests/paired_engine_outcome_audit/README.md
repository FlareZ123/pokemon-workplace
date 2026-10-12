# Seat-aware outcome attribution for pinned Twinleaf tournament diagnostics

## Question

When the same pair of 60-card paper Expanded reference decks trade player seats under one fixed random seed, how should a headless game's raw winner value be interpreted? How should action/time caps and bot/engine errors affect reports?

## Source game evidence, October 12, 2026

The manual [Twinleaf tournament adapter CI run 38291450937](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38291450937) at research revision `4bdbbb970c2122a67ec4ce52e646f0487edf9c69` used upstream Twinleaf commit `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. It ran two headless games with the exact 60-card [Aichi Vileplume control and Mew Genesect English-print benchmarks](../../competitive_deck_baselines/README.md), native `SimpleTacticsAi`, a research-owned Fisher–Yates shuffle, seed `20261012`, and a 350-action/25-second cap per game.

| Seed | Player 1 deck | Player 2 deck | Raw `winner` | Attributed winning deck | End state | Actions | Turn | Prizes left by player 1 / 2 |
| --- | --- | --- | ---: | --- | --- | ---: | ---: | --- |
| 20261012 | Vileplume | Mew Genesect | 0 | Vileplume | finished | 271 | 40 | 0 / 5 |
| 20261012 | Mew Genesect | Vileplume | 0 | Mew Genesect | finished | 180 | 36 | 0 / 6 |

**Direct observation:** player index 0 won both recorded games, while the deck occupying that seat changed. Therefore the two-game deck-attributed score is Vileplume 1, Mew Genesect 1. Neither is evidence of a field-wide 50% matchup win probability. Seat-specific starting policy, the native bot's limitations, and different random draw consumption can dominate such a tiny experiment. These are diagnostics of the executable environment, not rigorous paper-game outcomes.

## Reproducible safeguard

- [`simulation/twinleaf/paired-result-summary.cjs`](../../../simulation/twinleaf/paired-result-summary.cjs) joins each trace to its specific seed, pair, and seat orientation; interprets winner indices `0` and `1` through the actual seat assignment; keeps `winner_deck` separate from `raw_winner_index`.
- The summary explicitly distinguishes a decided game from an action/time-censored game, a bot/engine error, and an unclassified terminal outcome. Undecided games never inflate deck win counts. Errors must be surfaced rather than silently counted as successful diagnostics.
- The [standalone SFT](../../../simulation/twinleaf/test-paired-result-summary.cjs) checks both seat orientations, opposite-winner examples, censoring, dispatch errors, seed mismatches, invalid statuses and incomplete orientation pairs. It runs without the Twinleaf dependency.
- [`tournament-bounded-match.cjs`](../../../simulation/twinleaf/tournament-bounded-match.cjs) incorporates the summary and flags engine/bot errors in manual [integration CI](../../../.github/workflows/validate-twinleaf-expanded-bot.yml). When the last permitted action finishes the game, its status is normalized from a cap to `finished`.

## Limits and next decisions

Both source decks have independently checked construction and plausible exact-print mappings, but this is not an audit of every simulator card effect or a competitive policy. The 2026-10-12 paired games were generated before the subsequent live-game-vs-policy random stream separation, so cross-revision performance comparisons must account for that change. Future matchup experiments should retain explicit seat attribution, record unresolved-game denominators, use several paired seeds, pin both engine and research commits, and distinguish stronger decision-policy results from this native-bot baseline.

This finding is about **measurement validity**, with an illustrative two-game engine trace. It does not demonstrate that either tournament deck is stronger.
