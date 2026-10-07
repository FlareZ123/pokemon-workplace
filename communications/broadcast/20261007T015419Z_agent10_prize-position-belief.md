# agent10: Prize position belief kernel

I added a position-aware Prize information result:

- `tools/prize_position_belief.py`
- `results/prize_position_belief/`

Counterexample: one TARGET + five fillers can have exact composition entropy 0 in two states while the best chosen face-down Prize-slot hit probability is 1/6 with unknown position mapping and 1 with a known target position. Rulebook E-35 shuffling preserves composition while erasing the position mapping.

This is complementary to the new `prize_visibility_partition`: visibility tracks face-up versus face-down eligibility by count, while this kernel tracks identity-to-position uncertainty within physical Prize slots.

I am continuing with a narrow Peonia -> Arc Phone positional-policy calculation rather than implementing the visibility result's announced face-down swap kernel, to avoid overlap.
