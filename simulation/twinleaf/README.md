# Twinleaf paper Expanded research integration

## Pin and boundary

The existing Git submodule at `vendor/twinleafgg` points to upstream commit `3348ebdc898f175a2ed8f999133cd13d1afd01f5`, as established by the repository's Git state. Vendor source remains unmodified.

Research-owned code in this directory imports **only interfaces actually present in the pinned server**. It will assert the Git commit before execution. A changed vendor revision must receive an explicit compatibility review and passing tests. The first thin adapter is [headless-smoke.cjs](headless-smoke.cjs), intentionally CommonJS JavaScript with JSDoc types.

## Actual engine facilities used

The pinned `ptcg-server` contains an in-memory `game/store/store.ts` and `simple-bot/simple-tactics-ai.ts`. The executable smoke:

1. Loads Twinleaf source through the pinned server's own `ts-node/register/transpile-only`.
2. Registers **actual upstream** Regidrago V (SIT 135) and Grass/Fire basic Energy (BLW 105/106) card classes in `CardManager`.
3. Constructs two legal-size 60-card minimal smoke fixtures, each with four Regidrago V, 28 Grass Energy and 28 Fire Energy. These are engine validation fixtures, **not strategic deck proposals**.
4. Constructs an actual `Store` with `Format.EXPANDED`, dispatches two `AddPlayerAction` commands, and advances through prompts and actions.
5. Uses the engine's existing `BotArbiter` for coin/shuffle prompts and `SimpleTacticsAi` for tactical actions and remaining prompts. A seeded PRNG makes the random sequence reproducible.
6. Reports actual turn, action, attack, phase and winner fields as machine-readable JSON, including an explicit `status` value: `finished` or `action_limit`.
7. Asserts that the game did not fail deck creation, reached a real player turn, and completed at least the first turn. Every failed dispatch includes the action/prompt/turn/phase identity and is fatal for CI.

This is a **live state-machine integration**, without WebSocket, browser, ORM database or upstream code edits. The smoke uses the stock naive tactics from the pinned revision. No stronger player policy has been implemented or evaluated here.

## Run and CI budget

Workflow: [`twinleaf-headless-smoke.yml`](../../.github/workflows/twinleaf-headless-smoke.yml). It uses `actions/checkout` with submodules, Node according to the pinned vendor `.nvmrc`, and `npm ci` with the pinned server lockfile. The integration executes one seeded bounded test of at most **1,000 bot actions**; it intentionally avoids mass matches, concurrent jobs or runaway simulator costs. A 20-minute workflow timeout is a second protection.

The script accepts numeric parameters as `run(seed, maxActions)` when imported as a CommonJS module. No CLI parameters are needed; invoking it directly runs the defined smoke seed and prints the JSON result. The fixture can later be imported into a general runner after the action policy, prompt support and deck mapping have been checked.

## Important limitations

- Only three card class implementations are registered in the initial smoke. The source-verified 2026 Aichi decks are validated against the **English paper card database**, separately. Mapping 36 or more canonical prints to the correct Twinleaf `fullName`, verifying each engine card is implemented and consistent with official card text, and registering all required sets remain substantial future work.
- The test requires advancing a player turn. It may finish or reach its deliberate action cap. If the cap is reached, report it as a partial game; never count it as a completed match or a draw.
- An in-memory simple bot is a weak baseline. Never equate its game outcomes or action failures with competitive match strength.
- Twinleaf may implement some effects differently from paper Expanded. One observed discrepancy in pinned Regidrago V's Celestial Roar source comment/implementation should be inspected: the `if energyCardsDrawn.length == 0` comment states the discarded cards go to hand while code actually sends them to the discard pile. This is a misleading comment rather than demonstrated wrong effect; card behavior needs a targeted test.
- This runner avoids changing vendor code. If a defect is found, implement a reproducible research-side patch/hook with explicit upstream SHA and tested compatibility, per the project's integration policy.

## Next milestones

Capture one **completed** smoke match on CI, with bounded prompts and action count, before converting this into a win/loss collector. Map the newly published 60-card Regidrago and Shadow Rider references from their exact-print manifests to Twinleaf classes, fail closed when print matching or card effect support is missing, and compare engine behavior to hand-tested attack-copy/lock semantics. Design stronger per-archetype policies and matchup fixtures before attempting any competitive ranking.
