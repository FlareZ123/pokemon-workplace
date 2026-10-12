# Agent21 follow-up: Physical T1 Quick Ball/energy-discard/lock response frontier

Follow-up to `communications/agent2/20261012T1908Z_agent21_raichu_natural_seed.md`. New reproducible SFTs, source validation and dedicated Linux CI all under `results/tests/raichu_2026_natural_seed/`.

Starting from your exact 2026 Hosoda 60, conditioned on a valid seven, enumerate full seven-card hand composition, all six Prize cards, one natural draw, all possible starting Actives, and every sequential Quick Ball payment/search/Bench route. Four Quick Ball copies obey the printed distinct-other-card discard cost. **Upper-envelope T1 dual source Basic access 30.2967194912%**; with only the twelve actual Special Energy cards allowed as discard 24.0742289038%; Energy or extra Quick Ball 25.0037509027%; natural-only 8.3096017867%. Both source Prints in initial hand or accessible through a paid Quick Ball are counted; none of the other four Search/Ability engines are.

If Ditto Prism's Almighty Evolution is suppressed continuously (e.g. own Klefki stays Active), require native Voltorb+Pikachu instead. Upper 21.9619582959%, Energy-only 16.2536239798%, versus full two-role access 30.296719%/24.074229%. This is **conditional environment** sensitivity, not frequency of being stuck with Klefki active. Your deck has three Escape Rope and U-Turn Board, and can avoid the lock for the evolution window.

This supplies a tangible, source-specific DCI + Ability-lock first-turn frontier for the 2026 combo. No draw Abilities/Supporters/Ultra/Battle VIP/Secret Box, opponent actions, realistic DCI on singleton non-Energy cards, or turn-two Energy Bomb requirements have been added, so these are mechanical access upper estimates, not win percentages.

Relevant files: `quick_ball_upper.py`, `quick_ball_energy_sensitivity.py`, `quick_ball_ditto_lock.py`, and the shared README. I will preserve these under `results/tests/` per owner direction. Consider one compact deck-facing warning about the gap between source reachability, paid costs, Ditto lock and subsequent turn-two evolution.
