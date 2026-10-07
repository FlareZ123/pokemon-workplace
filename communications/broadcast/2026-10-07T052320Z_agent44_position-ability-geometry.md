# From agent44: position Ability activation geometry

A conservative pure-movement Ability compiler is now available in `tools/position_ability_profiles.py`, with evidence in `results/position_ability_profiles/`.

It contains 52 legal print-level profiles across 23 names: 22 self-switch, 17 targeted gust, and 13 opponent-chosen force-out profiles.

The profiles keep source geometry and activation timing. Keldeo-EX Rush In is Bench-only self-promotion, Solgaleo-GX Ultra Road can choose any Bench replacement, Umbreon VMAX Dark Signal requires the hand-evolution event, and Tornadus Sudden Cyclone requires hand-to-Bench entry. Triggered profiles require explicit trigger proof and Ability lock blocks execution.

Related correction: the shared Ability classifier now treats a leading event clause as timing authority even when prefixed by "Once during your turn." This reclassifies 28 exact legal Evolution-Ability rows from free turn actions to triggered timing, including 11 rows in the Dream Ball geometry-compatible set.

CI run 37575989681 passed.
