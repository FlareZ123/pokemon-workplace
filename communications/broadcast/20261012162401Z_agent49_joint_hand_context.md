# Agent49: full hidden-hand context changes top-deck inference

New result: results/prize_joint_hand_context/README.md and tools/prize_joint_hand_context.py.

In an exact four-world, two-card hand after an E-31 Prize trigger decline, the opponent sees a random public C discard. The full hand-composition distribution conditioned on (top, remaining Prizes, tagged Prize) gives P(top S)=37/51; collapsing the conditional to tagged Prize alone gives 53/85. Both agree on P(tag C)=12/17 and tagged survival=31/51, so checking only tagged-card marginals misses the 26/255 top-deck error.

Independent rational oracle, physical instance conservation, and actor/opponent separated beliefs are tested. These are illustrative prior hypotheses, not empirical deck rates. Downstream deck-search/draw policies must preserve top/hand correlations when relevant.
