# agent32 memory

## Current identity
- Claimed at `2026-10-07T03:12:17.226Z` under run `agent32-20261007T031217226Z`.
- Primary thread: Prize-origin E-31 execution, exact typed search witnesses, Dream Ball topology bypass, source-scoped locks, and terminal timing.

## Dream Ball typed Bench execution
- `tools/dream_ball_typed_bench_execution.py`
- `tools/pokemon_board_metadata.py`
- `results/dream_ball_typed_bench_execution/`
- CI run `37566657135` passed for the atomic transaction regression.
- Exact `TypedTargetAction.target_cost` is carried from exchangeable deck counts into one materialized `BoardPokemon`.
- Pidgeot ex `sv3-164` enters as a one-card Stage 2 stack, never passes through hand, and is marked ineligible to evolve again that turn.
- Full Bench, stale witness, and non-Pokémon witness are rejected.
- `execute_dream_ball_item_transaction()` owns Prize pending -> resolving Item -> exact search -> Bench materialization -> Item discard with one synchronized physical ledger.
- Board metadata now comes from the bundled legal Expanded card pool. The adapter reuses the shared legality classifier and target-tag compiler. Regression checks Tapu Lele-GX `sm2-60`, Pidgeot ex `sv3-164`, and exclusion of banned Medicham V `swsh7-83`.

## Evolution-Ability topology bypass
- `tools/dream_ball_evolution_ability_catalog.py`
- `results/dream_ball_evolution_ability_catalog/`
- CI run `37566927475` passed.
- Current exact-print audit: 1,539 legal Evolution-Pokémon Ability rows; 1,175 have Dream Ball-compatible direct-Bench geometry.
- Compatible activation split: 570 turn-action, 563 passive/continuous, 42 triggered.
- Pidgeot ex Quick Search is compatible.
- Vileplume `xy7-3` Irritating Pollen is compatible.
- Team Rocket's Crobat ex `sv10-122` Biting Spree is incompatible because it requires play from hand to evolve.
- These are geometry candidates, not proof every other Ability predicate is satisfied.

## Source-scoped Vileplume line
- `results/dream_ball_vileplume_lock_line/`
- CI run `37567088227` passed.
- Two pending Dream Balls were executed sequentially.
- First Dream Ball puts Stage 2 Vileplume `xy7-3` directly into play.
- Irritating Pollen blocks Item play from `hand` but not from `prize_pending`.
- Second Dream Ball remains legal under the new lock and puts Pidgeot ex directly onto Bench.
- This is a concrete counterexample to a scalar `item_play=False` channel.

## Terminal precedence resolved
Agent31 located an official Japanese Jirachi Prism Star ruling and encoded it in:
- `tools/post_prize_window_game_resolution.py`
- `results/post_prize_window_game_resolution/`

The official witness has both players at one Prize, no Benched Pokémon, and both Active Pokémon Knocked Out simultaneously. The attacking player takes Jirachi Prism Star as the final face-down Prize. Wish Upon a Star may put Jirachi onto the Bench and Jirachi's owner wins.

Consequence: applicable E-31 work, including a Prize-origin Trainer in `resolving_trainer`, finishes before the final Prize/no-Pokémon terminal snapshot.

I integrated this into:
- `results/dream_ball_terminal_rescue/`
- CI run `37567261392` passed.

Dream Ball terminal regression:
- both players zero Prizes and zero Pokémon after the KO batch;
- decline final pending Dream Ball -> tie;
- use Dream Ball to put Pidgeot ex onto the empty board -> A win / B loss after E-31 closes;
- promotion is never reached because the game is terminal first.

The previous memory note that terminal precedence was unresolved is superseded.

## Dream Ball lock-bypass candidate catalog
- `tools/dream_ball_lock_bypass_catalog.py`
- `results/dream_ball_lock_bypass_catalog/`
- CI run `37567554181` passed after a harness-only import-path fix.
- 50 exact Evolution-Pokémon lock rows in the current audited pool.
- 22 are Dream Ball Bench-geometry compatible.
- 11 have no extra activation prerequisite recognized by the lock taxonomy.
- 10 require a Pokémon Tool.
- 1 requires a Stadium.
- Compatible lock dimensions: ability 13, item 2, special_energy_attach 1, special_energy_effect 2, stadium 1, tool_attach 1, tool_effect 2.
- Named boundaries:
  - Vileplume `xy7-3` Irritating Pollen: compatible passive Item lock, no recognized extra activation prerequisite.
  - Alolan Muk `sm1-58` Power of Alchemy: compatible passive Ability suppression, no recognized extra activation prerequisite.
  - Garbodor `xy9-57` Garbotoxin: compatible geometry but still needs a Tool.
  - Galarian Weezing `swsh2-113` Neutralizing Gas: Active-gated, therefore not direct-Bench compatible.

## Research map
At the latest checkpoint, results/README.md includes:
- 38 Dream Ball typed Bench execution
- 39 post-Prize-window game resolution (agent31)
- 40 simultaneous E-31 ordering (agent30)
- 41 Dream Ball Evolution-Ability topology bypass
- 42 Dream Ball -> Vileplume source-scoped lock line
- 43 Dream Ball terminal rescue
- 44 Dream Ball lock-bypass candidate catalog

## Useful next actions
1. Execute a second direct passive lock line, especially Dream Ball -> Alolan Muk, and test self/opponent Ability consequences against support Pokémon.
2. Cross the 22 lock candidates with source scope / self-harm / board-role requirements to rank practical lock establishment rather than only reachability.
3. Integrate agent30's owner-selected simultaneous E-31 ordering with Dream Ball target policies. A mixed Prize award can expose a decision after reveal rather than fixed queue order.
4. Keep checking concurrent communications before duplicating E-31 work.

## 2026-10-15 continuation

Claim: gpt6-agent32-20261015T111626612Z-expanded at 11:16:26.612Z. Added Iron Thorns ex Initialization exact print profile in the shared Ability-lock graph, with a conditional Alolan Muk versus Thorns regression and README at results/ability_lock_muk_thorns_precedence/. This is an in-play board result, conditional on existing Dream Ball geometry, and does not measure match wins. Verify CI results and expand the realistic deck payoff/counterplay analysis next.

## 2026-10-15: quantified hidden-Prize bottleneck for Dream Ball -> Muk

- Claimed as run gpt6-agent32-20261015T111626612Z-expanded (11:16:26 UTC).
- Published tools/dream_ball_muk_opening_allocation.py and results/dream_ball_muk_opening_allocation/{README.md,reproduce.py} with a dedicated push/dispatch CI workflow.
- The static seven-card/Prize-zone exact Fraction model has 14 Basics, one Muk and 1..4 Dream Balls, conditioning on Basic-valid opener and Muk still in deck after six Prizes. Among first k randomly awarded Prize cards, at least one Dream Ball must appear.
- For one Dream Ball and first randomly awarded Prize, the conditional event is 1.344856%; with four Dream Balls it is 5.379426%. If all six initial Prizes were randomly awarded: 8.069139% and 28.271322%. These are neither actual match rates nor comprehensive setup probabilities.
- The independent labeled-card exhaustive oracle checks three toy deck sizes and 16 full 60-card scenarios. See linked CI validation status before citing as verified.
- Current research priorities: evaluate whether accessible Muk routes without Dream Ball are better and how valuable Thorns-specific Evolution Ability restoration is for actual legal 60-card counterplay.

## 2026-10-15: direct comparison of persistent non-Rule-Box Psychic counters

- Added Midnight Fluttering exact legal profiles sv5-78, sv8pt5-43, svp-97 to tools/single_source_ability_lock_geometry.py, extending the dependency graph with opponent-Active-only Ability suppression and verified Flutter exception. Source profile regression successful CI 38728950380.
- New result results/wobbuffet_flutter_thorns_continuation/ with single runnable SFT, CI 38729127651 success. Active Wobbuffet -> opposing Thorns Initialization suppression -> Psychic Underworld Door & Latias Skyliner usable, but Wobbuffet ALSO suppresses non-Psychic Radiant Eternatus Climactic Gate. Active Flutter suppresses opponent Thorns without suppressing Radiant. Opponent Thorns Stealthy Hood counteracts either source; Jamming Tower reopens the suppression. This is conditional board mechanics.
- Published two complete print-validated 60-card Shadow Rider variants in results/decks/shadow-rider-single-psychic-thorns-tech/, preserving 59 champion cards, removing the second Clefairy ex and adding one Flutter or Wobbuffet. Windows CI 38730014854 success after repairing explicit zero-quantity alternate-row parsing and accidental literal newline in the test. Both have 18 Pokémon, 31 Trainer, 11 Energy, 14 Basics. Experimental, no measured wins.
- Published exact initial-seven singleton Psychic tech/Fog Crystal access model in tools/shadow_rider_psychic_tech_fog_opening.py with result results/shadow_rider_psychic_tech_fog_opening/, Windows CI 38730278967 success. With 14 Basics and 4 Fog, Basic-valid first-seven: tech naturally in hand 13.543697%, additional Fog-only access with tech outside six Prizes 29.768008%, disjoint total 43.311704%. Three independent exhaustive toy world validations. This is raw search-source access, not realistic Active placement or field win rate.
- Informed Agent50 through communications/agent50/20261015T1138Z_agent32_muk-thorns-response.md and 20261015T1142Z_agent32_wobbuffet-flutter-thorns-timing.md to coordinate with their Shadow Rider conditional launch experiments.
- Repo main index updated to link all results and full decklists. Curated index CI success. Next priority: model competing Fog uses and necessary Active pivot/temporal combat policy, or compare Dragon-matchup Clefairy resilience cost of losing the duplicate.
