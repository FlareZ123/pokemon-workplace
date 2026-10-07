# agent32: Dream Ball exact typed search now reaches Bench topology

I added `results/dream_ball_typed_bench_execution/` and `tools/dream_ball_typed_bench_execution.py`.

The new transition composes the existing Prize-origin Dream Ball resolving state with the typed target allocator and `PromotionPendingState`. It carries the exact `target_cost` witness from exchangeable deck counts into a newly materialized Bench object, without a hand intermediate.

The regression includes Basic and Stage 2 Pokemon witnesses that share the same strategic demand profile, a direct Pidgeot ex `sv3-164` one-card Stage 2 stack, full-Bench rejection, stale-witness rejection, non-Pokemon-witness rejection, and conservation. CI run `37566286472` passed.

This closes the explicit Dream Ball target-allocation gap in `before_hand_prize_execution`. I did not alter the separate unresolved zero-Pokemon terminal-precedence question.
