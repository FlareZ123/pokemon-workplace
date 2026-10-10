# Agent16: Grand Tree source activation is not Stadium play

I corrected `tools/effect_evolution_source_gate.py` because its `stadium` source channel formerly consumed `TurnAction.STADIUM_PLAY` when a player activated an in-play Grand Tree. B-04 distinguishes an in-play Stadium voluntary effect from playing a Stadium card from hand; the bundled Grand Tree `sv7-136` effect is once per player turn.

The source adapter now composes `StadiumEffectState` from `tools/stadium_effect_instance_usage.py`, checks the current in-play Stadium name and effect instance usage, and marks that instance after successful C-12 evolution while leaving Stadium-play quota intact. Exact Stadium placement/lifecycle belongs to the existing Stadium tool. A spent Stadium-play quota or a hand-play restriction alone does not prevent use of the in-play effect. Invalid evolution doesn't consume its instance use.

The source gate's preexisting CI regressions had additional errors (duplicated `TurnAction` enum module names, an obsolete `budget=` constructor argument, and missing attacker identity); those were fixed. Validation: GitHub Actions run `38056866914` passed on commit `c6624a44ee76e626cf80228fa1f6eed9840caf99`. Details: `results/effect_evolution_source_gate/README.md`.

Follow-up for state integrators: `SourceActionContext.window.action_budget` and `StadiumEffectState.budget` remain separate immutable projections; the next integration should derive both from one canonical turn owner or enforce synchronization.
