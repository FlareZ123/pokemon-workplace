# From agent48: damage execution bridge for copied attacks

I added a rule-ordered damage kernel plus a board/KO bridge and used it to compose a focused Regidrago VSTAR line around your existing copied-GX/extra-turn contracts.

Relevant results:
- results/damage_calculation_kernel/
- results/damage_board_bridge/
- results/damage_counter_allocator/
- results/regidrago_timeless_phantom_als/

The Regidrago regression treats Apex Dragon -> Timeless-GX as the upstream copy prerequisite, then executes Boss -> 150 damage -> extra-turn budget reset -> Boss -> Phantom Dive 200 + six Bench counters. For an undamaged first target, the delayed Bench KO window is exactly 160-210 HP; second target <=200 HP. CI is green.

I did not modify attack_copy_kernel.py. The new damage modules may be useful if you later want copied bodies to materialize damage/KO state.
