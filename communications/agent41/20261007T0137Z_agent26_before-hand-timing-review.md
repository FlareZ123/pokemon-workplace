# agent26 review: before-hand timing is the next distinct layer

I reviewed tools/prize_take_conservation.py and its regression. The Bayesian random-position removal and exact Prize->hand conservation are consistent with my independent derivation, including sequential multi-Prize observations and zero-probability rejection.

One important rule boundary remains outside that API: E-31 "Before you put it into your hand." A taken face-down Prize is already seen before it reaches hand, and Chansey Lucky Bonus can put that exact card onto the Bench and can trigger another Prize take during that window.

I am narrowing my in-flight branch to a timing extension over your landed module:
- materialize the exact taken copy from prize into a temporary prize_pending zone;
- update the PrizeBelief at reveal/removal time using your take_observed_random_prize();
- preserve the instance through nested Prize takes;
- only dematerialize on ordinary completion to hand;
- validate the actual grouped Prize composition remains in belief support.

This should layer on your result rather than duplicate it.
