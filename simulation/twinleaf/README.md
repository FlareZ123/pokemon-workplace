# Twinleaf research integration: fixed-deck Expanded bot

**Status: minimal fixed-deck adapter; no reproducible competitive match runner yet.**

The repository vendors Twinleaf as a Git submodule at `vendor/twinleafgg`, pinned on 2026-10-12 to Git commit `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. `.gitmodules` gives the upstream remote `https://github.com/twinleafgg/twinleafgg.git`. The research-owned integration in this directory does not patch or send contributions to upstream.

## Critical policy blocker: hidden-order oracle (2026-10-12)

The pinned native `SimpleTacticsAi` evaluates Items against an authoritative cloned `State` containing the real, unrevealed deck order. A [60-card-conserving exhaustive regression](../../results/tests/twinleaf_hidden_topdeck_oracle/) demonstrates that it plays Pokégear 3.0 and tournament-relevant Trainers' Mail exactly when the secret top-seven or top-four search will hit a Supporter, while preserving the Item on hidden misses. In all 92 fixed-world tests, the Item choice differed according to hidden order. [CI evidence](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38301578059) also captures native score distortions.

The headless runner now emits `policy_hidden_information: unmasked_native_SimpleTacticsAi_order_oracle` in every trace and aggregate report. **Do not use these native-bot match outcomes to rank actual paper Expanded decks.** Stream-separated RNG, rules hooks and exact card mappings do not repair hidden-information decision leakage. A truly observation-consistent policy and comprehensive card-semantic audit remain needed.

## Corrected native Supporter planning counter (2026-10-12)

Pinned `SimpleTacticsAi` prematurely mutates `player.supporterTurn` while choosing Supporter actions, causing a legal Boss's Orders to raise `SUPPORTER_ALREADY_PLAYED` on live Store dispatch. This is verified with a [complete 60-card-conserving engine fixture](../../results/tests/twinleaf_supporter_policy_mutation/). The [manual CI regression](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302379592) confirms that restoring the counter before dispatch allows the same card to resolve legally, including exception-safe restoration.

The live match runner installs a research-owned `supporter_selection_live_counter_restore_v1` policy guard and reports its activation counts via `policy_repair_stats`. It does not edit the pinned vendor. Outcomes from pre-fix and post-fix policy versions are distinct experiments. The independent hidden-order decision oracle described above remains, so these results are still **engine diagnostics**.

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


## Independently bounded deck-candidate and bot-policy probes

The focused, **manual-only** [`twinleaf-manual-matchup.yml`](../../.github/workflows/twinleaf-manual-matchup.yml) builds the pinned engine and runs independent SFTs before dispatching at most six games. It includes the four fully mapped tournament lists plus two separate paper Expanded 60-card experiments implemented by [`candidate-deck-loader.cjs`](candidate-deck-loader.cjs): `mew_genesect_vip4` (+1 source-print Battle VIP Pass / -1 Special Red Card) and `regidrago_dragapult_2` (+1 source-print Dragapult ex / -1 Battle VIP Pass). Each source tournament deck remains unchanged, and the [candidate-loader SFT](test-candidate-deck-loader.cjs) asserts exact one-card identity difference and pinned card availability.

Bot `tactic_order` can be `native`, `attack_before_retreat`, `vip_first`, or `vip_attack_before_retreat`. The [research-only ordering adapter](tactic-order-policy.cjs) swaps the upstream Attack and Retreat constructor order, while [`vip-first-tactic.cjs`](vip-first-tactic.cjs) attempts a native `PlayCardAction` for a held Battle VIP Pass when the first-turn window and Bench space permit. All effects and game rules still come from pinned Twinleaf. Their standalone SFTs check eligibility and no mutation of the upstream constructor array.

The enhanced live trace now includes the original physical deck fingerprints, explicitly decoded deck winners, censored games, each player's first-turn hand at its first player action, named attack/Ability/played-card counters, Prize transitions, terminal Active and Bench identities, deck counts, and last native game logs. Source code: [`match-action-telemetry.cjs`](match-action-telemetry.cjs) and [its mutation-safety SFT](test-match-action-telemetry.cjs).

Interpreting the trace still requires caution. [Shadow Rider vs Regidrago](../../results/tests/twinleaf_shadow_rider_regidrago_baseline/) was 6–0 with native bot; on the same two seed pairs, [moving AttackTactic before RetreatTactic](../../results/tests/twinleaf_tactic_order_sensitivity/) changed a 4–0 native subset to 2–2, including a Regidrago win by opponent deck-out without Regidrago attacking. In the [Mew VIP4 mirror study](../../results/tests/mew_vip4_headless_counterfactual/), native bot played no VIP Pass in four games; the explicit VIP-first policy played six copies in the same four seat/seed positions and hit one wall cap. These are simulator/policy validity diagnostics, **not evidence of competitive superiority**.

## Live Underworld Door rules guard (Agent 43, 2026-10-12)

The bounded tournament match runner now **installs the existing research-owned Underworld Door target guard in each `runOne` call**, before any gameplay dispatch. This closes a prior integration gap: the separate card-level SFT had demonstrated an invalid non-Psychic attachment in pinned Twinleaf, but manual match probes had continued to run without the guard. Match traces and aggregated reports include `engine_hooks: ["shadow_rider_underworld_door_guard_v1"]`.

The [live-path integration SFT](test-tournament-engine-hooks.cjs) uses a two-action real-engine fixture and is enforced before matches in both manual workflows. The [card-level target SFT](test-underworld-door-targets.cjs) remains the source-backed semantic check. Detailed findings and replay restrictions are in [the focused research result](../../results/tests/twinleaf_underworld_live_hook/).

**Do not pool older Shadow Rider headless results with new guarded results as equivalent replications.** Earlier unguarded traces may have contained invalid Energy-attachment opportunities, though no claim is made that a specific old game exercised them. The guard improves one verified rules boundary without validating the bot's strategy, the remaining cards, or overall matchup win probabilities.


## Scheduled upstream revision review

The [Twinleaf upstream review workflow](../../.github/workflows/twinleaf-upstream-review.yml) checks the committed gitlink against upstream main weekly at 05:37 UTC on Mondays and on manual dispatch. Unchanged revisions cause only a lightweight discovery job. If a new revision is found, it fetches only the first-level submodule, compiles with the candidate's Node version, and runs selected compatibility tests before proposing a draft branch/PR. The working default-branch pin is never silently updated. A draft proposal still requires review of behavioral correctness, hooks and hardcoded engine SHA constants before merge.

Read [the maintenance procedure and limitations](../../results/tests/twinleaf_upstream_review/) before reviewing or enabling a proposed update. The new revision path and repository-token PR permissions have not yet been exercised; at the 2026-10-12 check, upstream main matched the pinned SHA.

The bounded matchup runner also emits censor-aware [paired score bounds](../../results/tests/paired_score_bounds/) by deck and engine seat. They are reporting diagnostics: a seat-swapped seed pair is one statistical unit, and native bot outcomes are not validated paper Expanded win probabilities.

## Regidrago Celestial Roar full-Energy correction (Agent 43, 2026-10-12)

The pinned Regidrago V SIT implementation incorrectly discards revealed **Special Energy** during `Celestial Roar`, despite the attack requiring attachment of **any Energy card** revealed among the top three. The published Aichi 10th-place Regidrago VSTAR list contains four Double Dragon Energy, so the issue materially changes some physically possible game states.

The research-owned, idempotent [`regidrago-celestial-roar.cjs`](hooks/regidrago-celestial-roar.cjs) installs inside every bounded tournament match via `ensureResearchEngineHooks`. It attaches every revealed Energy to the attacking Dragon Pokémon, retains exact source-card identity, and discards each non-Energy card. The original upstream gitlink remains untouched. Every trace and aggregate summary now labels both the Regidrago correction and the earlier Shadow Rider Underworld Door target guard.

The focused [source-pinned attack regression](test-regidrago-celestial-roar.cjs) verifies the old defect, mixed Basic/Special and all-Special reveals, idempotence and short-deck behavior. The [native full Store regression](test-regidrago-celestial-roar-store.cjs) confirms the resulting Double Dragon Energy produces two ANY units in the actual engine's provided-Energy map. Both passed [manual CI 38301157584](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38301157584); the prior bounded matchup plus focused SFT passed [38300711450](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38300711450). The [source-print exact probability and methodology](../../results/tests/twinleaf_regidrago_celestial_roar/) give a separate 18.994739918% blind-three chance of at least one Double Dragon from the untouched 60, without pretending this is a conditional match-rate estimate.

**Version incompatibility:** match runs before these source-pinned guards were installed or those with different `engine_hooks` labels must not be pooled as if simulated under identical game rules. The native bot's private hidden-order oracle and tactical weaknesses are also independently documented by other agents; guard installation does not validate native match winners.
