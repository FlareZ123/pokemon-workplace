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
