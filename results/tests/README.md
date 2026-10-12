# Reproducible research tests: staged migration

This directory is the intended home for narrowly scoped rule verifications, exact probability models, independent physical-card oracles, setup-access simulations and mechanics regressions supporting [the curated Expanded deck directory](../decks/) and [the human results index](../README.md).

## First migrated and revalidated result

- **[Raichu Prize-aware Item payment frontier](raichu_target_payment_frontier/):** exact conditional probability of retrieving a singleton Alolan Raichu using physically payable Ultra Ball or Computer Search, including Gladion fallback when the target is Prized. Verified by six independent physical-identity toy enumerations and [passing Windows CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292324506). Strict access 30.578700%, conditional source-sacrifice access 33.390969%. These are bounded first-turn access measurements, not winning percentages.

## New engine measurement check

- **[Twinleaf seat-aware winner and censoring audit](paired_engine_outcome_audit/):** the pinned live-engine winner values identify player seats, so two `winner:0` outcomes with Vileplume and Mew swapping seats mean one game won by each deck. Independent SFTs verify correct deck attribution, `DRAW=3` accounting, censored and errored games, seed matching and both orientations. [Manual CI 38292409329 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292409329) for the core paired reporting and actual two-game headless runner. This is measurement validation, not tournament-grade matchmaking.

- **[2026 Aichi Raichu exact-print and Prize-energy proof](raichu_2026_print_validation/):** published fourth-place 60-name count audit and representative English Expanded print proof, plus source-grounded Extra Energy Bomb two-Prize transition and 5-card conditional Electro Rain ceiling (420 unmodified damage when behind, 120 when not). Both [Windows CI 38293458838](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293458838) checks passed. This is a legality/rules ceiling, not a setup frequency or match win rate.

## Migration policy

The owner has requested that roughly 964 pre-existing atomic studies now at `results/<study>/` be migrated gradually to `results/tests/<study>/`. Many existing workflow paths, Python imports, Markdown relative links, and other agents' memory or broadcasts still refer to those locations. Before moving a particular study:

1. Determine dependent scripts, CI and inbound references; preserve a redirect at the old path where necessary.
2. Move executable reproducers alongside the result; repair root-path traversal and Markdown relative links.
3. Validate the moved entry point with a reproducible Windows CI workflow and inspect the result.
4. Update curated deck synthesis pages only when the test directly affects a deck or shortlist decision.
5. Keep clear labels separating game rules, exact access results, simulations and tournament placements.

This is a staged relocation plan. The many still-existing `results/<study>/` directories have **not** all been migrated. Avoid claiming otherwise, and avoid bulk path changes that destroy reproducer access.

- **[Regidrago response and next-Energy-attachment frontier](energy_discard_response_reattachment/):** 48 exact physical attack-readiness cells checked with an independent Energy-slot backtracker, plus 66 exact hypothetical probability tests. Demonstrates when opponent Special Energy counters reverse the preferred Dragon Impact discard payment. No matchup win rates are inferred.
