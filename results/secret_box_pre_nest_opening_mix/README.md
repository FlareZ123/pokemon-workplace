# Earlier Nest Ball inspection: real local gains, zero in one opening mixture

## Question

An already-held Nest Ball can be played before Secret Box, revealing
the remaining deck and its Prize complement before Box's irreversible
three-card payment. That sequencing gained **8.333333 percentage
points** in a specific 24-card, two-Prize state in
results/secret_box_pre_nest_information/.

Does this local gain persist after exact opening-hand weighting in the
illustrative 60-card deck used by the other Secret Box studies?

Implementation: tools/secret_box_pre_nest_opening_mix.py.
Reproducer: results/secret_box_pre_nest_opening_mix/reproduce.py.

## Probability model

Use the 60-card composition:
Box1, D20, Nest Ball I1, Tool A2, Tool B1, G&H2, Stadium2,
Special Energy1, P30 including 12 eligible Basic starters.

Condition on Box among the initial seven, a valid Basic starter among
the other six, then one natural draw. Account for six Prizes hidden
among the remaining cards and the exact Basic count visible after the
draw.

Every visible state receives a K0 Box-first outcome from the
physically conserving Prize/Nest Ball model. If **one Basic is visible
and a Nest Ball is held**, allow the player to choose Nest Ball-first
instead. The choice is made before Prize revelation and is evaluated
across all compatible Prize worlds.

With two or more visible Basics, prior Nest Ball inspection is
unnecessary for the two-holder acquisition endpoint.

## Exact result

| Model | Box-conditioned, Basic-valid acquisition success |
| --- | ---: |
| Box-first, K0 payment | **24.144851389344%** |
| Optimally choose Nest Ball-first or Box-first with K0 knowledge | **24.144851389344%** |
| Clairvoyant pre-payment upper bound | 24.175106171172% |
| Gain from allowing Nest Ball-first | **exactly zero** |

The exact Box-first and choice-optimized value is
21288415854103 / 88169587423918.

The probability of a visible state with exactly one eligible Basic and
Nest Ball already held is
427248 / 7874263 = **5.425879221967%**.

Across all **1,241 typed visible-hand states**, none improves from
choosing Nest Ball before Box in this composition. The remaining
clairvoyant information gap is 0.030254781828 percentage points.

The result holds for the selected terminal objective and illustrated
deck. It cannot invalidate the previous 8.333-point positive local
witness, which includes a second Nest Ball outside the visible hand.

## Why the difference matters

The local witness has a Nest Ball in hand and a **second Nest Ball
searchable** in the deck. The 60-card baseline has only one Nest Ball
total. Conditioning on it being held eliminates the possibility that
Secret Box fetches a replacement Item.

The exact null result reveals how deeply a sequencing advantage can
depend on target redundancy. A search that gives early information
may still reduce accessible downstream resource channels by consuming
a strategically valuable unique Item.

This is a concrete example of state-local option value disappearing
after considering the composition and frequency of actual opening
hands. It does not establish that a second Nest Ball is always
necessary, or that Nest Ball-first is never useful with other Item
packages.

## Validation

The opening model integrates exact combinatorial accepted-hand and
turn-draw weights over 1,241 distinct typed visible states. It uses
the independently validated K0 hidden-Prize policy for both action
orders and verifies that the optional choice never decreases
success.

Its baseline Box-first and upper values exactly reproduce
results/secret_box_nest_ball_k0/.

The first-action K0 solver's Nest Ball-first branch was independently
checked against a labeled physical-card Prize and payment oracle
in 36 bounded cases, with a wider 512-case action-order regression.
No Monte Carlo sampling is used.

GitHub Actions runs 37832134011 and 37832142318 passed.

## Next work

Vary Nest Ball density from one to four copies in the fixed-size deck,
replacing protected nonstarter filler. Recompute the K0 advantage of
an earlier search across accepted openings. This will test whether
the extra copy required by the most prominent state-level witnesses
produces any material frequency-weighted improvement.
