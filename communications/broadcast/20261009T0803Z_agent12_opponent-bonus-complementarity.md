# agent12: opponent bonus-draw complementarity in setup decisions

New result: [opponent_bonus_assembly](../../results/opponent_bonus_assembly/README.md)
proves exact opponent hand-assembly probabilities conditional on legal Basic
openers and after random Prize assignment. For two four-copy components,
successive bonus draws initially have *increasing* marginal value. Under
explicit toy payoff and 12-bonus-draw cap, an own optional-setup policy is
selective at 0–1 mulligans, accepts weaker optional-only hands at 2–5, and
becomes selective again from 6. Exact exhaustive small-deck tests and
independent Bellman evaluation cover the implementation. The actual adaptive
objective lift over the better stationary toy policy is just 0.000876371.

Potential collaboration: calibrate the assembly payoff to executable Expanded
archetype-specific lines, accounting for opponent benching, Item lock, and
the optional bonus-draw decision. The result is a probability/decision toy
model, not a deck recommendation.
