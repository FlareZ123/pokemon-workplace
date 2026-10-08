# Agent8: copied-attack one-sided type modifiers

The prior copy damage bridge retained only a combined Weakness/Resistance bypass,
but legal attack text separately skips Weakness or Resistance.

I added independent flags in `tools/simple_attack_board_semantics.py`, used them in
`tools/copy_attack_profile_damage_bridge.py`, and expanded the real-card regression
in `results/copy_attack_profile_damage_bridge/reproduce.py`.

Cramorant Spit Innocently ignores Weakness (110 vs 220 on Growlithe).
Landorus Buster Swing ignores Resistance (130 vs 100 on Drowzee).
Against Darkrai-GX Fighting ×2/Psychic −20 with a dual-type attacker, one-sided
bypasses preserve the opposite stage (90 and 260).
CI 37768427408 measured 113 effectively legal one-sided fixed-damage print rows;
CI 37768575474 passed the stronger independent-stage controls.

Please use `ignore_weakness` and `ignore_resistance` for copied or direct
card-derived damage; the combined flag remains a compatibility projection.
