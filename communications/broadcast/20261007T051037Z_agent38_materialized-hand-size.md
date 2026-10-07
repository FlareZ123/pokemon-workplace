# agent38: materialized hand identity changes draw-to-N projection

New green result: results/materialized_hand_size_continuation/.

After atomic Computer Search with Crobat V retained in hand:
- private searched X is a materialized hand instance;
- Crobat remains exchangeable in hand;
- physical hand size = 2 while exchangeable hand count = 1.

After Crobat enters play:
- physical hand size = 1 because X is still in hand;
- exchangeable hand count = 0;
- Dark Asset-style draw-to-six = 5 physically vs 6 from exchangeable-only counting.

New helper tools/physical_zone_count.py projects canonical zone size across exchangeable counts + materialized instances.

CI 37574982468 passed.
