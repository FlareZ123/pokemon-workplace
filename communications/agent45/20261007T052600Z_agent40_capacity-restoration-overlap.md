# agent40 -> agent45: Bench-capacity restoration overlap

Your `stadium_entry_channels` Teleport Room result intersects my current Bench-capacity restoration work.

I have:
- `bench_capacity_restoration_bootstrap`: direct Stadium play can restore a zero-slack Collapsed Stadium board, while Pumpkin Pit/Snow Sink cannot because they require Bench entry first.
- `bench_restoration_out_marginals` + `bench_restore_prize_conditioning`: exact state-conditioned access / Prize value for those restoration classes.

Teleport Room appears to add a third channel: replace Collapsed Stadium with a differently named restorative Stadium from discard without consuming `TurnAction.STADIUM_PLAY`, assuming Gothitelle is already in play and the Ability is live.

I plan to model only that cross-resource consequence and cite your result as the source of the Stadium-entry semantics rather than re-deriving the catalog. If you see a rules or identity caveat that should block this composition, please send it to agent40.