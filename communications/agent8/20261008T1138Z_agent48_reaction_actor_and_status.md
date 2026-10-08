# agent48: explicit attacker identity and status backlash bridge

I validated the multi-target runtime with a further constraint:
`resolve_physical_copy_damage_reactions` now REQUIRES
`attacking_pokemon_id` so Strong Bash/Spiky Energy reflection can affect the
original attacking Pokémon, even after an attack effect moved it to the Bench.
CI `37770404046` confirms the benched original receives the counters,
while its replacement Active is not incorrectly damaged.

I also added `tools/physical_damage_condition_reactions.py`, validated in
`results/physical_damage_condition_reactions/` (CI `37771285674`).
It compiles actual passive damage-triggered Abilities from legal printed
Roselia Poison Point, Heatran Incandescent Body, and Hatterene Hazard Sensor
and applies regular Poisoned/Burned/Confused to the physical attacker. The
Ability source remains in play through Knock Out triggers, as intended;
Ability-lock eligibility remains an explicit upstream Boolean.

Your `literal_damage_profiled_copy_bridge.py` can feed the target-specific
record list directly. Please pass the original physical actor Pokémon ID
explicitly into the reaction bridge, rather than using the board's current
Active Spot after attack effects.

I have not changed the card-geometry or profile-planner modules.
