# Pinned Twinleaf SimpleTacticsAi prematurely consumes the live Supporter counter

**Status:** Real pinned Store and complete native-bot defects reproduced, prevalidation research-side guard implemented and independently validated. **No competitive win-rate evidence.** Twinleaf revision: `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.

## Source-grounded defect

Pinned `ptcg-server/src/simple-bot/simple-tactics/play-supporter-tactic.ts` evaluates Supporters and returns a `PlayCardAction`. Before the Store receives that action, the tactic writes `player.supporterTurn = state.turn` directly to the authoritative `State`. This is a speculative **decision step**, not an actual play.

The implemented Boss's Orders (PAL 172) rejects an attempted play when `player.supporterTurn > 0` and raises `SUPPORTER_ALREADY_PLAYED`. The authoritative `playTrainerReducer` itself advances the Supporter counter when a Supporter resolves. Preemptively advancing the counter in the policy therefore conflicts with the game engine's own mechanics.

## Executable 60-card evidence

The [single executable regression](../../../simulation/twinleaf/test-supporter-policy-mutation.cjs) sets up a controlled Expanded turn-two state, with a legal Boss's Orders in hand and an opponent's Benched Regidrago V. Each side conserves exactly 60 physical cards.

Native `PlaySupporterTactic.useTactic` selects `PLAY_CARD_ACTION`, mutates the actor's counter from **0 to 2**, and then the real Store rejects the action with **`GameError.message = SUPPORTER_ALREADY_PLAYED`**. In an independently constructed, otherwise identical state, restoring the counter before `Store.dispatch` makes the engine accept Boss's Orders, move it out of hand and record actual Supporter use. The regression separately proves restoration even if policy computation throws.

**Crucial full-bot test:** Native `SimpleTacticsAi.decodeNextAction`, with only `PlaySupporterTactic` available as a tactic, returns **`PassTurnAction`** in the same otherwise-legal state and leaves `supporterTurn = 2`. `SimpleTacticsAi` performs its *own candidate validity simulation* after calling the tactic. A guard that restores the counter only after `decodeNextAction` returns is therefore too late to recover the discarded Supporter action. When a research-owned subclass restores the counter at the end of `PlaySupporterTactic.useTactic`, **before** native candidate validation, the full bot instead returns `PlayCardAction` and the real Store accepts it.

**Passing pinned-engine CI:** [complete SimpleTacticsAi regression 38302973557](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302973557), [earlier tactic/Store guard 38302379592](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302379592) and unguarded Store reproduction [38302220300](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302220300).

## Research-side fix and provenance

[`supporter-selection-guard.cjs`](../../../simulation/twinleaf/supporter-selection-guard.cjs) provides `wrapTactic(PlaySupporterTactic)`, a research-owned subclass that restores the live counter in `finally` at the crucial **prevalidation** boundary. A second guard wraps `decodeNextAction` as an outer safety net. Both restore only the counter after verifying that the speculative change matches the pinned source's known behavior. They preserve the returned native action and other State fields. It is independent of and does not modify the Twinleaf vendor submodule.

The [bounded live match runner](../../../simulation/twinleaf/tournament-bounded-match.cjs) replaces exactly the native Supporter tactic in each policy roster, then also applies the outer counter restoration around each bot policy decision. Each trace includes:

- `policy_hooks: ['supporter_prevalidation_and_dispatch_counter_restore_v2']`;
- `policy_repair_stats.restored_live_supporter_counters`.

Aggregate metadata preserves the same policy-hook version. Native v0 (unguarded), outer-only v1, and prevalidation v2 are **different decision policies** and should never be pooled as exchangeable head-to-head evidence. In particular, a v1 counter restoration count can be positive even when the native bot internally rejected the Supporter and passed the turn.

## Limits and next steps

This is a targeted mutation-repair boundary for the specific pinned `supporterTurn` side effect. It does not certify all other native tactics are free of mutation or strategic bias. The [confirmed hidden-deck oracle](../twinleaf_hidden_topdeck_oracle/) remains unresolved, so improved gameplay from this repair is still a bounded engine diagnostic.

Validate the hook in both paired seat orientations, inspect real Supporter plays and telemetry, and inspect new game errors when the previously blocked Supporter effects execute. Preserve the exact hook versions, RNG policy, deck identifiers and pinned vendor revision with every trace.
