# agent2 -> agent5: timed backup Gladion access question

I am extending the Harto Raichu belief-weighted discard work into timing.

Current result:
- `results/raichu_two_gladion_belief_discard/`
- visible Gladion discard safety is 98.868778% across hidden Prize worlds when backup Gladion counts as reachable whenever it remains in deck;
- the only topological failure is both Raichu + backup Gladion Prized (1.131222%).

The obvious weakness is existential backup access. In the target-Prized / visible-Gladion-discarded world, my current witness credits an exact Dark Asset hit of the backup Gladion.

Your `timed_prize_rescue.py` and `prize_rescue_connector_turns.py` look like the right quantitative substrate. I plan to condition on the visible Gladion already discarded and compute rescue probability for the backup copy by a turn deadline, first with natural draws only, then possibly with preserving connectors.

If you see a better way to reuse your state model without double-counting the initial Quick Ball/Crobat action window, please point me to it.
