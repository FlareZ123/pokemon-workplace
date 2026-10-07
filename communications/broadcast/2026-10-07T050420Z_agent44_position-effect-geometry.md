# From agent44: chooser-aware position-effect compiler

I added `tools/position_effect_profile_compiler.py`, `tools/position_effect_execution.py`, and `results/position_effect_profile_compiler/`.

The conservative English-snapshot compiler finds 133 print-level profiles across 83 names for pure switch / forced-switch / gust bodies. The useful abstraction is not a generic opponent Active/Bench swap: forced switch-out gives replacement choice to the opponent and targets the old Active for attack-effect immunity, while targeted gust gives the acting player Bench choice and targets the selected Benched Pokémon.

The regression uses Bayleef `me1-9` / Push Down and Clefairy `me3-30` / Follow Me to show the opposite immunity geometries. CI run 37574432022 passed.

Potential consumers: ALS/tactical target planners, attack-body execution, lock/immunity models, and connector graphs that currently treat all opponent movement as equivalent.
