# Pinned Twinleaf SimpleTacticsAi prematurely consumes the live Supporter counter

**Status:** Real pinned Store defect reproduced, research-side guard implemented and independently validated. **No competitive win-rate evidence.** Twinleaf revision: `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.

## Source-grounded defect

Pinned `ptcg-server/src/simple-bot/simple-tactics/play-supporter-tactic.ts` evaluates Supporters and returns a `PlayCardAction`. Before the Store receives that action, the tactic writes `player.supporterTurn = state.turn` directly to the authoritative `State`. This is a speculative **decision step**, not an actual play.

The implemented Boss's Orders (PAL 172) rejects an attempted play when `player.supporterTurn > 0` and raises `SUPPORTER_ALREADY_PLAYED`. The authoritative `playTrainerReducer` itself advances the Supporter counter when a Supporter resolves. Preemptively advancing the counter in the policy therefore conflicts with the game engine's own mechanics.

## Executable 60-card evidence

The [single executable regression](../../../simulation/twinleaf/test-supporter-policy-mutation.cjs) sets up a controlled Expanded turn-two state, with a legal Boss's Orders in hand and an opponent's Benched Regidrago V. Each side conserves exactly 60 physical cards.

Native `PlaySupporterTactic.useTactic` selects `PLAY_CARD_ACTION`, mutates the actor's counter from **0 to 2**, and then the real Store rejects the action with **`GameError.message = SUPPORTER_ALREADY_PLAYED`**. In an independently constructed, otherwise identical state, selecting the same action with the research guard correctly restores the counter before `Store.dispatch`, and the engine accepts it, moving Boss's Orders out of hand and recording actual Supporter use. The regression separately proves restoration even if policy computation throws.

**Passing pinned-engine CI:** [run 38302379592](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302379592) and unguarded/ordinary Store reproduction [run 38302220300](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302220300).

## Research-side fix and provenance

[`supporter-selection-guard.cjs`](../../../simulation/twinleaf/supporter-selection-guard.cjs) wraps `decodeNextAction`. It snapshots the player counter, evaluates the native bot, and restores that counter in `finally` if the pinned native tactic prematurely changed it. It verifies that the observed speculative value matches the known native source behavior before recording one repair. It preserves the returned native action and other State fields. It is independent of and does not modify the Twinleaf vendor submodule.

The [bounded live match runner](../../../simulation/twinleaf/tournament-bounded-match.cjs) now invokes the guard around every native bot policy decision. Each trace includes:

- `policy_hooks: ['supporter_selection_live_counter_restore_v1']`;
- `policy_repair_stats.restored_live_supporter_counters`.

Aggregate metadata preserves the same policy-hook version. Trials before and after this repair are **different decision policies** and should never be pooled as exchangeable head-to-head evidence.

## Limits and next steps

This is a targeted mutation-repair boundary for the specific pinned `supporterTurn` side effect. It does not certify all other native tactics are free of mutation or strategic bias. The [confirmed hidden-deck oracle](../twinleaf_hidden_topdeck_oracle/) remains unresolved, so improved gameplay from this repair is still a bounded engine diagnostic.

Validate the hook in both paired seat orientations, inspect real Supporter plays and telemetry, and inspect new game errors when the previously blocked Supporter effects execute. Preserve the exact hook versions, RNG policy, deck identifiers and pinned vendor revision with every trace.
