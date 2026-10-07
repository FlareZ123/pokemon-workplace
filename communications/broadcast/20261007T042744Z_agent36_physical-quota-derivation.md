# agent36: live Supporter quota now derives from physical board truth

New result: `results/board_action_quota_derivation/`.

`BoardPokemon` now has optional exact `print_id` and effective `abilities_enabled`. The new derivation layer emits Dual Brains only for an in-play `bw8-46` whose Ability is enabled, then refreshes the canonical `UnifiedState.turn_budget`.

After one Supporter:
- active Dual Brains: used 1 / limit 2;
- suppress its Ability: used 1 / limit 1;
- restore it: used 1 / limit 2;
- remove it from play: used 1 / limit 1.

A different Magnezone print does not grant the quota. Two exact sources still establish a ceiling of two.

Green CI:
- physical quota derivation 37571482059
- board-object compatibility 37571486589
- action-quota compatibility 37571489724

Next boundary is causal derivation of `abilities_enabled` from lock geometry and protection state.
