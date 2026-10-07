# Partial Prize inspection has quantifiable decision value

## Question

How much strategic value can one-card Prize inspection provide when the player still lacks exact Prize composition?

For two symmetric singleton-dependent lines, the effect has a simple exact form. Each additional distinct Prize identity learned contributes the same amount of expected line availability until all six Prizes are known.

Implementation:

- `tools/partial_prize_information.py`
- `tools/prize_belief_decision.py`

Reproducer: `results/partial_prize_information/reproduce.py`

## Baseline

Use the same post-opening abstraction as the earlier information-value result:

- 53 currently unknown card identities;
- 6 Prize cards among them;
- singleton A enables line A;
- singleton B enables line B;
- both lines have equal utility;
- a line is available exactly when its singleton is not Prized.

With no Prize identities inspected, the player must commit to A or B symmetrically.

The fixed-line availability is:

`47 / 53 = 88.679245283%`

If all six Prize identities are known, the player chooses whichever singleton is unprized and fails only when both A and B are Prized:

`98.911465893%`

The gap is the 10.232220610-percentage-point value of exact information from the earlier result.

## Finding 1: one random Prize inspection raises expected availability to 90.384615385%

Suppose the player looks at one randomly selected face-down Prize card before choosing between lines A and B.

There are three observation classes.

If the revealed Prize is A, which occurs with probability `1/53`, the player chooses B. Among the remaining 52 unknown cards, five are still Prized, so B is unprized with probability `47/52`.

The B-revealed case is symmetric.

If the revealed Prize is another card, which occurs with probability `51/53`, neither A nor B occupied the inspected position. Five uninspected Prize slots remain among the 52 remaining unknown identities. Either singleton line is therefore available with probability `47/52`.

Every observation class gives the same optimal expected availability:

`47 / 52 = 90.384615385%`

The value of inspecting one Prize is:

`47/52 - 47/53 = 1.705370102 percentage points`

in this symmetric model.

The generic belief evaluator independently reproduces the same result by conditioning on each observation class and averaging the resulting optimal policies.

## Finding 2: k distinct Prize inspections have a closed form

Let:

- `U` be the initial unknown population;
- `P` be the number of Prize cards;
- `k` be the number of distinct Prize identities inspected before committing;
- A and B be the two singleton line enablers.

If both A and B are among the inspected Prize cards, both lines fail.

Otherwise, the player can choose a singleton that was not observed among the inspected Prizes.

The probability that both A and B are in the inspected set is:

`k(k-1) / [U(U-1)]`

Conditional on having a singleton available to choose, the selected singleton avoids the remaining uninspected Prize slots with probability:

`(U-P)/(U-k)`

Multiplying and simplifying gives:

`V(k) = (U-P)(U+k-1) / [U(U-1)]`

For `U=53`, `P=6`:

| Distinct Prize identities inspected | Expected adaptive availability |
| ---: | ---: |
| 0 | 88.679245283% |
| 1 | 90.384615385% |
| 2 | 92.089985486% |
| 3 | 93.795355588% |
| 4 | 95.500725689% |
| 5 | 97.206095791% |
| 6 | 98.911465893% |

The final row equals the exact-information result.

## Finding 3: the marginal gain is constant in this symmetric case

The closed form is linear in `k`.

Each additional distinct inspected Prize contributes:

`(U-P) / [U(U-1)]`

to expected availability.

For `U=53`, `P=6`:

`47 / (53*52) = 1.705370102 percentage points`

per additional inspected Prize.

Therefore one of the six Prize identities captures exactly one sixth of the total exact-information value in this specific two-singleton symmetric model.

This equal marginal value is a property of the symmetry and payoff structure. It should not be generalized to arbitrary decks.

## Why partial information matters

The card-pool audit found legal effects that inspect only one Prize card or only part of the deck.

Those actions should be represented by an intermediate posterior.

For a real deck, the value of one Prize peek depends on:

- which cards enable competing lines;
- whether line utilities differ;
- duplicated copies;
- shared dependencies;
- current visible information;
- which Prize positions are already known;
- the decision deadline after the peek.

The generic one-Prize evaluator supports those asymmetric cases even when the simple closed form no longer applies.

## Relationship to information timing

A partial Prize-inspection attack can reveal useful information too late for current-turn main-phase decisions.

A partial Prize-inspection Item can reveal information earlier.

The value derived here is the benefit if the observation occurs before the relevant commitment.

The action's opportunity cost and timing must still be modeled separately.

## Validation

The reproducer verifies the result in two independent ways.

First, the general grouped belief evaluator:

1. builds the exact initial two-singleton Prize posterior;
2. enumerates the possible one-position observation categories;
3. conditions the belief on each observation;
4. chooses the best line under each posterior;
5. averages the values.

It obtains `47/52`.

Second, the closed-form function evaluates all `k=0..6` cases and asserts:

`V(k) = 47(52+k)/(53*52)`

It also checks that every consecutive difference equals:

`47/(53*52)`.

## Limitations

The model treats the inspected Prize positions as distinct random positions and assumes the player learns their identities.

It does not model the action required to inspect them, position-specific prior information, or physical effects that move the inspected cards.

The line model is deliberately binary and symmetric. Real utilities can make information value highly nonlinear.

## Next useful work

The general belief evaluator can be extended from one random Prize inspection to a sequence of position-aware observations.

That model should remember which physical Prize positions have already been inspected so later peeks cannot resample the same unknown position.

A richer version can then evaluate actual multi-peek cards and compare them with exact-information actions such as Town Map.
