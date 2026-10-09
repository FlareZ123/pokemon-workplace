# Exact bounds for uncertainty about Prize-trigger choices

## Research finding

When a player declines an optional E-31 Prize-card effect, the opponent can update beliefs about the hidden card using a behavioral choice model. If the activation probability is uncertain, **exact posterior bounds** are available without assuming a single rate.

Model: `tools/prize_trigger_policy_bounds.py`  
Regression: `results/prize_trigger_policy_bounds/reproduce.py`

## The vertex theorem

A hidden world w has prior probability p(w), pending Prize group g(w), and player activation probability u[g(w)]. For an event E, after a *public decline* the posterior is

`P(E|decline) = sum_w p(w)1_E(w)(1-u[g(w)]) / sum_w p(w)(1-u[g(w)])`.

Suppose each group rate can independently range across an interval [L_g,U_g]. Holding the other groups fixed, this posterior is a ratio of affine functions of u_g, and its derivative has constant sign wherever the denominator is positive. Its maximum or minimum can therefore occur at one endpoint. Repeat for each group to show a global extremum occurs at a **vertex of the independent policy box**. Vertices at which decline is impossible contribute no posterior. The implementation enumerates these vertices exactly.

## Chansey witness

Use the four-world prior in [the optional trigger result](../prize_optional_trigger_signal/). The opponent knows that, when the Bench is open, the player activates Chansey's Lucky Bonus between 40% and 80% of the time when available. An unrelated hidden Prize has 0% activation probability for Lucky Bonus.

| Belief after decline | Lower | Upper | Prior |
| --- | ---: | ---: | ---: |
| P(Chansey) | 1/6 = 16.67% | 3/8 = 37.50% | 50% |
| P(deck top S) | 3/10 = 30.00% | 17/40 = 42.50% | 50% |

A Bench-full situation in which all possible cards have zero activation probability produces no new information. The opponent's prior remains unchanged.

The regression uses exact rational enumeration of four worlds to test both bounds, enumerates a grid of interior policies for two variable groups, and rejects missing, illegal, and zero-observation policy intervals.

## Conditions and limitations

This is a mathematical bound *conditional on the prior and assumed behavioral intervals*, not an empirical statement about tournament players. Rates depend on the known board and whether a trigger is legally available. Independent groupwise intervals require the player's unknown choice policy to factor through the modeled hidden pending-card group; private hand/matchup effects must be incorporated into more detailed groups or modeled jointly.

The work reuses the existing pending-Prize joint belief which retains deck-top and unselected-Prize correlations. It addresses a single publicly observed decline; multi-card simultaneous ordering and further physical transitions remain separate.
