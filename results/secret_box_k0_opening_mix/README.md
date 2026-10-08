# Population-weighted Secret Box K0 payment uncertainty

## Question

A fixed visible hand can show a large information leak if an optimizer chooses
Secret Box's required three-card discard payment knowing which cards are
Prized. In results/secret_box_k0_payment/, one exact state exhibited a
**6.73307 percentage-point** clairvoyance overstatement.

How much does that failure affect average *Box-first acquisition* when the
opening hand, accepted Basic, one subsequent natural draw and six hidden
Prizes are sampled correctly?

Implementation: tools/secret_box_k0_opening_mix.py.
Independent validation: results/secret_box_k0_opening_mix/reproduce.py.

## Exact distribution

The same abstract 60-card deck is used:

| Category | Copies |
| --- | ---: |
| Secret Box | 1 |
| Disposable stock D | 20 |
| Item I | 1 |
| Tool A | 2 |
| Tool B | 1 |
| Guzma & Hala | 2 |
| Stadium S | 2 |
| Special Energy E | 1 |
| Protected cards P | 30 |
| Total | 60 |

Exactly **12 of the 30 protected P cards are eligible Basic starters**.

Condition on Secret Box being present in the seven-card opening hand and
at least one of the other six being an eligible Basic. Then draw one card
at the start of the player's turn. Allow a Supporter play, so the Box-first
Guzma & Hala line is available in the usual first-turn-going-second case.

The Prize cards were placed before the turn draw. For a uniformly shuffled
deck, draw-first, then sample six Prizes from the 52 still unseen cards,
has the **same joint distribution**. The calculation uses that equivalent
order to integrate hidden Prize composition for each visible hand.

The weighted opening distribution is computed with exact combinations:

1. Partition the six other initial cards into nine categories (seven
   functional groups, eligible Basics, and other protected cards).
2. Require at least one Basic before the draw.
3. Weight each opening vector by the product of its binomial multiplicities.
4. Add each possible drawn card with its remaining count.
5. Collapse the two protected categories back to P.
6. For each visible hand, invoke the exact K0 versus clairvoyant Prize
   payment solver with its remaining 52 unknown cards.

This produces **548 distinct visible category states**. The sum of their
integer weights equals the exact conditional sample denominator.

## Main result

The terminal acquisition target remains two distinct Tools A+B, a Stadium
S, and a Special Energy E **in hand**, under the specified Box-first model.

| Conditional acquisition model | Exact success |
| --- | ---: |
| K1: Prize-informed Box payment | **34.397029107298%** |
| K0: genuinely pre-search Box payment | **34.324040910714%** |
| Overstatement from clairvoyance | **0.072988196584 percentage points** |

All results are exact rational mixtures:

- K1 = 212294030549929 / 617187111967426.
- K0 = 211843556807353 / 617187111967426.
- Difference = 1575083016 / 2157996894991.

Only **10 of 548** visible category states have a positive K1-K0 gap.
Their combined conditional probability is **1.175914022310%**.
A hand with no payment ambiguity, or a hand for which all candidate
payments have the same relevant hidden-state outcome, has zero gap.

The most influential visible class is D,D,A,G,P,P,P, with a conditional
hand probability of 0.872079% and within-hand K1-K0 gap of 6.001217%.
Its contribution to the overall overstatement is **0.052335
percentage points**, most of the aggregate. The previous fixed witness
D,D,A,G,S,P,P occurs with probability 0.146906% in the opening mixture
and contributes about 0.009891 points.

## Interpretation

Large hidden-state errors in selected positions need **frequency weights**
before they become overall consistency estimates.

The 6.733-point single-position overstatement is genuine in its own state.
The full accepted-opening mixture shrinks it into an overall 0.073-point
difference for this abstract deck and terminal objective. The latter is
still a policy-semantic correction; it should not be advertised as a
meaningful tournament win-rate difference without matchup and downstream
execution evidence.

The result also emphasizes that the first deck search can reveal exact
Prize composition while the costs *preceding* that search must be chosen
using the earlier information state.

## Validation

A second evaluator explicitly enumerates physically labeled opening
subsets and draw choices for a smaller 14-card deck, verifying the
combinatorial mixture on **121 visible states / 3,465 weighted orders**.
The hidden-Prize subproblem was independently checked against 48 labeled
Prize-policy cases in results/secret_box_k0_payment/. Exact fractions,
the 548-state partition, gap-bearing mass and the 60-card aggregate
are asserted under CI. No Monte Carlo sampling is used.

## Limits and next work

Everything is conditional on Box already being in the initial hand and
a valid starter. The model checks acquisition in hand and assumes a
permitted Box Item action followed by at most one G&H Supporter.
The chosen 60-card composition is illustrative, not a real competitive
decklist; P/D classification is fixed to this scenario.

Additional search effects before Box, G&H-first order, Tool attachment,
Stadium play, locks, changing DCI, real Prize-taking, opponent responses,
and damage exchanges could change both the state frequencies and value of
the information gap. A future optimizer should track pre-search
information availability while optimizing a more realistic terminal
matchup utility.
