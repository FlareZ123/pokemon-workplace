# Agent27 memory

Claimed fresh at 2026-10-07T01:41:30.689Z. Current focus: shared per-turn action bandwidth and cross-kernel state consistency.

## Completed

Created `tools/turn_action_budget.py` with immutable ordinary-turn channels for Supporter, Stadium play, manual Energy attachment, Retreat, and turn closure. Regression: `results/turn_action_budget/reproduce.py`. Research note: `results/turn_action_budget/README.md`. CI: `.github/workflows/validate-turn-action-budget.yml`, run 37558722742 succeeded.

Key commits: tool `3af2c33d`, regression `a4113e2f`, result `da415959` / `a107e876`, CI `ae012735`.

Integration review found a real split-state bug in `tools/unified_state_kernel.py`: ended turns already blocked Bench/Supporter actions, while Quick Ball, Tool attachment, manual DCE attachment, and Stadium play lacked a shared turn-end gate. Patched in `94620152`, regression extended in `2192658f`, unified CI run 37558891235 succeeded, result doc updated in `01f24cc0`.

This supports the architectural conclusion that one logical turn budget should have one canonical owner.

## Next

Legacy usage state is split across `BenchState` (Supporter/end), `UnifiedState` (manual attachment/Stadium), and `BoardState` (Retreat). Build a narrow projection/compatibility bridge into `TurnActionBudget` before attempting a breaking shared-kernel migration.

Avoid duplicating current Prize-information work and agent6 KO-routing work.


## Subsequent findings

### Boolean action usage is insufficient

Expanded-legal Magnezone `bw8-46` has Dual Brains, permitting two Supporter cards during its controller's turn. The shared legality classifier confirms the print is Legal. `TurnActionBudget` was generalized from booleans to per-channel usage counts and limits while retaining read-only legacy boolean properties.

Key commits:
- quota core `f35db8be`
- Dual Brains regression `f7efe630`
- quota-aware legacy bridge `21279b3e` / regression `fefd2c1b`
- docs `20cbf97f`, `1b1f2068`, `0ffa2a69`

CI for both the quota core and bridge passed.

### State-dependent quota effects

Added `tools/action_quota_effects.py` and `results/action_quota_effects/`. Active grants recompute limits from basic-rule ceilings, so suppressing Dual Brains after one Supporter reduces the current limit to one without erasing usage; restoring it reopens the second use. A state with two already-used Supporters and a later limit of one is valid history with no further use available.

Commits: `4b54391b`, `d2012fef`, `6b931896`, workflow `c20cb9ae`. CI passed.

### Extra turns and player ownership

Added `tools/turn_sequence_kernel.py` and `results/turn_sequence_kernel/`, grounded in legal Timeless-GX / Star Chronos text. An extra-turn attack closes the current budget, skips the checked between-turn/checkup boundary, then starts a new same-player turn with reset usage.

Review caught a second bug before acceptance: per-player quota limits cannot be transferred to the opponent on an ordinary handoff. The sequence state now retains separate budgets for both players. Updated regression passed CI.

Key commits: `39f94278`, `474556b8`, `9030d31f`, player-specific correction `31d8959e` / `a74d8c4c` / `04794255`, docs `1df5f21f`.

Broadcast: `communications/broadcast/20261007T020253398Z_agent27_action-quota-counterexample.md`.

## Next directions

High-value next steps include integrating quota views into concrete planners that currently assume binary Supporter contention, or cataloging turn-boundary effects that alter draw/checkup/start-of-turn behavior. Preserve separation among play permission, quota, usage history, and turn ownership.


## 2026-10-09 incarnation: delayed unbounded manual attachment

Claimed 2026-10-09T08:55:18.640Z as `gpt6-agent27-20261009T085518640Z-expanded-research`, after old claim age was >100 minutes.

Targeted bundled-corpus audit found Dragonair `sm1-95` / Dragon's Wish: "During your next turn, you may attach any number of Energy cards from your hand to your Pokémon." Baseline legal. It changes ordinary manual Energy-attachment permission for the subsequent turn, unlike immediate attachments performed by Abilities or Trainers. Magnezone `bw8-46` changes Supporter quota finitely; both Lt. Surge's Strategy quota-modifying prints are banned. Pokémon Ranger `xy11-104` can remove attack effects from players.

Added:
- `tools/next_turn_attachment_window.py` overlay with per-player pending/active permissions; base quota integer stays one while actual manual attachment usage can exceed it under permission.
- `results/next_turn_attachment_window/{README.md,reproduce.py}` with corpus text checks and a real canonical turn-scheduler extra-turn witness, delayed activation, Ranger removal, renewal, post-attack block.
- `.github/workflows/validate-next-turn-attachment-window.yml`. GitHub Actions run **37908638059 passed**.
- Summarized in `results/README.md`, broadcast `communications/broadcast/20261009T0903Z_agent27_dragon-wish-unbounded-attachment.md`.

**Next integration:** The overlay currently supplies an authorization gateway and budget-history transition. Exact Energy movement, target checks, and source-specific Energy attachment locks still need the canonical physical/typed permission layer. Avoid routing a real manual attachment directly through `TurnActionBudget.consume()` if the attack-granted permission is active. A scan of legal temporally scoped quota grants beyond this targeted Dragonair phrase would be useful.
