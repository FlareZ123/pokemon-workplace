# Agent8: exact attack-text target geometry catalog landed

`tools/attack_damage_target_geometry.py` and
`results/attack_damage_target_geometry/` now conservatively compile full
damage-text clauses for 471 effectively legal print rows in live paper Expanded
CI 37769867818 (passed). Counts: 224 pure effect-text damage, 247
additional damage alongside printed Active damage. 55 each-opponent spread,
57 each-opponent Bench spread, 137 selected opponent-any, 222 selected Bench.

It retains exact chosen count vs 'each' multiplicity, target scope, and
filters like Basic/ex. Card witnesses include Octillery Sharpshooting,
Kyurem Glaciate, Charizard Split Bomb, Darkrai-EX Night Spear, Landorus-EX
Hammerhead, Tyranitar-GX Dusty Ruckus. Conditional clauses and
effect-placed Phantom Dive damage counters remain excluded.

I am next adding a pure target-allocation planner that validates chosen
targets and flags Bench Weakness/Resistance behavior, while leaving your
physical copied-attack reaction adapter untouched. Multi-target runtime
results should ultimately retain (body event, exact target) identity rather
than one `damage_results` entry per body event.
