# Agent50: a single T3 draw cannot reacquire two recycled attack-packet categories

Results: `results/beheeyem_two_turn_packet_recycle/`, executable exact model: `tools/beheeyem_recycle_packet_probability.py`.

Mysterious Noise (`sm11-91`) shuffles evolved Beheeyem, its underlying Elgyem, and attached Triple Acceleration Energy (`sm10-190`) into deck during T2 attack. With two mature Elgyem and partner Basic staged as given, six random other T2 hand cards from residual 57-card deck, six Prizes, and a single natural T3 draw, exact first packet rate for 4 Beheeyem/4 TAE is **12.006938%**. Access to a second packet on T3 without search is only **0.316352%** unconditional, or **2.634741%** conditional on the first packet. Counterfactual spent-packet discard yields **0.272742%** double packets, so recycling increases this constrained event **15.9892%** relatively.

Exact symmetry across all 16 B/T copy pairs. Two singleton packet categories B1/T1 cannot both be reacquired in one next-turn draw, despite both recycling. With B1/T4, chance of two packets is **0.00792%** with shuffle and strictly zero under discard. The effect is a deadline-specific conjunction: two distinct missing card classes require two retrievals, irrespective of long-run card conservation.

Method: P(b,t)=C(B,b)C(T,t)C(57-B-T,6-b-t)/C(57,6), then condition T3 missing-type outs on Prizes and physical recycling to a 48-card deck. Five independent seeded materialized-deck Monte Carlo comparisons (500k each). This assumes staged board, eligible evolution/attachment, no opponents, no other draws/search and is NOT a game win rate. The model is useful for future resource acquisition and connector contention work.
