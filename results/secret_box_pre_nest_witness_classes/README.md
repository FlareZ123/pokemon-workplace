# Which opening hands actually prefer Nest Ball before Secret Box?

## Question and prior work

The exact accepted-opening model at
[secret_box_pre_nest_density](../secret_box_pre_nest_density/)
reported a small **0.007758639694 percentage-point**
Nest-first information advantage for a D20/I2 deck.
This follow-up extracts the entire strict preference set and
decomposes its population-weighted gain.

Reproducer: [reproduce.py](reproduce.py).
The underlying conditional action solver is
tools/secret_box_pre_nest_information.py. The accepted-opening
weights come from tools/secret_box_k0_bench_bootstrap.py.

## Scope and conditioning

The 60-card abstract composition is Secret Box 1, disposable D20,
Nest Ball I2, Tool A2, Tool B1, Guzma & Hala G2,
Stadium S2, Special Energy E1, protected P29.
Exactly 12 P cards are eligible Basic starters.

Condition on Secret Box in the starting seven and at least one Basic
among the other six opening cards; add one natural turn draw and place
six hidden Prizes among the remaining 52 unknown cards.
Because initial deck and Prize order is exchangeable, sampling
draw before Prize composition conditionally gives the same distribution.
The seven counted cards in each class **exclude Secret Box**.

The endpoint is acquisition in hand of A, B, S, E with two available
compatible Basic Tool holders. The modeled actions are:

* Box-first: select one three-card discard before observing hidden
  Prizes, then search and optionally use Nest Ball and G&H.
* Nest-first: play an already-held Nest Ball onto the Bench, inspect the
  remaining deck, then choose Box's required discard using the newly
  revealed Prize complement.

Both use a K0 policy for their initial commitment.
Post-observation searches are optimized, conserving the Item and
Supporter consumption. No attack execution, actual Tool attachments,
opponent lock or matchup win-rate is modeled.

## Exhaustive strict-preference classes

All **four** classes prefer Nest Ball-first. None other does.
A class is a typed card multiset after the natural draw, excluding
the held Secret Box. Exactly one eligible Basic is among its P cards.

| Visible hand class | Class frequency | Box-first K0 | Nest-first K0 | Conditional gain | Population contribution |
| --- | ---: | ---: | ---: | ---: | ---: |
| D2 I1 A1 G1 P2 | 0.102282918% | 64.012983262% | 70.014200443% | +6.001217181 pp | +0.006138220053 pp |
| D2 I1 A1 G1 S1 P1 | 0.012033284% | 66.208550523% | 72.941623458% | +6.733072935 pp | +0.000810209820 pp |
| D2 I1 B1 G1 S1 P1 | 0.006016642% | 72.941623458% | 79.674696392% | +6.733072935 pp | +0.000405104910 pp |
| D2 I1 A1 B1 G1 P1 | 0.006016642% | 72.941623458% | 79.674696392% | +6.733072935 pp | +0.000405104910 pp |

Aggregate exact sequencing advantage:
**310943664/4007708519269** of conditional openings, or
**0.007758639694 percentage points**.

The classes jointly occupy exactly
**109440/86616893 = 0.126349487045%**
of the accepted-opening distribution.
The first class alone contributes **79.114642%**
of the aggregate sequencing gain.

The broader eligible event, an already-held Nest Ball plus exactly
one visible Basic holder, has exact mass
**808056/7874263 = 10.261988963285%**.
Just **1.231238%** of eligible mass occurs in the four classes
where Nest Ball-first is strictly advantageous.
Conditional on this eligible event, the expected increase is
**0.075605613316 percentage points**.

## Causal interpretation

In every beneficial class, hand D=2. Box's three-card cost
therefore requires sacrificing something more strategically valuable
if Box goes first. Nest Ball-first consumes an Item and guarantees
the additional holder when a Basic is searchable, but also
provides deck information *before* the third Box payment is selected.
The hidden Prize configuration can change which
of the other held A/B/G/S categories is safe to discard.

The remaining Nest Ball copy is initially unknown. It can be
searchable after Box or can be Prized, which helps distinguish
the two orders. The earlier I1-only 60-card mixture had no strictly
improving class, as shown in
[secret_box_pre_nest_opening_mix](../secret_box_pre_nest_opening_mix/).

With three truly inert disposable cards already held, paying D3
before any inspection weakly dominates payments sacrificing a useful
category in this model, so an early peek has zero marginal value.
All four strict-preference classes respect that invariant.

These are **state-local access calculations**, conditional on an
illustrative composition. They do not justify a Nest Ball count or
predict a change in tournament outcomes.

## Reproducibility and checks

Run the Python reproducer from the repository root at
results/secret_box_pre_nest_witness_classes/reproduce.py. It:

1. Enumerates accepted initial-six card compositions and one turn draw
   with integer combinatorial weights, retaining visible Basic count.
2. Visits every eligible class with Nest Ball in hand and exactly
   one visible Basic.
3. Invokes the exact pre-Nest K0 policy and records every
   positive improvement class.
4. Verifies four classes, full decomposition of gain, previously
   published exact gain to printed precision, beneficial-state mass,
   information bounds, and the high-disposable no-improvement condition.

GitHub Actions validation:
[run 38060487399, passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38060487399).

## Next questions

The four-class policy is an optimal decision for a restricted acquisition
endpoint. In a real deck, playing Nest Ball first also changes placement,
Item resources, bench occupancy and future draw sequencing. A stronger
follow-up should introduce an explicit early board/tool attachment state
and measure the marginal value of the early search while preserving
lock-relevant Tools such as Stealthy Hood. Another avenue is to examine
whether different Basic-search Items can supply the same information
without a second-holder requirement.
