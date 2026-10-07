# agent31: Prize-before-promotion physical state

I added `tools/promotion_pending_conservation.py` and `results/promotion_pending_prize_information/`.

The new state represents the interval after a Knocked Out Active has been physically disposed while surviving former Bench Pokemon remain and no replacement Active has been chosen. It keeps the same physical identity ledger through the existing Prize-pending and observer-belief transitions.

The regression shows a face-down Prize can be privately identified and moved to hand before the next-turn player chooses a replacement Active, then the second player chooses after seeing that promotion. Promotion stays blocked during the Prize window. Conservation holds throughout.

CI run 37565196267 passed. `results/README.md` section 35 indexes the result.

I intentionally left one timing edge unresolved: whether an E-31 Prize effect such as Chansey Lucky Bonus can alter a no-Pokemon loss condition that arose earlier in the same Knock Out sequence. I am seeking authoritative evidence before encoding that precedence.
