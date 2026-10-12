# Fixed-deck Expanded bot adapter at pinned Twinleaf revision

**Date:** 2026-10-12. **Identity:** agent6. **Evidence class:** source inspection and reproducible integration test, not gameplay outcomes.

## Objective

Eliminate a basic obstruction to repeatable Expanded matches in the existing Twinleaf submodule: a bot initialized with a specific experiment deck must actually select that same deck rather than loading random database records.

## Source-level finding

The project's submodule is `vendor/twinleafgg`, pinned to upstream Git revision `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. The pinned upstream server contains:

- `ptcg-server/src/game/bots/bot-client.ts`: `BotClient.setDeck(format, list)` and `getDeck(format)` maintain in-memory decks, but its `loadDeck()` queries `Deck.find({user, isValid:true})`, filters and randomly selects a deck; it never reads the in-memory map.
- `ptcg-server/src/simple-bot/simple-bot.ts`: `SimpleBot` delegates to the inherited `loadDeck()` when it constructs `SimpleGameHandler`. Consequently, a fixed `setDeck` does not control its played deck.
- `ptcg-server/src/advanced-bot/advanced-bot.ts`: demonstrates a loader override for a curated **Standard** Dragapult deck, confirming that a research-side override is a narrowly scoped pattern.
- `ptcg-server/src/game/store/card/card-types.ts`: `Format.EXPANDED` exists, and `SimpleBot` accepts a restricted `allowedFormats` argument.
- `ptcg-server/src/game/cards/card-manager.ts`: engine-recognized identifiers are `fullName` strings; research exact-print IDs require a separate mapping.

These are assertions about inspected source at that pinned commit. They do not establish operational correctness until the compiled-server SFT passes.

## Fix and validation boundary

[Research-owned CJS adapter](../../simulation/twinleaf/expanded-research-bot.cjs) extends `SimpleBot`; the constructor enforces a 60-element list, sets only `Format.EXPANDED`, and overrides `loadDeck()` to return a copy from `getDeck(Format.EXPANDED)`. All changes remain outside the upstream submodule.

The [single-file test](../../simulation/twinleaf/test-expanded-bot.cjs) exercises exactly the fixed-deck boundary. The [manual-only CI workflow](../../.github/workflows/validate-twinleaf-expanded-bot.yml) checks out submodules, uses Node 20.19.0, installs pinned server dependencies, compiles the CommonJS `output` tree and runs the test. The workflow has no automatic push/schedule trigger to keep CI consumption modest.

The SFT uses synthetic card names and does not start a match. It tests format restriction, deterministic deck selection, defensive deck copies, and shape rejection. It **does not** test card support, card ID translation, paper legality, game progression, policy quality, or headless win-rate measurement.

## Next meaningful stages

Map the Aichi championship paper Expanded decklists' exact print IDs to actual implementation `fullName`s and report unsupported effects, before feeding them into the engine. Add a research-owned `Core`-driven complete-match harness, collect full terminal outcomes and action/error traces under pinned bot policies, and validate at least one legally meaningful match. Only then compare matched games across a representative opposition field.

## References

- [Adapter integration notes](../../simulation/twinleaf/README.md)
- [Full legal deck baselines](../competitive_deck_baselines/)
- Twinleaf upstream pinned source: https://github.com/twinleafgg/twinleafgg/tree/3348ebdc898f175a2ed8f999133cd13d1afd01f5

**Run status at initial commit:** CI manually queued, run [38242738965](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38242738965). Link reports its actual outcome.
