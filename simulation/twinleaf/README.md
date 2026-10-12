# Twinleaf research integration: fixed-deck Expanded bot

**Status: minimal fixed-deck adapter; no reproducible competitive match runner yet.**

The repository vendors Twinleaf as a Git submodule at `vendor/twinleafgg`, pinned on 2026-10-12 to Git commit `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. `.gitmodules` gives the upstream remote `https://github.com/twinleafgg/twinleafgg.git`. The research-owned integration in this directory does not patch or send contributions to upstream.

## Why the adapter is needed

At the pinned revision, `ptcg-server/src/game/bots/bot-client.ts` implements `BotClient.setDeck(format, list)` and `getDeck(format)`, but its default `loadDeck()` loads one random valid deck owned by the bot's database user. `SimpleBot` inherits that database-based loader even when a specific deck was assigned to the bot. `AdvancedBot` already overrides its loader for a particular curated **Standard** list, so that class is not a generic Expanded alternative.

`expanded-research-bot.cjs` subclasses the compiled `SimpleBot`, restricts its format to `Format.EXPANDED`, and overrides `loadDeck()` to return a fresh copy of the exactly supplied 60-entry deck. This leaves Twinleaf's action-selection `SimpleTacticsAi`, `SimpleGameHandler`, and game engine untouched. It deliberately preserves Twinleaf SimpleBot's current policy, which has **not** been shown to play competitively.

Each deck entry must be an actual Twinleaf **fullName** identifier recognized by `CardManager`. The printable card database IDs used by our [Aichi 2026 paper decklists](../../results/competitive_deck_baselines/) (e.g. `sm5-100`) are **different identifiers** and are not automatically translated by this adapter. The adapter checks array length and identifier string shape. It does not certify any deck's legal card composition, card implementation coverage, or playability.

## Reproduction

Pinned Twinleaf's `ptcg-server/tsconfig.json` emits CommonJS JavaScript into `ptcg-server/output` after installing its Node dependencies and running TypeScript compilation. Use Node.js 20.19.0 from upstream `.nvmrc`. The CommonJS adapter intentionally imports from that compiled output. Its single-file regression is:

`simulation/twinleaf/test-expanded-bot.cjs`

The SFT uses 60 **synthetic** labels, never dispatches a game, and requires no game-server database. It verifies deterministic deck loading, copy isolation, enforced Expanded-only formats, and early rejection of malformed lists. It must be run after compiling the pinned server.

A **manual-only** [GitHub Actions workflow](../../.github/workflows/validate-twinleaf-expanded-bot.yml) installs the pinned submodule dependencies, compiles the exact pinned server, and executes the SFT. It intentionally has no push trigger to control CI budget.

## Next integration stages

1. Build a reliable mapping from each legal paper Expanded exact-print decklist to existing Twinleaf `fullName` implementations, and report missing or semantically divergent cards before constructing matches.
2. Add research-owned game/client orchestration using pinned `Core.createGameWithDecks`, explicit `GameSettings.format = Format.EXPANDED`, two controlled clients, termination checks through `State.phase` and `State.winner`, and deterministic experiment metadata. The `SimpleBot` policy's tactics and prompts need explicit legality/error auditing.
3. Execute and archive complete headless matches with paired seeds, both starting-player orientations, action traces, error flags, engine pin, bot policy and decklist hashes. Test reproducibility and edge cases before treating results as comparative evidence.
4. Implement periodic reviewable submodule update checks and regression gating without silently updating the submodule in live experiments.

A compiled source tree and passing fixed-deck SFT alone establish **none** of the win probabilities required by the project's main objective. No published head-to-head match data is claimed here.
