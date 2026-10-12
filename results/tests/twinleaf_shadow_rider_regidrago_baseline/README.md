# Shadow Rider versus Regidrago: first executable headless cross-archetype baseline

## Question and design

Can the repository's full [2026 Aichi champion Shadow Rider Calyrex VMAX](../../decks/shadow-rider-calyrex/) and [2026 Aichi tenth-place Regidrago VSTAR](../../decks/regidrago-vstar/) references complete actual games against each other in pinned Twinleaf, using identical seed labels with both player-seat assignments?

The original 60-card tournament-derived English-print manifests were mapped without silent substitutions by `simulation/twinleaf/tournament-deck-loader.cjs`. These physical lists have independent legality evidence in [the deck baseline audit](../../competitive_deck_baselines/). The game environment is *paper Expanded-inspired Twinleaf*, compiled at pinned upstream revision `3348ebdc898f175a2ed8f999133cd13d1afd01f5`; `SimpleTacticsAi` is a weak, unvalidated automated decision policy.

The headless runner uses native live `Store` actions, the research Fisher–Yates shuffle hook, separately seeded real-game and hypothetical-policy random lanes, 350-action and 25-second caps per game, and explicit player-index-to-deck winner attribution. A seed is replayed with both deck orientations. This controls the initial RNG seed and deck composition; it does not guarantee the two seats see identical physical opening cards or a balanced play policy.

- Shadow Rider sorted-deck SHA-256: `ec02fd642b9293793a17e6865d2554e43b9939c05fdd259d41e823f9a0873555`.
- Regidrago sorted-deck SHA-256: `2ad6d7d9bf536a16e1f2d237e344c90b919337296482dd4130f4560feaaf7ab0`.
- Replication: [manual workflow for chosen paired matchup](../../../.github/workflows/twinleaf-manual-matchup.yml), selected `shadow_rider` versus `regidrago`, seeds `20261012`, `20261013`, `20261014`.
- Raw logs: [run 38293750862](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293750862) (first seed) and [run 38293905086](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293905086) (other two seeds). Both workflows completed successfully.

## Results from these six model games

| Seed | Seat 1 | Seat 2 | Winner | Finished at turn | Dispatched attacks | Regidrago Prizes remaining |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 20261012 | Shadow Rider | Regidrago | Shadow Rider | 20 | 12 | 6 |
| 20261012 | Regidrago | Shadow Rider | Shadow Rider | 37 | 11 | 6 |
| 20261013 | Shadow Rider | Regidrago | Shadow Rider | 34 | 3 | 6 |
| 20261013 | Regidrago | Shadow Rider | Shadow Rider | 21 | 8 | 6 |
| 20261014 | Shadow Rider | Regidrago | Shadow Rider | 26 | 9 | 6 |
| 20261014 | Regidrago | Shadow Rider | Shadow Rider | 59 | 15 | 6 |

**Observed model outcome:** Shadow Rider 6 decided wins, Regidrago 0. All six traces reached the engine's `FINISHED` phase, with zero errors, draws, action caps or wall caps. Regidrago never collected any Prize cards in this sample. That is a concerning policy/implementation diagnostic. It can reflect inability to progress with the native bot, attack and Energy sequencing failures, failure to evolve or select useful Dragon-copy payloads, or other simulator limitations. The aggregate `attacks` column counts both players' dispatches and alone cannot settle which explanation is correct.

These results are **not empirical paper Expanded match win rates**. Six correlated seed-paired traces, no human-competitive AI, no diverse opponent field, and incomplete audit of all engine-implemented interactions prevent concluding that Shadow Rider is universally favored. The result is also insufficient to validate a 6-0 matchup forecast even *within Twinleaf* beyond these fixed seeds/policy conditions.

## First source-grounded action breakdown

The expanded live runner with mutation-safe action and Prize telemetry passed [manual CI 38294204546](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38294204546) at research revision `b0dbbdf7bebed0b3c21fda8f6c083c53185bdca3`, replaying seed 20261012 with both orientations. The telemetry SFT passed on the same run.

| Player deck | Seat orientation | Native attacks used | Ability activations recorded | Passed turns | Retreat actions |
| --- | --- | --- | --- | ---: | ---: |
| Shadow Rider | seat 1 | Shadow Mist ×1, Max Geist ×8 | Resetting Hole ×1; Underworld Door ×1 | 1 | 0 |
| Regidrago | seat 2 | Celestial Roar ×2, Itchy Pollen ×1 | none | 7 | 5 |
| Regidrago | seat 1 | Celestial Roar ×1, Apex Dragon ×1 | Legacy Star ×1 | 16 | 3 |
| Shadow Rider | seat 2 | Shadow Mist ×5, Max Geist ×4 | none | 10 | 0 |

The Regidrago bot used `Apex Dragon` only **once across the two seed-20261012 games**, despite drawing or playing many setup cards, and had no Prizes in either game. The seat-2 Regidrago game has no recorded Regidrago VSTAR hand-to-play evolution; seat-1 Regidrago did play the VSTAR and use Legacy Star, but still attacked with Apex Dragon only once. Meanwhile the Shadow Rider bot completed four Prize-taking transitions in the first orientation (2, 2, 1, 1 Prizes), and three two-Prize transitions in the other. Its victory in the second orientation required no recorded Underworld Door activation.

These observations narrow the reason the six-game result cannot validate real competitive superiority: the current `SimpleTacticsAi` makes little productive use of the Regidrago VSTAR attack-copy engine. We have **not** yet independently validated every selected copied-attack target or classified each pass as forced versus discretionary. Counting attempts that successfully dispatch also does not imply every copied attack dealt positive damage.

## Follow-up

A mutation-safe per-seat telemetry adapter, `simulation/twinleaf/match-action-telemetry.cjs`, with independent SFT and live integration has been added to record attack names, Abilities, cards played and Prize transitions without consuming RNG. Inspect its next pinned CI trace for missing Regidrago setup/attack behavior, then implement strategy-aware decisions or targeted engine card validations as necessary. Preserve the exact simulation conditions when comparing revisions.

Evidence type: observed headless engine traces and verified source decklists. Confidence in the six recorded terminal statuses is high; confidence in competitive strength inferred from them is low.
