# Agent 34: native Supporter-selection live-State mutation and research guard

**Confirmed on pinned Twinleaf** `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. Native `PlaySupporterTactic.useTactic` writes `player.supporterTurn = state.turn` before returning a Supporter action. Its otherwise valid Boss's Orders then fails in the real Store with `GameError.message = SUPPORTER_ALREADY_PLAYED`.

A 60-card-conserving real-engine reproduction passed in [CI 38302220300](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302220300). [CI 38302379592](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302379592) verifies a research-side `finally` guard that restores the counter *before* native dispatch, including on policy exceptions; the exact Boss's Orders then resolves legally.

Code: `simulation/twinleaf/supporter-selection-guard.cjs`, `simulation/twinleaf/test-supporter-policy-mutation.cjs`. Detailed result: `results/tests/twinleaf_supporter_policy_mutation/README.md`.

The standard bounded runner now invokes the guard for every `decodeNextAction` and labels traces with `policy_hooks:['supporter_selection_live_counter_restore_v1']` and `policy_repair_stats.restored_live_supporter_counters`. **Do not pool earlier unguarded native policy traces with new guarded traces**. A full tournament probe verification is running.

Independent blocker still exists: [known native hidden top-deck oracle](../../results/tests/twinleaf_hidden_topdeck_oracle/README.md). This Supporter fix cannot make native results trustworthy competitive win rates.

No vendor/upstream modifications or upstream interactions were made.
