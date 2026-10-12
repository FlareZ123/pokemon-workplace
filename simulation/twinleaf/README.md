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

## Print-level coverage diagnostic

[Conservative print matcher](print-coverage.cjs) and its [SFT](test-print-coverage.cjs) read both published 2026 Aichi 60-card baselines directly from the results entry point and the `resources/sets/en.json` print-to-PTCGO code catalog. They compare each paper (set, collector number, printed name) triple with the card metadata that the **pinned compiled Twinleaf registry** exports. An exact match yields the engine `fullName`. A matching set/number with a differing name is flagged for review, while missing print IDs and unresolved set codes are reported separately. No replacement print is silently treated as equivalent. This detects existence and basic print identity only; effects and legality still require separate verification.

## Next integration stages

1. Resolve the coverage diagnostic's unmatched and name-mismatched Aichi prints, including explicit source reviews of semantically equivalent reprints where appropriate, before constructing actual game decks.
2. Add research-owned game/client orchestration using pinned `Core.createGameWithDecks`, explicit `GameSettings.format = Format.EXPANDED`, two controlled clients, termination checks through `State.phase` and `State.winner`, and deterministic experiment metadata. The `SimpleBot` policy's tactics and prompts need explicit legality/error auditing.
3. Execute and archive complete headless matches with paired seeds, both starting-player orientations, action traces, error flags, engine pin, bot policy and decklist hashes. Test reproducibility and edge cases before treating results as comparative evidence.
4. Implement periodic reviewable submodule update checks and regression gating without silently updating the submodule in live experiments.

A compiled source tree and passing fixed-deck SFT alone establish **none** of the win probabilities required by the project's main objective. No published head-to-head match data is claimed here.


## Seeded live Store smoke: first completed match

The independently tested [\`headless-smoke.cjs\`](headless-smoke.cjs) extends the integration by executing **an actual complete headless match**, independently of the fixed-deck adapter above. It runs the upstream TypeScript \`Store\`, \`AddPlayerAction\`, card classes, \`SimpleTacticsAi\`, and \`BotArbiter\` in memory. It uses \`ts-node/register/transpile-only\` from pinned server dependencies, without building a WebSocket server, database, or modifying the upstream code.

The smoke deck for **each** player is deliberately simplistic: four Regidrago V SIT, 28 BLW Grass Energy, 28 BLW Fire Energy. These are legal-size engine fixtures, not tournament lists or strategic candidates. The script asserts the exact pinned upstream SHA and a normal \`Format.EXPANDED\` game, seeds \`Math.random\` with 20261012, dispatches all bot/prompt actions through the live Store, and returns JSON with phase history, turns, actions, attacks, winner and a \`finished\` or \`action_limit\` status. It bounds execution at 1,000 dispatches.

**Observed pinned-revision CI outcome**, [run 38242872905](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38242872905): \`finished\`, **43 actions**, **6 turns**, **5 attacks**, \`winner=0\`, actual pinned engine revision \`3348ebdc898f175a2ed8f999133cd13d1afd01f5\`. Workflow \`.github/workflows/twinleaf-headless-smoke.yml\` runs this single seeded smoke in bounded Ubuntu CI.

A real integration obstacle was discovered and resolved: recursive GitHub checkout of the upstream dependency fails because its nested \`vendor/pokemon-cards-css\` submodule has no matching URL in the upstream \`.gitmodules\`. The workflow initializes only the known first-level \`vendor/twinleafgg\` submodule and verifies its actual pinned SHA before running. This reproducibly avoids the malformed nested pointer without touching upstream.

This proves that one instrumented, complete game can execute headlessly through the pinned engine. The naive SimpleBot policy and all-Energy filler decks make the recorded winner and turn count **unsuitable for estimating paper Expanded deck strength**. Further work should translate full-paper card manifests to implemented Twinleaf class identifiers, validate semantic coverage, run real tournament reference decks under stronger decision policies, and pin seeds plus paired seat orientations for fair match comparisons. This smoke does not yet imply that the engine accepts the source-verified Aichi Shadow Rider, Vileplume, or Regidrago lists in full.

## Preflight audit for playable Aichi decks

The manual-only `validate-twinleaf-expanded-bot.yml` workflow now runs `test-tournament-print-audit.cjs` after compiling the pinned engine. The research-side `tournament-baselines.cjs` reads the four complete 60-card English print lists from `results/competitive_deck_baselines/README.md` (Vileplume, Shadow Rider, Regidrago and Mew Genesect). The `tournament-print-audit.cjs` module performs a strict triple lookup `(set code, set number, printed card name)` against compiled Twinleaf set implementations, then checks attack names in order and the presence of printed Ability names among engine powers.

The resulting workflow artifact `twinleaf-print-coverage.json` reports every source-print mismatch, missing print, ambiguous engine print and code-mapping failure, with distinct-print and physical-copy coverage per deck. It deliberately does **not** auto-substitute another printing, presume that a matching name implies correct effects, or announce head-to-head strength. A successful preflight only establishes that the exact list can be mapped to candidate engine card implementations. Actual matches additionally require behavior audits, strategy policies, and consistent format setup.

## Seeded physical-game RNG isolation from bot lookahead (2026-10-12)

The bounded 60-card match runner now uses the research-only [RNG stream ledger](random-stream-ledger.cjs) with a separate seeded lane for physical game actions and speculative `SimpleTacticsAi` evaluation. This closes a verified replay-sequencing defect: the original runner let speculative policy evaluations consume the live seeded shuffle/coin stream. In one pre-fix Mega Absol diagnostic, **662 of 793** draws occurred inside policy evaluation.

The [standalone SFT](test-random-stream-ledger.cjs) proves that 700 speculative draws cannot change the next physical-game draw; the fully compiled pinned-engine [CI run 38292013716](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292013716) passed. The runner reports `random_stream_policy`, `game_random_calls`, `policy_random_calls`, and `random_sources` alongside deck hashes, shuffle hook, and seed. Read the [evidence and pre/post data](../../results/twinleaf_rng_stream_isolation/) before using or comparing any recorded diagnostics.

**Still unsupported:** treating `SimpleTacticsAi` as a competitive Expanded policy; full card-semantic parity; fair matchup win-rate estimates. The bot's counterfactual default arbitration is all-heads/no-shuffle, unlike the physical random game. Results from earlier shared-RNG traces must not be pooled with separated-RNG traces as matched replicates.


## Manual controlled tournament matchup diagnostics

The manual-only [`validate-twinleaf-expanded-bot.yml`](../../.github/workflows/validate-twinleaf-expanded-bot.yml) now accepts a choice of two distinct **strictly mapped** Aichi 60-card benchmark decks: `vileplume`, `shadow_rider`, `regidrago`, and `mew_genesect`. Choose up to three distinct unsigned 32-bit seeds in a comma-separated string. Each seed produces two games with the decks swapping player seats; `tournament-probe-settings.cjs` rejects unknown decks, duplicate selections, invalid seeds and over-budget input before any games run. Limits remain 350 engine actions and 25 seconds per game, for at most six games in one manual dispatch. There are no per-commit triggers.

The report contains the exact deck multiset SHA-256 hashes, original and swapped seat assignments, Twinleaf revision, shuffle and RNG stream policies, raw game traces and an explicit `paired_results` census. The [`paired-result-summary.cjs`](paired-result-summary.cjs) assigns winners to the actual deck in the seat: the pinned Twinleaf `GameWinner` enum is `PLAYER_1=0`, `PLAYER_2=1`, `DRAW=3` and `NONE=-1`. Completed draws never count as wins, while time/action caps remain censored and bot/engine errors are auditable. Invalid terminal statuses fail the manual integration checks. Two dependency-free SFTs are [`test-paired-result-summary.cjs`](test-paired-result-summary.cjs) and [`test-tournament-probe-settings.cjs`](test-tournament-probe-settings.cjs).

The [seed-paired Vileplume versus Mew example](../../results/tests/paired_engine_outcome_audit/) demonstrates why `winner:0` in two seat-swapped games means **one win for each deck**. The low-quality native policy, finite wall/action limits, and incomplete cross-card engine semantic audits preclude field-wide competitive win-rate claims. Preserve the distinction between executable headless diagnostics and real paper Expanded evidence.
