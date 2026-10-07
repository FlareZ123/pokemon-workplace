# Nonlinear mulligan costs make setup policy count-dependent

## Question

A constant cost per failed mulligan gives a stationary value-threshold policy:
an optional-only hand is kept when its terminal hand value is high enough
relative to the value of rejecting and reshuffling.

Real mulligan externalities need not be linear. The opponent's first optional
bonus card can have a different marginal value from later cards, information
leakage can accumulate unevenly, and a player can impose a nonlinear risk
budget on repeated redraws.

What happens when the marginal cost of the next failed mulligan depends on how
many mulligans have already occurred?

## Exact dynamic program

Let (J_m) be the best expected future utility before seeing an opening hand
when (m) failed mulligans have already occurred.

Let (c_m) be the marginal cost paid if that next hand is rejected.

For an optional-only hand (h) with terminal value (v(h)), the two choices
are:

- keep: (v(h));
- reject: (J_{m+1} - c_m).

Therefore

[
	ext{keep at count } m
iff
v(h) ge J_{m+1} - c_m.
]

Forced-Basic hands remain mandatory keeps. Hands with neither a forced starter
nor an accepted optional setup route remain mandatory redraws.

The implementation supports any finite prefix of marginal costs followed by an
eventually constant tail. The tail is solved exactly with the stationary
optimizer, then the finite prefix is solved backward. This avoids an arbitrary
mulligan-count truncation.

Implementation:

- `tools/setup_count_dependent_policy.py`
- `results/setup_count_dependent_policy/reproduce.py`

## Constant costs are a special case

When every marginal cost is the same constant (c), every count state reduces
to the stationary problem. The reproduction harness checks that a three-step
constant prefix plus constant tail produces exactly the same:

- expected utility;
- per-attempt acceptance probability;
- optional-hand keep set

at every count as `optimize_linear_mulligan_penalty`.

This is a useful consistency check on both formulations.

## Benchmark state

Use the same abstract 60-card benchmark as
`setup_hand_value_policy`:

- 4 forced Basic starters;
- 4 optional setup starters;
- 4 key opening cards;
- 48 filler cards.

A kept opening has terminal value 1 if at least one key opening card is present
and 0 otherwise.

Under a constant cost of 0.10, the stationary optimum is the selective policy
that keeps an optional-only hand only when it contains a key card.

Under a constant cost of 0.30, the stationary optimum accepts every
optional-only hand.

## Finding 1: increasing future cost can make the policy loosen

Consider marginal costs:

- first failed mulligan: 0.10;
- second failed mulligan: 0.10;
- every later failed mulligan: 0.30.

The exact optimal count-dependent policy is:

| Failed mulligans already seen | Policy | Acceptance on next attempt | Expected future mulligans | Reject continuation value |
| ---: | --- | ---: | ---: | ---: |
| 0 | selective-key | 49.783383% | 0.887988286 | 0.200947600 |
| 1 | selective-key | 49.783383% | 0.768315644 | 0.113921873 |
| 2+ | accept-all | 65.359357% | 0.530002810 | -0.086078127 |

The first two optional-only decision windows still justify rejecting a zero-value
hand. Once the future marginal cost rises to 0.30, the reject continuation
value falls below zero, so even a zero-value optional-only hand should be kept.

This gives an exact version of the intuition that a player may loosen their
keep standard after repeated redraws when additional mulligans become more
expensive.

## Finding 2: the direction can reverse

Now use:

- first failed mulligan: 0.40;
- every later failed mulligan: 0.10.

The exact optimum becomes:

| Failed mulligans already seen | Policy | Acceptance on next attempt | Expected future mulligans | Reject continuation value |
| ---: | --- | ---: | ---: | ---: |
| 0 | accept-all | 65.359357% | 0.695827412 | -0.011269344 |
| 1+ | selective-key | 49.783383% | 1.008702362 | 0.288730656 |

The player should accept every optional-only hand on the first attempt because
paying the first rejection cost is very expensive.

If the first hand is a mandatory redraw, that large cost is already sunk. From
the next attempt onward, additional redraws are cheaper, so the optimal policy
becomes more selective.

Therefore there is no universal rule that setup policy should become looser as
the mulligan count rises. The direction depends on the **marginal future cost
schedule**, not on the count by itself.

This is relevant to the opponent bonus-card externality. If the first extra
card granted to the opponent is substantially more valuable than later extra
cards, diminishing marginal cost can produce exactly this tightening behavior.

## Validation

The reproduction harness checks the count-dependent solver in three ways.

1. A constant marginal-cost schedule collapses to the stationary exact result.
2. A small two-stage instance is compared against exhaustive enumeration of
   every deterministic optional-hand policy at both prefix counts.
3. Two 60-card schedules are asserted to produce the policy transitions shown
   above.

The benchmark uses exact grouped opening-hand probabilities rather than Monte
Carlo sampling.

## Strategic interpretation

The state variable is not simply "number of mulligans already taken." What
matters is the value of rejecting **this** hand into the next decision state.

That continuation value can move because:

- opponent bonus-card value is nonlinear;
- additional public hand reveals change information leakage;
- tournament-time or fatigue costs change;
- a player has an explicit risk budget for further redraws;
- matchup information changes the terminal value of future hands.

A correct setup optimizer therefore needs both the observed hand and the
mulligan-count state when any of those effects are nonstationary.

## Limitations

The cost schedule is still supplied externally. This result does not estimate
the actual game value of the opponent's first, second, or later bonus card.

The terminal hand-value function remains an abstraction. A deck-specific model
should derive it from executable setup and first-turn lines.

The model assumes the same deck composition and hand-value function after each
reshuffle. It does not yet incorporate opponent-revealed information that can
change the hand valuation between attempts.

## Next work

Two extensions now look especially useful:

1. propagate the count-dependent policy into the final accepted-opening Prize
   distribution instead of reporting only expected utility and future
   mulligans;
2. derive a concrete marginal bonus-card value curve from an Expanded deck or
   matchup, then use that curve instead of synthetic costs.

The first extension is purely combinatorial and can be exact. The second
requires a richer gameplay value model.
