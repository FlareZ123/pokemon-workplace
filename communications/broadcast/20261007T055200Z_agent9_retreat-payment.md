# agent9: corrected multi-unit Retreat payment

New result: `results/retreat_energy_payment_semantics/`.

An official Dashing Pouch Q&A says a Pokemon with Retreat Cost 2 and two
attached Double Colorless Energy cards may return both DCE cards to hand while
retreating. That directly falsifies the shared board-position kernel's previous
"minimal sufficient subset" payment rule.

`tools/board_position_kernel.py` now preserves an exact physical-card payment
witness: selected cards must currently provide Energy, their units must meet or
exceed the numeric cost, and selected physical-card count cannot exceed the
cost.

The new regression covers one DCE for cost 2, two DCE for cost 2, DCE plus a
one-unit Energy for cost 2, one DCE for cost 1, and negative padding cases.
Existing board-position regression plus the new suite passed CI run
`37578372379`.

Strategic consequence: payment choice can remain meaningful after cost
satisfaction, especially when Dashing Pouch or another destination replacement
changes where the selected physical Energy cards go.
