# Agent 9: Exact typed Energy free-Retreat source and provider distinction

2026-10-12. Implemented
`tools/retreat_typed_energy_no_cost.py`, integrated into
`retreat_environment_modifiers.py` and
`board_derived_retreat.py`; complete source-scan and physical
regressions are in `results/retreat_typed_energy_no_cost/`.
CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38281119342
PASSED.

English Expanded-labeled Ability corpus yields 27 exact prints:
14 self-source typed Energy no-cost Abilities, 13 Bench-capable
friendly-team auras (Darkrai-EX, Zeraora-GX, Clefable ex,
Archaludon, Manaphy-EX). Static source records validate printed
card name, exact ID and Ability state.

Critical distinction: existing dynamic Special Energy normalization
purposely rewrites provided Energy *quantity* as generic `C` units.
Typed Abilities must still recognize printed type provision.
A bounded print-specific type supplier now handles Rainbow,
Aurora, Legacy, Prism, Double Dragon, Fusion Strike, Unit,
Counter, Reversal and Luminous Energy, conditioned on live holder
traits, other Special attachments and Prize position.

Physical witness: Stage1 with Reversal Energy + Benched Darkrai
Dark Cloak against Galar Mine. At own/opponent Prizes (6,5),
Reversal provides three of every type and Dark Cloak makes
Retreat cost zero, yielding actual legal no-payment Retreats.
At (5,5), Reversal provides only one Colorless and Retreat cost
is four. Disabling the Aura source restores cost four at (6,5).

This is a precise source-specific slice, not a complete provider
catalog or full game simulation. Reuse the shared typed function
rather than assuming Colorless payment snapshots encode types.
