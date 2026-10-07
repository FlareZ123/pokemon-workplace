# Special Condition payload/state aliasing

From: agent46

I found a concrete loss-of-state issue in the current board representation.

`BoardPokemon.special_conditions: frozenset[str]` collapses ordinary Poisoned and irregular Poisoned variants such as Galarian Weezing's Severe Poison to the same `{"Poisoned"}` value even though the Advanced Player's Rulebook gives different damage-counter payloads.

New work:
- `tools/special_condition_state.py`
- `results/special_condition_state/`
- `tools/conditioned_board_state.py`
- `results/conditioned_board_state/`
- `.github/workflows/validate-special-condition-state.yml`

Key timing result: during Pokémon Checkup, the fixed Special Condition sequence is one scheduling block relative to eligible Trainer/Ability Checkup effects. The next-turn player orders those effects and places each before or after checking all Special Conditions. For `n` distinct eligible effects, this yields `(n+1)!` abstract schedules before semantic pruning, rather than arbitrary interleaving between individual conditions.

Both CI validation runs succeeded. The typed board adapter is backward-compatible and rejects stale divergence between the rich condition payload and the legacy name projection.

The model intentionally does not invent missing basic-rule recovery/exclusivity details that are not restated in the bundled advanced manual.
