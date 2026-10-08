# Nest Ball redundancy creates a small, nonmonotonic pre-Box inspection benefit

## Question

A state-local example with an already-held Nest Ball and another
searchable copy showed an 8.3333 percentage-point access advantage
from playing Nest Ball **before** Secret Box, because the deck is
inspected before Box's compulsory three-card payment.

The original 60-card illustrative deck had only one Nest Ball; its
exact accepted-opening mixture gave **zero** benefit from allowing
Nest-first ordering. What happens if one to four Nest Ball copies are
permitted, replacing other protected nonstarter cards?

Implementation: tools/secret_box_pre_nest_density.py.
Reproducer: results/secret_box_pre_nest_density/reproduce.py.
Underlying complete solver:
results/secret_box_pre_nest_information/ and
results/secret_box_pre_nest_opening_mix/.

## Model

In each row, the deck has exactly 60 cards:

- one Secret Box, conditioned to be held in the initial seven;
- D disposable cards, as specified;
- I Nest Ball copies, as specified;
- two Tool A, one Tool B, two Guzma & Hala, two Stadium S and one
  Special Energy E;
- P = 51 - D - I protected cards, of which exactly 12 are eligible
  Basic starters.

Condition on a valid Basic in the six other opening cards, then add
the next natural draw. Integrate six hidden Prizes exactly, including
how many eligible Basics survive in the searchable deck.

The terminal event requires A+B+S+E in hand **and** two compatible
Basic Tool holders. Nest Ball may be used after Box to build an extra
holder, or when held may be played before Box for both a Basic and
deck/Prize information.

In the "choice" policy, the player chooses the ordering based only
on the visible hand. It can adapt subsequent payments to observations
from a legally played Nest Ball. Item consumption and Box/G&H
two-stage discard costs are conserved.

## Exact probability results

The table is conditional on Box in the opening and a valid Basic
start. The sequencing gain is the difference between the two policy
columns, in **percentage points**.

| Disposable D | Nest Ball copies I | Box-first K0 | Best K0 ordering | Earlier-search gain |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 1 | 4.840384% | 4.840384% | **0.000000 pp** |
| 10 | 2 | 7.642098% | 7.644791% | **0.002693 pp** |
| 10 | 3 | 9.803331% | 9.804633% | **0.001302 pp** |
| 20 | 1 | 24.144851% | 24.144851% | **0.000000 pp** |
| 20 | 2 | 31.212215% | 31.219974% | **0.007759 pp** |
| 20 | 3 | 35.222532% | 35.224927% | **0.002395 pp** |
| 20 | 4 | 38.521637% | 38.522097% | **0.000460 pp** |
| 30 | 2 | 61.166930% | 61.176426% | **0.009497 pp** |

Two Nest Ball copies introduce a strictly positive advantage from
legally inspecting the deck before paying Box. The best action order
improves over Box-first in just **four distinct visible hand classes**
for each tested two-Nest-Ball configuration.

With D20 and two Nest Ball copies, those four classes have only
**0.126349% combined probability** under the specified accepted
opening/turn draw distribution. The resulting earlier-search gain
is **0.0077586397 percentage points**.

Increasing Nest Ball copies further increases the frequency of
initially held Nest Ball options, but it also creates more redundant
paths through which Box-first can complete the terminal objective.
The earlier-search gain falls in the tested three- and four-copy
cases. This is an observed nonmonotonicity in the toy composition,
not a general optimization theorem about all Item densities.

With D30 and I2 the gain reaches 0.009497 points. This remains tiny
relative to the state-local 8.333-point witness.

## Interpretation

This distinguishes three different effects which should not be
conflated:

1. **Item-package access:** Increasing I from one to two copies
   can increase Box-first success by multiple percentage points.
   This gain includes better ability to search/bench extra Basics
   and obtain disposable/replacement Items.
2. **Information timing:** Of that change, the incremental value
   of allowing a held Nest Ball to be played before Box is less than
   0.01 points in every tested 60-card composition.
3. **State selection:** Positive 8.333-point local witnesses can be
   valid yet rare in an actual opening distribution.

These rates all measure one narrow two-Tool acquisition plus
Basic-holder objective. Adding Item cards also displaces other
cards in a real deck, and the model does not score any strategic
value of those displaced cards beyond the protected/disposable
classification.

## Validation

All opening-hand probabilities are exact combinatorial integers,
and hidden-Prize/action policies are optimized using rational
arithmetic. No Monte Carlo is used.

The underlying prior-Nest information policy was independently
tested against 36 small labeled physical-card hidden-Prize trees,
and a 512-case scan verifies the K0 upper bound, the high-disposable
payment dominance and 16 local ordering witnesses.

The full 60-card accepted-opening evaluator separately checks that
the Box-first result and clairvoyant upper exactly match the earlier
Nest Ball Prize study. This density extension executes the same
verified function on eight physical 60-card compositions, checking
the information bound and state-mass bound per configuration.

The GitHub Actions workflow is
.github/workflows/validate-secret-box-pre-nest-density.yml;
run **37832329190** passed.

## Limits and further work

The two target Tools may be acquired in hand but are not actually
attached by the executor. All Basic holders are treated as
Tool-compatible and otherwise unoccupied. Stadium play, Energy
attachment, evolution, attack timing, opponent lock/pressure and
matchup utility are omitted.

A stronger conclusion would require actual Expanded list models
where prior Nest Ball searches also serve useful setup purposes
regardless of information value. One cannot infer that running
two Nest Ball copies is worthwhile purely because the extra copy
produces a nonzero information premium.
